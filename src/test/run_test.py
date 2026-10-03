"""Chạy chiến thuật trong policy_params.json trên một split và ghi output/<thời gian>/predictions.json.

    python src/test/run_test.py --split test                     # cần module đọc ảnh + câu (src/perception.py)
    python src/test/run_test.py --split validation --oracle      # dùng scenes.json thay cho đọc ảnh, để kiểm tra luồng

Test không có scenes.json, nên phải có src/perception.py cung cấp
    perceive(image_path: Path, mission: str) -> dict
trả về một cảnh cùng định dạng phần tử của scenes.json
(các khóa cần dùng: nodes, edges, landmarks, robot, weather, mission).
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
ROOT = SRC.parent
sys.path.insert(0, str(SRC))

from policies import load_params, predict_scene  # noqa: E402
from scene_graph import DATA, Graph, load_split  # noqa: E402


def scene_groups(rows):
    """Gom 10 dòng liên tiếp (robot 0..9) thành một cảnh."""
    for i in range(0, len(rows), 10):
        group = rows[i:i + 10]
        assert [r["robot_id"] for r in group] == list(range(10)), f"cảnh ở dòng {i} không đủ robot 0..9"
        assert len({(r["image"], r["mission"]) for r in group}) == 1, f"cảnh ở dòng {i} không cùng ảnh/yêu cầu"
        yield group


def load_perceive():
    try:
        from perception import perceive
    except ImportError:
        sys.exit("Chưa có src/perception.py (hàm perceive(image_path, mission) -> scene dict). "
                 "Test không có scenes.json nên cần khâu CV + NLP; "
                 "dùng --split validation --oracle để chạy thử luồng.")
    return perceive


def macro_accuracy(rows, labels, preds):
    per = {}
    for r in range(10):
        idx = [i for i, row in enumerate(rows) if row["robot_id"] == r]
        per[r] = sum(preds[i] == labels[i] for i in idx) / len(idx)
    return sum(per.values()) / 10, per


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="test", choices=["train", "validation", "test"])
    ap.add_argument("--oracle", action="store_true", help="dùng scenes.json thay cho perception (không có ở test)")
    ap.add_argument("--out-root", type=Path, default=ROOT / "output")
    a = ap.parse_args()

    rows, labels, scenes = load_split(a.split)
    if a.oracle and scenes is None:
        sys.exit(f"split {a.split} không có scenes.json, không chạy được --oracle")
    perceive = None if a.oracle else load_perceive()
    robots, tie_break = load_params()

    t0 = time.time()
    preds = []
    for k, group in enumerate(scene_groups(rows)):
        if a.oracle:
            scene = scenes[k]
        else:
            scene = perceive(DATA / a.split / group[0]["image"], group[0]["mission"])
        preds.extend(predict_scene(Graph(scene), robots, tie_break))
    assert len(preds) == len(rows)

    out_dir = a.out_root / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "predictions.json").write_text(json.dumps(preds), encoding="utf-8")

    meta = {"split": a.split, "mode": "oracle" if a.oracle else "perception",
            "rows": len(preds), "seconds": round(time.time() - t0, 1)}
    if labels is not None:
        macro, per = macro_accuracy(rows, labels, preds)
        meta["macro_accuracy"] = round(macro, 4)
        meta["per_robot"] = {str(r): round(v, 4) for r, v in per.items()}
        print(f"macro accuracy: {macro:.4f}", {r: round(v, 4) for r, v in per.items()})
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"đã ghi {len(preds)} dự đoán vào {out_dir / 'predictions.json'}")


if __name__ == "__main__":
    main()
