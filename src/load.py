import os
import pandas as pd
from sqlalchemy import create_engine

class Load:
    """ Classe responsável por ler os arquivos tratados em parquet da camada silver e
    carregar no banco de dados PostgreSQL. """

    def __init__(self, db_user: str = "admin", db_pass: str = "senha123", db_host: str = "localhost", db_port: str = "5432", db_name: str = "acoes") -> None:
        self.db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}" # Cria a URL de conexão com o banco de dados PostgreSQL rodando via Docker

        self.engine = create_engine(self.db_url) # Cria o engine do SQLAlchemy para se conectar ao banco de dados

    def executar(self, caminho_parquet: str, nome_tabela: str = "fato_cotacoes") -> None:
        if not os.path.exists(caminho_parquet): # Verifica se o arquivo parquet existe antes de tentar carregá-lo
            raise FileNotFoundError(f"O arquivo {caminho_parquet} não foi encontrado.")

        print(f"[LOAD] Iniciando carregamento dos dados do arquivo: {caminho_parquet} para a tabela: {nome_tabela}")

        df = pd.read_parquet(caminho_parquet) # Lê o arquivo parquet em um DataFrame do Pandas

        df.to_sql(name = nome_tabela, con = self.engine, if_exists = "append", index = False) # Carrega os dados do DataFrame para a tabela no banco de dados PostgreSQL    

        print(f"[LOAD] Dados carregados com sucesso na tabela: {nome_tabela} do banco de dados PostgreSQL.")
        
 
