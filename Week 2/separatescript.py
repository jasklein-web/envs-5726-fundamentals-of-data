import sys
sys.path.insert(1, r'C:\Users\jasklein\PycharmProjects\envs-5726-fundamentals-of-data\Week 2')

import organizations

american_water = organizations.Company(name='American Water', market_cap=28940000000, share_value=148.4)

american_water_shares = american_water.get_number_of_shares()
print(american_water_shares)

partnership_of_delaware_estuary = organizations.NonProfit(name='Partnership of the Delaware Estuary', assets=3140000, designation='501c3')

print(partnership_of_delaware_estuary.name)
print(partnership_of_delaware_estuary.assets)
print(partnership_of_delaware_estuary.designation)