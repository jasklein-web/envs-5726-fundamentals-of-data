# TASK 1

from pathlib import Path
from typing import List
import csv
from collections import namedtuple

csv_path = Path('/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Survey.csv')

with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.reader(csv_file)
    headers = next(reader)

    g_columns = [col for col in headers if col.startswith('G')]
    g_indices = [headers.index(col) for col in g_columns]

    SurveyRecord = namedtuple('SurveyRecord', field_names=g_columns)

    survey_table = []

    for row in reader:
        if len(row) < len(headers):
            row = row + [''] * (len(headers) - len(row))
        g_row_data = [row[idx] for idx in g_indices]
        survey_record = SurveyRecord(*g_row_data)
        survey_table.append(survey_record)

print(survey_table[0])

# TASK 2

def convert_yesno_to_binary(table: List[tuple]) -> List[tuple]:
    named_tuple_class = type(table[0])
    converted_rows = []

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
        converted_rows.append(named_tuple_class(*converted_list))

    return converted_rows

binary_survey_table = convert_yesno_to_binary(survey_table)
print(binary_survey_table[0])

# TASK 3

def convert_values_to_numeric(table: List[tuple]) -> List[tuple]:
    named_tuple_class = type(table[0])
    column_name_list = named_tuple_class._fields

    numeric_column_list = []
    for column_name in column_name_list:
        column_values = [getattr(row, column_name) for row in table]

        unique_non_numeric_column_values = set(
            [v for v in column_values if not isinstance(v, (int, float, complex))]
        )

        map_dict = {unique_value: idx for idx, unique_value in enumerate(unique_non_numeric_column_values)}

        numeric_column_values = [
            map_dict[val] if val in map_dict else val for val in column_values
        ]

        numeric_column_list.append(numeric_column_values)

    numeric_row_table = list(zip(*numeric_column_list))
    numeric_tuple_table = [named_tuple_class(*row) for row in numeric_row_table]
    return numeric_tuple_table

final_converted_table = convert_values_to_numeric(binary_survey_table)
print(final_converted_table[0])

# TASK 5

import pandas as pd
import numpy as np

df = pd.DataFrame(final_converted_table)

corr_matrix = df.corr()

upper = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
upper_corr = corr_matrix.where(upper)

to_drop = [col for col in upper_corr.columns if any(upper_corr[col] > 0.75)]

df_reduced = df.drop(columns=to_drop)

print(df_reduced.isna().sum())
print(df_reduced.head())

df_fixed = df_reduced.loc[:, df_reduced.var() > 0]

# TASK 6

from factor_analyzer import FactorAnalyzer

fa = FactorAnalyzer(rotation=None)
fa.fit(df_fixed)

loadings = fa.loadings_
variance = fa.get_factor_variance()

print(loadings)
print(variance)