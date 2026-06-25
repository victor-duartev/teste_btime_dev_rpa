#Desenvolvedor: VICTOR DUARTE VENANCIO
#Última atualização: 25/06/2024

#Este script tem como finalidade acessar o site do Banco Central e extrair a as Taxas de Juros de Pessoa Jurídica para Capital de giro com prazo até 365 dias
#A automação lê a base de dados "CNPJS.csv", localizada na pasta "input", buscando CNPJs a serem procurados, extrai com a tabela fornecida  pelo Bacen, e popula
#o arquivo "Tabela Taxa Juros até 365.csv" com as Taxas de Juros dos respctivos CNPJS buscados, salvado o arquivo na pasta "output".

#Após, mantém o arquivo "Tabela Taxa Juros até 365.csv" na pasta "output" (podendo ser consumido em outro processo se necessário), e copia o arquivo para pasta
#do respectivo dia na pasta "historico". A automação excuta o mesmo processo para o arquivo "CNPJS.csv" adicionando a data atual no nomedo arquivo, porém, mantém 
#o arquivo na pasta "input" (podendo ser consumido em outro processo se necessário).

#As pastas "uteis" e "telas" contém módulos necessários para o funcionamento da automação.

#Importação de bibliotecas
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import shutil
import logging

#Importação de módulos
from telas.tela_bacen import TelaBacen
from uteis.uteis import Uteis

#Definição de varáveis gerais
__driver = ""
data_atual = datetime.now().strftime("%Y_%m_%d")
caminho_script = Path(__file__).resolve().parent
caminho_output = os.path.join(caminho_script, "output")
caminho_intput = os.path.join(caminho_script, "input")
caminho_arquivo_input = os.path.join(caminho_intput, "CNPJS.csv")
caminho_historico_data_atual = os.path.join(caminho_script, "historico", data_atual)
subprocessos_fechar = ["excel.exe"] #"chrome.exe" "chromedriver.exe"
lista_diretorios = [caminho_output, caminho_historico_data_atual, caminho_intput]

