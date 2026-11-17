# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3"]
# ///
"""Read-only AWS inventory for architecture diagrams (describe/list/get calls only, never writes).

Usage:
  python -X utf8 scripts/aws_inventory.py --profile isx-vietnt --regions ap-northeast-1,ap-southeast-1 --output inventory.json
  python -X utf8 scripts/aws_inventory.py --regions ap-northeast-1 --costs 2026-10 --output inventory.json
  (after `aws login`, for boto3: eval "$(aws configure export-credentials --profile <p> --format env)"; unset AWS_PROFILE)

Collects per region: EC2 instances (Name, type, state, instance profile, VPC/subnet, Environment tag), VPCs, subnets,
NAT gateways, VPC endpoints, Batch compute environments, SQS queues, Lambda functions, and a tag census
(resource type x Environment / Name). Global: S3 buckets (region + tags), CloudFront distributions, IAM roles used
by instance profiles. --costs YYYY-MM adds amortized cost by tag Name (1 Cost Explorer request, $0.01).

Output: JSON to --output (or stdout). Progress/warnings to stderr. Each failed call is recorded under "errors"
(e.g. AccessDenied) instead of aborting.
Exit codes: 0 ok, 2 bad arguments, 3 no credentials / session expired (run `aws login`), 4 boto3 missing.
"""
import argparse
import collections
import datetime as dt
import json
import sys

try:
    import boto3
    import botocore.exceptions as bex
    from botocore.exceptions import ClientError, NoCredentialsError, TokenRetrievalError
except ImportError:
    print("boto3 is required: pip install boto3", file=sys.stderr)
    sys.exit(4)

# credential problems that mean "run aws login again" (LoginRefreshRequired exists only in newer botocore)
CRED_ERRORS = tuple(c for c in (NoCredentialsError, TokenRetrievalError, getattr(bex, "LoginRefreshRequired", None),
                                getattr(bex, "SSOTokenLoadError", None), getattr(bex, "UnauthorizedSSOTokenError", None)) if c)


def tagmap(tags):
    return {t["Key"]: t["Value"] for t in (tags or [])}


def safe(errors, label, fn):
    try:
        return fn()
    except CRED_ERRORS:
        raise
    except ClientError as ex:
        code = ex.response.get("Error", {}).get("Code", "ClientError")
        if code in ("ExpiredToken", "ExpiredTokenException", "UnrecognizedClientException", "InvalidClientTokenId"):
            raise NoCredentialsError()
        errors.append({"call": label, "error": code})
        print(f"warn: {label}: {code}", file=sys.stderr)
        return None


def paginate(client, op, key, **kw):
    out = []
    for page in client.get_paginator(op).paginate(**kw):
        out.extend(page.get(key, []))
    return out


