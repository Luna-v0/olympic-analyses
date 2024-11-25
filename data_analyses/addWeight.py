import pandas as pd

# Caminho dos arquivos CSV
events_file = "data/by_event.csv"
sports_file = "data/by_sport.csv"

# Função para processar um arquivo
def process_file(file_path):
    try:
        # Carregar o arquivo CSV em um DataFrame
        df = pd.read_csv(file_path)
    except FileNotFoundError as e:
        print(f"Erro ao carregar o arquivo {file_path}: {e}")
        return None

    # Verificar se as colunas necessárias existem
    required_columns = ["Height", "BMI"]
    if not all(col in df.columns for col in required_columns):
        print(f"Erro: O arquivo {file_path} não contém as colunas necessárias ('Height' e 'BMI').")
        return None

    # Calcular a nova coluna Weight
    def calculate_weight(row):
        height = row["Height"]
        bmi = row["BMI"]
        # Verificar se os valores são válidos
        if height > 0 and bmi > 0:
            return bmi * height/100 * height/100
        return None  # Retorna None para valores inválidos

    # Aplicar a fórmula para criar a coluna Weight
    df["Weight"] = df.apply(calculate_weight, axis=1)

    # Reorganizar as colunas para que 'Weight' fique entre 'Height' e 'BMI'
    columns = list(df.columns)
    height_index = columns.index("Height")
    columns.insert(height_index + 1, columns.pop(columns.index("Weight")))  # Move 'Weight'
    df = df[columns]

    # Salvar o DataFrame atualizado em um novo arquivo
    output_file = file_path.replace(".csv", "_updated.csv")
    df.to_csv(output_file, index=False)
    print(f"Arquivo atualizado salvo como '{output_file}'.")

    # Informar se houve algum problema com valores inválidos
    invalid_entries = df["Weight"].isna().sum()
    if invalid_entries > 0:
        print(f"Atenção: {invalid_entries} entradas tinham valores inválidos (Height ou BMI <= 0).")

    return df

# Processar os dois arquivos
process_file(events_file)
process_file(sports_file)