#Configuração de Logging
logging.basicConfig(filename="app.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

#Validações gerais de ambiente
def validar_ambiente():
    logging.info("Inicio - Validar Ambiente")
    global tela_bacen, uteis

    try:
        #Instanciamento de classes
        tela_bacen = TelaBacen(__driver)
        uteis = Uteis()

        #Fechar subprocessos que serão utilizados pela automação
        for subprocesso in subprocessos_fechar:
            uteis.fechar_subprocesso(subprocesso)

        #Criação de diretórios se necessário
        for diretorio in lista_diretorios:
            uteis.conferir_existencia_diretorio(diretorio)

        logging.info("Fim - Validar Ambiente")
        return True
    
    except Exception as e:
        raise Exception(f"Falha ao validar ambiente: {e}")


#Validação de base a ser processada
def validar_base():
    logging.info("Inicio - Validar Base")
    global cnpjs_validos, cnpjs, df_base

    try:
        #Leitura de base
        df_base = pd.read_csv(caminho_arquivo_input, dtype=str, delimiter=";")
        df_base["STATUS"] = ""
        df_base["DATA HORA PROCESSAMENTO"] = ""

        #Validação de campo de CNPJ
        cnpjs = df_base["CNPJ"].tolist()
        cnpjs_validos = cnpjs
        for cnpj in cnpjs:
            if cnpj.strip() != "":
                continue

            #Caso o campo nao seja válido desconsidera linha para processamento
            else:
                data_hora_processamento = datetime.now().strftime("%d/%m/%Y %H:%M")
                df_base.loc[df_base["CNPJ"] == cnpj, "DATA HORA PROCESSAMENTO"] = data_hora_processamento
                df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Invalido"
                cnpjs_validos.drop(cnpj)
                logging.info("Campo vazio na coluna CNPJ.")

        #Não havendo campos válidos para serem processados o processo se encerra
        if not cnpjs_validos:
            logging.info("Não existem campos de CNPJ válidos para processamento.")
            logging.info("Fim - Validar Base")
            return False

        logging.info("Fim - Validar Base")
    
    except Exception as e:
        raise Exception(f"Falha ao validar base: {e}")
            

def acessar_sistema():
    logging.info("Inicio - Acessar Sistema")
    global __driver

    try:
        #Tenta 3 vezes acessar sistema
        tentativas = 0
        for tentativas in range (1, 4):
            try:
                #Iniciação do driver e navegação até url destinada
                logging.info("Iniciando driver Chrome e navegando até url destinada")
                __driver = tela_bacen.abrir_navegador_chrome()
                tela_bacen.acessar_url()
                break
            
            except:
                if tentativas == 3:
                    raise Exception(f"Falha ao obter Tabela Taxa Juros: {e}")
                
                tela_bacen.acessar_url()
                tentativas += tentativas 
    
        logging.info("Fim - Acessar Sistema")
        return True

    except Exception as e:
        raise Exception(f"Falha ao acessar sistema: {e}")


def obter_tabela_taxa_juros():
    logging.info("Inicio - Obter Tabela de Juros")
    global df_tabela_taxa_juros

    tentativas = 0
    try:
        for tentativas in range(1, 4):
            logging.info(f"Tentativa {tentativas} de obter tabela de Taxa de Juros.")
            try:
                #Navegação até tabela de taxa de juros
                logging.info("Clicar no botao 'Rejeitar Cookies'.")
                tela_bacen.clicar_fechar_cookies()
                logging.info("Clicar no opcao 'Mais series'.")
                tela_bacen.clicar_mais_series()
                tela_bacen.aguardar_carregmento_grafico()
                logging.info("Clicar no botao 'Taxas de Juros'.")
                tela_bacen.clicar_taxa_de_juros()
                logging.info("Clicar no opcao 'Capital de giro com prazo até 365 dias'.")
                tela_bacen.clicar_capital_giro_ate_365()

                #Criação do DF através da tabela obtida
                logging.info("Obter tabela de Taxas de Juros.")
                df_tabela_taxa_juros = tela_bacen.obter_tabela_capital_giro()

                if df_tabela_taxa_juros.empty:
                    logging.info("Tabela de Taxas de Juros vazia.")
                    return False
                
                break
                
            except:
                if tentativas == 3:
                    raise Exception(f"Falha ao obter Tabela Taxa Juros. Tentativas: 3.")
                
                tela_bacen.acessar_url()
                tentativas += tentativas 
        
        logging.info("Fim - Obter Tabela de Juros")
        return True
    
    except Exception as e:
            raise Exception(f"Falha ao obter Tabela Taxa Juros: {e}")
         

def tratar_resultados():
    logging.info("Inicio - Tratar resultados")
    global df_tabela_taxa_juros

    data_hora_processamento_nome = datetime.now().strftime("%Y_%m_%d_%H_%M")
    data_hora_processamento = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas_deletar = []

    try:
        #Remoção de conteudo desnecessário do DF
        df_tabela_taxa_juros.columns = df_tabela_taxa_juros.columns.get_level_values(1)
        df_tabela_taxa_juros = df_tabela_taxa_juros.drop(columns=['Posição'])

        logging.info("Savando dados de Taxas de Juros em arquivo.")
        #Busca dos CNPJS informados anteriormente na Base
        for i, row in df_tabela_taxa_juros.iterrows():
            if row['CNPJ'] not in cnpjs_validos:
                linhas_deletar.append(i)
        df_tabela_taxa_juros = df_tabela_taxa_juros.drop(index=linhas_deletar)
        
        #Salvamento do arquivo nas respecivas pastas
        logging.info("Salvando dados de Taxas de Juros em arquivo.")
        df_tabela_taxa_juros.to_csv(os.path.join(caminho_output, "Tabela Taxa Juros até 365.csv"), sep=";", index=False)
        df_tabela_taxa_juros.to_csv(os.path.join(caminho_historico_data_atual, "Tabela Taxa Juros até 365.csv"), sep=";", index=False)

        #Verificação de qual CNPJ foi processado corretamente
        logging.info("Atualizando arquivo de Base.")
        for cnpj in cnpjs:
            status = df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"].iloc[0]

            #Popula campo de STATUS com base no processamento ou não do CNPJ
            if cnpj in cnpjs_validos:
                df_base.loc[df_base["CNPJ"] == cnpj, "DATA HORA PROCESSAMENTO"] = data_hora_processamento
                if status.strip() == "":
                    if cnpj in df_tabela_taxa_juros["CNPJ"].values:
                        df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Processado"
                    else:
                        df_base.loc[df_base["CNPJ"] == cnpj, "STATUS"] = "Não encontrado"

        #Salvamento do arquivo nas respecivas pastas
        logging.info("Salvando arquivo de Base.")
        df_base.to_csv(caminho_arquivo_input, sep=";", index=False)
        os.rename(caminho_arquivo_input, os.path.join(caminho_intput, f"CNPJS_{data_hora_processamento_nome}.csv"))
        shutil.copy(os.path.join(caminho_intput, f"CNPJS_{data_hora_processamento_nome}.csv"), caminho_historico_data_atual)

        logging.info("Fim - Tratar resultados")
            
    except Exception as e:
        raise Exception(f"Falha ao obter Tabela Taxa Juros: {e}")


#Execução da automação
if __name__ == "__main__":
    if validar_ambiente():
        validar_base()
        acessar_sistema()
        if obter_tabela_taxa_juros():
            #Encerrar instancia o Chrome
            __driver.quit()
            tratar_resultados()

