"""Khảo sát dữ liệu cho khâu CV (ảnh → đồ thị), ghi báo cáo Markdown.

    python src/inspect_data.py --data-root delivery_public --out docs/DATA_NOTES_stats.md
    python src/inspect_data.py --data-root delivery_public --check-images   # mở mọi ảnh để đối chiếu kích thước

Chỉ đọc train và validation (scenes.json). Không đọc test.
Quy ước "look" (kiểu vẽ) dùng làm lớp cho EdgePatchNet:
    look(status, road_look) = road_look[status] nếu status ∈ {normal, crowded, covered}, ngược lại "closed".
"""
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

LOOKS = ["normal", "crowded", "covered", "closed"]
EDGE_LOOK_CLASSES = ["none"] + LOOKS  # "none" = cặp kề nhau không có đường
LANDMARKS = ["library", "dorm", "sports", "clinic", "canteen", "parking", "lecture", "lab", "office", "gate"]
ONEWAY = ["none", "forward", "backward"]  # forward = được đi a → b (a là giao lộ trên/trái)


def look_of(status, road_look):
    return road_look[status] if status in road_look else "closed"


def oneway_class(edge):
    if edge["oneway_to"] is None:
        return "none"
    return "forward" if edge["oneway_to"] == edge["b"] else "backward"


def quantiles(values, qs=(0, 0.05, 0.25, 0.5, 0.75, 0.95, 1)):
    v = sorted(values)
    if not v:
        return "–"
    return " / ".join(f"{v[min(len(v) - 1, int(q * (len(v) - 1)))]:.3g}" for q in qs)


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "–"


def class_weights(counter, classes):
    total = sum(counter[c] for c in classes)
    k = len(classes)
    inv = {c: total / (k * counter[c]) if counter[c] else 0.0 for c in classes}
    sq = {c: math.sqrt(w) for c, w in inv.items()}
    return inv, sq


def scene_d(s):
    """d = trung vị khoảng cách pixel giữa hai giao lộ kề nhau (theo rc, cả hai tồn tại)."""
    xy = {tuple(n["rc"]): n["xy"] for n in s["nodes"]}
    ds = []
    for (r, c), p in xy.items():
        for q in ((r + 1, c), (r, c + 1)):
            if q in xy:
                ds.append(math.dist(p, xy[q]))
    return median(ds)


def node_offsets(s, d):
    """Độ lệch tâm giao lộ khỏi đường thẳng hàng/cột (theo d), sau khi bỏ xoay toàn cục bằng trung vị."""
    rows, cols = defaultdict(list), defaultdict(list)
    for n in s["nodes"]:
        rows[n["rc"][0]].append(n["xy"][1])
        cols[n["rc"][1]].append(n["xy"][0])
    out = []
    for n in s["nodes"]:
        out.append(abs(n["xy"][1] - median(rows[n["rc"][0]])) / d)
        out.append(abs(n["xy"][0] - median(cols[n["rc"][1]])) / d)
    return out


