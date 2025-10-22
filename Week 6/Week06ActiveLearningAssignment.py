import csv

#Task 1
hazards_path = "/Users/jasonklein/Downloads/EJSCREEN_BlockGroup_Hazards.csv"
social_vul_path = "/Users/jasonklein/Downloads/EJScreen_BlockGroup_SocialVulnerability.csv"

with open(social_vul_path, 'r') as socvul_file:
    socvul_reader = csv.reader(socvul_file)
    socvul_headers = next(socvul_reader)
    socvul_data = list(socvul_reader)

with open(hazards_path, 'r') as hazards_file:
    hazards_reader = csv.reader(hazards_file)
    hazards_headers = next(hazards_reader)
    hazards_data = list(hazards_reader)

hazards_join_dict = {}
for row in hazards_data:
    unique_id = row[hazards_headers.index('ID_HAZ')]
    hazards_join_dict[unique_id] = row

joined_headers = socvul_headers + hazards_headers

full_outer_joined_table = []
for target_row in socvul_data:
    unique_id = target_row[socvul_headers.index('ID_SOCVUL')]

    if unique_id in hazards_join_dict:
        join_row = hazards_join_dict[unique_id]
        full_outer_joined_table.append(target_row + join_row)
    else:
        join_row = [None] * len(hazards_headers)
        full_outer_joined_table.append(target_row + join_row)

target_id_set = set()
for target_row in socvul_data:
    unique_id = target_row[socvul_headers.index('ID_SOCVUL')]
    target_id_set.add(unique_id)

for id_haz in hazards_join_dict:
    if id_haz not in target_id_set:
        null_target_row = [None] * len(socvul_headers)
        hazard_data_row = hazards_join_dict[id_haz]
        full_outer_joined_table.append(null_target_row + hazard_data_row)

print(f"After Full Outer Join, we have {len(full_outer_joined_table)} total rows.")

output_path = "/Users/jasonklein/Downloads/EJScreen_Full_Outer_Join.csv"
with open(output_path, 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(joined_headers)
    writer.writerows(full_outer_joined_table)

print(f"Task 1 Complete! Full Outer Join saved to: {output_path}")

#Task 2
total_rows = len(full_outer_joined_table)
id_socvul_index = joined_headers.index('ID_SOCVUL')
id_haz_index = joined_headers.index('ID_HAZ')

valid_id_socvul_count = 0
valid_id_haz_count = 0

for row in full_outer_joined_table:
    if row[id_socvul_index] is not None:
        valid_id_socvul_count += 1
    if row[id_haz_index] is not None:
        valid_id_haz_count += 1

print(f"\nTask 2 Metrics:")
print(f"There are {valid_id_socvul_count} valid ID_SOCVUL out of {total_rows} total joined rows")
print(f"There are {valid_id_haz_count} valid ID_HAZ out of {total_rows} total joined rows")

#Task 3
hazards_id_set = set(hazards_join_dict.keys())
inner_join_ids = target_id_set.intersection(hazards_id_set)
number_of_inner_join_rows = len(inner_join_ids)

print(f"\nTask 3 Metrics:")
print(f"There are {number_of_inner_join_rows} inner joined rows of {total_rows} total Block Groups")

#Task 4
inner_join_table = []
for row in full_outer_joined_table:
    if row[id_socvul_index] is not None and row[id_haz_index] is not None:
        inner_join_table.append(row)

print(f"\nTask 4 - Inner Join Filter:")
print(f"Filtered table has {len(inner_join_table)} rows.")

cleaned_inner_join_table = []

regression_columns = ['PEOPCOLORPCT', 'D2_DSLPM', 'D2_PNPL', 'D2_PTRAF', 'D2_LDPNT', 'D2_DWATER']
regression_indexes = [joined_headers.index(col) for col in regression_columns]

for row in inner_join_table:
    cleaned_row = row.copy()

    for col_index in regression_indexes:
        value = row[col_index]

        if value is None or value == '' or value == ' ':
            cleaned_row[col_index] = '0'
        else:
            try:
                float_val = float(value)
                cleaned_row[col_index] = str(float_val)
            except (ValueError, TypeError):
                cleaned_row[col_index] = '0'

    cleaned_inner_join_table.append(cleaned_row)

print("Data cleaning completed for regression columns.")

inner_join_output_path = "/Users/jasonklein/Downloads/EJScreen_Inner_Join.csv"
with open(inner_join_output_path, 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(joined_headers)
    writer.writerows(cleaned_inner_join_table)

print(f"Cleaned Inner Join table saved to: {inner_join_output_path}")
print("Use this file for Multiple Regression in Excel.")

print(f"\nSample validation - first row regression values:")
sample_row = cleaned_inner_join_table[0]
for col in regression_columns:
    idx = joined_headers.index(col)
    print(f"  {col}: {sample_row[idx]}")