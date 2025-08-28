class Company:
    def __init__(self, name, market_cap, share_value):
        self.name = name
        self.market_cap = market_cap
        self.share_value = share_value

    def get_number_of_shares(self):
        return self.market_cap / self.share_value

class NonProfit:
    def __init__(self, name, assets, designation):
        self.name = name
        self.assets = assets
        self.designation = designation

    def get_number_of_shares(self):
        return self.market_cap / self.share_value