def analyse(scenes):
    st = defaultdict(Counter)
    num = defaultdict(list)
    d_by_style = defaultdict(list)
    legend_text = defaultdict(Counter)
    for s in scenes:
        style = s["style"]
        st["style"][style] += 1
        st["weather"][s["weather"]] += 1
        st["heading"][s["robot"]["heading"]] += 1
        rl = s["road_look"]
        swapped = any(k != v for k, v in rl.items())
        st["road_look"][json.dumps(rl, sort_keys=True)] += 1
        st["swapped"][swapped] += 1
        st["swapped_by_style"][(style, swapped)] += 1
        st["size"][f"{s['width']}x{s['height']}"] += 1
        st["grid"][f"{s['grid']['rows']}x{s['grid']['cols']}"] += 1
        num["n_nodes"].append(len(s["nodes"]))
        num["missing_nodes"].append(s["grid"]["rows"] * s["grid"]["cols"] - len(s["nodes"]))
        num["n_landmarks"].append(len(s["landmarks"]))
        num["n_legend"].append(len(s["legend"]))

        d = scene_d(s)
        d_by_style[style].append(d)
        num["d_over_short_side"].append(d / min(s["width"], s["height"]))
        num["node_offset_over_d"].extend(node_offsets(s, d))

        deg = s["degradation"]
        num["rotation"].append(deg["rotation_deg"])
        num["blur"].append(deg["blur"])
        if deg["jpeg_quality"] is not None:
            num["jpeg_quality"].append(deg["jpeg_quality"])
        st["deg_flags"]["rotated"] += deg["rotation_deg"] != 0
        st["deg_flags"]["blur"] += deg["blur"] > 0
        st["deg_flags"]["jpeg"] += deg["jpeg_quality"] is not None
        st["ext"][s["image"].rsplit(".", 1)[1]] += 1
        st["deg_by_style"][(style, "rotated" if deg["rotation_deg"] != 0 else "-",
                            "blur" if deg["blur"] > 0 else "-", "jpeg" if deg["jpeg_quality"] else "-")] += 1
        kinds = [r["kind"] for r in s["legend"]]
        st["legend_order"][" > ".join("place*" if k.startswith("place:") else k for k in kinds
                                      if not (k.startswith("place:") and kinds[kinds.index(k) - 1].startswith("place:")
                                              and kinds.index(k) > 0))] += 1

        # Cạnh và cặp kề nhau
        nodes = {tuple(n["rc"]) for n in s["nodes"]}
        edges = {(tuple(e["a"]), tuple(e["b"])): e for e in s["edges"]}
        for (r, c) in nodes:
            for q in ((r + 1, c), (r, c + 1)):
                if q not in nodes:
                    continue
                e = edges.get(((r, c), q))
                if e is None:
                    st["pair"]["no_edge"] += 1
                    st["look"]["none"] += 1
                    st["look_by_style"][(style, "none")] += 1
                    continue
                st["pair"]["edge"] += 1
                st["status"][e["status"]] += 1
                lk = look_of(e["status"], rl)
                st["look"][lk] += 1
                st["look_by_style"][(style, lk)] += 1
                st["status_to_look"][(e["status"], lk)] += 1
                st["stairs"][e["stairs"]] += 1
                st["oneway"][oneway_class(e)] += 1
                st["oneway_dir"][("vertical" if q[0] != r else "horizontal", oneway_class(e))] += 1

        # Giao lộ: landmark / robot
        lm_at = {tuple(l["rc"]): l["type"] for l in s["landmarks"]}
        robot = tuple(s["robot"]["rc"])
        for n in nodes:
            st["node_landmark"][lm_at.get(n, "background")] += 1
            st["node_robot"][n == robot] += 1
        for t, k in Counter(lm_at.values()).items():
            st["landmark_dup"][k] += 1

        # Chú giải
        for row in s["legend"]:
            st["legend_kind"][row["kind"]] += 1
            legend_text[row["kind"]][row["text"]] += 1
            sw, lb = row["swatch"], row["label"]
            num["swatch_w_over_d"].append((sw[2] - sw[0]) / d)
            num["swatch_h_over_d"].append((sw[3] - sw[1]) / d)
            num["label_w_over_d"].append((lb[2] - lb[0]) / d)
            num["label_h_over_d"].append((lb[3] - lb[1]) / d)
            if row["kind"] in rl:
                st["legend_swatch_look"][(row["kind"], rl[row["kind"]])] += 1
        lx = min(r["swatch"][0] for r in s["legend"]) / s["width"]
        ly = min(r["swatch"][1] for r in s["legend"]) / s["height"]
        st["legend_pos"][(style, "right" if lx > 0.5 else "left", "bottom" if ly > 0.5 else "top")] += 1
        wb = s["weather_box"]
        num["weather_box_over_d"].append((wb[2] - wb[0]) / d)
        st["weather_pos"][(style, "right" if wb[0] / s["width"] > 0.5 else "left",
                           "bottom" if wb[1] / s["height"] > 0.5 else "top")] += 1
    return st, num, d_by_style, legend_text


