import pandas as pd

df = pd.read_csv("data/raw/messages.csv")

print(df.head())
print()
print("Total messages:", len(df))
print()
print("Categories:")
print(df["category"].value_counts())
print()
print("Risk levels:")
print(df["risk_level"].value_counts())