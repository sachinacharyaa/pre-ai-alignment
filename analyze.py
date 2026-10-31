"""Paired seed-level summaries and bootstrap intervals for the toy experiment."""
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean

def bootstrap_ci(values, seed=123, reps=5000):
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sample = [rng.choice(values) for _ in values]
        estimates.append(mean(sample))
    estimates.sort()
    return [estimates[int(0.025 * reps)], estimates[int(0.975 * reps)]]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="results/trials.csv")
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.csv, newline="", encoding="utf-8")))
    by_seed_policy = defaultdict(list)
    for row in rows:
        by_seed_policy[(int(row["seed"]), row["policy"])].append(row)

    paired = defaultdict(list)
    seeds = sorted({int(r["seed"]) for r in rows})
    for seed in seeds:
        for metric in ("true_score", "proxy_score", "gaming_flag"):
            a = mean(float(r[metric]) for r in by_seed_policy[(seed, "proxy_optimizer")])
            b = mean(float(r[metric]) for r in by_seed_policy[(seed, "random_baseline")])
            paired[metric].append(a - b)

    output = {}
    for metric, values in paired.items():
        output[metric] = {
            "mean_paired_difference_optimizer_minus_baseline": mean(values),
            "bootstrap_95_percentile_interval": bootstrap_ci(values),
            "n_seeds": len(values),
        }
    print(json.dumps(output, indent=2))
    Path("results/analysis.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
