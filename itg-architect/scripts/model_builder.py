"""Write a diagram model in ABSOLUTE page coordinates; save it in the parent-relative format drawio_render.py reads.

Why: edge "points" are absolute while groups / nodes are relative to their parent, so hand-written models drift and
edges end up crossing labels. Placing everything in page coordinates and computing anchors with p() keeps routes exact.

    from model_builder import Model
    M = Model("L2 stage", "Title …", 2460, 1240)
    M.res("nat", "EC2 isx-stage-nat t3.nano (terraform/stage-network/nat.tf)")
    M.group("cloud", "aws_cloud", "AWS Cloud", 150, 40, 2060, 1180)
    M.group("vpc", "vpc", "VPC …", 970, 120, 1200, 350, parent="cloud")
    M.node("nat", "nat", "isx-stage-nat<br>NAT t3.nano", 1076, 230, group="vpc", ref="nat")
    M.edge("cf", "ec2", "VPC origin", exit=[1, 0.5], entry=[0, 0.5], points=[[420, 274], [420, 224]])
    M.p("cf", 0.25, 0)        # absolute [x, y] of a node anchor, for points
    M.save("L2-stage.model.json")

Groups must be declared before their children (parents first).
"""
import json


class Model:
    def __init__(self, name, title, w, h):
        self.m = {"name": name, "title": title, "page": {"w": w, "h": h}, "resources": {}, "groups": [], "nodes": [], "edges": []}
        self.abs = {}  # id -> (x, y, w, h) in page coordinates

    def res(self, key, text):
        self.m["resources"][key] = text

    def group(self, gid, gtype, label, x, y, w, h, parent=None, **kw):
        self.abs[gid] = (x, y, w, h)
        g = {"id": gid, "type": gtype, "label": label, "w": w, "h": h, **kw}
        if parent:
            px, py, _, _ = self.abs[parent]
            g.update(parent=parent, x=x - px, y=y - py)
        else:
            g.update(x=x, y=y)
        self.m["groups"].append(g)

    def node(self, nid, service, label, x, y, group=None, size=48, ref=None):
        self.abs[nid] = (x, y, size, size)
        n = {"id": nid, "service": service, "label": label, "size": size}
        if group:
            gx, gy, _, _ = self.abs[group]
            n.update(group=group, x=x - gx, y=y - gy)
        else:
            n.update(x=x, y=y)
        if ref:
            n["ref"] = ref
        self.m["nodes"].append(n)

    def p(self, nid, fx, fy):
        """Absolute point of a node at fractions (fx, fy) of its box: (1, 0.5) = right middle."""
        x, y, w, h = self.abs[nid]
        return [round(x + w * fx), round(y + h * fy)]

    def edge(self, a, b, label="", kind="normal", exit=None, entry=None, points=None):
        e = {"from": a, "to": b, "label": label}
        if kind != "normal":
            e["kind"] = kind
        if exit:
            e["exit"] = exit
        if entry:
            e["entry"] = entry
        if points:
            e["points"] = points
        self.m["edges"].append(e)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.m, f, ensure_ascii=False, indent=2)
            f.write("\n")
