import pandas as pd

REQUIRED = ["app_name", "age_years", "yearly_cost", "active_users",
            "vendor_supported", "migration_cost"]


def _to_number(value):
    """Turn values like '₹8,00,000' into 800000. Returns NaN if not possible."""
    if pd.isna(value):
        return float("nan")
    text = str(value).replace("₹", "").replace(",", "").strip()
    return pd.to_numeric(text, errors="coerce")


def clean_data(df):
    """Clean the raw data. Returns (clean_df, rejected_df)."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # Fix formats
    df["app_name"] = df["app_name"].astype(str).str.strip()
    for col in ["age_years", "yearly_cost", "active_users", "migration_cost"]:
        df[col] = df[col].apply(_to_number)

    support = df["vendor_supported"].astype(str).str.strip().str.lower()
    df["vendor_supported"] = support.map(
        {"yes": "Yes", "y": "Yes", "true": "Yes", "no": "No", "n": "No", "false": "No"}
    )

    # Remove duplicates (same app listed twice)
    df = df.drop_duplicates(subset="app_name", keep="first")

    # Missing user count -> treat as 0 users
    df["active_users"] = df["active_users"].fillna(0)

    # Reject invalid rows and keep the reason
    reason = pd.Series("", index=df.index)
    reason[df["yearly_cost"].isna() | (df["yearly_cost"] < 0)] = "Invalid yearly cost"
    reason[df["migration_cost"].isna() | (df["migration_cost"] <= 0)] = "Invalid migration cost"
    reason[df["age_years"].isna() | (df["age_years"] < 0)] = "Invalid age"
    reason[df["vendor_supported"].isna()] = "Unknown vendor support"

    rejected = df[reason != ""].copy()
    rejected["reject_reason"] = reason[reason != ""]
    clean = df[reason == ""].copy()
    return clean.reset_index(drop=True), rejected.reset_index(drop=True)


def score_data(df, horizon_years=3):
    """Add debt score (0-100), priority, savings and ROI columns."""
    df = df.copy()

    cost_per_user = df["yearly_cost"] / df["active_users"].clip(lower=1)

    age_pts = (df["age_years"] / 15).clip(upper=1) * 30
    cost_pts = (cost_per_user / 50000).clip(upper=1) * 30
    usage_pts = (1 - (df["active_users"] / 200).clip(upper=1)) * 20
    support_pts = (df["vendor_supported"] == "No") * 20

    df["debt_score"] = (age_pts + cost_pts + usage_pts + support_pts).round(1)

    df["priority"] = pd.cut(
        df["debt_score"], bins=[-1, 39.99, 69.99, 100], labels=["Low", "Medium", "High"]
    )

    df["net_savings"] = df["yearly_cost"] * horizon_years - df["migration_cost"]
    df["roi_percent"] = (df["net_savings"] / df["migration_cost"] * 100).round(1)

    return df.sort_values("debt_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    raw = pd.read_csv("sample_apps.csv")
    clean, rejected = clean_data(raw)
    result = score_data(clean)

    print("=== RANKED APPLICATIONS ===")
    print(result[["app_name", "debt_score", "priority", "net_savings", "roi_percent"]]
          .to_string(index=False))
    print("\n=== REJECTED ROWS ===")
    print(rejected[["app_name", "reject_reason"]].to_string(index=False))
    print(f"\nRows in: {len(raw)} | clean: {len(clean)} | rejected: {len(rejected)}")