import pandas as pd

# Load just the first row to see headers
try:
    # Try comma first
    df = pd.read_csv('datos_madrid_2024_2026.csv', nrows=0)
except:
    # Try semicolon if comma fails
    df = pd.read_csv('datos_madrid_2024_2026.csv', sep=';', nrows=0)

print("Las columnas reales de tu CSV son:")
print(df.columns.tolist())