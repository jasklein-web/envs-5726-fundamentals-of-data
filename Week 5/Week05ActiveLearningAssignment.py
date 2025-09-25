from pathlib import Path
import json
import csv

json_path = Path(r'/Users/jasonklein/Downloads/Trase_CIV_Cocoa_SupplyChain_Data.json')

with open(json_path) as f:
    data = json.load(f)

records = data['cote_divoire_cocoa_v1_1_1']['data']

data_headers = ['trader_group', 'country_of_destination', 'cocoa_deforestation_15_years_total_exposure',
                'cocoa_net_emissions_15_years_total']
data_table = []

summary_by_trader = {}
summary_by_country = {}

for record in records:
    supply_chain = record['supply_chain_data']
    cocoa_data = record['cocoa_data']

    trader_group = supply_chain['trader_group']
    country_of_destination = supply_chain['country_of_destination']
    cocoa_deforestation_15_years_total_exposure = cocoa_data['cocoa_deforestation_15_years_total_exposure']
    cocoa_net_emissions_15_years_total = cocoa_data['cocoa_net_emissions_15_years_total']

    data_table.append([trader_group, country_of_destination, cocoa_deforestation_15_years_total_exposure,
                       cocoa_net_emissions_15_years_total])

    if trader_group not in summary_by_trader:
        summary_by_trader[trader_group] = {
            'cocoa_deforestation_list': [],
            'cocoa_net_emissions_list': []
        }
    summary_by_trader[trader_group]['cocoa_deforestation_list'].append(
        float(cocoa_deforestation_15_years_total_exposure))
    summary_by_trader[trader_group]['cocoa_net_emissions_list'].append(
        float(cocoa_net_emissions_15_years_total))

    if country_of_destination not in summary_by_country:
        summary_by_country[country_of_destination] = {
            'cocoa_deforestation_list': [],
            'cocoa_net_emissions_list': []
        }
    summary_by_country[country_of_destination]['cocoa_deforestation_list'].append(
        float(cocoa_deforestation_15_years_total_exposure))
    summary_by_country[country_of_destination]['cocoa_net_emissions_list'].append(
        float(cocoa_net_emissions_15_years_total))

print(data_headers)
for row in data_table:
    print(row)

output_path = Path(r'/Users/jasonklein/Downloads/Trase_CIV_Cocoa_SupplyChain_Data.csv')
with open(output_path, "w", newline="" , encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows([data_headers]+data_table)

summary_trader_path = Path(r'/Users/jasonklein/Downloads/summary_by_trader.json')
with open(summary_trader_path, "w", encoding="utf-8") as f:
    json.dump(summary_by_trader, f, indent=4)

summary_country_path = Path(r'/Users/jasonklein/Downloads/summary_by_country.json')
with open(summary_country_path, "w", encoding="utf-8") as f:
    json.dump(summary_by_country, f, indent=4)

"""
trader_sums = []
for trader, values in summary_by_trader.items():
    total_deforestation = sum(values['cocoa_deforestation_list'])
    trader_sums.append((trader, total_deforestation))

max_sum = max(total for _, total in trader_sums)

filtered_trader_sums = [
    (trader, total) for trader, total in trader_sums if total > 0.1 * max_sum
]

filtered_trader_path = Path(r'/Users/jasonklein/Downloads/summary_trader_filtered.csv')
with open(filtered_trader_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["trader_group", "cocoa_deforestation_sum"])
    writer.writerows(filtered_trader_sums)
"""

def summarize_and_filter(summary_dict, key, threshold=0.1):
    sums = []
    for name, values in summary_dict.items():
        total = sum(values[key])
        sums.append((name, total))
    max_sum = max(total for _, total in sums)
    return [(name, total) for name, total in sums if total > threshold * max_sum]

trader_deforestation = summarize_and_filter(summary_by_trader, 'cocoa_deforestation_list')
trader_emissions = summarize_and_filter(summary_by_trader, 'cocoa_net_emissions_list')
country_deforestation = summarize_and_filter(summary_by_country, 'cocoa_deforestation_list')
country_emissions = summarize_and_filter(summary_by_country, 'cocoa_net_emissions_list')

def save_summary(data, headers, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

save_summary(trader_deforestation, ["trader_group", "cocoa_deforestation_sum"], Path(r'/Users/jasonklein/Downloads/summary_trader_deforestation.csv'))
save_summary(trader_emissions, ["trader_group", "cocoa_net_emissions_sum"], Path(r'/Users/jasonklein/Downloads/summary_trader_emissions.csv'))
save_summary(country_deforestation, ["country_of_destination", "cocoa_deforestation_sum"], Path(r'/Users/jasonklein/Downloads/summary_country_deforestation.csv'))
save_summary(country_emissions, ["country_of_destination", "cocoa_net_emissions_sum"], Path(r'/Users/jasonklein/Downloads/summary_country_emissions.csv'))