
import csv
import json
import random
import statistics
from collections import defaultdict


INPUT_FILE = "results_distribution_shift/trials.csv"
BOOTSTRAP_SAMPLES = 10000


def mean(values):
    return statistics.mean(values)


def bootstrap_ci(values, rng, samples=BOOTSTRAP_SAMPLES):
    estimates = []

    for _ in range(samples):
        resampled = [
            rng.choice(values)
            for _ in range(len(values))
        ]
        estimates.append(mean(resampled))

    estimates.sort()

    lower = estimates[int(0.025 * samples)]
    upper = estimates[int(0.975 * samples)]

    return [lower, upper]


def main():
    rng = random.Random(42)

    # Group results by similarity, seed and policy
    grouped = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    with open(INPUT_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            similarity = float(row["similarity"])
            seed = int(row["seed"])
            policy = row["policy"]

            grouped[similarity][seed][policy].append({
                "training": float(row["training_score"]),
                "heldout": float(row["heldout_score"])
            })

    report = {}

    for similarity in sorted(grouped.keys(), reverse=True):

        optimizer_advantages = []
        generalization_gaps = []

        for seed in sorted(grouped[similarity].keys()):

            seed_data = grouped[similarity][seed]

            optimizer = seed_data["training_optimizer"]
            baseline = seed_data["random_baseline"]

            optimizer_heldout = mean([
                x["heldout"] for x in optimizer
            ])

            baseline_heldout = mean([
                x["heldout"] for x in baseline
            ])

            optimizer_training = mean([
                x["training"] for x in optimizer
            ])

            optimizer_advantages.append(
                optimizer_heldout - baseline_heldout
            )

            generalization_gaps.append(
                optimizer_training - optimizer_heldout
            )

        report[str(similarity)] = {
            "seeds": len(optimizer_advantages),

            "optimizer_heldout_advantage": {
                "mean": mean(optimizer_advantages),
                "bootstrap_95_ci": bootstrap_ci(
                    optimizer_advantages, rng
                )
            },

            "optimizer_generalization_gap": {
                "mean": mean(generalization_gaps),
                "bootstrap_95_ci": bootstrap_ci(
                    generalization_gaps, rng
                )
            }
        }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
