"""Thống kê tổng quan bộ dữ liệu Phenikaa Campus Courier v2.

    python src/data_overview/data_stats.py              # in báo cáo + ghi src/data_overview/stats.json

Train/validation: thống kê đầy đủ từ observations, labels và scenes.json.
Test: chỉ thống kê cấu trúc (số dòng, định dạng/kích thước ảnh). Không đọc nội dung câu
yêu cầu của test, vì luật thi cấm dùng nội dung test để viết luật hay từ điển.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from scene_graph import ACTIONS, DATA, HEADING, load_split, scene_labels, turn_kind  # noqa: E402

TURN_NAMES = ["thẳng", "rẽ phải", "rẽ trái", "quay đầu"]
NEGATIONS = ["không", "khong", "đừng", "dung ", "chẳng", "chang ", "chưa", "chua "]


def pct(n, d):
    return round(100 * n / d, 1) if d else 0.0


def summary(values):
    v = sorted(values)
    if not v:
        return {}
    return {"min": v[0], "median": v[len(v) // 2], "mean": round(sum(v) / len(v), 2), "max": v[-1]}


def image_stats(split, image_paths):
    fmt, sizes = Counter(), Counter()
    for p in image_paths:
        with Image.open(DATA / split / p) as im:
            fmt[im.format] += 1
            sizes[f"{im.width}x{im.height}"] += 1
    return {"format": dict(fmt), "top_sizes": dict(sizes.most_common(8)), "n_distinct_sizes": len(sizes)}


def scene_stats(scenes):
    n = len(scenes)
    out = {}

    out["style"] = dict(Counter(s["style"] for s in scenes))
    deg = [s["degradation"] for s in scenes]
    out["degradation"] = {
        "rotation_deg": summary([d["rotation_deg"] for d in deg]),
        "pct_rotated": pct(sum(d["rotation_deg"] != 0 for d in deg), n),
        "pct_blur": pct(sum(d["blur"] > 0 for d in deg), n),
        "pct_jpeg": pct(sum(d["jpeg_quality"] is not None for d in deg), n),
        "jpeg_quality": summary([d["jpeg_quality"] for d in deg if d["jpeg_quality"] is not None]),
    }
    swapped = [s for s in scenes if any(k != v for k, v in s["road_look"].items())]
    out["legend_swapped"] = {"pct_scenes": pct(len(swapped), n),
                             "patterns": dict(Counter(json.dumps(s["road_look"], sort_keys=True)
                                                      for s in swapped).most_common(6))}

    grid, missing, n_edges, density = Counter(), [], [], []
    status, stairs, oneway = Counter(), 0, 0
    for s in scenes:
        R, C = s["grid"]["rows"], s["grid"]["cols"]
        grid[f"{R}x{C}"] += 1
        missing.append(R * C - len(s["nodes"]))
        n_edges.append(len(s["edges"]))
        density.append(len(s["edges"]) / (R * (C - 1) + C * (R - 1)))
        for e in s["edges"]:
            status[e["status"]] += 1
            stairs += e["stairs"]
            oneway += e["oneway_to"] is not None
    total_e = sum(status.values())
    out["grid"] = {
        "rows_x_cols_top": dict(grid.most_common(10)),
        "rows": summary([s["grid"]["rows"] for s in scenes]),
        "cols": summary([s["grid"]["cols"] for s in scenes]),
        "missing_nodes_per_scene": summary(missing),
        "edges_per_scene": summary(n_edges),
        "edge_density_vs_full_grid": summary([round(d, 3) for d in density]),
        "edge_status_pct": {k: pct(v, total_e) for k, v in status.most_common()},
        "pct_edges_stairs": pct(stairs, total_e),
        "pct_edges_oneway": pct(oneway, total_e),
    }

    lm_types, n_lm, dup_types = Counter(), [], Counter()
    for s in scenes:
        c = Counter(l["type"] for l in s["landmarks"])
        n_lm.append(len(s["landmarks"]))
        lm_types.update(c)
        for t, k in c.items():
            if k > 1:
                dup_types[t] += 1
    out["landmarks"] = {"per_scene": summary(n_lm), "type_count": dict(lm_types.most_common()),
                        "scenes_with_duplicate_type": dict(dup_types.most_common()),
                        "pct_scenes_any_duplicate": pct(sum(
                            any(v > 1 for v in Counter(l["type"] for l in s["landmarks"]).values())
                            for s in scenes), n)}

    out["robot_heading"] = dict(Counter(s["robot"]["heading"] for s in scenes))
    out["weather"] = dict(Counter(s["weather"] for s in scenes))

    m = [s["mission"] for s in scenes]
    texts = [x["text"] for x in m]
    goal_dup = sum(sum(l["type"] == x["goal"] for l in s["landmarks"]) > 1 for s, x in zip(scenes, m))
    out["mission"] = {
        "chars": summary([len(t) for t in texts]),
        "words": summary([len(t.split()) for t in texts]),
        "pct_no_diacritics": pct(sum(t.isascii() for t in texts), n),
        "pct_has_negation_word": pct(sum(any(w in t.lower() for w in NEGATIONS) for t in texts), n),
        "goal_type": dict(Counter(x["goal"] for x in m).most_common()),
        "pct_with_via": pct(sum(x["via"] is not None for x in m), n),
        "via_type": dict(Counter(x["via"] for x in m if x["via"]).most_common()),
        "pct_goal_duplicated_on_map": pct(goal_dup, n),
        "goal_ref_kind": dict(Counter(x["goal_ref"]["kind"] for x in m if x["goal_ref"])),
        "via_ref_kind": dict(Counter(x["via_ref"]["kind"] for x in m if x["via_ref"])),
        "pct_urgent": pct(sum(x["urgent"] for x in m), n),
        "pct_fragile": pct(sum(x["fragile"] for x in m), n),
    }
    return out


def label_stats(scenes, labels):
    L = scene_labels(labels)
    n = len(L)
    per_robot = {}
    for r in range(10):
        ys = [L[i][r] for i in range(n)]
        turns = Counter(turn_kind(HEADING[scenes[i]["robot"]["heading"]], L[i][r]) for i in range(n))
        per_robot[str(r)] = {
            "action_pct": {ACTIONS[a]: pct(c, n) for a, c in sorted(Counter(ys).items())},
            "vs_heading_pct": {TURN_NAMES[k]: pct(c, n) for k, c in sorted(turns.items())},
            "agree_with_robot0_pct": pct(sum(L[i][r] == L[i][0] for i in range(n)), n),
        }
    distinct = Counter(len(set(l)) for l in L)
    return {
        "per_robot": per_robot,
        "distinct_actions_per_scene_pct": {str(k): pct(v, n) for k, v in sorted(distinct.items())},
        "pct_all_10_agree": pct(distinct.get(1, 0), n),
    }


def main():
    report = {}
    for split in ("train", "validation", "test"):
        rows, labels, scenes = load_split(split)
        images = sorted({r["image"] for r in rows})
        rep = {"rows": len(rows), "scenes": len(rows) // 10, "images": len(images),
               "has_labels": labels is not None, "has_scenes_json": scenes is not None,
               "image": image_stats(split, images)}
        if scenes is not None:
            rep.update(scene_stats(scenes))
        if labels is not None:
            rep["labels"] = label_stats(scenes, labels)
        report[split] = rep
        print(f"=== {split} ===")
        print(json.dumps(rep, ensure_ascii=False, indent=1))

    (HERE / "stats.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"đã ghi {HERE / 'stats.json'}")


if __name__ == "__main__":
    main()
