import pandas as pd


def remove_duplicates(df):
    """Remove duplicate records."""
    return df.drop_duplicates()


def convert_dates(df):
    """Convert the date column to datetime."""
    df["date"] = pd.to_datetime(df["date"])
    return df


def fill_missing_lead_time(df):
    """Fill missing lead_time_days with the median."""
    df["lead_time_days"] = df["lead_time_days"].fillna(
        df["lead_time_days"].median()
    )
    return df


def clean_dataset(df):
    """Run the full preprocessing pipeline."""
    df = remove_duplicates(df)
    df = convert_dates(df)
    df = fill_missing_lead_time(df)
    return df