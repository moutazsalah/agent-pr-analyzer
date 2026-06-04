# Assignment 02: Intelligent Tools for Software Evolution

This project analyzes AI-generated pull requests from the AIDev-pop/AIDev dataset for the coursework assignment.

## Goal

Answer the three required research questions and one additional research question:

- RQ1: Do AI coding agents differ in pull request acceptance rates?
- RQ2: Do AI coding agents differ in review turnaround time?
- RQ3: What repository/project factors are associated with acceptance of AI-generated PRs?
- RQ4-B: Are AI PRs more accepted when they modify peripheral artifacts rather than core source code?

RQ4-B is the initial choice because it is usually reproducible from touched-file paths and produces clear tables and plots.

## Project Structure

```text
data/
  raw/          Original downloaded dataset files
  processed/    Cleaned analysis-ready files
figures/        Exported plots for the report and presentation
notebooks/      Reproducible Jupyter analysis
report/         ACM-style report files
presentation/   10-minute presentation files
```

## Planned Analysis

1. Load the AIDev-pop/AIDev dataset.
2. Inspect available columns and identify PR, repository, agent, review, and file-change fields.
3. Define PR acceptance clearly, likely as whether the PR was merged.
4. Compute RQ1 acceptance rates by agent and run a statistical comparison.
5. Compute RQ2 review turnaround metrics by agent and run a non-parametric test.
6. Build an RQ3 multivariable model with agent identity and at least five project/change factors.
7. Classify changed files for RQ4-B and compare acceptance between core and peripheral changes.
8. Export all tables and figures for the report.

## How To Run

Install the required Python packages:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Download the analysis datasets:

```text
.venv/bin/python scripts/download_data.py
```

Run the reproducible notebook:

```text
.venv/bin/jupyter notebook notebooks/analysis.ipynb
```

The notebook is the main reproducible workflow for the submission. It prepares the one-row-per-PR analysis table, runs the research-question analyses, and exports tables/figures.

You can also run the data-preparation helper script directly:

```text
.venv/bin/python scripts/prepare_data.py
```

The main notebook is:

```text
notebooks/analysis.ipynb
```

After the dataset is available in `data/raw/`, run the notebook from top to bottom to reproduce the results.

## AI Usage Acknowledgement

AI assistance was used for planning the analysis workflow, structuring the project, and drafting reproducibility documentation. All final analysis choices, interpretation, and submitted content should be reviewed by the authors.
