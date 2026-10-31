
"""
Experiment 3: Does optimization generalize to unseen tasks?

Synthetic simulation only. This is not a real LLM-agent evaluation.
"""

import argparse
import csv
import json
import random
import statistics
from pathlib import Path


def clamp(value):
    return max(0.0, min(1.0, value))


def make_candidates(rng, n, task_noise=0.25):
    candidates = []

    for i in range(n):
        # General ability across tasks
        general_ability = rng.random()

        # Performance on familiar training tasks
        training_score = clamp(
            general_ability + rng.gauss(0, task_noise)
        )

        # Performance on completely different unseen tasks
        heldout_score = clamp(
            general_ability + rng.gauss(0, task_noise)
        )

        candidates.append({
            "candidate_id": i,
            "general_ability": general_ability,
            "training_score": training_score,
            "heldout_score": heldout_score
        })

    return candidates


def run_one(seed, candidates_per_round=40, rounds=10,
            task_noise=0.25):

    rng = random.Random(seed)
    rows = []

    for round_id in range(rounds):

        pool = make_candidates(
            rng,
            candidates_per_round,
            task_noise
        )

        # Random baseline: select randomly
        baseline_pick = rng.choice(pool)

        # Optimizer: select ONLY using training score
        optimizer_pick = max(
            pool,
            key=lambda x: x["training_score"]
        )

        for policy, pick in [
            ("random_baseline", baseline_pick),
            ("training_optimizer", optimizer_pick)
        ]:

            rows.append({
                "seed": seed,
                "round": round_id,
                "policy": policy,
                **pick
            })

    return rows


def summarize(rows):

    output = {}

    for policy in sorted({r["policy"] for r in rows}):

        subset = [
            r for r in rows
            if r["policy"] == policy
        ]

        training = [
            r["training_score"] for r in subset
        ]

        heldout = [
            r["heldout_score"] for r in subset
        ]

        general = [
            r["general_ability"] for r in subset
        ]

        output[policy] = {
            "n": len(subset),
            "mean_training_score": statistics.mean(training),
            "mean_heldout_score": statistics.mean(heldout),
            "mean_general_ability": statistics.mean(general),
            "training_minus_heldout": statistics.mean([
                t - h for t, h in zip(training, heldout)
            ])
        }

    return output


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--candidates", type=int, default=40)
    parser.add_argument("--task-noise", type=float, default=0.25)
    parser.add_argument(
        "--out",
        default="results_generalization"
    )

    args = parser.parse_args()

    all_rows = []

    for seed in range(args.seeds):
        all_rows.extend(
            run_one(
                seed,
                candidates_per_round=args.candidates,
                rounds=args.rounds,
                task_noise=args.task_noise
            )
        )

    summary = summarize(all_rows)

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "trials.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=all_rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(all_rows)

    report = {
        "experiment": "generalization to unseen tasks",
        "configuration": vars(args),
        "summary": summary,
        "interpretation_warning": (
            "Synthetic simulation only. Training and held-out "
            "scores share a general ability component. This is "
            "a simplified model of generalization, not a real "
            "evaluation of AI agents."
        )
    }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
