"""
Desenvolvedor: VICTOR DUARTE VENANCIO
Última atualização: 25/06/2024

Este script tem como finalidade acessar o site do Banco Central e extrair, via API, a as Taxas de Juros de Pessoa Jurídica para Capital de giro com prazo até 365 dias
A automação lê a base de dados "CNPJS.csv", localizada na pasta "input", buscando CNPJs a serem procurados, extrai com a tabela fornecida pelo Bacen, e popula
o arquivo "Tabela Taxa Juros até 365.csv" com as Taxas de Juros dos respctivos CNPJS buscados, salvado o arquivo na pasta "output".

Após, mantém o arquivo "Tabela Taxa Juros até 365.csv" na pasta "output" (podendo ser consumido em outro processo se necessário), e copia o arquivo para pasta
do respectivo dia na pasta "historico". A automação excuta o mesmo processo para o arquivo "CNPJS.csv" adicionando a data atual no nomedo arquivo, porém, mantém 
o arquivo na pasta "input" (podendo ser consumido em outro processo se necessário).
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests

# Definição de variáveis gerais (API Olinda do Banco Central do Brasil)
url_api = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo?$filter=Segmento%20eq%20'PESSOA%20JUR%C3%8DDICA'&$select=Segmento,InstituicaoFinanceira,cnpj8,TaxaJurosAoMes,TaxaJurosAoAno&$top=100&$format=json"
modalidade = "Capital de giro com prazo ate 365 dias - Prefixado"
segmento = "Pessoa Juridica"

data_atual = datetime.now().strftime("%Y_%m_%d")
caminho_script = Path(__file__).resolve().parent
caminho_output = caminho_script / "output"
caminho_input = caminho_script / "input"
caminho_arquivo_input = caminho_input / "CNPJS.csv"
caminho_historico_data_atual = caminho_script / "historico" / data_atual
lista_diretorios = [caminho_output, caminho_historico_data_atual, caminho_input]

# Configuração de Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Validações gerais de ambiente
def validar_ambiente() -> bool:
    logging.info("Inicio - Validar Ambiente")
    try:
        for diretorio in lista_diretorios:
            diretorio.mkdir(parents=True, exist_ok=True)
        logging.info("Fim - Validar Ambiente")
        return True
    except Exception as e:
        raise Exception(f"Falha ao validar ambiente: {e}")


# Validação de base a ser processada
def validar_base():
    logging.info("Inicio - Validar Base")
    global df_base, cnpjs, cnpjs_validos

    try:
        if not caminho_arquivo_input.exists():
            logging.error(f"Arquivo de entrada não encontrado em: {caminho_arquivo_input}")
            return False

        df_base = pd.read_csv(caminho_arquivo_input, dtype=str, delimiter=";")
        df_base["STATUS"] = ""
        df_base["DATA HORA PROCESSAMENTO"] = ""

        cnpjs = df_base["CNPJ"].fillna("").tolist()
        cnpjs_validos = [c.strip() for c in cnpjs if c.strip() != ""]

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        mask_invalido = df_base["CNPJ"].fillna("").str.strip() == ""
        df_base.loc[mask_invalido, "STATUS"] = "Invalido"
        df_base.loc[mask_invalido, "DATA HORA PROCESSAMENTO"] = data_hora

        if not cnpjs_validos:
            logging.info("Não existem CNPJs válidos para processamento.")
            return False

        logging.info(f"{len(cnpjs_validos)} CNPJs válidos para processamento.")
        logging.info("Fim - Validar Base")
        return True

    except Exception as e:
        raise Exception(f"Falha ao validar base: {e}")


def obter_tabela_taxa_juros():
    logging.info("Inicio - Obter Tabela de Juros (API Bacen)")
    global df_tabela_taxa_juros

    headers = {
        "Accept": "application/json"
    }

    try:
        for tentativa in range(1, 4):
            logging.info(f"Tentativa {tentativa}")

            resp = requests.get(url_api, headers=headers, timeout=60)
            data = resp.json()

            registros = data.get("value", [])
            df_tabela_taxa_juros = pd.DataFrame(registros)

            if df_tabela_taxa_juros.empty:
                logging.warning("Resposta vazia da API")
                continue

            logging.info(f"Sucesso: {len(df_tabela_taxa_juros)} linhas")
            return True

        return False

    except Exception as e:
        raise Exception(f"Falha ao obter Tabela Taxa Juros: {e}")

#Tratamento de resultados e salvamento de arquivos
def tratar_resultados():
    logging.info("Inicio - Tratar resultados")
    global df_tabela_taxa_juros

    data_hora_nome = datetime.now().strftime("%Y_%m_%d_%H_%M")
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
        df_tabela_taxa_juros = df_tabela_taxa_juros.rename(columns={"InstituicaoFinanceira": "Instituição Financeira", "cnpj8": "CNPJ", "TaxaJurosAoMes": "Taxa Juros ao Mes", "TaxaJurosAoAno": "Taxa Juros ao Ano"})
        df_tabela_taxa_juros = df_tabela_taxa_juros[["CNPJ","Instituição Financeira","Taxa Juros ao Mes","Taxa Juros ao Ano"]]

        #Limpeza de strings para do cruzamento de dados
        df_tabela_taxa_juros["CNPJ"] = df_tabela_taxa_juros["CNPJ"].astype(str).str.strip()

        #Seleção dos CNPJS informados na base
        df_tabela_taxa_juros = df_tabela_taxa_juros[df_tabela_taxa_juros["CNPJ"].isin(cnpjs_validos)].reset_index(drop=True)

        #Salvamento do arquivo de Taxas de Juros
        arquivo_saida = "Tabela Taxa Juros até 365.csv"
        logging.info("Salvando dados de Taxas de Juros em arquivo.")
        df_tabela_taxa_juros.to_csv(caminho_output / arquivo_saida, sep=";", index=False)
        df_tabela_taxa_juros.to_csv(caminho_historico_data_atual / arquivo_saida, sep=";", index=False)

        #Atualização do STATUS na base original
        logging.info("Atualizando arquivo de Base.")
        cnpjs_encontrados = set(df_tabela_taxa_juros["CNPJ"].tolist())
        for cnpj in cnpjs_validos:
            df_base.loc[df_base["CNPJ"] == cnpj, "DATA HORA PROCESSAMENTO"] = data_hora
            df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = (
                "Processado" if cnpj in cnpjs_encontrados else "Não encontrado"
            )

        #Salvamento da base atualizada
        logging.info("Salvando arquivo de Base.")
        df_base.to_csv(caminho_arquivo_input, sep=";", index=False)
        novo_nome = caminho_input / f"CNPJS_{data_hora_nome}.csv"
        os.rename(caminho_arquivo_input, caminho_input / f"CNPJS_{data_hora_nome}.csv")
        shutil.copy(novo_nome, caminho_historico_data_atual)

        logging.info("Fim - Tratar resultados")

    except Exception as e:
        raise Exception(f"Falha ao tratar resultados: {e}")


#Execução da automação
if __name__ == "__main__":
    if validar_ambiente() and validar_base():
        if obter_tabela_taxa_juros():
            tratar_resultados()