def region_inventory(s, region, errors):
    ec2 = s.client("ec2", region_name=region)
    r = {"region": region}
    res = safe(errors, f"{region} ec2.describe_instances", lambda: paginate(ec2, "describe_instances", "Reservations"))
    r["ec2_instances"] = [{
        "id": i["InstanceId"], "name": tagmap(i.get("Tags")).get("Name"), "type": i["InstanceType"],
        "state": i["State"]["Name"], "vpc": i.get("VpcId"), "subnet": i.get("SubnetId"),
        "instance_profile": (i.get("IamInstanceProfile") or {}).get("Arn", "").split("/")[-1] or None,
        "environment": tagmap(i.get("Tags")).get("Environment"), "public_ip": bool(i.get("PublicIpAddress")),
    } for rv in (res or []) for i in rv["Instances"]]
    vpcs = safe(errors, f"{region} ec2.describe_vpcs", lambda: ec2.describe_vpcs()["Vpcs"]) or []
    r["vpcs"] = [{"id": v["VpcId"], "cidr": v["CidrBlock"], "name": tagmap(v.get("Tags")).get("Name"),
                  "environment": tagmap(v.get("Tags")).get("Environment"), "default": v.get("IsDefault")} for v in vpcs]
    subs = safe(errors, f"{region} ec2.describe_subnets", lambda: paginate(ec2, "describe_subnets", "Subnets")) or []
    r["subnets"] = [{"id": x["SubnetId"], "vpc": x["VpcId"], "cidr": x["CidrBlock"], "az": x["AvailabilityZone"],
                     "public": x.get("MapPublicIpOnLaunch"), "name": tagmap(x.get("Tags")).get("Name")} for x in subs]
    nats = safe(errors, f"{region} ec2.describe_nat_gateways", lambda: paginate(ec2, "describe_nat_gateways", "NatGateways")) or []
    r["nat_gateways"] = [{"id": n["NatGatewayId"], "vpc": n["VpcId"], "state": n["State"], "name": tagmap(n.get("Tags")).get("Name")} for n in nats]
    eps = safe(errors, f"{region} ec2.describe_vpc_endpoints", lambda: paginate(ec2, "describe_vpc_endpoints", "VpcEndpoints")) or []
    r["vpc_endpoints"] = [{"id": e["VpcEndpointId"], "vpc": e["VpcId"], "service": e["ServiceName"], "type": e["VpcEndpointType"],
                           "name": tagmap(e.get("Tags")).get("Name")} for e in eps]
    b = s.client("batch", region_name=region)
    ces = safe(errors, f"{region} batch.describe_compute_environments", lambda: paginate(b, "describe_compute_environments", "computeEnvironments")) or []
    r["batch_compute_envs"] = [{"name": c["computeEnvironmentName"], "state": c.get("state"), "type": c.get("type"),
                                "instance_types": (c.get("computeResources") or {}).get("instanceTypes"),
                                "alloc": (c.get("computeResources") or {}).get("type"),
                                "max_vcpus": (c.get("computeResources") or {}).get("maxvCpus")} for c in ces]
    sqs = s.client("sqs", region_name=region)
    r["sqs_queues"] = [u.rsplit("/", 1)[-1] for u in (safe(errors, f"{region} sqs.list_queues", lambda: sqs.list_queues().get("QueueUrls", [])) or [])]
    lam = s.client("lambda", region_name=region)
    fns = safe(errors, f"{region} lambda.list_functions", lambda: paginate(lam, "list_functions", "Functions")) or []
    r["lambda_functions"] = [{"name": f["FunctionName"], "runtime": f.get("Runtime"), "memory": f.get("MemorySize")} for f in fns]
    tg = s.client("resourcegroupstaggingapi", region_name=region)
    census = collections.Counter()
    untagged_name = []
    for m in (safe(errors, f"{region} tagging.get_resources", lambda: paginate(tg, "get_resources", "ResourceTagMappingList", ResourcesPerPage=100)) or []):
        arn = m["ResourceARN"]
        parts = arn.split(":")
        rtype = parts[2] + "/" + (parts[5].split("/")[0] if len(parts) > 5 else "")
        t = tagmap(m.get("Tags"))
        census[f"{rtype}|{t.get('Environment', '-')}"] += 1
        if "Name" not in t:
            untagged_name.append(rtype)
    r["tag_census"] = [{"type": k.split("|")[0], "environment": k.split("|")[1], "count": v} for k, v in sorted(census.items())]
    r["no_name_tag_by_type"] = dict(collections.Counter(untagged_name))
    return r


