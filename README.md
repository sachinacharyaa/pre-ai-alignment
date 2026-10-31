Alignment Research Pre-work: Proxy Optimization, Metric Gaming, and Generalization
Project overview
This project uses small Python simulations to explore a central AI
safety question:

If an AI system gets a high score, does that mean it has actually
become better at the real task?

A score is often only an imperfect measurement of what we care about. A
system optimized against that score may become good at the measurement
without improving equally at the real goal. It may also perform well on
familiar tasks but struggle on new ones.

We built simple simulated candidates and compared two strategies: -
Random baseline: chooses a candidate randomly. - Optimizer:
chooses the candidate with the highest score it is allowed to use.

These are synthetic simulations, not experiments on real AI models. They
illustrate possible mechanisms; they do not prove how real AI systems
behave.
Why we did this
The work connects to three questions in the broader project on automated
alignment researchers:
1. Metric gaming: Can an agent get a high evaluation score by
   exploiting weaknesses in the score?
2. Generalization: Does a method that works on familiar tasks also
   work on new tasks?
3. Evaluation reliability: How can we check whether an apparent
   improvement is real?
The broader project also asks whether agents can make progress on
problems without clear numerical scores. We have not tested that
question yet.
Key terms in simple language
  Term                                Simple meaning
  True score                          How good a candidate actually is at
the underlying goal in the
simulation.

  Proxy score                         An easier-to-measure score used to
select candidates. It may not
perfectly measure the real goal.

  Gaming flag                         A label marking candidates that
receive an artificial bonus on the
proxy score.

  Random baseline                     A strategy that chooses a candidate
randomly.

  Optimizer                           A strategy that chooses the
candidate with the highest
permitted selection score.

  Training task                       A familiar task whose score the
optimizer can use.

  Held-out task                       A separate, unseen task used only
for evaluation.

  Generalization                      Performing well on tasks that were
not used during selection or
development.

  Generalization gap                  Training score minus held-out
score. A larger positive gap means
performance is better on familiar
tasks than unseen tasks.
Bootstrap confidence interval       A range estimating uncertainty in
an average by repeatedly resampling
experiment results.
Scores range from 0 to 1. For example, 0.80 means 0.80 on the score
scale; it is not automatically an 80% probability of success.
Experiment 1: Proxy optimization and metric gaming
Question
Does choosing candidates by a proxy score improve their actual quality?
Does this selection process favor candidates that benefit from a
weakness in the proxy?
What we did
Each simulated candidate received: - true_score: an underlying quality
score. - proxy_score: the true score plus random measurement noise. -
gaming_flag: whether the candidate received an artificial bonus on the
proxy score.

For candidates with gaming_flag = 1, we added 0.35 to the proxy
score. We then limited the proxy score to the range 0 to 1.

The gaming flag was assigned randomly. It did not mean the candidate had
low true quality, and it did not represent an AI intentionally deciding
to cheat.

We compared random selection with selecting the candidate that had the
highest proxy score. The main run used 30 random seeds, 10 rounds per
seed, 40 candidates per round, and a gaming rate of 0.25.
Results
  Measurement                   Random baseline   Proxy optimizer
  Mean proxy score                        0.560             1.000
Mean true score                         0.491             0.821
Proxy minus true score                  0.069             0.179
Gaming-flagged selections               27.7%             64.3%

The optimizer's mean true-score advantage over the baseline was
0.330, with a 95% bootstrap interval of 0.298 to 0.362 across 30
seeds.
What we found and why it matters
The optimizer improved both the proxy score and the true score in this
simulation. It also selected many more candidates that received the
artificial proxy bonus. The difference between proxy and true score was
larger for the optimizer.

Simple takeaway: Optimizing a proxy can improve the real goal while
also favoring candidates that benefit from weaknesses in the score. We
should not trust the optimization score alone.

The proxy score reached its maximum of 1.0, creating a ceiling effect.
Extra check: candidate-pool size
We also varied the number of candidates per round.
 Candidates per   Optimizer proxy    Optimizer true    Gaming-flagged
          round             score             score        selections

             10             0.974             0.816             49.7%

             40             1.000             0.821             64.3%

            100             1.000             0.821             62.0%

The proxy score reached its ceiling by 40 candidates. True score changed
very little between 10 and 100 candidates. The gaming-flagged rate did
not rise steadily, so we cannot claim that larger pools always produce
more gaming-flagged selections. These are descriptive averages; we did
not run a formal statistical comparison across pool sizes.
Experiment 2: Add an independent evaluation score
Why we did it
A candidate should not be judged only by the same score used to select
it. We added a second measurement that the optimizer could not see.

Each candidate received: - proxy_score: used for selection. -
true_score: the underlying simulated quality. -
independent_eval_score: the true score plus separate random evaluation
noise.

