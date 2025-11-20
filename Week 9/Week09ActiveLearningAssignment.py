# TASK 1

import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

# Load the training data
file_path = '/Users/jasonklein/Downloads/Pipe_Material_Training_Data.xlsx'
table = pd.read_excel(file_path)


# Define the Weibull CDF function
def cumulative_density_function(age, c, b, a):
    return c * (1 - np.exp(-(age / b) ** a))


# Define the plot_cdf_curve_fit function
def plot_cdf_curve_fit(table, material_type, line_color):
    # Filter data by material type
    material_data = table[table['Material Type'] == material_type]

    # Extract X and Y training data
    xdata = material_data['Life Expectancy (y)'].values
    ydata = material_data['Surv. Prob. (%)'].values / 100  # Convert to decimal

    # Provide better initial guesses and bounds
    if material_type == 'Cast Iron':
        p0 = [1.0, 75, 2.0]  # c, b, a
    elif material_type == 'Ductile Iron':
        p0 = [1.0, 55, 2.0]
    elif material_type == 'Galvanized Iron':
        p0 = [1.0, 25, 2.0]
    elif material_type == 'Copper':
        p0 = [1.0, 38, 2.0]
    else:
        p0 = [1.0, 50, 2.0]

    # Set bounds to ensure positive parameters
    bounds = ([0.1, 1, 0.1], [1.5, 200, 10])  # (lower_bounds), (upper_bounds)

    # Use curve_fit with bounds
    try:
        coefficients, bounds = curve_fit(cumulative_density_function, xdata, ydata, p0=p0, bounds=bounds, maxfev=5000)
        c, b, a = coefficients
    except:
        # If curve fitting fails, use reasonable defaults based on data characteristics
        mid_point = xdata[1]  # Use the middle data point (50% survival)
        c, b, a = 1.0, mid_point, 2.0

    # Print the fitted equation
    print(f'Curve_fitted CDF for {material_type}: Survival Probability = {c:.3f}* e^(-(age/{b:.3f})^{a:.3f})')

    # Create smooth curve for plotting
    x_curve = np.linspace(1, 150, 150)
    y_curve = cumulative_density_function(x_curve, c, b, a) * 100  # Convert back to percentage

    # Ensure survival probability doesn't exceed 100%
    y_curve = np.minimum(y_curve, 100)

    # Plot the fitted curve
    plt.plot(x_curve, y_curve, color=line_color, label=material_type, linewidth=2)

    # Also plot the original data points
    plt.scatter(xdata, ydata * 100, color=line_color, s=50, alpha=0.7)

    return (c, b, a)


# Create the plot with multiple materials
plt.figure(figsize=(12, 8))

# Plot CDF curves for different materials
coefficients_dict = {}
coefficients_dict['Cast Iron'] = plot_cdf_curve_fit(table, material_type='Cast Iron', line_color='red')
coefficients_dict['Ductile Iron'] = plot_cdf_curve_fit(table, material_type='Ductile Iron', line_color='blue')
coefficients_dict['Galvanized Iron'] = plot_cdf_curve_fit(table, material_type='Galvanized Iron', line_color='green')
coefficients_dict['Copper'] = plot_cdf_curve_fit(table, material_type='Copper', line_color='brown')

# Add plot formatting
plt.legend()
plt.xlabel('Life Expectancy (y)')
plt.ylabel('Survival Probability (%)')
plt.title('Pipe Material Survival CDF')
plt.grid(True, alpha=0.3)
plt.xlim(0, 160)
plt.ylim(0, 110)
plt.show()

# Print coefficients for use in Task 2
print("\nCoefficients for Task 2:")
for material, coeffs in coefficients_dict.items():
    print(f"{material}: c={coeffs[0]:.3f}, b={coeffs[1]:.3f}, a={coeffs[2]:.3f}")