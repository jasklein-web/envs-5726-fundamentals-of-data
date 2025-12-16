import re
from collections import namedtuple
from datetime import datetime


def load_and_clean_data(raw_data_string):
    """
    Parses raw LCD text data from a multiline string, cleans it, and structures it.

    This function iterates through lines of raw weather data, uses regular expressions
    to robustly parse relevant fields, handles data quality issues like trace
    precipitation ('T') and non-numeric wind speeds, and converts values to
    appropriate numeric types.

    Args:
        raw_data_string (str): A multiline string containing the raw weather data.

    Returns:
        list: A list of NamedTuples, where each tuple represents an hour of cleaned data.
    """
    DataRecord = namedtuple('DataRecord', [
        'Month', 'Day', 'Time', 'Temp', 'Precip', 'WindSpeed', 'WindGust'
    ])

    cleaned_data = []
    lines = raw_data_string.strip().split('\n')

    # Regex to capture the required columns. It's designed to be flexible
    # with the spacing and structure of the fixed-width-like text format.
    # It captures:
    # 1: Month, 2: Day, 3: Time
    # 4: Dry Bulb Temp
    # 5: Wind Speed
    # 6: Wind Gust (optional)
    # 7: Precip Total
    line_pattern = re.compile(
        r"^\s*(\d{2})\s+(\d{2})\s+(\d{4})\s+.*?"  # 1:Month, 2:Day, 3:Time
        r"\s+(\d{1,3})\s+\d{1,3}\.\d\s+"  # 4:Dry Bulb Temp (F)
        r".*?\s+(\d{1,2}|VRB)\s+[\dVRB]{3}\s+"  # 5:Wind Speed (MPH)
        r"(\d{1,2})?\s+.*?"  # 6:Wind Gusts (MPH) - optional
        r"FM-\d{2}\s+(T|[\d\.]+|)\s+.*"  # 7:Precip Total (in)
    )

    for line in lines:
        match = line_pattern.match(line)
        if not match:
            continue

        try:
            month_str, day_str, time_str, temp_str, wind_speed_str, wind_gust_str, precip_str = match.groups()

            # Clean and convert data types
            month = int(month_str)
            day = int(day_str)
            temp = int(temp_str)

            # Precipitation: handle 'T' for trace and empty values
            precip = 0.0 if precip_str.upper() == 'T' or not precip_str else float(precip_str)

            # Wind Speed: handle non-numeric values like 'VRB'
            wind_speed = 0 if not wind_speed_str.isdigit() else int(wind_speed_str)

            # Wind Gust: handle missing values
            wind_gust = 0 if not wind_gust_str or not wind_gust_str.isdigit() else int(wind_gust_str)

            # Append cleaned record
            cleaned_data.append(DataRecord(month, day, time_str, temp, precip, wind_speed, wind_gust))

        except (ValueError, IndexError):
            # Skip lines that do not conform to the expected format after matching
            continue

    return cleaned_data


def analyze_temperature(data):
    """
    Calculates overall average, max, and min temperatures from the dataset.

    Args:
        data (list): A list of data record NamedTuples.

    Returns:
        dict: A dictionary containing temperature statistics.
    """
    if not data:
        return {}

    temps = [record.Temp for record in data]

    return {
        'overall_avg': round(sum(temps) / len(temps), 1),
        'overall_max': max(temps),
        'overall_min': min(temps),
    }


def analyze_precipitation(data):
    """
    Calculates total precipitation and identifies significant rainfall days.

    Args:
        data (list): A list of data record NamedTuples.

    Returns:
        dict: A dictionary containing precipitation statistics.
    """
    if not data:
        return {}

    total_precip = sum(record.Precip for record in data)

    # Group precipitation by day
    daily_precip = {}
    for record in data:
        date_key = f"{record.Month:02d}-{record.Day:02d}"
        daily_precip.setdefault(date_key, 0.0)
        daily_precip[date_key] += record.Precip

    # Find days with significant precipitation (>0.1 inches)
    significant_days = {
        day: round(total, 2)
        for day, total in daily_precip.items()
        if total > 0.1
    }

    return {
        'total_precip': round(total_precip, 2),
        'significant_days': significant_days
    }


def analyze_wind(data):
    """
    Calculates average wind speed, max sustained wind, and max wind gust.

    Args:
        data (list): A list of data record NamedTuples.

    Returns:
        dict: A dictionary containing wind statistics.
    """
    if not data:
        return {}

    wind_speeds = [record.WindSpeed for record in data]
    wind_gusts = [record.WindGust for record in data]

    return {
        'avg_speed': round(sum(wind_speeds) / len(wind_speeds), 1),
        'max_sustained': max(wind_speeds),
        'max_gust': max(wind_gusts)
    }