The independent evaluation did not receive the artificial gaming bonus.
The optimizer still selected candidates using only the proxy score.
Results
This was a new run with 30 seeds, 10 rounds, 40 candidates per round,
gaming rate 0.25, and evaluation noise 0.10.

  Measurement                            Random baseline   Proxy optimizer
  Mean proxy score                                 0.603             1.000
Mean true score                                  0.525             0.827
Mean independent evaluation                      0.525             0.815
Proxy minus independent evaluation               0.077             0.185
Gaming-flagged selections                        25.3%             59.0%
What we found
The optimizer's independent evaluation score was close to its true
score, but lower than its proxy score. This is consistent with the proxy
giving an overly favorable picture of selected candidates.

Important limitation: This independent evaluation was another noisy
measurement of the same underlying quality. It was not a genuine test on
unseen tasks and did not establish generalization.
Experiment 3: Generalization to unseen tasks
Question
If we choose candidates based on familiar tasks, do those candidates
also perform well on new tasks?
What we did
Each candidate received: - general_ability: an ability that helps
across tasks. - training_score: performance on familiar tasks. -
heldout_score: performance on a separate unseen task.

Both task scores were based on general ability, with separate random
task noise. The optimizer selected candidates using only
training_score. We then measured their held-out scores.

We used 30 seeds, 10 rounds per seed, and 40 candidates per round.
Results
  Measurement                       Random baseline   Training optimizer
  Mean training score                         0.506                0.999
Mean held-out score                         0.516                0.791
Mean general ability                        0.507                0.844
Training minus held-out score              -0.010                0.209
What we found
The optimizer selected candidates with almost perfect training scores.
Their held-out score was lower, at about 0.791.

But the optimizer still performed much better than random selection on
unseen tasks: 0.791 compared with 0.516.

Simple takeaway: The optimizer found candidates with stronger
general ability, so some of their performance transferred to new tasks.
However, their familiar-task score was higher than their unseen-task
score. That difference is the generalization gap.
Experiment 4: Generalization under task distribution shift
Why we changed the experiment
The previous experiment showed a gap between familiar and unseen tasks.
We next wanted to understand why that gap might change.

We introduced similarity. It controls how strongly a candidate's
task-specific advantage on the training task is related to its
task-specific advantage on the held-out task.
Similarity Meaning in this simulation

      1.00 Training and held-out task-specific effects are identical.
      0.75 Strong positive relationship.
      0.50 Moderate positive relationship.
      0.25 Weak positive relationship.
      0.00 No correlation between task-specific effects.
General ability still transfers at every setting. Only the relationship
between task-specific effects changes.

The optimizer selected candidates using only the training score.
Held-out scores were hidden until evaluation.
Results: optimizer performance
Task similarity    Training score    Held-out score    Generalization
                                                                  gap

           1.00             0.999             0.999             0.000

           0.75             0.999             0.952             0.048

           0.50             0.999             0.900             0.099

           0.25             0.999             0.847             0.152

           0.00             0.999             0.791             0.209

The generalization gap is:

training score - held-out score

As task-specific similarity decreased, the gap became larger.
Results: held-out advantage over random selection
Task similarity         Optimizer   Random held-out         Optimizer
                   held-out score             score         advantage

           1.00             0.999             0.506             0.493

           0.75             0.952             0.514             0.438

           0.50             0.900             0.516             0.384

           0.25             0.847             0.517             0.330

           0.00             0.791             0.516             0.275

What we found and why
Two things happened:
1. The optimizer's held-out performance decreased as task-specific
   similarity decreased.
2. The optimizer still performed better than random selection at every
   similarity setting.
Why did it retain an advantage at similarity 0.00? Because general
ability still transferred, even though task-specific advantages did not.

Simple takeaway: A method can transfer some benefits to unseen tasks
because it identifies generally capable candidates. But it can lose
performance when new tasks require different task-specific skills.
Experiment 5: Bootstrap confidence intervals
Why we did it
An average alone does not show how much results vary between simulation
runs. We used the 30 random seeds as the units for statistical analysis.

For each seed, we calculated: - The optimizer's held-out score minus the
random baseline's held-out score. - The optimizer's training score minus
its held-out score.

Then we used bootstrap resampling:
1. Start with the 30 seed-level results.
2. Randomly sample 30 of them, allowing a seed to be selected more than
   once.
3. Calculate the average for that resampled set.
4. Repeat 10,000 times.
5. Use the 2.5th and 97.5th percentiles as the endpoints of the 95%
   bootstrap interval.
