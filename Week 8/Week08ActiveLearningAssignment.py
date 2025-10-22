from typing import NamedTuple, List
import csv
from pathlib import Path
import pandas as pd
from factor_analyzer import FactorAnalyzer
import numpy as np


class SurveyRecord(NamedTuple):
    G1_1: str
    G1_2: str
    G2_1: str
    G2_2: str
    G2_3: str
    G2_4: str
    G2_5: str
    G2_6: str
    G2_7: str
    G2_8: str
    G2_9: str
    G2_10: str
    G2_11: str
    G3_1: str
    G3_2: str
    G3_3: str
    G3_4: str
    G3_5: str
    G3_6: str
    G3_7: str
    G3_8: str
    G3_9: str
    G3_10: str
    G4_1: str
    G4_2: str
    G5_1: str
    G5_2: str
    G6_1: str
    G6_2: str
    G6_3: str
    G6_4: str
    G6_5: str
    G6_6: str
    G6_7: str
    G6_8: str
    G6_9: str
    G6_10: str
    G6_11: str
    G6_12: str
    G6_13: str
    G7_1: str
    G8_1: str
    G9_1: str
    G10_1: str
    G10_2: str
    G11_1: str
    G11_2: str
    G11_3: str
    G11_4: str
    G11_5: str
    G11_6: str
    G11_7: str
    G11_8: str
    G11_9: str
    G11_10: str
    G11_11: str
    G11_12: str
    G11_13: str
    G11_14: str
    G12_1: str
    G13_1: str
    G14_1: str
    G15_1: str
    G15_2: str


def convert_yesno_to_binary(table):
    converted_table = []
    for row in table:
        row_list = list(row)
        converted_list = []
        for value in row_list:
            if value == '':
                converted_list.append(0)
            elif value == 'Do not know':
                converted_list.append(0)
            elif value == 'No':
                converted_list.append(0)
            elif value == 'Yes':
                converted_list.append(1)
            else:
                converted_list.append(value)
        converted_row = SurveyRecord(*converted_list)
        converted_table.append(converted_row)
    return converted_table


def get_categories(table, category_column):
    unique_values = set()
    for row in table:
        value = getattr(row, category_column)
        unique_values.add(value)
    return unique_values


def get_non_numeric_values(table):
    non_numeric_count = 0
    for row_index, row in enumerate(table):
        for column_name in row._fields:
            value = getattr(row, column_name)
            if not isinstance(value, (int, float, complex)):
                print(f"Row {row_index} Column {column_name}: {value}")
                non_numeric_count += 1
    return non_numeric_count


# TASK 1: Load CSV and create NamedTuples
print("=== TASK 1: Creating NamedTuples from CSV ===")
csv_path = Path('/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Survey.csv')
survey_record_table = []

with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.reader(csv_file)
    headers = next(reader)

    g_columns = [header for header in headers if header.startswith('G')]

    for row in reader:
        g_values = []
        for header in g_columns:
            col_index = headers.index(header)
            cell_value = row[col_index]
            g_values.append(cell_value)

        survey_record = SurveyRecord(*g_values)
        survey_record_table.append(survey_record)

print("First row of original data:")
print(survey_record_table[0])
print()

# TASK 2: Convert Yes/No to binary
print("=== TASK 2: Converting Yes/No to Binary ===")
binary_survey_table = convert_yesno_to_binary(survey_record_table)
print("First row after binary conversion:")
print(binary_survey_table[0])
print()

# TASK 3: Get unique categories
print("=== TASK 3: Getting Unique Categories ===")
g1_1_categories = get_categories(binary_survey_table, 'G1_1')
print("Unique values in G1_1:", g1_1_categories)
print()

# Define mapping dictionaries
G1_1_map = {
    'Storage Tanks tap / tap stand': 1,
    'Tube wells / handpump': 2,
    'Piped water tap / tap stand': 3,
    'No water accessible': 4,
    'Surface water pond, stream, etc.': 5,
    'Unprotected Well': 6
}

