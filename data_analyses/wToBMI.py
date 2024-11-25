import pandas as pd

# Caminho dos arquivos CSV
events_file = "data/yourEvents.csv"
sports_file = "data/yourSports.csv"

# Carregar os arquivos CSV em DataFrames
try:
    events_df = pd.read_csv(events_file)
    sports_df = pd.read_csv(sports_file)
except FileNotFoundError as e:
    print(f"Erro ao carregar os arquivos: {e}")
    exit()

# Verificar se as colunas necessárias existem
required_columns = ["Weight", "Height"]
if not all(col in events_df.columns for col in required_columns):
    print("Erro: Os arquivos não contêm as colunas necessárias ('Weight' e 'Height').")
    exit()

# Aplicar a fórmula na coluna Weight
def calculate_bmi(row):
    height = row["Height"]
    weight = row["Weight"]
    # Verificar se os valores são válidos
    if height > 0 and weight > 0:
        return weight / (height * height)
    return None  # Retorna None para valores inválidos

# Aplicar a fórmula linha a linha
events_df["Weight"] = events_df.apply(calculate_bmi, axis=1)

# Salvar os resultados em um novo arquivo CSV
output_file = "data/yourEvents_updated.csv"
events_df.to_csv(output_file, index=False)
print(f"Arquivo atualizado salvo como '{output_file}'.")

# Informar se houve algum problema com valores inválidos
invalid_entries = events_df["Weight"].isna().sum()
if invalid_entries > 0:
    print(f"Atenção: {invalid_entries} entradas tinham valores inválidos (Weight ou Height <= 0).")
