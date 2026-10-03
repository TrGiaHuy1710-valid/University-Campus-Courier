"""Chấm chiến thuật trong policy_params.json trên đồ thị oracle (scenes.json), không fit lại.

    python src/evaluate_oracle.py                      # train + validation
    python src/evaluate_oracle.py --split validation --show-errors
"""
import argparse

from policies import load_params, predict_scene
from scene_graph import ACTIONS, Graph, load_split, scene_labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", nargs="*", default=["train", "validation"])
    ap.add_argument("--show-errors", action="store_true")
    a = ap.parse_args()
    robots, tie_break = load_params()
    for split in a.split:
        _, labels, scenes = load_split(split)
        L = scene_labels(labels)
        ok = [0] * 10
        for i, s in enumerate(scenes):
            pred = predict_scene(Graph(s), robots, tie_break)
            for r in range(10):
                ok[r] += pred[r] == L[i][r]
                if pred[r] != L[i][r] and a.show_errors:
                    print(f"  {s['scene_id']} robot {r}: nhãn {ACTIONS[L[i][r]]}, đoán {ACTIONS[pred[r]]}")
        per = [o / len(scenes) for o in ok]
        print(f"{split}: macro={sum(per) / 10:.4f}", {r: round(p, 4) for r, p in enumerate(per)})


if __name__ == "__main__":
    main()
