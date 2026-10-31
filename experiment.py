"""Toy experiment: proxy optimization vs held-out objective.

This is a transparent simulation, not an LLM-agent evaluation and not evidence
about real AI alignment. It isolates one mechanism: selecting candidates using
a proxy score that can disagree with the true objective.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
import statistics
from pathlib import Path

def make_candidates(rng, n, proxy_noise=0.18, gaming_rate=0.25):
    """Candidate has a true score and a proxy score.

    Some candidates receive an artificial proxy boost without a true-score boost,
    representing a toy form of metric gaming. All values are bounded [0, 1].
    """
    rows = []
    for i in range(n):
        true_score = rng.random()
        noise = rng.gauss(0, proxy_noise)
        gaming = rng.random() < gaming_rate
        proxy_score = true_score + noise + (0.35 if gaming else 0.0)
        proxy_score = max(0.0, min(1.0, proxy_score))
        rows.append({
            "candidate_id": i,
            "true_score": true_score,
            "proxy_score": proxy_score,
            "gaming_flag": int(gaming),
        })
    return rows

def run_one(seed, candidates_per_round=40, rounds=10, gaming_rate=0.25):
    rng = random.Random(seed)
    all_rows = []
    history = []

    for round_id in range(rounds):
        pool = make_candidates(rng, candidates_per_round, gaming_rate=gaming_rate)

        # Baseline: select one random candidate from the current pool.
        baseline_pick = rng.choice(pool)

        # Adaptive/proxy-optimizing agent: select the candidate with highest proxy.
        adaptive_pick = max(pool, key=lambda x: x["proxy_score"])

        # Independent evaluator sees true_score, which the selection policy does not.
        for policy, pick in (("random_baseline", baseline_pick),
                             ("proxy_optimizer", adaptive_pick)):
            row = {
                "seed": seed,
                "round": round_id,
                "policy": policy,
                **pick,
            }
            all_rows.append(row)
            history.append(row)

    return all_rows

def summarize(rows):
    output = {}
    for policy in sorted({r["policy"] for r in rows}):
        subset = [r for r in rows if r["policy"] == policy]
        true_scores = [r["true_score"] for r in subset]
        proxy_scores = [r["proxy_score"] for r in subset]
        gaming = [r["gaming_flag"] for r in subset]
        output[policy] = {
            "n": len(subset),
            "mean_proxy_score": statistics.mean(proxy_scores),
            "mean_true_score": statistics.mean(true_scores),
            "proxy_minus_true": statistics.mean(
                [r["proxy_score"] - r["true_score"] for r in subset]
            ),
            "fraction_gaming_flagged": statistics.mean(gaming),
        }
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--candidates", type=int, default=40)
    parser.add_argument("--gaming-rate", type=float, default=0.25)
    parser.add_argument("--out", default="results")
    args = parser.parse_args()

    if args.seeds < 1 or args.rounds < 1 or args.candidates < 2:
        parser.error("seeds/rounds must be positive and candidates must be >= 2")
    if not 0 <= args.gaming_rate <= 1:
        parser.error("--gaming-rate must be between 0 and 1")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in range(args.seeds):
        rows.extend(run_one(seed, args.candidates, args.rounds, args.gaming_rate))

    summary = summarize(rows)
    with (out / "trials.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "experiment": "proxy optimization and metric gaming (toy simulation)",
        "configuration": vars(args),
        "summary": summary,
        "interpretation_warning": (
            "Synthetic simulation only. It does not evaluate an LLM or establish "
            "claims about real AI alignment. Results depend on the toy data-generating process."
        ),
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
