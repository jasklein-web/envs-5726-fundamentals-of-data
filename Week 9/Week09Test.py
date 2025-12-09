import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime

# TASK 1: Weibull CDF fitting (from previous task)

# Load the data
def load_pipe_materials_data():
    data = {
        'Material Type': ['Cast Iron', 'Cast Iron', 'Cast Iron',
                          'Ductile Iron', 'Ductile Iron', 'Ductile Iron',
                          'Galvanized Iron', 'Galvanized Iron', 'Galvanized Iron',
                          'Copper', 'Copper', 'Copper'],
        'Life Expectancy (y)': [10, 75, 150, 10, 55, 110, 10, 25, 50, 10, 38, 75],
        'Surv. Prob. (%)': [100, 50, 10, 100, 50, 10, 100, 50, 10, 100, 50, 10]
    }
    return pd.DataFrame(data)


# Using standard Weibull survival function (2 parameters)
def weibull_survival(t, scale, shape):
    """Standard Weibull survival function: S(t) = exp(-(t/scale)^shape)"""
    return np.exp(-(t / scale) ** shape)


def plot_cdf_curve_fit(table, material_type, line_color):
    # Filter data
    material_data = table[table['Material Type'] == material_type]
    xdata = material_data['Life Expectancy (y)'].values
    ydata = material_data['Surv. Prob. (%)'].values / 100

    # Get reasonable initial guesses
    # scale parameter: around the age where survival is 50%
    scale_guess = xdata[1] if len(xdata) > 1 else xdata[0] * 2
    shape_guess = 1.0

    try:
        # Fit the Weibull survival function
        params, _ = curve_fit(weibull_survival, xdata, ydata,
                              p0=[scale_guess, shape_guess],
                              bounds=([1, 0.1], [200, 5]))
        scale, shape = params

        print(f'Weibull fit for {material_type}: S(t) = exp(-(t/{scale:.2f})^{shape:.4f})')

        # Generate smooth curve
        x_curve = np.linspace(0, max(xdata) * 1.2, 200)
        y_curve = weibull_survival(x_curve, scale, shape) * 100

        # Plot
        plt.plot(x_curve, y_curve, color=line_color, label=material_type, linewidth=2)

        return (scale, shape)

    except Exception as e:
        print(f"Error fitting {material_type}: {e}")
        return None


# Main execution
pipe_materials_table = load_pipe_materials_data()

plt.figure(figsize=(12, 8))

# Plot all materials
plot_cdf_curve_fit(pipe_materials_table, 'Cast Iron', 'red')
plot_cdf_curve_fit(pipe_materials_table, 'Ductile Iron', 'blue')
plot_cdf_curve_fit(pipe_materials_table, 'Galvanized Iron', 'green')
plot_cdf_curve_fit(pipe_materials_table, 'Copper', 'brown')

# Formatting
plt.legend()
plt.xlabel('Life Expectancy (y)')
plt.ylabel('Survival Probability (%)')
plt.title('Pipe Material Survival CDF')
plt.show

plt.show()

# TASK 2: Process Water Mains data

# Load the water mains data from CSV
def load_water_mains_data():
    """Load the water mains data from CSV file"""
    file_path = "/Users/jasonklein/Downloads/Water_Mains.csv"
    water_mains_table = pd.read_csv(file_path)
    return water_mains_table


# Define the Weibull CDF function (same as Task 1)
def cumulative_density_function(age, c, b, a):
    """Weibull CDF function for survival probability"""
    return 1 - c * np.exp(-(age / b) ** a)


# Store coefficients by material type (update with your actual coefficients from Task 1)
def create_coefficients_dict():
    """Create a dictionary to store Weibull coefficients by material type"""
    # IMPORTANT: Replace these with your actual coefficients from Task 1
    # Format: {material: (c, b, a)}
    coefficients = {
        'Cast Iron': (1.0, 75.0, 2.0),  # Replace with your actual values
        'Ductile Iron': (1.0, 55.0, 2.0),  # Replace with your actual values
        'Galvanized Iron': (1.0, 25.0, 2.0),  # Replace with your actual values
        'Copper': (1.0, 38.0, 2.0)  # Replace with your actual values
    }
    return coefficients


