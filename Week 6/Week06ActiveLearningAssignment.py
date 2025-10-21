import pandas as pd
import statsmodels.api as sm

hazards_path = "/Users/jasonklein/Downloads/EJSCREEN_BlockGroup_Hazards.csv"
social_vul_path = "/Users/jasonklein/Downloads/EJScreen_BlockGroup_SocialVulnerability.csv"
output_path = "/Users/jasonklein/Downloads/Joined_EJSCREEN_BlockGroup.csv"

hazards = pd.read_csv(hazards_path)
social_vul = pd.read_csv(social_vul_path)

joined = pd.merge(
    hazards,
    social_vul,
    how="outer",
    left_on="ID_HAZ",
    right_on="ID_SOCVUL"
)

joined.to_csv(output_path, index=False)

print(f"Full outer join completed. File saved as:\n{output_path}")

joined_path = "/Users/jasonklein/Downloads/Joined_EJSCREEN_BlockGroup.csv"
joined = pd.read_csv(joined_path)

total_rows = len(joined)
valid_socvul = joined['ID_SOCVUL'].notna().sum()
valid_haz = joined['ID_HAZ'].notna().sum()

print(f"There are {valid_socvul} valid ID_SOCVUL out of {total_rows} total joined rows")
print(f"There are {valid_haz} valid ID_HAZ out of {total_rows} total joined rows")

socvul_ids = set(joined['ID_SOCVUL'].dropna())
haz_ids = set(joined['ID_HAZ'].dropna())

inner_join_ids = socvul_ids.intersection(haz_ids)
inner_join_count = len(inner_join_ids)

total_rows = len(joined)

print(f"There are {inner_join_count} inner joined rows of {total_rows} total Block Groups")

joined = joined.fillna(0)

inner_join = joined[(joined['ID_HAZ'] != 0) & (joined['ID_SOCVUL'] != 0)]

inner_join_path = "/Users/jasonklein/Downloads/InnerJoin_EJSCREEN_BlockGroup.csv"
inner_join.to_csv(inner_join_path, index=False)

print(f"Inner join table created and saved to:\n{inner_join_path}")
print(f"Rows in inner join table: {len(inner_join)}")

df = pd.read_csv(inner_join_path)

df = df.fillna(0)

y = df['PEOPCOLORPCT']
X = df[['D2_DSLPM', 'D2_PNPL', 'D2_PTRAF', 'D2_LDPNT', 'D2_DWATER']]

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()

print(model.summary())