# TASK 1

from pathlib import Path  # Import Path class for cross-platform file path handling
from typing import List  # Import List type hint for better code documentation
import csv  # Import CSV module for reading CSV files
from collections import namedtuple  # Import namedtuple for creating structured data classes

# Create a Path object representing the location of the CSV file
csv_path = Path('/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Survey.csv')

# Open the CSV file with UTF-8 encoding that handles BOM (Byte Order Mark)
with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
    # Create a CSV reader object that will iterate over rows in the file
    reader = csv.reader(csv_file)

    # Read the first row which contains column headers and move reader to next row
    headers = next(reader)

    # Filter headers to only include columns that start with 'G' (WASH-related columns)
    g_columns = [col for col in headers if col.startswith('G')]

    # Get the index positions of the G columns in the original headers list
    g_indices = [headers.index(col) for col in g_columns]

    # Create a namedtuple class called 'SurveyRecord' with the G columns as field names
    SurveyRecord = namedtuple('SurveyRecord', field_names=g_columns)

    # Initialize an empty list to store all the survey records
    survey_table = []

    # Iterate through each remaining row in the CSV file
    for row in reader:
        # Extract only the values corresponding to the G columns using their indices
        g_row_data = [row[idx] for idx in g_indices]

        # Create a SurveyRecord instance by unpacking the filtered row data
        survey_record = SurveyRecord(*g_row_data)

        # Add the newly created SurveyRecord to our table
        survey_table.append(survey_record)

# Print the first SurveyRecord to verify the data structure
print(survey_table[0])


# TASK 2

# Define a function that converts 'Yes'/'No' responses to binary 1/0 values
def convert_yesno_to_binary(table: List[tuple]) -> List[tuple]:
    # Get the class/type of the first tuple (SurveyRecord namedtuple class)
    named_tuple_class = type(table[0])

    # Initialize an empty list to store the converted rows
    converted_rows = []

    # Iterate through each namedtuple in the input table
    for row in table:
        # Convert the namedtuple to a regular list for mutability
        row_list = list(row)

        # Initialize an empty list for the converted values of this row
        converted_list = []

        # Process each value in the current row
        for value in row_list:
            # Check if value is empty string, 'Do not know', or 'No' - convert to 0
            if value in ['', 'Do not know', 'No']:
                converted_list.append(0)  # Map to binary 0
            # Check if value is 'Yes' - convert to 1
            elif value == 'Yes':
                converted_list.append(1)  # Map to binary 1
            # For all other values, keep them unchanged
            else:
                converted_list.append(value)

        # Reconstruct a namedtuple from the converted list and add to results
        converted_rows.append(named_tuple_class(*converted_list))

    # Return the complete list of converted namedtuples
    return converted_rows

# Apply the binary conversion function to the survey table
binary_survey_table = convert_yesno_to_binary(survey_table)

# Print the first converted record for verification
print(binary_survey_table[0])


# TASK 3
# Take the binary-converted data from Task 2 and convert EVERY remaining string value into unique numeric codes

def convert_values_to_numeric(table: List[tuple]) -> List[tuple]:
    # Get the namedtuple class from the first element
    named_tuple_class = type(table[0])

    # Get the list of field names (column names) from the namedtuple class
    column_name_list = named_tuple_class._fields

    # Initialize an empty list to store each column's converted values separately
    numeric_column_list = []

    # Process each column independently
    for column_name in column_name_list:
        # Extract all values for this column from all rows using getattr
        column_values = [getattr(row, column_name) for row in table]

        # Create a set of unique values that are NOT already numeric
        unique_non_numeric_column_values = set(
            # List comprehension filtering out numeric values
            [v for v in column_values if not isinstance(v, (int, float, complex))]
        )

        # Create a dictionary mapping each unique string to a unique integer index
        map_dict = {unique_value: idx for idx, unique_value in enumerate(unique_non_numeric_column_values)}

        # Convert all values in this column: mapped values get integers, others stay same
        numeric_column_values = [
            map_dict[val] if val in map_dict else val for val in column_values
        ]

        # Add this column's converted values to our column-wise list
        numeric_column_list.append(numeric_column_values)

    # Transpose the column-wise data back to row-wise using zip and unpacking
    numeric_row_table = list(zip(*numeric_column_list))

    # Reconstruct namedtuples from each row of numeric values
    numeric_tuple_table = [named_tuple_class(*row) for row in numeric_row_table]

    # Return the fully numeric-converted table
    return numeric_tuple_table


# Apply the numeric conversion function to the binary-converted table
final_converted_table = convert_values_to_numeric(binary_survey_table)

# Print the first fully numeric record for verification
print(final_converted_table[0])