def parse_install_date(date_str):
    """
    Parse the InstallDate string with format: '8/9/2018  4:40:00 PM'
    Handles various edge cases in date formatting
    """
    if pd.isna(date_str):
        return pd.NaT

    # Clean up the date string - remove extra spaces
    date_str = str(date_str).strip()

    # Try different date formats
    date_formats = [
        '%m/%d/%Y %I:%M:%S %p',  # 8/9/2018 4:40:00 PM
        '%m/%d/%Y %I:%M %p',  # 8/9/2018 4:40 PM
        '%m/%d/%y %I:%M:%S %p',  # 8/9/18 4:40:00 PM
        '%m/%d/%y %I:%M %p',  # 8/9/18 4:40 PM
        '%m/%d/%Y %H:%M:%S',  # 8/9/2018 16:40:00
        '%m/%d/%Y %H:%M',  # 8/9/2018 16:40
        '%m/%d/%y %H:%M:%S',  # 8/9/18 16:40:00
        '%m/%d/%y %H:%M',  # 8/9/18 16:40
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue

    # If none of the formats work, return NaT
    return pd.NaT


def calculate_age_and_survival_probability(water_mains_table):
    """
    Add Age and Survival_Probability columns to the water mains table
    """
    # Set current year (as per assignment example: 2025)
    current_year = 2025

    print("Processing InstallDate column...")

    # Parse InstallDate using our custom function
    water_mains_table['InstallDate'] = water_mains_table['InstallDate'].apply(parse_install_date)

    # Check for any parsing issues
    invalid_dates = water_mains_table['InstallDate'].isna().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} dates could not be parsed")

    # Calculate Age (years from install date to current year)
    water_mains_table['Age'] = current_year - pd.to_datetime(water_mains_table['InstallDate']).dt.year

    # For any invalid dates, set age to 0
    water_mains_table['Age'] = water_mains_table['Age'].fillna(0).astype(int)

    # Get coefficients dictionary
    coefficients_dict = create_coefficients_dict()

    print("Calculating Survival Probability...")

    # Calculate survival probability for each row
    survival_probs = []
    for idx, row in water_mains_table.iterrows():
        material = row['Material']
        age = row['Age']

        if material in coefficients_dict:
            c, b, a = coefficients_dict[material]

            # Calculate survival probability using Weibull CDF
            try:
                # Avoid division by zero
                if b == 0:
                    prob = 100 if age == 0 else 0
                else:
                    prob = cumulative_density_function(age, c, b, a) * 100

                # Cap at 100% as per instructions
                if prob > 100:
                    prob = 100
                elif prob < 0:
                    prob = 0

            except (ValueError, ZeroDivisionError) as e:
                # Handle calculation errors
                prob = 100 if age == 0 else 0
        else:
            # Default for unknown materials
            print(f"Warning: Material '{material}' not in coefficients dictionary")
            prob = 100

        survival_probs.append(round(prob, 2))

    water_mains_table['Survival_Probability'] = survival_probs

    return water_mains_table


# Main execution for Task 2
if __name__ == "__main__":
    print("=" * 70)
    print("TASK 2: Water Mains Age and Survival Probability Calculation")
    print("=" * 70)

    try:
        # Load the data
        water_mains_table = load_water_mains_data()
        print(f"Successfully loaded {len(water_mains_table)} rows")

        # Display original data (first 5 rows)
        print("\nOriginal data (first 5 rows):")
        print(water_mains_table.head().to_string())

        # Calculate Age and Survival Probability
        water_mains_table = calculate_age_and_survival_probability(water_mains_table)

        # Display results (first 5 rows) as requested
        print("\n" + "=" * 70)
        print("RESULTS - First 5 rows with Age and Survival_Probability:")
        print("=" * 70)

        # Print each row as a dictionary
        for i in range(min(5, len(water_mains_table))):
            row = water_mains_table.iloc[i]
            print(f"\nRow {i}:")
            for col in ['MainType', 'Diameter', 'InstallDate', 'Material', 'Age', 'Survival_Probability']:
                value = row[col]
                # Format the InstallDate for better display
                if col == 'InstallDate' and not pd.isna(value):
                    value = value.strftime('%m/%d/%Y')
                print(f"  {col}: {value}")

        # Also show in tabular format
        print("\n\nTabular view (first 5 rows):")
        print(water_mains_table[['MainType', 'Diameter', 'Material', 'Age', 'Survival_Probability']].head().to_string())

    except FileNotFoundError:
        print("ERROR: File not found at /Users/jasonklein/Downloads/Water_Mains.csv")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("Please check your data format and try again.")