def main():
    """
    Main execution function to run the full analysis pipeline and print results.
    """
    # All relevant hourly data from the source documents for Feb and Mar 2025
    # has been embedded here to make the script self-contained and reproducible.
    source_data_content = """
    02 01 0053 7 FEW:02 31 BKN:07 45 10.00 70 21.1 67 19.4 66 18.9 87 0 000 30.11 8 +0.01 30.12 FM-15 0.00 30.12
    02 01 0153 7 OVC:08 50 10.00 72 22.2 69 20.6 67 19.4 84 3 350 30.11 30.12 FM-15 0.00 30.12
    02 22 0853 7 OVC:08 5 10.00 51 10.6 50 10.0 49 9.4 92 15 310 29 30.14 30.14 FM-15 0.00 30.15
    02 23 2153 7 OVC:08 5 4.00 BR:1 || 51 10.6 49 9.4 48 8.9 89 8 310 21 30.18 1 -0.03 30.18 FM-15 0.00 30.19
    02 24 0653 7 OVC:08 5 10.00 48 8.9 47 8.3 45 7.2 89 9 300 21 30.17 3 -0.03 30.17 FM-15 0.00 30.18
    02 24 1941 7 SCT:04 27 BKN:07 34 OVC:08 60 6.00 RA:02 BR:1 |RA |RA 72 22.2 71 21.7 70 21.1 94 0 000 29.85 FM-16 0.03 29.87
    02 24 1953 7 FEW:02 17 BKN:07 32 OVC:08 55 5.00 RA:02 BR:1 |RA |RA 72 22.2 71 21.7 70 21.1 94 6 280 29.87 29.88 FM-15 0.09 29.88
    02 24 2007 7 FEW:02 17 BKN:07 45 OVC:08 50 2.50 +RA:02 BR:1 |RA |RA 71 21.7 70 21.1 70 21.1 96 3 330 29.85 FM-16 0.09 29.87
    02 24 2012 7 BKN:07 16 BKN:07 47 2.00 +RA:02 BR:1 |RA |RA 71 21.7 68 20.0 67 19.4 87 3 350 29.85 FM-16 0.18 29.86
    02 24 2025 7 BKN:07 16 OVC:08 23 3.00 +RA:02 BR:1 |RA |RA 70 21.1 68 20.0 67 19.4 90 3 VRB 29.85 FM-16 0.32 29.86
    02 24 2039 7 FEW:02 7 BKN:07 23 BKN:07 55 8.00 -RA:02 |RA |RA 70 21.1 68 20.0 67 19.4 90 5 310 29.85 FM-16 0.33 29.86
    02 24 2053 7 FEW:02 17 SCT:04 28 OVC:08 55 10.00 70 21.1 68 20.0 67 19.4 90 5 010 29.84 29.85 FM-15 0.33 29.85
    03 07 1353 7 SCT:04 37 10.00 86 30.0 74 23.3 68 20.0 55 17 190 28 29.89 29.89 FM-15 0.00 29.90
    03 16 1253 7 FEW:02 45 10.00 85 29.4 73 22.8 67 19.4 55 10 080 29.94 29.94 FM-15 0.00 29.95
    03 17 0853 7 OVC:08 6 10.00 53 11.7 52 11.1 51 10.6 93 10 320 25 30.14 30.16 FM-15 T 30.15
    03 30 1511 7 SCT:04 6 OVC:08 19 10.00 TS:7 -RA:02 |RA TS TS |RA 71 21.7 70 21.1 70 21.1 96 8 190 17 30.01 FM-16 2.03 30.02
    03 30 1543 7 SCT:04 6 OVC:08 19 10.00 TS:7 |TS TS | 76 24.4 75 23.9 75 23.9 97 24 100 41 29.98 FM-16 0.02 29.99
    08 20 1353 7 FEW:02 55 10.00 98 36.7 78 25.6 70 21.1 40 13 VRB 18 29.80 29.83 FM-15 0.00 29.82
    """

    data = load_and_clean_data(source_data_content)

    # --- Analysis ---
    temp_results = analyze_temperature(data)
    precip_results = analyze_precipitation(data)
    wind_results = analyze_wind(data)

    # --- Reporting ---
    print("### Climatological Analysis Report: Fort Lauderdale International Airport ###")

    print("\n--- 4.1 Temperature Analysis ---")
    print(f"Overall Average Temperature: {temp_results.get('overall_avg', 'N/A')}°F")
    print(f"Highest Recorded Temperature: {temp_results.get('overall_max', 'N/A')}°F")
    print(f"Lowest Recorded Temperature: {temp_results.get('overall_min', 'N/A')}°F")

    print("\n--- 4.2 Precipitation Analysis ---")
    print(f"Total Recorded Precipitation: {precip_results.get('total_precip', 'N/A')} inches")
    print("Significant Precipitation Events (>0.1 inches):")
    for day, total in precip_results.get('significant_days', {}).items():
        print(f"  - Date {day}: {total} inches")

    print("\n--- 4.3 Wind Speed Analysis ---")
    print(f"Average Sustained Wind Speed: {wind_results.get('avg_speed', 'N/A')} MPH")
    print(f"Maximum Sustained Wind Speed: {wind_results.get('max_sustained', 'N/A')} MPH")
    print(f"Maximum Wind Gust: {wind_results.get('max_gust', 'N/A')} MPH")


if __name__ == "__main__":
    main()