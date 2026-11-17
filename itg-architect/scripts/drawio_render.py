# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a diagram model (JSON) into a draw.io file with official AWS (mxgraph.aws4) icons.

Usage:
  python scripts/drawio_render.py model.json --out L1-account.drawio [--url-file viewer_url.txt]
  python scripts/drawio_render.py model.json --check        # validate only, print JSON report

Model format: see assets/model.example.json. Coordinates of groups/nodes are relative to their parent group.
Exit codes: 0 ok, 2 bad arguments / unreadable model, 3 model validation errors (unknown service, missing ref, bad parent).
"""
import argparse
import base64
import json
import sys
import urllib.parse
import zlib
from xml.sax.saxutils import escape

COLORS = {"compute": "#ED7100", "storage": "#7AA116", "database": "#C925D1", "networking": "#8C4FFF",
          "integration": "#E7157B", "security": "#DD344C", "management": "#E7157B", "ml": "#01A88D",
          "devtools": "#C925D1", "general": "#232F3E"}
# service -> (kind, aws4 name, color group, verified-by-render)
SERVICES = {
    "ec2": ("res", "ec2", "compute", True), "batch": ("res", "batch", "compute", True),
    "ecr": ("res", "ecr", "compute", True), "lambda": ("res", "lambda", "compute", True),
    "ecs": ("res", "ecs", "compute", False), "fargate": ("res", "fargate", "compute", False),
    "ebs": ("res", "elastic_block_store", "storage", True), "s3": ("res", "s3", "storage", True),
    "efs": ("res", "elastic_file_system", "storage", False), "rds": ("res", "rds", "database", False),
    "dynamodb": ("res", "dynamodb", "database", True), "elasticache": ("res", "elasticache", "database", False),
    "sqs": ("res", "sqs", "integration", True), "sns": ("res", "sns", "integration", False),
    "eventbridge": ("res", "eventbridge", "integration", True), "step_functions": ("res", "step_functions", "integration", False),
    "api_gateway": ("res", "api_gateway", "networking", True), "cloudfront": ("res", "cloudfront", "networking", True),
    "route_53": ("res", "route_53", "networking", True), "nat": ("shape", "nat_gateway", "networking", True),
    "vpc_endpoint": ("shape", "endpoints", "networking", True), "waf": ("res", "waf", "security", True),
    "guardduty": ("res", "guardduty", "security", True), "kms": ("res", "key_management_service", "security", True),
    "secrets_manager": ("res", "secrets_manager", "security", False), "iam": ("res", "identity_and_access_management", "security", False),
    "cognito": ("res", "cognito", "security", True), "config": ("res", "config", "management", True),
    "cloudwatch": ("res", "cloudwatch_2", "management", True), "systems_manager": ("res", "systems_manager", "management", False),
    "cost_explorer": ("res", "cost_explorer", "storage", True), "bedrock": ("res", "bedrock", "ml", True),
    "codebuild": ("res", "codebuild", "devtools", True), "users": ("shape", "users", "general", True),
}
GROUPS = {
    "aws_cloud": ("group_aws_cloud_alt", "#232F3E", "none", "#232F3E", 0),
    "region": ("group_region", "#00A4A6", "none", "#147EBA", 1),
    "vpc": ("group_vpc2", "#8C4FFF", "none", "#AAB7B8", 0),
    "subnet_private": ("group_security_group", "#00A4A6", "#E6F6F7", "#147EBA", 0),
    "subnet_public": ("group_security_group", "#7AA116", "#F2F6E8", "#248814", 0),
}
GROUP_BASE = ("outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;"
              "collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;verticalAlign=top;align=left;spacingLeft=30;")
EDGE_KIND = {"normal": ("#545B64", 0), "cost": ("#DD344C", 1), "async": ("#545B64", 1)}


def html_label(text):
    return escape(str(text).replace("\n", "<br>"), {'"': "&quot;"})


def validate(model):
    errors, warnings = [], []
    ids = set()
    for g in model.get("groups", []):
        if g["id"] in ids:
            errors.append(f"duplicate id {g['id']}")
        ids.add(g["id"])
        if g.get("type") not in GROUPS and g.get("type") != "box":
            errors.append(f"group {g['id']}: unknown type {g.get('type')!r} (use {sorted(GROUPS) + ['box']})")
    gids = {g["id"] for g in model.get("groups", [])}
    for g in model.get("groups", []):
        if g.get("parent") and g["parent"] not in gids:
            errors.append(f"group {g['id']}: parent {g['parent']!r} not found")
    refs = set(model.get("resources", {}).keys()) if isinstance(model.get("resources"), dict) else None
    for n in model.get("nodes", []):
        if n["id"] in ids:
            errors.append(f"duplicate id {n['id']}")
        ids.add(n["id"])
        svc = SERVICES.get(n.get("service"))
        if not svc:
            errors.append(f"node {n['id']}: unknown service {n.get('service')!r}; add it to references/drawio-aws4.md + SERVICES first")
        elif not svc[3]:
            warnings.append(f"node {n['id']}: service {n['service']!r} not render-verified yet, check the image")
        if n.get("group") and n["group"] not in gids:
            errors.append(f"node {n['id']}: group {n['group']!r} not found")
        if refs is not None and n.get("ref") and n["ref"] not in refs:
            errors.append(f"node {n['id']}: ref {n['ref']!r} not in resources table")
        if refs is not None and not n.get("ref") and n.get("service") != "users":
            warnings.append(f"node {n['id']}: no ref to a resource row")
    for e in model.get("edges", []):
        for k in ("from", "to"):
            if e.get(k) not in ids:
                errors.append(f"edge {e.get('from')}->{e.get('to')}: {k} not found")
        if not e.get("label"):
            warnings.append(f"edge {e.get('from')}->{e.get('to')}: no label")
        if e.get("kind", "normal") not in EDGE_KIND:
            errors.append(f"edge {e.get('from')}->{e.get('to')}: kind must be one of {sorted(EDGE_KIND)}")
    return errors, warnings


def render(model):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    cid = lambda x: "n_" + x
    if model.get("title"):
        cells.append(f'<mxCell id="title" value="{html_label(model["title"])}" style="text;html=1;whiteSpace=wrap;align=left;fontSize=14;fontStyle=1;" vertex="1" parent="1">'
                     f'<mxGeometry x="20" y="0" width="1400" height="24" as="geometry"/></mxCell>')
    for g in model.get("groups", []):
        if g["type"] == "box":
            style = (f"rounded=1;arcSize=4;whiteSpace=wrap;html=1;verticalAlign=top;align=left;spacingLeft=8;fontSize=12;fontStyle=1;"
                     f"strokeColor={g.get('stroke', '#545B64')};fillColor={g.get('fill', '#F2F3F3')};dashed=1;container=1;collapsible=0;")
        else:
            icon, stroke, fill, font, dashed = GROUPS[g["type"]]
            style = GROUP_BASE + f"grIcon=mxgraph.aws4.{icon};strokeColor={stroke};fillColor={fill};fontColor={font};dashed={dashed};"
        parent = cid(g["parent"]) if g.get("parent") else "1"
        cells.append(f'<mxCell id="{cid(g["id"])}" value="{html_label(g.get("label", ""))}" style="{style}" vertex="1" parent="{parent}">'
                     f'<mxGeometry x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" as="geometry"/></mxCell>')
    for n in model.get("nodes", []):
        kind, name, cgroup, _ = SERVICES[n["service"]]
        color = COLORS[cgroup]
        common = ("sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;dashed=0;verticalLabelPosition=bottom;"
                  "verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;")
        if kind == "res":
            style = common + f"fillColor={color};strokeColor=#ffffff;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{name};"
        else:
            style = common + f"fillColor={color};strokeColor=none;pointerEvents=1;shape=mxgraph.aws4.{name};"
        size = n.get("size", 48)
        parent = cid(n["group"]) if n.get("group") else "1"
        cells.append(f'<mxCell id="{cid(n["id"])}" value="{html_label(n.get("label", ""))}" style="{style}" vertex="1" parent="{parent}">'
                     f'<mxGeometry x="{n["x"]}" y="{n["y"]}" width="{size}" height="{size}" as="geometry"/></mxCell>')
    for i, e in enumerate(model.get("edges", [])):
        color, dashed = EDGE_KIND[e.get("kind", "normal")]
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor={color};strokeWidth=1.5;"
                 f"dashed={dashed};fontSize=10;fontColor={color};labelBackgroundColor=#ffffff;")
        cells.append(f'<mxCell id="e{i}" value="{html_label(e.get("label", ""))}" style="{style}" edge="1" parent="1" '
                     f'source="{cid(e["from"])}" target="{cid(e["to"])}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    w, h = model.get("page", {}).get("w", 1600), model.get("page", {}).get("h", 1000)
    return (f'<mxfile host="app.diagrams.net"><diagram name="{html_label(model.get("name", "architecture"))}" id="d1">'
            f'<mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="{w}" pageHeight="{h}" math="0" shadow="0"><root>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")


def viewer_url(xml):
    enc = urllib.parse.quote(xml, safe="-_.!~*'()")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = base64.b64encode(c.compress(enc.encode()) + c.flush()).decode()
    return "https://viewer.diagrams.net/?lightbox=1&nav=1#R" + urllib.parse.quote(data, safe="")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", help="model JSON file (see assets/model.example.json)")
    ap.add_argument("--out", help="output .drawio path")
    ap.add_argument("--url-file", help="write a viewer.diagrams.net preview URL to this file")
    ap.add_argument("--check", action="store_true", help="validate only")
    a = ap.parse_args()
    try:
        model = json.load(open(a.model, encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print(f"cannot read model: {ex}", file=sys.stderr)
        return 2
    errors, warnings = validate(model)
    report = {"errors": errors, "warnings": warnings, "groups": len(model.get("groups", [])),
              "nodes": len(model.get("nodes", [])), "edges": len(model.get("edges", []))}
    if errors or a.check:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 3 if errors else 0
    if not a.out:
        print("--out is required unless --check", file=sys.stderr)
        return 2
    xml = render(model)
    open(a.out, "w", encoding="utf-8").write(xml)
    report["out"] = a.out
    if a.url_file:
        open(a.url_file, "w", encoding="utf-8").write(viewer_url(xml))
        report["url_file"] = a.url_file
    for w in warnings:
        print("warning: " + w, file=sys.stderr)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
