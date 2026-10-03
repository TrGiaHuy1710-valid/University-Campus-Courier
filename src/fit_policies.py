"""Suy ra chiến thuật từng robot từ nhãn train, dùng chú thích scenes.json làm đầu vào hoàn hảo.

    python src/fit_policies.py                # fit trên train, chấm train + validation, ghi policy_params.json
    python src/fit_policies.py --robots 3 5   # chỉ fit lại một số robot (giữ nguyên các robot khác)
    python src/fit_policies.py --search-conditions   # tìm lại cả cách tách điều kiện (chậm hơn)

Cách làm: với mỗi robot và mỗi cách tách điều kiện (không tách / mưa / gấp / dễ vỡ),
chạy coordinate descent trên lưới tham số chi phí, rồi giữ cách tách cho accuracy cao nhất.
"""
import argparse
import json
import time
from multiprocessing import Pool

from policies import PARAMS_PATH, DEFAULT_TIE_BREAK, condition_value, predict
from scene_graph import Graph, load_split, scene_labels

ROBOTS_JSON = PARAMS_PATH.parent / "delivery_public" / "robots.json"

PLAN_GRID = {
    "crowded": [1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 15],
    "covered": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.5, 2],
    "stairs_cost": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6],
    "turn_right": [0, 0.25, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5],
    "turn_left": [0, 0.25, 0.5, 1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 6],
    "turn_uturn": [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 20, 30, 50, 100],
    "oneway_cost": [0, 0.5, 1, 2],
    "first_turn": [True, False],
}
GREEDY_GRID = {
    "crowded": [0, 0.3, 0.5, 1, 1.5],
    "covered": [-0.3, 0, 0.3, 0.5],
}
CONDITIONS = [None, "rain", "urgent", "fragile"]
# Điều kiện đã tìm ra ở lần chạy với --search-conditions (dùng mặc định để fit nhanh).
KNOWN_CONDITION = {0: None, 1: None, 2: None, 3: "rain", 4: "rain", 5: None,
                   6: "urgent", 7: "fragile", 8: None, 9: None}
# Mô tả dễ đọc của quy tắc đã suy ra (ghi kèm vào policy_params.json).
RULE_TEXT = {
    0: "Ít cạnh nhất (mọi đoạn chi phí 1).",
    1: "Đường đông tốn 6, còn lại 1.",
    2: "Đường mái che tốn 0.5, còn lại 1.",
    3: "Mưa: mái che tốn 0.2 (rất thích mái che). Khô: đường đông tốn 3.",
    4: "Đi được bậc thang; đường đông tốn 2. Mưa: mỗi đoạn bậc thang tốn thêm 4. Khô: bậc thang không tốn thêm.",
    5: "Ít cạnh + mỗi lần rẽ trái/phải tốn 3, quay đầu tốn 30 (tính cả bước đầu so với hướng mũi).",
    6: "Gấp: ít cạnh nhất. Không gấp: đường đông tốn 5, mái che 0.9.",
    7: "Dễ vỡ: đường đông tốn 7, rẽ tốn 1.5, quay đầu tốn 15. Không dễ vỡ: ít cạnh nhất.",
    8: "Ít cạnh + rẽ phải tốn 0.5, rẽ trái tốn 4.5, quay đầu tốn 9.",
    9: "Tham lam: chọn đích trước mắt (via nếu có) là bản gần ô xuất phát nhất theo Manhattan "
       "(hòa thì (hàng, cột) nhỏ hơn); đi sang ô kề có Manhattan tới đích nhỏ nhất, đường đông +0.3.",
}
COMMON_RULES = [
    "Bỏ cạnh đóng, không đi ngược đường một chiều, chỉ robot 4 đi bậc thang.",
    "Có via: tối ưu tổng chi phí start→via→goal (trạng thái giữ cả hướng để tính phí rẽ).",
    "Tham chiếu không gian chỉ rõ thì dùng đúng ô đó; nếu loại địa điểm có 2 bản và không chỉ rõ, "
    "robot lập kế hoạch chọn bản cho tổng chi phí nhỏ nhất.",
    "Hòa chi phí: ưu tiên đi thẳng > rẽ phải > rẽ trái > quay đầu so với hướng mũi robot.",
]


# Điểm khởi đầu cho coordinate descent: chi phí đơn vị, "cấm quay đầu", và các mức phạt rẽ.
SEEDS = [{}, {"turn_uturn": 100},
         {"turn_right": 3, "turn_left": 3, "turn_uturn": 30},
         {"crowded": 7, "turn_right": 1.5, "turn_left": 1.5, "turn_uturn": 15},
         {"turn_right": 0.5, "turn_left": 4.5, "turn_uturn": 9}]
# Bước dịch chuyển kết hợp: đặt rẽ phải = rẽ trái cùng lúc.
TURN_BOTH = [0, 0.25, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]


def plan_params(flat, legged):
    return {
        "edge": {"normal": 1, "crowded": flat["crowded"], "covered": flat["covered"]},
        "turn": [0, flat["turn_right"], flat["turn_left"], flat["turn_uturn"]],
        "legged": legged,
        "stairs_cost": flat["stairs_cost"] if legged else 0,
        "first_turn": flat["first_turn"],
        "oneway_cost": flat["oneway_cost"],
    }


def greedy_params(flat, legged):
    return {"edge_penalty": {"normal": 0, "crowded": flat["crowded"], "covered": flat["covered"]},
            "legged": legged}


# ---- dữ liệu dùng chung cho các tiến trình con ----
_G = _L = None


def _init(split):
    global _G, _L
    _, labels, scenes = load_split(split)
    _G = [Graph(s) for s in scenes]
    _L = scene_labels(labels)


