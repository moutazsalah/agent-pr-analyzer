from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".c", ".cc", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".kts", ".scala", ".r",
    ".m", ".mm", ".sh", ".bash", ".zsh", ".ps1", ".sql", ".lua", ".dart", ".ex",
    ".exs", ".erl", ".clj", ".fs", ".fsx", ".vb",
}
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc", ".pdf"}
CONFIG_FILENAMES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "requirements.txt",
    "pyproject.toml", "poetry.lock", "pipfile", "pipfile.lock", "cargo.toml", "cargo.lock",
    "go.mod", "go.sum", "pom.xml", "build.gradle", "gradle.properties", "makefile",
    "cmakelists.txt", "dockerfile", "docker-compose.yml", "docker-compose.yaml",
}


def read(name: str, columns=None) -> pd.DataFrame:
    return pd.read_parquet(RAW / f"{name}.parquet", columns=columns)


def parse_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def file_category(filename: str) -> str:
    path = str(filename or "").lower()
    parts = set(Path(path).parts)
    name = Path(path).name
    suffix = Path(path).suffix
    dependency_files = {
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
        "cargo.lock", "go.sum",
    }

    if path.startswith(".github/workflows/") or "/.github/workflows/" in path:
        return "ci_cd"
    if "dependabot" in path or "dependencies" in parts or name in dependency_files:
        return "dependencies"
    if "infra" in parts or "terraform" in parts or suffix in {".tf", ".tfvars"}:
        return "infrastructure"
    if (
        "tests" in parts
        or "test" in parts
        or "spec" in parts
        or "__tests__" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
    ):
        return "tests"
    if path.startswith("docs/") or "/docs/" in path or suffix in DOC_EXTENSIONS:
        return "documentation"
    if name in CONFIG_FILENAMES or path.startswith(".github/") or suffix in {".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf"}:
        return "build_config"
    if suffix in SOURCE_EXTENSIONS:
        return "core_source"
    return "other"


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    pr = read("pull_request")
    repo = read("repository").rename(columns={"id": "repo_id", "url": "repository_url"})
    task = read("pr_task_type")[["id", "type", "confidence"]].rename(
        columns={"id": "pr_id", "type": "task_type", "confidence": "task_type_confidence"}
    )

    pr = pr.rename(columns={"id": "pr_id"})
    for column in ["created_at", "closed_at", "merged_at"]:
        pr[column] = parse_time(pr[column])

    pr["is_closed"] = pr["closed_at"].notna() | pr["state"].eq("closed")
    pr["is_merged"] = pr["merged_at"].notna()
    pr["time_to_close_hours"] = (pr["closed_at"] - pr["created_at"]).dt.total_seconds() / 3600
    pr["time_to_merge_hours"] = (pr["merged_at"] - pr["created_at"]).dt.total_seconds() / 3600

    reviews = read("pr_reviews")
    reviews["submitted_at"] = parse_time(reviews["submitted_at"])
    human_reviews = reviews[reviews["user_type"].str.lower().ne("bot")]
    review_agg = human_reviews.groupby("pr_id").agg(
        review_count=("id", "count"),
        first_review_at=("submitted_at", "min"),
    )

    comments = read("pr_comments")
    comments["created_at"] = parse_time(comments["created_at"])
    human_comments = comments[comments["user_type"].str.lower().ne("bot")]
    comment_agg = human_comments.groupby("pr_id").agg(
        comment_count=("id", "count"),
        first_comment_at=("created_at", "min"),
    )

    files = read("pr_commit_details", columns=["pr_id", "sha", "filename", "additions", "deletions", "changes"])
    files["file_category"] = files["filename"].map(file_category)
    file_agg = files.groupby("pr_id").agg(
        commit_count=("sha", "nunique"),
        files_changed=("filename", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        churn=("changes", "sum"),
    )
    categories = pd.crosstab(files["pr_id"], files["file_category"]).gt(0).add_prefix("touches_")
    file_agg = file_agg.join(categories, how="left").fillna(False)

    issues = read("related_issue")
    issue_agg = issues.groupby("pr_id").agg(is_issue_linked=("issue_id", lambda s: s.notna().any()))

    repo_volume = pr.groupby("repo_id").size().rename("repo_ai_pr_volume")

    df = (
        pr.merge(repo, on="repo_id", how="left")
        .merge(task, on="pr_id", how="left")
        .join(review_agg, on="pr_id")
        .join(comment_agg, on="pr_id")
        .join(file_agg, on="pr_id")
        .join(issue_agg, on="pr_id")
        .join(repo_volume, on="repo_id")
    )

    df["first_human_response_at"] = df[["first_review_at", "first_comment_at"]].min(axis=1)
    df["time_to_first_review_hours"] = (df["first_review_at"] - df["created_at"]).dt.total_seconds() / 3600
    df["time_to_first_comment_hours"] = (df["first_comment_at"] - df["created_at"]).dt.total_seconds() / 3600
    df["time_to_first_human_response_hours"] = (
        df["first_human_response_at"] - df["created_at"]
    ).dt.total_seconds() / 3600

    for column in ["review_count", "comment_count", "commit_count", "files_changed", "additions", "deletions", "churn"]:
        df[column] = df[column].fillna(0)
    df["is_issue_linked"] = df["is_issue_linked"].fillna(False)

    touch_columns = [column for column in df.columns if column.startswith("touches_")]
    for column in touch_columns:
        df[column] = df[column].fillna(False)
    df["touches_peripheral_only"] = (
        df[touch_columns].any(axis=1)
        & ~df.get("touches_core_source", pd.Series(False, index=df.index))
    )

    numeric_controls = ["stars", "forks", "files_changed", "commit_count", "additions", "deletions", "churn", "repo_ai_pr_volume"]
    for column in numeric_controls:
        df[f"log1p_{column}"] = np.log1p(df[column].fillna(0))

    output = PROCESSED / "pr_analysis.parquet"
    df.to_parquet(output, index=False)
    print(f"Wrote {len(df):,} PR rows to {output}")
    print(df["agent"].value_counts().to_string())


if __name__ == "__main__":
    main()