G4_1_map = {
    'Most girls and women bathe in communal/public bathing facilities': 1,
    'Most girls and women bathe in bathing cubicles inside the shelter': 2,
    'Most girls and women bathe in open areas outside the shelter': 3,
    'Most girls and women bathe in bathing cubicles shared between shelters': 4
}

G5_1_map = {
    'Most men and boys bathe in communal/public bathing facilities': 1,
    'Most men and boys bathe in bathing cubicles inside the shelter': 2,
    'Most men and boys bathe in open areas outside the shelter': 3,
    'Most men and boys bathe in bathing cubicles shared between shelters': 4
}

G10_1_map = {
    'Most girls and women use communal/public latrines': 1,
    'Most girls and women use a private latrine inside the shelter': 2,
    'Most girls and women use open areas outside the shelter': 3,
    'Most girls and women use a private latrine shared between shelters': 4
}

# TASK 4: Map all string values to numbers
print("=== TASK 4: Mapping All Values to Numbers ===")
final_numeric_data = []
for row in binary_survey_table:
    numeric_row = []

    for column_name in row._fields:
        value = getattr(row, column_name)

        if column_name == 'G1_1' and value in G1_1_map:
            numeric_value = G1_1_map[value]
        elif column_name == 'G4_1' and value in G4_1_map:
            numeric_value = G4_1_map[value]
        elif column_name == 'G5_1' and value in G5_1_map:
            numeric_value = G5_1_map[value]
        elif column_name == 'G10_1' and value in G10_1_map:
            numeric_value = G10_1_map[value]
        elif isinstance(value, str):
            if value == '':
                numeric_value = 0
            elif value in ['Do not know', 'No']:
                numeric_value = 0
            elif value == 'Yes':
                numeric_value = 1
            else:
                numeric_value = 0
        else:
            numeric_value = value

        numeric_row.append(numeric_value)

    final_numeric_data.append(numeric_row)

final_survey_table = []
for numeric_row in final_numeric_data:
    final_row = SurveyRecord(*numeric_row)
    final_survey_table.append(final_row)

print("First row after complete conversion to numbers:")
print(final_survey_table[0])
print()

# TASK 5: Check for non-numeric values
print("=== TASK 5: Checking for Non-Numeric Values ===")
non_numeric_count = get_non_numeric_values(final_survey_table)
print(f"Total non-numeric values found: {non_numeric_count}")
print()

# Create DataFrame and clean data
df = pd.DataFrame(final_numeric_data, columns=SurveyRecord._fields)
df = df.astype(float)

# Remove zero-variance columns
zero_variance_columns = []
for column in df.columns:
    if df[column].std() == 0:
        zero_variance_columns.append(column)

df = df.drop(columns=zero_variance_columns)

print(f"Removed {len(zero_variance_columns)} zero-variance columns")
print(f"Final DataFrame shape: {df.shape}")
print()

# TASKS 6-8: Perform Factor Analysis
print("=== TASKS 6-8: Performing Factor Analysis ===")
fa = FactorAnalyzer(rotation="varimax")
fa.fit(df)

number_of_factors = 5
fa = FactorAnalyzer(n_factors=number_of_factors, rotation="varimax")
fa.fit(df)

factor_names = [f'Factor{i + 1}' for i in range(number_of_factors)]

loadings_df = pd.DataFrame(fa.loadings_, columns=factor_names, index=df.columns)
variance_df = pd.DataFrame(fa.get_factor_variance(), columns=factor_names,
                           index=['Sum of Squared Loadings', 'Proportional Variance', 'Cumulative Variance'])

# Save files to Downloads folder
downloads_path = Path('/Users/jasonklein/Downloads')
loadings_file = downloads_path / 'IOM_Rohingya_WASH_Loadings.csv'
variance_file = downloads_path / 'IOM_Rohingya_WASH_Variance.csv'

loadings_df.to_csv(loadings_file)
variance_df.to_csv(variance_file)

print("Factor analysis completed successfully!")
print(f"Loadings saved to: {loadings_file}")
print(f"Variance explained saved to: {variance_file}")
print()
print("Variance explained by each factor:")
print(variance_df)