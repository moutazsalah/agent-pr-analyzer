from pathlib import Path

import pandas as pd
from datasets import load_dataset


DATASET = "hao-li/AIDev"
SUBSETS = [
    "pull_request",
    "repository",
    "pr_reviews",
    "pr_comments",
    "pr_commit_details",
    "pr_task_type",
    "related_issue",
]


def main() -> None:
    raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for subset in SUBSETS:
        output_path = raw_dir / f"{subset}.parquet"
        if output_path.exists():
            print(f"Skipping {subset}: {output_path} already exists")
            continue

        print(f"Downloading {subset}...")
        dataset = load_dataset(DATASET, subset, split="train")
        df = pd.DataFrame(dataset)
        df.to_parquet(output_path, index=False)
        print(f"Wrote {len(df):,} rows to {output_path}")


if __name__ == "__main__":
    main()
