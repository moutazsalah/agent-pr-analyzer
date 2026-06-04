# AI Agent Pull Request Analysis

This repository analyzes AI-generated pull requests from the AIDev dataset to study how AI coding agents participate in software evolution workflows.

The project builds a reproducible PR-level dataset, compares acceptance and review behavior across agents, models factors associated with merge outcomes, and examines whether peripheral changes are accepted differently from core source-code changes.

## Research Questions

- **RQ1:** Do AI coding agents differ in pull request acceptance rates?
- **RQ2:** Do AI coding agents differ in review turnaround time?
- **RQ3:** What repository/project factors are associated with acceptance of AI-generated PRs?
- **RQ4-B:** Are AI PRs more accepted when they modify peripheral artifacts rather than core source code?

## Repository Structure

```text
scripts/
  download_data.py     Download AIDev tables from Hugging Face
  prepare_data.py      Build the one-row-per-PR analysis dataset
  analyze_rq1.py       Standalone RQ1 helper analysis

notebooks/
  analysis.ipynb       Main reproducible analysis notebook
  analysis.executed.ipynb

data/
  processed/*.csv      Exported result tables
  raw/                 Downloaded raw data, ignored by Git

figures/               Exported plots used in the report
report/                ACM-style report source and references
```

Large raw and processed parquet files are not tracked in Git. They can be recreated with the steps below.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Reproduce the Analysis

Download the dataset:

```bash
.venv/bin/python scripts/download_data.py
```

Prepare the PR-level analysis table:

```bash
.venv/bin/python scripts/prepare_data.py
```

Run the notebook:

```bash
.venv/bin/jupyter notebook notebooks/analysis.ipynb
```

Run all cells from top to bottom. The notebook regenerates the processed tables in `data/processed/` and figures in `figures/`.

## Main Outputs

Generated result tables include:

```text
data/processed/rq1_acceptance_by_agent.csv
data/processed/rq2_turnaround_by_agent.csv
data/processed/rq3_logistic_regression_odds_ratios.csv
data/processed/rq4b_acceptance_by_scope.csv
data/processed/rq4b_acceptance_by_file_category.csv
data/processed/rq4b_acceptance_by_agent_and_scope.csv
```

Generated figures include:

```text
figures/rq1_acceptance_by_agent.png
figures/rq2_turnaround_by_agent.png
figures/rq3_logistic_regression_odds_ratios.png
figures/rq4b_acceptance_by_scope.png
figures/rq4b_acceptance_by_agent_and_scope.png
```

The ACM-style report source is available at:

```text
report/report_acm.tex
```

## Data

This project uses the AIDev dataset (`hao-li/AIDev`) from Hugging Face. The raw dataset files are downloaded locally into `data/raw/`, which is intentionally excluded from Git because of file size.

## Notes on Interpretation

Acceptance is defined as a pull request having a merge timestamp. Review turnaround is measured as time from PR creation to the first human review or comment. File categories are inferred from paths and extensions, so category-level results should be interpreted as heuristic and observational rather than causal.

## AI Usage Acknowledgement

ChatGPT/Codex was used to support analysis planning, repository inspection, requirement interpretation, and manuscript drafting. The reported analyses, results, and interpretations remain the responsibility of the author.
