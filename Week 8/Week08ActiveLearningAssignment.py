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

#TASK 4

"""
After researching keywords like ‘factor_analyzer NaN error’, ‘factor analyzer correlation matrix zero determinant’, and 
‘factor analysis multicollinearity’, I found that the issue happens because the factor_analyzer library internally computes a 
correlation matrix. If two columns are perfectly or almost perfectly correlated, the correlation matrix becomes singular. 
When the library tries to invert that matrix, the inversion produces NaN values. So even though my actual dataset has no NaNs, 
the correlation matrix created by factor_analyzer does contain NaNs due to multicollinearity.

The solution is to detect and remove highly correlated columns before running factor analysis.
"""

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

"""
The NaN table represents the correlation matrix after the library tries to invert it, and the NaNs indicate columns that 
were too correlated to remain in the dataset.

To fix this, I removed the highly correlated columns and also filtered out any zero-variance columns. This produces a 
DataFrame called `df_fixed` that can successfully be used in factor analysis.
"""

# TASK 6

from factor_analyzer import FactorAnalyzer

# Create factor analysis object and perform initial factor analysis
fa = FactorAnalyzer(rotation="varimax")
fa.fit(df_fixed)

# Perform factor analysis with the determined number of factors
number_of_factors = 5
fa = FactorAnalyzer(n_factors=number_of_factors, rotation="varimax")
fa.fit(df_fixed)

# Create factor names
factor_names = [f'Factor{i+1}' for i in range(number_of_factors)]

# Loadings DataFrame
loadings_df = pd.DataFrame(fa.loadings_,
                           columns=factor_names,
                           index=df_fixed.columns)

# Get variance of each factor
index_names = [
    'Sum of Squared Loadings',
    'Proportional Variance',
    'Cumulative Variance'
]

variance_df = pd.DataFrame(fa.get_factor_variance(),
                           columns=factor_names,
                           index=index_names)

# Export results
loadings_df.to_csv(r"/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Loadings.csv")
variance_df.to_csv(r"/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Variance.csv")

"""
According to Dr. Kumar’s interpretation, factor analysis reveals the underlying dimensions of the WASH dataset, meaning 
it groups related survey questions into clusters that represent broader WASH themes. This helps us understand which aspects 
of water, sanitation, and hygiene vary the most across the refugee camps.

A different environmental problem where factor analysis could be useful would be urban environmental justice. For example, 
if a city collects dozens of environmental and health indicators like PM2.5, traffic density, asthma rates, temperature, and 
green space, factor analysis could uncover the underlying risk factors such as ‘traffic emissions’, ‘heat exposure’, or 
‘socioeconomic vulnerability’. This reduces a large number of variables into a few interpretable factors that help guide 
policy decisions.
"""