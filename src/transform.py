import json
import os
import pandas as pd

class Transform:
    """ Classe responsável por pegar os dados brutos da camada bronze, filtrar apenas os dados relevnates
    e salvar no formato parquet na camada silver do data-lake. """

    def __init__(self, output_dir: str = "data-lake/silver") -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True) # Cria a pasta de saída se não existir

    def executar(self, camiho_json_bronze: str) -> str:
        print(f"[SILVER] Iniciando transformação dos dados do arquivo: {camiho_json_bronze}")

        with open(camiho_json_bronze, "r", encoding="utf-8") as f:
            dados_raw = json.load(f)

        resultados = dados_raw.get("results", [])
        dados_acao = resultados[0] if resultados else {}

        # Renomeando o nome das colunas e colocando no padrão snake_case
        dado_limpo = {
            "ativo" : dados_acao.get("symbol"),
            "nome_empresa" : dados_acao.get("shortName"),
            "preco_atual" : float(dados_acao.get("regularMarketPrice", 0.0)),
            "variacao_pct" : float(dados_acao.get("regularMarketChangePercent", 0.0)),
            "maxima_dia" : float(dados_acao.get("regularMarketDayHigh", 0.0)),
            "minima_dia" : float(dados_acao.get("regularMarketDayLow", 0.0)),
            "preco_fechamento_anterior" : float(dados_acao.get("regularMarketPreviousClose", 0.0)),
            "volume_negociado" : int(dados_acao.get("regularMarketVolume", 0)),
            "data_hora_coleta" : pd.Timestamp.now()
        }

        df = pd.DataFrame([dado_limpo]) # Converte em DataFrame do Pandas

        # Tratamentos com Pandas

        # Tratamento de valores nulos
        # Se algum preço for nulo, substitui por 0.0 para evitar problemas em análises futuras
        colunas_numericas = [
            "preco_atual",
            "variacao_pct",
            "maxima_dia",
            "minima_dia",
            "preco_fechamento_anterior",
            "volume_negociado"
        ]
        df[colunas_numericas] = df[colunas_numericas].fillna(0.0).astype(float)

        # Padronização de Timestamp
        df["data_hora_coleta"] = pd.to_datetime(df["data_hora_coleta"])

        # Remoção de dados duplicados, caso existam
        df = df.drop_duplicates(subset=["ativo", "data_hora_coleta"])

        # FIm dos tratamentos com Pandas


        ticker = str(dados_acao.get("symbol")).lower()
        caminho_arquivo_parquet = os.path.join(self.output_dir, f"{ticker}_tratado.parquet")

        df.to_parquet(caminho_arquivo_parquet, index=False) # Salva o DataFrame no formato parquet

        print(f"[SILVER] Transformação concluída e dados salvos em: {caminho_arquivo_parquet}")
        return caminho_arquivo_parquet