# Now EVERY value in EVERY column is a number (went from just binary responses in Task 2 to categorical strings in Task 3)

# TASK 4

"""
After researching keywords like 'factor_analyzer NaN error', 'factor analyzer correlation matrix zero determinant', and 
'factor analysis multicollinearity', I found that the issue happens because the factor_analyzer library internally computes a 
correlation matrix. If two columns are perfectly or almost perfectly correlated, the correlation matrix becomes singular. 
When the library tries to invert that matrix, the inversion produces NaN values. So even though my actual dataset has no NaNs, 
the correlation matrix created by factor_analyzer does contain NaNs due to multicollinearity.

The solution is to detect and remove highly correlated columns before running factor analysis.
"""

# TASK 5

import pandas as pd  # Import pandas for DataFrame operations
import numpy as np  # Import numpy for numerical operations and matrix manipulation

# Convert the list of namedtuples to a pandas DataFrame
df = pd.DataFrame(final_converted_table)

# Calculate the correlation matrix for all numeric columns in the DataFrame
corr_matrix = df.corr()

# Create a boolean mask for the upper triangle of the correlation matrix (excluding diagonal)
upper = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)

# Apply the mask to keep only the upper triangle values (set others to NaN)
upper_corr = corr_matrix.where(upper)

# Identify columns that have correlation > 0.75 with any other column for these columns to be dropped
to_drop = [col for col in upper_corr.columns if any(upper_corr[col] > 0.75)]

# Create a new DataFrame with the highly correlated columns removed
df_reduced = df.drop(columns=to_drop)

# Print the count of NaN values in each column to verify no NaNs exist
print(df_reduced.isna().sum())

# Print the first 5 rows of the reduced DataFrame for visual inspection
print(df_reduced.head())

# Remove any columns with zero variance (all same values), which cause issues in factor analysis
df_fixed = df_reduced.loc[:, df_reduced.var() > 0]

"""
The NaN table represents the correlation matrix after the library tries to invert it, and the NaNs indicate columns that 
were too correlated to remain in the dataset.

To fix this, I removed the highly correlated columns and also filtered out any zero-variance columns. This produces a 
DataFrame called `df_fixed` that can successfully be used in factor analysis.
"""

# ===== TASK 6: PERFORMING FACTOR ANALYSIS =====

from factor_analyzer import FactorAnalyzer  # Import the FactorAnalyzer class

# Create FactorAnalyzer object with varimax rotation for interpretable factors
fa = FactorAnalyzer(rotation="varimax")

# Fit the factor analysis model to our cleaned data (initial fit)
fa.fit(df_fixed)

# Set the number of factors to extract (determined from prior analysis/scree plot)
number_of_factors = 5

# Create a new FactorAnalyzer with the specified number of factors
fa = FactorAnalyzer(n_factors=number_of_factors, rotation="varimax")

# Fit the factor analysis model with the specified number of factors
fa.fit(df_fixed)

# Create descriptive names for each factor (Factor1, Factor2, etc.)
factor_names = [f'Factor{i + 1}' for i in range(number_of_factors)]

# Create a DataFrame of factor loadings (relationship between variables and factors)
loadings_df = pd.DataFrame(fa.loadings_,
                           columns=factor_names,
                           index=df_fixed.columns)

# Define row names for the variance statistics DataFrame
index_names = [
    'Sum of Squared Loadings',  # Total variance explained by each factor
    'Proportional Variance',  # Percentage of total variance explained
    'Cumulative Variance'  # Running total of variance explained
]

# Create a DataFrame of variance statistics for each factor
variance_df = pd.DataFrame(fa.get_factor_variance(),
                           columns=factor_names,
                           index=index_names)

# Save the factor loadings to a CSV file for further analysis
loadings_df.to_csv(r"/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Loadings.csv")

# Save the variance statistics to a CSV file for documentation
variance_df.to_csv(r"/Users/jasonklein/Downloads/IOM_Rohingya_WASH_Variance.csv")

"""
According to Dr. Kumar's interpretation, factor analysis reveals the underlying dimensions of the WASH dataset, meaning 
it groups related survey questions into clusters that represent broader WASH themes. This helps us understand which aspects 
of water, sanitation, and hygiene vary the most across the refugee camps.

A different environmental problem where factor analysis could be useful would be urban environmental justice. For example, 
if a city collects dozens of environmental and health indicators like PM2.5, traffic density, asthma rates, temperature, and 
green space, factor analysis could uncover the underlying risk factors such as 'traffic emissions', 'heat exposure', or 
'socioeconomic vulnerability'. This reduces a large number of variables into a few interpretable factors that help guide 
policy decisions.
"""