class Company:
    def __init__(self, name, market_cap, share_value):
        self.name = name
        self.market_cap = market_cap
        self.share_value = share_value

    def get_number_of_shares(self):
        return self.market_cap / self.share_value

american_water_company = Company(name='American Water', market_cap=28940000000, share_value=148.4)

print(american_water_company.name)
print(american_water_company.market_cap)

fmc_company = Company(name='FMC', market_cap=4730000000, share_value=123.45)
wawa_company = Company(name='Wawa', market_cap=14900000000, share_value=160.2)

print(fmc_company.name)
print(fmc_company.market_cap)
print(wawa_company.name)
print(wawa_company.market_cap)

def get_number_of_shares(market_cap, share_value):
    return market_cap / share_value

american_water_shares = american_water_company.get_number_of_shares()
print(american_water_shares)

class MyClass:
    def __init__(self, number):
        self.number = number
    def round_number(self):
        return round(self.number)
    def add_to_rounded_number(self, number_to_add):
        return self.round_number()+number_to_add

my_instance = MyClass(number = 5.2)
my_sum = my_instance.add_to_rounded_number(number_to_add = 3)
print(my_sum)