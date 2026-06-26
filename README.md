## Descrição

Este projeto tem como objetivo automatizar a consulta da tabela de Taxas de Juros para Pessoa Jurídica – Capital de Giro com prazo de até 365 dias, disponível no Banco Central do Brasil (BACEN).

O projeto possui duas abordagens de execução:

- Automação via Selenium (web scraping no portal do Bacen)
- Integração via API oficial do Bacen (OLINDA)

Ambas as versões realizam a leitura de uma base de CNPJs e geram um arquivo CSV contendo apenas os registros encontrados.

Além disso, o processo mantém histórico dos arquivos para auditoria.

---

## Tecnologias utilizadas

- Python 3.x
- Selenium
- Requests
- Pandas
- WebDriver (Google Chrome)

---

## Estrutura do projeto

WEB-SCRAPING-PIPELINE
│
├── historico/
│   └── AAAA_MM_DD/
│
├── input/
│   └── CNPJS.csv
│
├── output/
│   └── Tabela Taxa Juros até 365.csv
│
├── telas/
│   └── tela_bacen.py
│
├── uteis/
│   └── uteis.py
│
├── app.log
├── main.py
├── main_api.py
└── requirements.txt

---

# Modos de Execução

## 1. Versão Web Scraping (Selenium)

### Funcionamento

1. Valida ambiente
2. Cria diretórios
3. Lê base CNPJs
4. Acessa portal do Bacen
5. Extrai dados via interface web
6. Filtra CNPJs
7. Gera CSV
8. Atualiza status
9. Salva histórico

---

## 2. Versão API (Recomendada)

### Endpoint

https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo?$filter=Segmento eq 'PESSOA JURÍDICA'&$select=Segmento,InstituicaoFinanceira,cnpj8,TaxaJurosAoMes,TaxaJurosAoAno&$top=100&$format=json

### Funcionamento

1. Valida ambiente
2. Lê base CNPJs
3. Consulta API Bacen
4. Converte JSON em DataFrame
5. Renomeia colunas
6. Filtra CNPJs
7. Gera CSV
8. Atualiza status
9. Salva histórico

---

## Arquivo de entrada

input/CNPJS.csv

Formato:

CNPJ
00000000
11111111

---

## Arquivo de saída

output/Tabela Taxa Juros até 365.csv

historico/AAAA_MM_DD/

---

## Status da base

STATUS:
- Processado
- Não encontrado
- Inválido

---

## Tratamento de erros

- Falhas de rede
- Timeout
- JSON inválido
- CNPJs inválidos
- Erros Selenium

Logs: app.log

---

## Execução

Web:
python main.py

API:
python main_api.py

---

## Autor

Victor Duarte Venancio