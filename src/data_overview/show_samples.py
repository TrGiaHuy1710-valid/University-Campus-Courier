"""Vẽ chú thích của scenes.json đè lên ảnh để hiểu dữ liệu trông như thế nào.

    python src/data_overview/show_samples.py                  # 1 cảnh train cho mỗi kiểu vẽ
    python src/data_overview/show_samples.py --split validation --index 0 5 12

Ảnh lưu ở src/data_overview/samples/<split>_<index>.png, gồm bản gốc (trái) và bản có chú thích (phải):
  - chấm tím: tâm giao lộ (nodes[].xy)
  - đường màu: trạng thái THẬT của đoạn đường (xám=thường, cam=đông, xanh=mái che, đỏ=đóng)
  - S = bậc thang, mũi tên ngắn = hướng được đi của đường một chiều
  - khung xanh lá: swatch của chú giải, khung vàng: chữ của chú giải, khung tím: biểu tượng thời tiết
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from scene_graph import DATA, load_split  # noqa: E402

COLOUR = {"normal": (128, 128, 128), "crowded": (255, 140, 0), "covered": (0, 90, 255), "closed": (230, 0, 0)}
SHORT = {"library": "TV", "dorm": "KTX", "sports": "TT", "clinic": "YT", "canteen": "CA",
         "parking": "XE", "lecture": "GD", "lab": "TN", "office": "HC", "gate": "CT"}


def draw(split, index, out_dir):
    _, labels, scenes = load_split(split)
    s = scenes[index]
    orig = Image.open(DATA / split / s["image"]).convert("RGB")
    im = orig.copy()
    d = ImageDraw.Draw(im)
    xy = {tuple(n["rc"]): n["xy"] for n in s["nodes"]}
    for e in s["edges"]:
        a, b = xy[tuple(e["a"])], xy[tuple(e["b"])]
        d.line([tuple(a), tuple(b)], fill=COLOUR[e["status"]], width=5)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if e["stairs"]:
            d.text((mx + 5, my + 5), "S", fill=(0, 0, 0))
        if e["oneway_to"]:
            t = xy[tuple(e["oneway_to"])]
            tx, ty = mx + (t[0] - mx) * 0.4, my + (t[1] - my) * 0.4
            d.line([(mx, my), (tx, ty)], fill=(255, 0, 255), width=3)
            d.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=(255, 0, 255))
    for x, y in xy.values():
        d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=(160, 0, 200), width=2)
    for lm in s["landmarks"]:
        x, y = xy[tuple(lm["rc"])]
        d.text((x + 8, y - 20), SHORT[lm["type"]], fill=(160, 0, 200))
    rx, ry = xy[tuple(s["robot"]["rc"])]
    d.text((rx + 8, ry + 8), "R " + s["robot"]["heading"], fill=(160, 0, 200))
    for row in s["legend"]:
        d.rectangle(row["swatch"], outline=(0, 170, 0), width=2)
        d.rectangle(row["label"], outline=(220, 180, 0), width=2)
    d.rectangle(s["weather_box"], outline=(160, 0, 200), width=2)

    canvas = Image.new("RGB", (orig.width * 2 + 10, orig.height), "white")
    canvas.paste(orig, (0, 0))
    canvas.paste(im, (orig.width + 10, 0))
    out = out_dir / f"{split}_{index}.png"
    canvas.save(out)

    info = {k: s[k] for k in ("scene_id", "style", "grid", "robot", "weather", "road_look", "degradation")}
    info["mission"] = s["mission"]
    info["labels"] = dict(zip(range(10), labels[index * 10:index * 10 + 10]))
    print(json.dumps(info, ensure_ascii=False))
    print(f"đã lưu {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train", choices=["train", "validation"])
    ap.add_argument("--index", type=int, nargs="*")
    a = ap.parse_args()
    out_dir = HERE / "samples"
    out_dir.mkdir(exist_ok=True)
    idx = a.index
    if not idx:
        _, _, scenes = load_split(a.split)
        first = {}
        for i, s in enumerate(scenes):
            first.setdefault(s["style"], i)
        idx = sorted(first.values())
    for i in idx:
        draw(a.split, i, out_dir)


if __name__ == "__main__":
    main()
