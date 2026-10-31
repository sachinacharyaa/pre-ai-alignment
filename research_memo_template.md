# Pre-work research memo

## Title
When Does Proxy Optimization Fail to Generalize? A Toy Simulation

## Motivation
Explain why automated alignment research needs independent evaluation.

## Research question and hypothesis
State the question, hypothesis, and what observation would count against it.

## Experimental setup
- Policies compared:
- Candidate generation:
- Proxy metric:
- Independent objective:
- Seeds / rounds / pool size:
- Metrics:
- Reproducibility instructions:

## Results
Insert observed numbers from `results/summary.json` and `results/analysis.json`.
Do not write this section before running the experiments.

## Interpretation
What did the data support? What did it not support? Were the differences large
or uncertain? Did sensitivity runs change the interpretation?

## Limitations
This is a synthetic simulation, not an LLM-based researcher or a real alignment
benchmark. The toy metric-gaming mechanism is stipulated by the experimenter.
Results cannot establish how frontier models behave.

## Next experiment
Describe how you would test the question using a real, public alignment benchmark,
including held-out tasks and an independent evaluator.
