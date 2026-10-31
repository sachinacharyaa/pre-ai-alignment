
"""Toy experiment: proxy optimization and independent evaluation.

This is a synthetic simulation, not an LLM-agent evaluation.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from pathlib import Path


def clamp(value):
    return max(0.0, min(1.0, value))


def make_candidates(
    rng,
    n,
    proxy_noise=0.18,
    eval_noise=0.10,
    gaming_rate=0.25,
):
    rows = []

    for i in range(n):
        # Underlying quality of the candidate
        true_score = rng.random()

        # Original benchmark score
        noise = rng.gauss(0, proxy_noise)
        gaming = rng.random() < gaming_rate

        proxy_score = true_score + noise
        if gaming:
            proxy_score += 0.35

        proxy_score = clamp(proxy_score)

        # Separate evaluation: no gaming bonus
        independent_eval_score = clamp(
            true_score + rng.gauss(0, eval_noise)
        )

        rows.append({
            "candidate_id": i,
            "true_score": true_score,
            "proxy_score": proxy_score,
            "independent_eval_score": independent_eval_score,
            "gaming_flag": int(gaming),
        })

    return rows


def run_one(
    seed,
    candidates_per_round=40,
    rounds=10,
    gaming_rate=0.25,
    eval_noise=0.10,
):
    rng = random.Random(seed)
    all_rows = []

    for round_id in range(rounds):
        pool = make_candidates(
            rng,
            candidates_per_round,
            gaming_rate=gaming_rate,
            eval_noise=eval_noise,
        )

        # Random baseline
        baseline_pick = rng.choice(pool)

        # Optimizer selects using proxy score ONLY
        optimizer_pick = max(
            pool,
            key=lambda x: x["proxy_score"]
        )

        for policy, pick in (
            ("random_baseline", baseline_pick),
            ("proxy_optimizer", optimizer_pick),
        ):
            row = {
                "seed": seed,
                "round": round_id,
                "policy": policy,
                **pick,
            }
            all_rows.append(row)

    return all_rows


def summarize(rows):
    output = {}

    for policy in sorted({r["policy"] for r in rows}):
        subset = [r for r in rows if r["policy"] == policy]

        output[policy] = {
            "n": len(subset),
            "mean_proxy_score": statistics.mean(
                r["proxy_score"] for r in subset
            ),
            "mean_true_score": statistics.mean(
                r["true_score"] for r in subset
            ),
            "mean_independent_eval_score": statistics.mean(
                r["independent_eval_score"] for r in subset
            ),
            "proxy_minus_true": statistics.mean(
                r["proxy_score"] - r["true_score"]
                for r in subset
            ),
            "proxy_minus_independent": statistics.mean(
                r["proxy_score"] - r["independent_eval_score"]
                for r in subset
            ),
            "fraction_gaming_flagged": statistics.mean(
                r["gaming_flag"] for r in subset
            ),
        }

    return output


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--candidates", type=int, default=40)
    parser.add_argument("--gaming-rate", type=float, default=0.25)
    parser.add_argument("--eval-noise", type=float, default=0.10)
    parser.add_argument("--out", default="results_independent")

    args = parser.parse_args()

    if args.seeds < 1 or args.rounds < 1 or args.candidates < 2:
        parser.error("Seeds/rounds must be positive; candidates >= 2")

    if not 0 <= args.gaming_rate <= 1:
        parser.error("Gaming rate must be between 0 and 1")

    if args.eval_noise < 0:
        parser.error("Evaluation noise cannot be negative")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = []

    for seed in range(args.seeds):
        rows.extend(
            run_one(
                seed,
                args.candidates,
                args.rounds,
                args.gaming_rate,
                args.eval_noise,
            )
        )

    summary = summarize(rows)

    with (out / "trials.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "experiment": "proxy optimization with independent evaluation",
        "configuration": vars(args),
        "summary": summary,
        "interpretation_warning": (
            "Synthetic simulation only. Independent evaluation is a "
            "separate noisy measurement of the same underlying quality, "
            "not a genuine unseen-task generalization test."
        ),
    }

    (out / "summary.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
