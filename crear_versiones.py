import pandas as pd
df = pd.read_csv('data/attrition.csv')
df.iloc[:900].to_csv('data/attrition_v1.csv', index=False)
df.to_csv('data/attrition_v2.csv', index=False)
print(f'v1: {len(df.iloc[:900])} filas')
print(f'v2: {len(df)} filas')
