from src.extract import Extract
from src.transform import Transform
from src.load import Load

def rodar_pipeline(ticker: str) -> None:
    """ Pipeline de ETL para extrair, transformar e carregar dados de cotações de ações. """

    print(f"[PIPELINE] Iniciando pipeline para o ticker: {ticker}")

    # Etapa 1: Extração
    extractor = Extract(ticker=ticker)
    arquivo_bronze = extractor.executar()

    # Etapa 2: Transformação    
    transformer = Transform()
    arquivo_silver = transformer.executar(arquivo_bronze)

    # Etapa 3: Carga
    loader = Load()
    loader.executar(caminho_parquet=arquivo_silver)

    print(f"[PIPELINE] Pipeline concluído para o ticker: {ticker}")

if __name__ == "__main__":
    ativos = ["PETR4", "VALE3", "ITUB4"]  # Lista de ativos para processar

    for ativo in ativos:
        rodar_pipeline(ativo)