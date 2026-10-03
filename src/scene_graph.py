"""Đọc dữ liệu và dựng đồ thị lưới từ chú thích scenes.json."""
import json
from pathlib import Path

ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
DELTA = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
HEADING = {name: i for i, name in enumerate(ACTIONS)}

DATA = Path(__file__).resolve().parent.parent / "delivery_public"


def load_split(split, data=DATA):
    d = Path(data) / split
    rows = json.loads((d / "observations.json").read_text(encoding="utf-8"))
    labels_p = d / "labels.json"
    labels = json.loads(labels_p.read_text(encoding="utf-8")) if labels_p.exists() else None
    scenes_p = d / "scenes.json"
    scenes = json.loads(scenes_p.read_text(encoding="utf-8")) if scenes_p.exists() else None
    return rows, labels, scenes


def scene_labels(labels):
    """Gom nhãn theo cảnh: mỗi cảnh có 10 dòng liên tiếp cho robot 0..9."""
    return [labels[i:i + 10] for i in range(0, len(labels), 10)]


def turn_kind(h_from, h_to):
    """0 = đi thẳng, 1 = rẽ phải, 2 = rẽ trái, 3 = quay đầu."""
    if h_from == h_to:
        return 0
    right = {0: 3, 3: 1, 1: 2, 2: 0}
    if right[h_from] == h_to:
        return 1
    if right[h_to] == h_from:
        return 2
    return 3


class Graph:
    """Đồ thị có hướng: adj[node] = [(action, neighbour, status, stairs), ...]."""

    def __init__(self, scene):
        self.nodes = {tuple(n["rc"]) for n in scene["nodes"]}
        self.adj = {n: [] for n in self.nodes}
        self.oneway = set()  # các cạnh có hướng (u, v) thuộc đường một chiều
        for e in scene["edges"]:
            if e["status"] == "closed":
                continue
            a, b = tuple(e["a"]), tuple(e["b"])
            one = tuple(e["oneway_to"]) if e["oneway_to"] else None
            for u, v in ((a, b), (b, a)):
                if one is not None and v != one:
                    continue
                act = next(k for k, (dr, dc) in DELTA.items() if (u[0] + dr, u[1] + dc) == v)
                self.adj[u].append((act, v, e["status"], e["stairs"]))
                if one is not None:
                    self.oneway.add((u, v))
        self.landmarks = {}
        for lm in scene["landmarks"]:
            self.landmarks.setdefault(lm["type"], []).append(tuple(lm["rc"]))
        self.start = tuple(scene["robot"]["rc"])
        self.heading = HEADING[scene["robot"]["heading"]]
        self.rain = scene["weather"] == "rain"
        self.mission = scene["mission"]
