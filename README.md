# Automated Alignment Research: Pre-work Experiment

## Research question
When a selection process optimizes a proxy score, does its apparent improvement
generalize to an independent objective when some candidates can game the proxy?

## Scope and honesty
This is a small, synthetic simulation designed to validate an experimental idea.
It is not an LLM agent, not an alignment benchmark, and not evidence that real
AI systems exhibit the same behavior. Do not describe it as a finding about
frontier models. The research contribution at this stage is the design,
reproducibility, analysis, and clear statement of limitations.

## Requirements
Python 3.10+; standard library only.

## Run
```bash
python experiment.py --seeds 30 --rounds 10 --candidates 40 --gaming-rate 0.25
python analyze.py
```

Outputs:
- `results/trials.csv`: every selected candidate and its proxy/true scores
- `results/summary.json`: descriptive summary and configuration
- `results/analysis.json`: paired seed-level differences and bootstrap intervals

## Experimental plan
1. Main run: 30 seeds, 10 rounds, 40 candidates per round, gaming rate 0.25.
2. Sensitivity: repeat at gaming rates 0.0, 0.1, 0.25, 0.5.
3. Ablation: repeat with different candidate pool sizes (10, 40, 100).
4. Report proxy score and true score separately; never select on true score.
5. Discuss the limitation that the simulated agent selects from a random pool,
   rather than generating hypotheses or writing code like an LLM research agent.

## Expected qualitative behavior (not a result to assume)
Proxy optimization will usually raise proxy scores relative to random selection.
Whether and how much true scores improve depends on noise, gaming rate, and pool
size. Run the experiment and report the observed results, including surprises.

## Next step toward the mentor's actual project
Replace the toy candidate generator with a published alignment benchmark and an
LLM-based research agent only after defining:
- a target capability or failure mode,
- a trusted baseline,
- a held-out evaluation set,
- a threat model for metric gaming,
- compute/API budget and safety boundaries.
