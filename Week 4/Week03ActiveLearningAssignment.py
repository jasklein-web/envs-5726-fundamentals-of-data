from pathlib import Path
import csv
import statistics

# TASK 1
print('Task 1')

edgar_path = Path(r'/Users/jasonklein/Documents/SEC_EDGAR_10K')

headers = ["Company Name", "Year", "Count Sustainability", "Count AI"]
edgar_table_rows = []

for file_path in edgar_path.glob('*'):
    if file_path.is_file():
        file_stem = file_path.stem

        if 'msft' in file_stem:
            file_stem = file_stem.replace('10k_', '')

        company_name = ('Amazon' if 'amzn' in file_stem else
                        'Google' if 'goog' in file_stem else
                        'Microsoft' if 'msft' in file_stem else
                        'Nvidia' if 'nvda' in file_stem else
                        'Unknown')

        parts = file_stem.split('-')
        if parts[1][:4].isdigit():
            year = int(parts[1][:4])
        else:
            year = None

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            file_content_upper = f.read().upper()

        count_sustainability = file_content_upper.count('SUSTAINABILITY')
        count_ai = file_content_upper.count('ARTIFICIAL INTELLIGENCE')

        edgar_table_rows.append([company_name, year, count_sustainability, count_ai])

company_order = ["Amazon", "Google", "Microsoft", "Nvidia"]
edgar_table_rows.sort(key=lambda row: (company_order.index(row[0]), row[1]))

final_table = [headers] + edgar_table_rows[:10]
for row in final_table:
    print(row)

#TASK 2
print('Task 2')

def get_average_by_company(headers, table, column_name_to_average, company_name):
    column_index = headers.index(column_name_to_average)

    values = [row[column_index] for row in table if row[0].upper() == company_name.upper()]

    if not values:
        return 0
    return statistics.mean(values)

report_headers = headers
report_table = edgar_table_rows

for company_name in ['NVIDIA', 'Microsoft', 'Google', 'Amazon']:
    for column_name_to_average in ['Count Sustainability', 'Count AI']:
        column_average = get_average_by_company(
            headers=report_headers,
            table=report_table,
            column_name_to_average=column_name_to_average,
            company_name=company_name
        )
        print(f"The average {column_name_to_average} for {company_name} is {column_average}")

#TASK 3
print('Task 3')

complete_table = [headers] + edgar_table_rows

company_files = {
    "Amazon": "SEC_10k_Amazon_Metrics.csv",
    "Alphabet": "SEC_10k_Google_Metrics.csv",
    "Microsoft": "SEC_10k_Microsoft_Metrics.csv",
    "Nvidia": "SEC_10k_Nvidia_Metrics.csv"
}

for company_name, file_name in company_files.items():
    company_rows = [row for row in complete_table if row[0] == company_name]
    company_table = [headers] + company_rows

    with open(Path(f'/Users/jasonklein/Downloads/{file_name}'), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(company_table)


