"""Experiment ENN: {{HYPOTHESIS_IN_ONE_SENTENCE}}.

{{CONTEXT — 2-3 sentences explaining what led to this experiment.
Reference the previous experiment's key finding that motivated
this hypothesis.}}
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src importable when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    # cfg = load_config("config.yaml")
    # dm = DataManager(cfg.data.db_path)
    # data = dm.load(...)
    print("Loading data...")

    # ------------------------------------------------------------------
    # 2. Define variants to compare
    # ------------------------------------------------------------------
    variants = [
        ("variant_a", dict(param1=1, param2="x")),
        ("variant_b", dict(param1=2, param2="y")),
    ]

    # ------------------------------------------------------------------
    # 3. Run each variant and collect metrics
    # ------------------------------------------------------------------
    rows = []
    for name, params in variants:
        print(f"Running {name}...")
        # result = run_one(**params)
        # metrics = compute_metrics(result)
        metrics = {"total_return_pct": 0.0, "sharpe": 0.0, "max_dd_pct": 0.0}
        row = {"variant": name, **params, **metrics}
        rows.append(row)
        print(f"  {name}: sharpe={row['sharpe']:.3f}  ret={row['total_return_pct']:.2f}%")

    # ------------------------------------------------------------------
    # 4. Build DataFrame and save
    # ------------------------------------------------------------------
    df = pd.DataFrame(rows)
    out = Path("results/exp_NN_{{TOPIC}}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    # ------------------------------------------------------------------
    # 5. Print sorted leaderboard
    # ------------------------------------------------------------------
    print("\n======= LEADERBOARD (by Sharpe) =======")
    print(df.sort_values("sharpe", ascending=False).to_string(index=False))
    print(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()
