
"""
Experiment 4: Generalization under task distribution shift.

Synthetic simulation only. This is not a real LLM-agent evaluation.
"""

import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path


SIMILARITIES = [1.0, 0.75, 0.50, 0.25, 0.0]


def clamp(value):
    return max(0.0, min(1.0, value))


def make_candidates(rng, n, similarity, task_effect=0.25):
    candidates = []

    for i in range(n):
        # Ability that transfers across all tasks
        general_ability = rng.random()

        # Candidate-specific strength on training tasks
        training_specialization = rng.gauss(0, task_effect)

        # Independent task-specific variation
        independent_specialization = rng.gauss(0, task_effect)

        # How much training-task specialization transfers
        # to unseen tasks
        heldout_specialization = (
            similarity * training_specialization
            + math.sqrt(1 - similarity ** 2)
            * independent_specialization
        )

        training_score = clamp(
            general_ability + training_specialization
        )

        heldout_score = clamp(
            general_ability + heldout_specialization
        )

        candidates.append({
            "candidate_id": i,
            "general_ability": general_ability,
            "training_score": training_score,
            "heldout_score": heldout_score
        })

    return candidates


def run_one(seed, similarity, candidates_per_round=40,
            rounds=10, task_effect=0.25):

    rng = random.Random(seed)
    rows = []

    for round_id in range(rounds):

        pool = make_candidates(
            rng,
            candidates_per_round,
            similarity,
            task_effect
        )

        # Random selection
        baseline_pick = rng.choice(pool)

        # Optimization uses training score ONLY
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
                "similarity": similarity,
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

        training = [r["training_score"] for r in subset]
        heldout = [r["heldout_score"] for r in subset]
        general = [r["general_ability"] for r in subset]

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
    parser.add_argument("--task-effect", type=float, default=0.25)
    parser.add_argument(
        "--out",
        default="results_distribution_shift"
    )

    args = parser.parse_args()

    all_rows = []
    all_summaries = {}

    for similarity in SIMILARITIES:

        similarity_rows = []

        for seed in range(args.seeds):

            rows = run_one(
                seed=seed,
                similarity=similarity,
                candidates_per_round=args.candidates,
                rounds=args.rounds,
                task_effect=args.task_effect
            )

            similarity_rows.extend(rows)

        all_rows.extend(similarity_rows)

        all_summaries[str(similarity)] = summarize(
            similarity_rows
        )

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
        "experiment": "generalization under task distribution shift",
        "configuration": vars(args),
        "task_similarities": SIMILARITIES,
        "results_by_similarity": all_summaries,
        "interpretation_warning": (
            "Synthetic simulation only. Task-specific effects "
            "are correlated according to the similarity parameter. "
            "This does not establish how real AI agents generalize."
        )
    }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