def global_inventory(s, errors, regions):
    g = {}
    s3 = s.client("s3")
    buckets = safe(errors, "s3.list_buckets", lambda: s3.list_buckets()["Buckets"]) or []
    out = []
    for bk in buckets:
        name = bk["Name"]
        loc = safe(errors, f"s3.get_bucket_location {name}", lambda: s3.get_bucket_location(Bucket=name).get("LocationConstraint")) or "us-east-1"
        tags = {}
        try:
            tags = tagmap(s3.get_bucket_tagging(Bucket=name).get("TagSet"))
        except ClientError:
            pass
        out.append({"name": name, "region": loc, "environment": tags.get("Environment"), "name_tag": tags.get("Name")})
    g["s3_buckets"] = out
    cw_by_region = collections.defaultdict(list)
    for b in out:
        if b["region"] in regions:
            cw_by_region[b["region"]].append(b["name"])
    sizes = {}
    end = dt.datetime.utcnow()
    for region, names in cw_by_region.items():
        cw = s.client("cloudwatch", region_name=region)
        q = [{"Id": f"m{i}", "MetricStat": {"Metric": {"Namespace": "AWS/S3", "MetricName": "BucketSizeBytes", "Dimensions": [
            {"Name": "BucketName", "Value": n}, {"Name": "StorageType", "Value": "StandardStorage"}]}, "Period": 86400, "Stat": "Average"}}
             for i, n in enumerate(names[:500])]
        resp = safe(errors, f"{region} cloudwatch.get_metric_data", lambda: cw.get_metric_data(MetricDataQueries=q, StartTime=end - dt.timedelta(days=3), EndTime=end))
        for m in (resp or {}).get("MetricDataResults", []):
            if m["Values"]:
                sizes[names[int(m["Id"][1:])]] = round(m["Values"][0] / 2**30, 1)
    for b in out:
        b["standard_gib"] = sizes.get(b["name"])
    cf = s.client("cloudfront")
    dists = safe(errors, "cloudfront.list_distributions", lambda: cf.list_distributions().get("DistributionList", {}).get("Items", [])) or []
    g["cloudfront"] = [{"id": d["Id"], "aliases": d.get("Aliases", {}).get("Items", []), "origins": [o["DomainName"] for o in d["Origins"]["Items"]],
                        "waf": bool(d.get("WebACLId"))} for d in dists]
    iam = s.client("iam")
    profiles = safe(errors, "iam.list_instance_profiles", lambda: paginate(iam, "list_instance_profiles", "InstanceProfiles")) or []
    g["instance_profiles"] = [{"name": p["InstanceProfileName"], "roles": [r["RoleName"] for r in p["Roles"]]} for p in profiles]
    return g


def costs_by_name(s, month, errors):
    start = dt.date.fromisoformat(month + "-01")
    end = (start.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    ce = s.client("ce", region_name="us-east-1")
    flt = {"Not": {"Dimensions": {"Key": "RECORD_TYPE", "Values": ["Credit", "Refund", "Tax"]}}}
    resp = safe(errors, "ce.get_cost_and_usage (TAG Name)", lambda: ce.get_cost_and_usage(
        TimePeriod={"Start": str(start), "End": str(min(end, dt.date.today()))}, Granularity="MONTHLY",
        Metrics=["AmortizedCost", "UnblendedCost"], GroupBy=[{"Type": "TAG", "Key": "Name"}], Filter=flt))
    if not resp:
        return None
    rows = [{"name": g["Keys"][0].split("$", 1)[1] or "(no Name tag)",
             "amortized": round(float(g["Metrics"]["AmortizedCost"]["Amount"]), 2),
             "unblended": round(float(g["Metrics"]["UnblendedCost"]["Amount"]), 2)} for t in resp["ResultsByTime"] for g in t["Groups"]]
    rows.sort(key=lambda x: -x["amortized"])
    return {"month": month, "ce_requests": 1, "metric": "AmortizedCost by tag Name",
            "total_unblended": round(sum(r["unblended"] for r in rows), 2), "by_name": rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", help="AWS profile (omit when credentials are exported to env)")
    ap.add_argument("--regions", required=True, help="comma separated, e.g. ap-northeast-1,ap-southeast-1")
    ap.add_argument("--costs", metavar="YYYY-MM", help="also fetch amortized cost by tag Name (1 Cost Explorer request, $0.01)")
    ap.add_argument("--output", help="write JSON here instead of stdout")
    a = ap.parse_args()
    regions = [x.strip() for x in a.regions.split(",") if x.strip()]
    if not regions:
        print("--regions is empty", file=sys.stderr)
        return 2
    s = boto3.Session(profile_name=a.profile) if a.profile else boto3.Session()
    errors = []
    try:
        ident = s.client("sts").get_caller_identity()
        data = {"collected_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "account": ident["Account"], "caller": ident["Arn"].split("/")[-1], "regions": []}
        for region in regions:
            print(f"region {region}…", file=sys.stderr)
            data["regions"].append(region_inventory(s, region, errors))
        print("global…", file=sys.stderr)
        data["global"] = global_inventory(s, errors, regions)
        if a.costs:
            print(f"cost explorer {a.costs} (1 request)…", file=sys.stderr)
            data["costs"] = costs_by_name(s, a.costs, errors)
    except CRED_ERRORS:
        print("no valid AWS credentials or session expired: run `aws login` (then export credentials for boto3)", file=sys.stderr)
        return 3
    data["errors"] = errors
    text = json.dumps(data, ensure_ascii=False, indent=1, default=str)
    if a.output:
        open(a.output, "w", encoding="utf-8").write(text)
        print(f"wrote {a.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
