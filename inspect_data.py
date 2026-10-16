import pandas as pd

file_path = "data/train.csv"

df = pd.read_csv(file_path, nrows=100)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())