The interval estimates uncertainty in the average. It does not mean
there is a 95% probability that a research hypothesis is true.
Statistical results
           Similarity Held-out advantage (95% Generalization gap (95%
                          bootstrap interval)     bootstrap interval)

                 1.00  0.493 \[0.453, 0.532\]  0.000 \[0.000, 0.000\]

                 0.75  0.438 \[0.395, 0.480\]  0.048 \[0.038, 0.057\]

                 0.50  0.384 \[0.341, 0.426\]  0.099 \[0.084, 0.114\]

                 0.25  0.330 \[0.288, 0.372\]  0.152 \[0.133, 0.172\]

                 0.00  0.275 \[0.233, 0.317\]  0.209 \[0.186, 0.231\]

How to read one result
At similarity 0.00: - Estimated held-out advantage: 0.275. - 95%
bootstrap interval: 0.233 to 0.317.

The estimated average advantage was 0.275. When we repeatedly resampled
the 30 seed-level results, the interval ran from 0.233 to 0.317.

All five held-out advantage intervals are above zero. This supports a
positive optimizer advantage over random selection at each tested
similarity level in this simulation.

The generalization-gap intervals also increase as similarity decreases.
This supports the pattern that lower task-specific similarity is
associated with a larger gap in this model.

Statistical caution: These intervals estimate uncertainty at each
similarity level. They are not, by themselves, a formal statistical test
of the trend across all five levels. The simulation also uses a
simplified model and fixed parameter choices.
Overall findings
Across the experiments, we learned:
1. Proxy optimization: Selecting by a proxy can improve the
   underlying simulated objective, but it can also favor candidates
   that benefit from weaknesses in that proxy.
2. Independent evaluation: A separate measurement can reveal that
   the selection score is more optimistic than another evaluation. But
   a second noisy measurement of the same quality is not a true
   unseen-task test.
3. Generalization: Candidates selected for high training
   performance can also perform better on unseen tasks, but their
   performance may drop.
4. Task similarity: In our simulation, the less related the
   training and held-out task-specific effects are, the larger the
   generalization gap becomes.
5. Uncertainty: Bootstrap intervals show that the patterns were
   consistent across the 30 simulated seeds, under the assumptions of
   this model.
Central conclusion
In these synthetic experiments, optimizing a score improved
performance on the underlying simulated objective and on held-out
tasks. However, optimization also increased selection for candidates
benefiting from an artificial proxy bonus, and the advantage on unseen
tasks decreased as task-specific similarity decreased. This
illustrates why evaluation should include independent measurements and
genuinely held-out tasks, rather than relying only on the score used
during optimization.

What this project does not show
It is important to be precise about the limits of this work:
- We did not run experiments on Claude, GPT, or other real frontier
  models.
- We did not build an autonomous AI research agent.
- The gaming flag was assigned by the simulation; it was not evidence
  of intentional deception.
- The held-out task is simulated using a mathematical relationship
  with the training task. It is not a real-world benchmark.
- We did not test larger models, agent-generated research methods, or
  problems without clear numerical scores.
- Bootstrap intervals describe variation across simulated seeds, not
  variation across real AI systems.
This is best described as preliminary simulation work exploring
mechanisms relevant to AI evaluation and alignment research.
Project files and how to run
The scripts below are expected to be in the project folder.
  File or folder                      Purpose
  experiment.py                     Runs the currently selected
simulation.

  analyze_generalization.py         Calculates bootstrap intervals for
the distribution-shift experiment.

  results_independent/              Output from the
independent-evaluation experiment.

  results_generalization/           Output from the basic
generalization experiment.
results_distribution_shift/       Output from the task-similarity
experiment.
The same experiment.py file was replaced as the project progressed.
The current version runs Experiment 4, while earlier outputs are kept in
their separate result folders.
Run the current distribution-shift experiment
python3 experiment.py --seeds 30 --rounds 10 --candidates 40
Calculate bootstrap intervals
python3 analyze_generalization.py
The analysis script reads results_distribution_shift/trials.csv and
prints the statistical results.
Python requirements
The scripts use the Python standard library. No external Python
packages, API keys, GPU, or paid model access are required.
What should we do next?
This work is a starting point, not the final answer to the broader
research questions.

Useful next steps:
1. Robustness checks: Repeat the distribution-shift experiment with
   different strengths of task-specific specialization and different
   candidate-pool sizes.
2. Improve statistical analysis: Test the trend across similarity
   levels directly and check sensitivity to the score ceiling at 1.0.
3. More realistic evaluation: Model multiple training and held-out
   tasks rather than one score for each.
4. Connect to real agents: Once the simulation is understood, test
   whether similar patterns appear when actual AI agents propose
   methods and are evaluated on separate tasks.
5. Test fuzzy objectives: Explore independent rubrics or blinded
   human evaluation when there is no simple numerical score.
The next step is to make the simulation more realistic and test whether
its findings are robust before making claims about real AI systems.