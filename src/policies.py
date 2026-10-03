"""Chiến thuật của 10 robot, dựng từ tham số trong policy_params.json.

Mỗi robot có:
  kind      : "plan" (Dijkstra với chi phí) hoặc "greedy" (chỉ nhìn một bước)
  condition : null | "rain" | "urgent" | "fragile" — trường quyết định bộ tham số nào được dùng
  params    : {"default": {...}} hoặc {"true": {...}, "false": {...}} theo condition
Quy tắc phá hòa chung: ưu tiên theo kiểu rẽ so với hướng mũi robot (tie_break).
"""
import json
from pathlib import Path

from planner import action_costs, optimal_actions, targets
from scene_graph import turn_kind

PARAMS_PATH = Path(__file__).resolve().parent.parent / "policy_params.json"

# 0 = thẳng, 1 = rẽ phải, 2 = rẽ trái, 3 = quay đầu
DEFAULT_TIE_BREAK = [0, 1, 2, 3]


def condition_value(g, condition):
    if condition is None:
        return "default"
    if condition == "rain":
        return "true" if g.rain else "false"
    return "true" if g.mission[condition] else "false"


def break_tie(g, actions, tie_break):
    rank = {k: i for i, k in enumerate(tie_break)}
    return min(actions, key=lambda a: rank[turn_kind(g.heading, a)])


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def greedy_target(g):
    """Đích trước mắt (via nếu có): bản gần ô xuất phát nhất theo Manhattan, hòa thì lấy (hàng, cột) nhỏ hơn."""
    goal, via = targets(g)
    tg = via if via else goal
    return min(tg, key=lambda t: (manhattan(g.start, t), t))


def greedy_scores(g, p):
    """Robot tham lam: điểm = Manhattan từ ô kề tới đích trước mắt + phạt nhỏ theo trạng thái đường."""
    tg = greedy_target(g)
    out = {}
    for act, v, status, stairs in g.adj[g.start]:
        if stairs and not p.get("legged", False):
            continue
        out[act] = manhattan(v, tg) + p["edge_penalty"][status]
    return out


def scores(g, spec):
    p = spec["params"][condition_value(g, spec.get("condition"))]
    if spec["kind"] == "greedy":
        return greedy_scores(g, p)
    return action_costs(g, p)


def predict(g, spec, tie_break=DEFAULT_TIE_BREAK):
    sc = scores(g, spec)
    opt = optimal_actions(sc)
    if not opt:
        # Không có đường hợp lệ: đi theo hướng mũi nếu được, ngược lại 0.
        return g.heading
    return break_tie(g, opt, tie_break)


def load_params(path=PARAMS_PATH):
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    robots = {int(k): v for k, v in cfg["robots"].items()}
    return robots, cfg.get("tie_break", DEFAULT_TIE_BREAK)


def predict_scene(g, robots, tie_break=DEFAULT_TIE_BREAK):
    return [predict(g, robots[r], tie_break) for r in range(10)]
