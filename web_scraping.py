"""
Desenvolvedor: VICTOR DUARTE VENANCIO
Última atualização: 25/06/2024

Este script tem como finalidade acessar o site do Banco Central e extrair a as Taxas de Juros de Pessoa Jurídica para Capital de giro com prazo até 365 dias
A automação lê a base de dados "CNPJS.csv", localizada na pasta "input", buscando CNPJs a serem procurados, extrai com a tabela fornecida  pelo Bacen, e popula
o arquivo "Tabela Taxa Juros até 365.csv" com as Taxas de Juros dos respctivos CNPJS buscados, salvado o arquivo na pasta "output".

Após, mantém o arquivo "Tabela Taxa Juros até 365.csv" na pasta "output" (podendo ser consumido em outro processo se necessário), e copia o arquivo para pasta
do respectivo dia na pasta "historico". A automação excuta o mesmo processo para o arquivo "CNPJS.csv" adicionando a data atual no nomedo arquivo, porém, mantém 
o arquivo na pasta "input" (podendo ser consumido em outro processo se necessário).

As pastas "uteis" e "telas" contém módulos necessários para o funcionamento da automação.
"""

# Importação de bibliotecas
import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil
import logging

# Importação de módulos
from telas.tela_bacen import TelaBacen
from uteis.uteis import Uteis

# Definição de variáveis gerais
__driver = ""

data_atual = datetime.now().strftime("%Y_%m_%d")

caminho_script = Path(__file__).resolve().parent

caminho_output = caminho_script / "output"
caminho_input = caminho_script / "input"
caminho_arquivo_input = caminho_input / "CNPJS.csv"
caminho_historico_data_atual = caminho_script / "historico" / data_atual

subprocessos_fechar = ["excel.exe"]

lista_diretorios = [
    caminho_output,
    caminho_historico_data_atual,
    caminho_input
]

# Configuração de Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Validações gerais de ambiente
def validar_ambiente():
    logging.info("Inicio - Validar Ambiente")
    global tela_bacen, uteis

    try:
        tela_bacen = TelaBacen(__driver)
        uteis = Uteis()

        for subprocesso in subprocessos_fechar:
            uteis.fechar_subprocesso(subprocesso)

        for diretorio in lista_diretorios:
            diretorio.mkdir(parents=True, exist_ok=True)

        logging.info("Fim - Validar Ambiente")
        return True

    except Exception as e:
        raise Exception(f"Falha ao validar ambiente: {e}")


# Validação de base a ser processada
def validar_base():
    logging.info("Inicio - Validar Base")
    global cnpjs_validos, cnpjs, df_base

    try:
        df_base = pd.read_csv(caminho_arquivo_input, dtype=str, delimiter=";")
        df_base["STATUS"] = ""
        df_base["DATA HORA PROCESSAMENTO"] = ""

        cnpjs = df_base["CNPJ"].tolist()
        cnpjs_validos = []

        for cnpj in cnpjs:
            if cnpj and cnpj.strip() != "":
                cnpjs_validos.append(cnpj)
            else:
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Invalido"
                df_base.loc[df_base["CNPJ"] == cnpj, "DATA HORA PROCESSAMENTO"] = data_hora

        if not cnpjs_validos:
            logging.info("Não existem campos de CNPJ válidos para processamento.")
            return False

        logging.info("Fim - Validar Base")
        return True

    except Exception as e:
        raise Exception(f"Falha ao validar base: {e}")


def acessar_sistema():
    logging.info("Inicio - Acessar Sistema")
    global __driver

    try:
        for tentativa in range(1, 4):
            try:
                __driver = tela_bacen.abrir_navegador_chrome()
                tela_bacen.acessar_url()
                logging.info("Fim - Acessar Sistema")
                return True

            except Exception as e:
                if tentativa == 3:
                    raise Exception(f"Falha ao abrir sistema: {e}")

                tela_bacen.acessar_url()

        return False

    except Exception as e:
        raise Exception(f"Falha ao acessar sistema: {e}")


def obter_tabela_taxa_juros():
    logging.info("Inicio - Obter Tabela de Juros")
    global df_tabela_taxa_juros

    try:
        for tentativa in range(1, 4):
            try:
                tela_bacen.clicar_fechar_cookies()
                tela_bacen.clicar_mais_series()
                tela_bacen.aguardar_carregmento_grafico()
                tela_bacen.clicar_taxa_de_juros()
                tela_bacen.clicar_capital_giro_ate_365()

                df_tabela_taxa_juros = tela_bacen.obter_tabela_capital_giro()

                if df_tabela_taxa_juros.empty:
                    continue

                logging.info(f"Tabela obtida com {len(df_tabela_taxa_juros)} linhas.")
                return True

            except Exception:
                if tentativa == 3:
                    raise Exception("Falha ao obter Tabela Taxa Juros.")

                tela_bacen.acessar_url()

        return False

    except Exception as e:
        raise Exception(f"Falha ao obter Tabela Taxa Juros: {e}")


def tratar_resultados():
    logging.info("Inicio - Tratar resultados")
    global df_tabela_taxa_juros

    data_hora_nome = datetime.now().strftime("%Y_%m_%d_%H_%M")
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
        df_tabela_taxa_juros.columns = df_tabela_taxa_juros.columns.get_level_values(1)
        df_tabela_taxa_juros = df_tabela_taxa_juros.drop(columns=["Posição"])

        df_tabela_taxa_juros = df_tabela_taxa_juros.rename(columns={
            "% a.m.": "Taxa Juros ao Mes",
            "% a.a.": "Taxa Juros ao Ano"
        })

        linhas_deletar = [
            i for i, row in df_tabela_taxa_juros.iterrows()
            if row["CNPJ"] not in cnpjs_validos
        ]

        df_tabela_taxa_juros = df_tabela_taxa_juros.drop(index=linhas_deletar)

        arquivo_saida = "Tabela Taxa Juros até 365.csv"

        df_tabela_taxa_juros.to_csv(caminho_output / arquivo_saida, sep=";", index=False)
        df_tabela_taxa_juros.to_csv(caminho_historico_data_atual / arquivo_saida, sep=";", index=False)

        for cnpj in cnpjs:
            if cnpj in cnpjs_validos:
                df_base.loc[df_base["CNPJ"] == cnpj, "DATA HORA PROCESSAMENTO"] = data_hora

                if cnpj in df_tabela_taxa_juros["CNPJ"].values:
                    df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Processado"
                else:
                    df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Não encontrado"

        df_base.to_csv(caminho_arquivo_input, sep=";", index=False)

        novo_nome = caminho_input / f"CNPJS_{data_hora_nome}.csv"

        caminho_arquivo_input.rename(novo_nome)
        shutil.copy(novo_nome, caminho_historico_data_atual)

        logging.info("Fim - Tratar resultados")

    except Exception as e:
        raise Exception(f"Falha ao tratar resultados: {e}")


# Execução da automação
if __name__ == "__main__":
    if validar_ambiente() and validar_base():
        acessar_sistema()

        if obter_tabela_taxa_juros():
            __driver.quit()
            tratar_resultados()
