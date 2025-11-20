# TASK 1

from pathlib import Path
from typing import List
import csv
from collections import namedtuple

csv_path = Path('/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Survey.csv')

with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.reader(csv_file)
    headers = next(reader)

    # Filter the header list to only the columns whose names start with 'G'
    g_columns = [col for col in headers if col.startswith('G')]
    g_indices = [headers.index(col) for col in g_columns]

    # Create a NamedTuple type where the fields match the G columns
    SurveyRecord = namedtuple('SurveyRecord', field_names=g_columns)

    survey_table = []

    # Look up the values only for the G columns
    # Put those values into a NamedTuple (SurveyRecord)
    # Append that record to survey_table
    for row in reader:
        if len(row) < len(headers):
            row = row + [''] * (len(headers) - len(row))
        g_row_data = [row[idx] for idx in g_indices]
        survey_record = SurveyRecord(*g_row_data)
        survey_table.append(survey_record)

print(survey_table[0])

# TASK 2

# Take the list of NamedTuples and return a new one with binary values
def convert_yesno_to_binary(table: List[tuple]) -> List[tuple]:
    named_tuple_class = type(table[0])
    converted_rows = []

    # Convert non-yes to 0 and yes to 1
    for row in table:
        row_list = list(row)
        converted_list = []
        for value in row_list:
            if value in ['', 'Do not know', 'No']:
                converted_list.append(0)
            elif value == 'Yes':
                converted_list.append(1)
            else:
                converted_list.append(value)
        # Rebuild the NamedTuple with the binary values
        converted_rows.append(named_tuple_class(*converted_list))

    return converted_rows

binary_survey_table = convert_yesno_to_binary(survey_table)
print(binary_survey_table[0])

# TASK 3

def convert_values_to_numeric(table: List[tuple]) -> List[tuple]:
    # Get the NamedTuple type and all column names
    named_tuple_class = type(table[0])
    column_name_list = named_tuple_class._fields

    numeric_column_list = []
    for column_name in column_name_list:
       # Get all values for the current column
        column_values = [getattr(row, column_name) for row in table]

        # Find all values that are not already numeric
        unique_non_numeric_column_values = set(
            [v for v in column_values if not isinstance(v, (int, float, complex))]
        )

        # Create and apply mapping
        map_dict = {unique_value: idx for idx, unique_value in enumerate(unique_non_numeric_column_values)}

        numeric_column_values = [
            map_dict[val] if val in map_dict else val for val in column_values
        ]

        numeric_column_list.append(numeric_column_values)

   # Combine all converted columns back into rows using zip and rebuild the rows as NamedTuples
    numeric_row_table = list(zip(*numeric_column_list))
    numeric_tuple_table = [named_tuple_class(*row) for row in numeric_row_table]
    return numeric_tuple_table

final_converted_table = convert_values_to_numeric(binary_survey_table)
print(final_converted_table[0])

# TASK 5

import pandas as pd
import numpy as np

# Create a pandas DataFrame from the cleaned NamedTuples
df = pd.DataFrame(final_converted_table)

# Calculate a correlation matrix for all numeric columns
corr_matrix = df.corr()

# Keep only the upper triangle of the correlation matrix to avoid duplicates
upper = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
upper_corr = corr_matrix.where(upper)

# Identify columns that are correlated above 0.75 with another column to be removed
to_drop = [col for col in upper_corr.columns if any(upper_corr[col] > 0.75)]

df_reduced = df.drop(columns=to_drop)

# Show the number of NaNs and a sample of the reduced DataFrame
print(df_reduced.isna().sum())
print(df_reduced.head())

# Remove zero-variance columns
df_fixed = df_reduced.loc[:, df_reduced.var() > 0]

# TASK 6

from factor_analyzer import FactorAnalyzer

# Initialize and fit a factor analysis model to the cleaned data
fa = FactorAnalyzer(rotation=None)
fa.fit(df_fixed)

# Extract the factor loadings and variance explained by each factor
loadings = fa.loadings_
variance = fa.get_factor_variance()

print(loadings)
print(variance)