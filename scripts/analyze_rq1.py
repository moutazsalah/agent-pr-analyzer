from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportion_confint


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "pr_analysis.parquet")

    table = (
        df.groupby("agent")
        .agg(
            total_prs=("pr_id", "count"),
            closed_prs=("is_closed", "sum"),
            merged_prs=("is_merged", "sum"),
        )
        .reset_index()
        .sort_values("merged_prs", ascending=False)
    )
    table["acceptance_rate"] = table["merged_prs"] / table["closed_prs"]

    ci = table.apply(
        lambda row: proportion_confint(
            count=row["merged_prs"],
            nobs=row["closed_prs"],
            alpha=0.05,
            method="wilson",
        ),
        axis=1,
    )
    table["acceptance_ci_low"] = [x[0] for x in ci]
    table["acceptance_ci_high"] = [x[1] for x in ci]

    output = PROCESSED / "rq1_acceptance_by_agent.csv"
    table.to_csv(output, index=False)

    contingency = table[["merged_prs", "closed_prs"]].copy()
    contingency["not_merged_closed_prs"] = contingency["closed_prs"] - contingency["merged_prs"]
    chi2, p_value, dof, expected = chi2_contingency(contingency[["merged_prs", "not_merged_closed_prs"]])

    print(table.to_string(index=False))
    print()
    print(f"Chi-square test: chi2={chi2:.3f}, dof={dof}, p={p_value:.3g}")

    plot_data = table.sort_values("acceptance_rate", ascending=False)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sns.barplot(data=plot_data, x="agent", y="acceptance_rate", color="#4C78A8", ax=ax)
    yerr_low = plot_data["acceptance_rate"] - plot_data["acceptance_ci_low"]
    yerr_high = plot_data["acceptance_ci_high"] - plot_data["acceptance_rate"]
    ax.errorbar(
        x=range(len(plot_data)),
        y=plot_data["acceptance_rate"],
        yerr=[yerr_low, yerr_high],
        fmt="none",
        color="black",
        capsize=4,
        linewidth=1,
    )
    ax.set_xlabel("Agent")
    ax.set_ylabel("Acceptance rate among closed PRs")
    ax.set_ylim(0, min(1.0, plot_data["acceptance_ci_high"].max() + 0.08))
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(FIGURES / "rq1_acceptance_by_agent.png", dpi=200)


if __name__ == "__main__":
    main()
