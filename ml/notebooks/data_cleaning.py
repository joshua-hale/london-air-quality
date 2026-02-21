import pandas as pd

def merge_pollution_weather_data() -> pd.DataFrame:
    """
    Merge pollution and weather data parquets
    Note: Data required no further cleaning 
    - No missing data
    - No null values
    - No problematic 0 values
    """

    pollution = pd.read_parquet("data/raw/pollution/all_boroughs_2025-2026.parquet")
    weather = pd.read_parquet("data/raw/weather/all_boroughs_2025-2026.parquet")

    df = pollution.merge(weather, on=["timestamp", "borough"], suffixes=("", "_weather"))

    df = df.drop(columns=["latitude_weather", "longitude_weather"])

    return df


if __name__ == "__main__":
    df = merge_pollution_weather_data()
    df.to_parquet("data/processed/cleaned_data.parquet")
    print(f"Merged rows: {len(df)}")
    print(df.shape)
    print(df.isnull().sum())