def _acc(job):
    robot, kind, flat, legged, idx = job
    build = greedy_params if kind == "greedy" else plan_params
    spec = {"kind": kind, "condition": None, "params": {"default": build(flat, legged)}}
    return sum(predict(_G[i], spec) == _L[i][robot] for i in idx)


def initial_flat(kind, grid):
    if kind == "greedy":
        return {k: 0 for k in grid}
    flat = {k: 0 for k in grid}
    flat.update(crowded=1, covered=1, first_turn=True, stairs_cost=0)
    return flat


def coordinate_descent(pool, robot, kind, legged, idx, seed, sweeps=4):
    grid = GREEDY_GRID if kind == "greedy" else PLAN_GRID
    if kind == "plan" and not legged:
        grid = {k: v for k, v in grid.items() if k != "stairs_cost"}
    flat = dict(initial_flat(kind, grid), **seed)
    best = pool.map(_acc, [(robot, kind, flat, legged, idx)])[0]
    for _ in range(sweeps):
        improved = False
        for key, values in grid.items():
            cands = [dict(flat, **{key: v}) for v in values if v != flat[key]]
            scores = pool.map(_acc, [(robot, kind, c, legged, idx) for c in cands])
            if scores and max(scores) > best:
                j = scores.index(max(scores))
                best, flat, improved = scores[j], cands[j], True
        if kind == "plan":
            cands = [dict(flat, turn_right=v, turn_left=v) for v in TURN_BOTH]
            scores = pool.map(_acc, [(robot, kind, c, legged, idx) for c in cands])
            if max(scores) > best:
                j = scores.index(max(scores))
                best, flat, improved = scores[j], cands[j], True
        if not improved or best == len(idx):
            break
    return flat, best


def fit_branch(pool, robot, kind, legged, idx):
    seeds = [{}] if kind == "greedy" else SEEDS
    return max((coordinate_descent(pool, robot, kind, legged, idx, sd) for sd in seeds), key=lambda r: r[1])


def fit_robot(pool, robot, kind, legged, graphs, n_search, conditions):
    build = greedy_params if kind == "greedy" else plan_params
    results = []
    for cond in conditions:
        params, correct, total = {}, 0, 0
        values = ["default"] if cond is None else ["true", "false"]
        for val in values:
            idx = [i for i, g in enumerate(graphs) if condition_value(g, cond) == val][:n_search]
            flat, ok = fit_branch(pool, robot, kind, legged, idx)
            params[val] = build(flat, legged)
            correct, total = correct + ok, total + len(idx)
            print(f"    {cond}={val}: {ok}/{len(idx)} {flat}", flush=True)
        acc = correct / total
        print(f"  robot {robot} condition={cond}: {acc:.4f}", flush=True)
        results.append((acc, cond is None, cond, params))
        if cond is None and acc == 1.0:
            break
    acc, _, cond, params = max(results, key=lambda r: (round(r[0], 4), r[1]))
    return {"kind": kind, "condition": cond, "params": params}


def evaluate(robots, split):
    _, labels, scenes = load_split(split)
    L = scene_labels(labels)
    per = {}
    for r in sorted(robots):
        ok = sum(predict(Graph(s), robots[r], DEFAULT_TIE_BREAK) == L[i][r] for i, s in enumerate(scenes))
        per[r] = ok / len(scenes)
    return sum(per.values()) / len(per), per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--robots", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--n-search", type=int, default=800, help="số cảnh train tối đa mỗi nhánh điều kiện khi tìm")
    ap.add_argument("--search-conditions", action="store_true",
                    help="thử mọi cách tách điều kiện thay vì dùng KNOWN_CONDITION")
    a = ap.parse_args()

    meta = {r["robot_id"]: r for r in json.loads(ROBOTS_JSON.read_text(encoding="utf-8"))}
    old = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))["robots"] if PARAMS_PATH.exists() else {}
    robots = {int(k): v for k, v in old.items()}

    _, _, scenes = load_split("train")
    graphs = [Graph(s) for s in scenes]
    t0 = time.time()
    with Pool(initializer=_init, initargs=("train",)) as pool:
        for r in a.robots:
            kind = "greedy" if r == 9 else "plan"
            print(f"fit robot {r} ({meta[r]['name']}, {kind})", flush=True)
            conds = CONDITIONS if a.search_conditions else [KNOWN_CONDITION[r]]
            spec = fit_robot(pool, r, kind, meta[r]["legged"], graphs, a.n_search, conds)
            spec["name"] = meta[r]["name"]
            spec["rule"] = RULE_TEXT[r]
            robots[r] = spec
    print(f"fit xong sau {time.time() - t0:.0f}s")

    report = {}
    for split in ("train", "validation"):
        macro, per = evaluate(robots, split)
        report[split] = {"macro_accuracy": round(macro, 4), "per_robot": {str(k): round(v, 4) for k, v in per.items()}}
        print(split, f"macro={macro:.4f}", {k: round(v, 4) for k, v in per.items()})

    out = {
        "description": "Chiến thuật suy ra từ nhãn train với đồ thị lấy từ scenes.json (oracle perception).",
        "common_rules": COMMON_RULES,
        "tie_break": DEFAULT_TIE_BREAK,
        "tie_break_meaning": "thứ tự ưu tiên khi hòa, theo kiểu rẽ so với hướng mũi: 0=thẳng, 1=phải, 2=trái, 3=quay đầu",
        "robots": {str(k): robots[k] for k in sorted(robots)},
        "oracle_accuracy": report,
    }
    PARAMS_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"đã ghi {PARAMS_PATH}")


if __name__ == "__main__":
    main()
