import pandas as pd

df = pd.read_csv('../data/online_retail_clean.csv', encoding='latin1', nrows=5)

print("="*60)
print("CSV FAYL TUZILISHI")
print("="*60)
print("\nUstunlar:")
print(df.columns.tolist())
print("\nBirinchi 5 qator:")
print(df.head())
print("\nUstunlar soni:", len(df.columns))