def render(stats, out_path):
    L = []
    w = L.append
    w("# Thống kê dữ liệu cho khâu CV (sinh tự động bởi `src/inspect_data.py`)\n")
    w("Đọc kèm `docs/DATA_NOTES.md` (phần diễn giải và các quy ước đã chốt).\n")
    splits = list(stats)
    n = {sp: sum(stats[sp][0]["style"].values()) for sp in splits}

    def table(title, key, classes=None, transform=str):
        w(f"\n### {title}\n")
        w("| giá trị | " + " | ".join(splits) + " |")
        w("|---|" + "---|" * len(splits))
        keys = classes or sorted(set().union(*(stats[sp][0][key] for sp in splits)), key=str)
        for k in keys:
            cells = []
            for sp in splits:
                c = stats[sp][0][key]
                tot = sum(c.values())
                cells.append(f"{c[k]} ({pct(c[k], tot)})")
            w(f"| {transform(k)} | " + " | ".join(cells) + " |")

    def numeric(title, key, scale=1.0):
        w(f"\n### {title}\n")
        w("| split | min / p5 / p25 / median / p75 / p95 / max |")
        w("|---|---|")
        for sp in splits:
            w(f"| {sp} | {quantiles([x * scale for x in stats[sp][1][key]])} |")

    w("\n## 1. Kích thước\n")
    w("| split | cảnh |")
    w("|---|---|")
    for sp in splits:
        w(f"| {sp} | {n[sp]} |")
    table("Style", "style")
    table("Định dạng file ảnh", "ext")
    table("Kích thước ảnh (top)", "size",
          classes=[k for k, _ in (stats[splits[0]][0]["size"] + stats[splits[-1]][0]["size"]).most_common(12)])
    table("Lưới hàng×cột (top)", "grid",
          classes=[k for k, _ in (stats[splits[0]][0]["grid"] + stats[splits[-1]][0]["grid"]).most_common(15)])
    numeric("Số giao lộ mỗi cảnh", "n_nodes")
    numeric("Số giao lộ khuyết mỗi cảnh", "missing_nodes")
    numeric("Số địa điểm mỗi cảnh", "n_landmarks")
    numeric("Số dòng chú giải mỗi cảnh", "n_legend")

    w("\n## 2. Khoảng cách d giữa hai giao lộ kề nhau (pixel, trung vị mỗi cảnh)\n")
    w("| split | style | min / p5 / p25 / median / p75 / p95 / max |")
    w("|---|---|---|")
    for sp in splits:
        for style, ds in sorted(stats[sp][2].items()):
            w(f"| {sp} | {style} | {quantiles(ds)} |")
    numeric("d / cạnh ngắn của ảnh", "d_over_short_side")
    numeric("Độ lệch tâm giao lộ khỏi hàng/cột thẳng (theo d, gồm cả ảnh xoay)", "node_offset_over_d")

    w("\n## 3. Suy giảm chất lượng ảnh (degradation)\n")
    table("Tỉ lệ cảnh bị suy giảm (đếm cờ)", "deg_flags", classes=["rotated", "blur", "jpeg"])
    w("\n(tỉ lệ ở bảng trên là trên tổng số cờ; tỉ lệ trên số cảnh:)\n")
    for sp in splits:
        f = stats[sp][0]["deg_flags"]
        w(f"- {sp}: xoay {pct(f['rotated'], n[sp])}, mờ {pct(f['blur'], n[sp])}, JPEG {pct(f['jpeg'], n[sp])}")
    table("Suy giảm theo style (style, xoay, mờ, jpeg)", "deg_by_style",
          classes=sorted(set().union(*(stats[sp][0]["deg_by_style"] for sp in splits))))
    numeric("Góc xoay (độ, mọi cảnh)", "rotation")
    numeric("Blur (sigma, mọi cảnh)", "blur")
    numeric("Chất lượng JPEG (chỉ cảnh có nén)", "jpeg_quality")

    w("\n## 4. Chú giải hoán đổi (road_look)\n")
    table("Cảnh có road_look khác ánh xạ đồng nhất", "swapped", classes=[False, True])
    table("road_look (mọi mẫu)", "road_look")
    table("Hoán đổi theo style", "swapped_by_style",
          classes=sorted(set().union(*(stats[sp][0]["swapped_by_style"] for sp in splits))))
    table("status → look (trên các cạnh thật)", "status_to_look",
          classes=sorted(set().union(*(stats[sp][0]["status_to_look"] for sp in splits))))
    table("Dòng chú giải (kind → look của swatch)", "legend_swatch_look",
          classes=sorted(set().union(*(stats[sp][0]["legend_swatch_look"] for sp in splits))))

    w("\n## 5. Cặp giao lộ kề nhau: có cạnh / không có cạnh / đóng\n")
    table("Cặp kề nhau (cả hai giao lộ tồn tại)", "pair", classes=["edge", "no_edge"])
    table("Trạng thái cạnh (status)", "status", classes=LOOKS)

    w("\n## 6. Phân bố lớp cho từng task\n")
    for title, key, classes in [
        ("EdgePatchNet / look (gồm none = không có đường)", "look", EDGE_LOOK_CLASSES),
        ("EdgePatchNet / stairs (trên cạnh thật)", "stairs", [False, True]),
        ("EdgePatchNet / oneway (forward = đi được a→b)", "oneway", ONEWAY),
        ("NodePatchNet / landmark theo giao lộ", "node_landmark", ["background"] + LANDMARKS),
        ("NodePatchNet / có robot", "node_robot", [False, True]),
        ("NodePatchNet / heading (trên giao lộ có robot)", "heading", ["UP", "DOWN", "LEFT", "RIGHT"]),
        ("CropClsNet / legend kind", "legend_kind", None),
        ("CropClsNet / weather", "weather", ["dry", "rain"]),
    ]:
        table(title, key, classes)
        c = stats[splits[0]][0][key]
        cls = classes or sorted(c, key=str)
        inv, sq = class_weights(c, cls)
        w("\nClass weight (train): " + ", ".join(f"`{k}`: inv={inv[k]:.2f}, sqrt={sq[k]:.2f}" for k in cls))
    table("Look theo style (gồm none)", "look_by_style",
          classes=sorted(set().union(*(stats[sp][0]["look_by_style"] for sp in splits))))
    table("Oneway theo hướng đoạn", "oneway_dir",
          classes=sorted(set().union(*(stats[sp][0]["oneway_dir"] for sp in splits))))
    table("Số bản của một loại địa điểm trên cùng bản đồ", "landmark_dup", classes=[1, 2])

    w("\n## 7. Chú giải và thời tiết: vị trí, kích thước\n")
    table("Vị trí khối chú giải (style, ngang, dọc)", "legend_pos",
          classes=sorted(set().union(*(stats[sp][0]["legend_pos"] for sp in splits))))
    table("Vị trí biểu tượng thời tiết", "weather_pos",
          classes=sorted(set().union(*(stats[sp][0]["weather_pos"] for sp in splits))))
    table("Thứ tự dòng chú giải (place* = khối địa điểm liên tiếp)", "legend_order")
    numeric("Swatch rộng / d", "swatch_w_over_d")
    numeric("Swatch cao / d", "swatch_h_over_d")
    numeric("Label rộng / d", "label_w_over_d")
    numeric("Label cao / d", "label_h_over_d")
    numeric("Weather box cạnh / d", "weather_box_over_d")

    w("\n## 8. Chữ trong chú giải theo kind (train + validation)\n")
    merged = defaultdict(Counter)
    for sp in splits:
        for k, c in stats[sp][3].items():
            merged[k].update(c)
    w("| kind | các cách viết (số lần) |")
    w("|---|---|")
    for k in sorted(merged):
        w(f"| `{k}` | " + "; ".join(f"{t} ({c})" for t, c in merged[k].most_common()) + " |")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(L) + "\n", encoding="utf-8")


def check_images(data_root, split, scenes):
    from PIL import Image
    bad = 0
    modes = Counter()
    for s in scenes:
        with Image.open(Path(data_root) / split / s["image"]) as im:
            modes[im.mode] += 1
            bad += (im.width, im.height) != (s["width"], s["height"])
    print(f"{split}: {bad} ảnh lệch kích thước so với scenes.json; mode gốc: {dict(modes)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-root", type=Path, default=Path("delivery_public"))
    ap.add_argument("--out", type=Path, default=Path("docs/DATA_NOTES_stats.md"))
    ap.add_argument("--splits", nargs="*", default=["train", "validation"])
    ap.add_argument("--check-images", action="store_true")
    a = ap.parse_args()
    stats = {}
    for sp in a.splits:
        scenes = json.loads((a.data_root / sp / "scenes.json").read_text(encoding="utf-8"))
        stats[sp] = analyse(scenes)
        if a.check_images:
            check_images(a.data_root, sp, scenes)
    render(stats, a.out)
    print(f"đã ghi {a.out}")


if __name__ == "__main__":
    main()
