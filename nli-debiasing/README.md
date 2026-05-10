# Spurious Correlation Identification and Debiased Data to Improve Natural Language Inference

> This project was completed as a final project for a master's course.

## Overview

This project investigates dataset bias in Natural Language Inference (NLI) and explores whether training on debiased data improves model generalization. The work is divided into two parts: identifying spurious correlations in the SNLI dataset and evaluating the impact of training on a debiased alternative.

## Process

### 1. Artifact Detection
Using the competency problems framework from Gardner et al. (2021), a hypothesis test is applied to each token in the SNLI vocabulary. Under the assumption that language cannot be reduced to simple feature-label correlations, any statistically significant association between a word token and a class label (entailment, neutral, or contradiction) is treated as a dataset artifact. Z-scores are computed per token-label pair, and a Bonferroni-corrected significance threshold is used to flag artifacts. The SNLI training set was found to contain 3.65% artifact tokens, compared to 1.98% in the debiased SNLI Par-Z dataset.

### 2. Measuring Model Bias
To assess whether models internalize dataset artifacts, an ELECTRA-small model was fine-tuned on each dataset and evaluated on synthetic single-token inputs. A higher predicted probability for high z-score tokens relative to low z-score tokens indicates learned bias. The SNLI-trained model showed substantially higher bias across all three classes compared to the SNLI Par-Z-trained model.

### 3. Evaluation on SNLI-hard
Both models were evaluated on the SNLI-hard test set — a challenging subset designed to exclude examples solvable via hypothesis-only shortcuts. The model fine-tuned on SNLI Par-Z achieved **80.59% accuracy** on SNLI-hard, outperforming the SNLI-trained model's **77.23%**, while accepting a modest drop on the standard SNLI validation set (87.02% vs 89.43%).

## Key Results

| Fine-tuning Dataset | SNLI Validation | SNLI-hard |
|---|---|---|
| SNLI | **89.43%** | 77.23% |
| SNLI Par-Z | 87.02% | **80.59%** |

## References

- Gardner et al. (2021). *Competency problems: On finding and removing artifacts in language data.* arXiv:2104.08646
- Wu et al. (2022). *Generating Data to Mitigate Spurious Correlations in Natural Language Inference Datasets.* arXiv:2203.12942
- Gururangan et al. (2018). *Annotation Artifacts in Natural Language Inference Data.* arXiv:1803.02324
