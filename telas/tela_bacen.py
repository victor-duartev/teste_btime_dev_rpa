#Desenvolvedor: VICTOR DUARTE VENANCIO
#Última atualização: 25/06/2024

#Este módulo contém funções que interagem com o sistema do Bacen.

#Importação de bibliotecas
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO

#Criação de classe
class TelaBacen():

    __URL_BACEN = "https://www.bcb.gov.br/"
    __XPATH_OPCAO_MAIS_SERIES = "//a[text()=' Mais séries ']"
    __XPATH_BOTAO_TAXAS_DE_JUROS = "//bcb-hub//div[normalize-space(.)='Taxas de Juros']"
    __XPATH_OPCAO_CAPITAL_GIRO_ATE_365 = "//h2[normalize-space(.)='Pessoa jurídica']/following::h3[normalize-space(.)='Taxas prefixadas']/following::a[normalize-space(.)='Capital de giro com prazo até 365 dias']"
    __XPATH_TABELA_TAXAS_JUROS = "//table[.//th[normalize-space(.)='Taxas Juros']]"
    __XPATH_BOTAO_FECHAR_COOKIES = "//button[contains(., 'Rejeitar cookies')]"
    __XPATH_GRAFICO_SISTEMA_POUPANCA = "//a[contains(normalize-space(.), 'Sistema Brasileiro de Poupança e Empréstimo')]"
    __XPATH_SPAN_SIGA_BC = "//span[normalize-space(.)='Siga o BC']"

    def __init__(self, driver):
        self.__driver = driver


    def abrir_navegador_chrome(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            self.__driver = webdriver.Chrome(options=options)

            return self.__driver
        
        except Exception as e:
            raise Exception(f"Falha ao acessar site do Bacen: {e}")
    

    def acessar_url(self):
        try:
            self.__driver.get(self.__URL_BACEN)

        except Exception as e:
            raise Exception(f"Falha ao acessar site do Bacen: {e}")


    def clicar_fechar_cookies(self):
        try:
            botao_fechar = WebDriverWait(self.__driver, 5).until(EC.element_to_be_clickable((By.XPATH, self.__XPATH_BOTAO_FECHAR_COOKIES)))
            if botao_fechar:
                botao_fechar.click()

        except:
            pass


    def clicar_mais_series(self):
        try:
            elemento = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, self.__XPATH_OPCAO_MAIS_SERIES)))
            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, self.__XPATH_OPCAO_MAIS_SERIES))).click()

        except Exception as e:
            raise Exception(f"Falha ao clicar em 'Mais Séries': {e}")
        
    
    def aguardar_carregmento_grafico(self):
        try:
            elemento = WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.XPATH, self.__XPATH_GRAFICO_SISTEMA_POUPANCA)))
            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        
        except Exception as e:
            raise Exception(f"Falha ao aguardar carregamento do grafico preços: {e}")


    def clicar_taxa_de_juros(self):
        try:
            elemento = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, self.__XPATH_SPAN_SIGA_BC)))
            visivel = ""
            while not visivel:
                self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                visivel = WebDriverWait(self.__driver, 10).until(EC.visibility_of_element_located((By.XPATH, self.__XPATH_SPAN_SIGA_BC)))
                WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, self.__XPATH_BOTAO_TAXAS_DE_JUROS)))

            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, self.__XPATH_BOTAO_TAXAS_DE_JUROS))).click()

        except Exception as e:
            raise Exception(f"Falha ao clicar no botão 'Taxas de Juros': {e}")


    def clicar_capital_giro_ate_365(self):
        try:
            elemento = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, self.__XPATH_OPCAO_CAPITAL_GIRO_ATE_365)))
            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, self.__XPATH_OPCAO_CAPITAL_GIRO_ATE_365))).click()

        except Exception as e:
            raise Exception(f"Falha ao clicar na opção 'Capital de giro com prazo até 365 dias': {e}")


    def obter_tabela_capital_giro(self):
        try:
            elemento = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, self.__XPATH_TABELA_TAXAS_JUROS)))
            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            table = self.__driver.find_element(By.XPATH, self.__XPATH_TABELA_TAXAS_JUROS)
            html = table.get_attribute("outerHTML")
            df = pd.read_html(StringIO(html))[0]
            df = df.astype(str)

            return df
        
        except Exception as e:
            raise Exception(f"Falha ao obter tabela 'Taxa de Juros':  {e}")