import json
import os
import datetime as datetime
import requests

class Extract:
    """ Classe responsável por extrair dados da API pública de cotações de ações
    e salvar na camada bronze do data-lake. """

    def __init__(self, ticker: str, output_dir: str = "data-lake/bronze") -> None:
        self.ticker = ticker.upper()
        self.url = f"https://brapi.dev/api/quote/{self.ticker}"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True) # Cria a pasta de saída se não existir

    def executar(self) -> str:
        response = requests.get(self.url)
        response.raise_for_status()  # Levanta uma exceção se a requisição falhar

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # Formato de timestamp para o nome do arquivo para evitar sobrescrição
        caminho_arquivo = os.path.join(self.output_dir, f"{self.ticker.lower()}_{timestamp}.json")

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=4, ensure_ascii=False)

        print(f"[BRONZE] Dados extraídos e salvos em: {caminho_arquivo}")
        return caminho_arquivo