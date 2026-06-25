# Web Scraping - Taxas de Juros BACEN

## Descrição

Este projeto tem como objetivo automatizar a consulta da tabela de **Taxas de Juros para Pessoa Jurídica – Capital de Giro com prazo de até 365 dias**, disponível no portal do Banco Central do Brasil (BACEN).

A automação realiza a leitura de uma base de CNPJs, acessa o site do BACEN utilizando Selenium, obtém a tabela de taxas de juros vigente e gera um arquivo CSV contendo apenas os CNPJs informados na base de entrada.

Além da geração do resultado, o processo mantém um histórico dos arquivos processados para fins de auditoria.

---

## Tecnologias utilizadas

* Python 3.x
* Selenium
* Pandas
* WebDriver (Google Chrome)

---

## Estrutura do projeto

```
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
└── requirements.txt
```

---

## Funcionamento

O processo executa as seguintes etapas:

1. Valida o ambiente de execução.
2. Cria automaticamente os diretórios necessários.
3. Lê o arquivo `input/CNPJS.csv`.
4. Valida os CNPJs informados.
5. Acessa o portal do Banco Central.
6. Navega até a página de Taxas de Juros.
7. Obtém a tabela "Capital de giro com prazo até 365 dias".
8. Filtra apenas os CNPJs presentes no arquivo de entrada.
9. Gera o arquivo de saída.
10. Atualiza o status de processamento da base.
11. Armazena os arquivos processados na pasta `historico`.

---

## Arquivo de entrada

O arquivo deve estar localizado em:

```
input/CNPJS.csv
```

Formato esperado (com base na tabela Bacen):

| CNPJ     |
| -------- |
| 00000000 |
| 11111111 |
| 22222222 |

Separador utilizado:

```
;
```

---

## Arquivo de saída

Após o processamento será gerado:

```
output/
    Tabela Taxa Juros até 365.csv
```

O arquivo contém apenas os registros correspondentes aos CNPJs informados na entrada.

Também será criada uma cópia na pasta:

```
historico/AAAA_MM_DD/
```

---

## Status da base

Ao término da execução, o arquivo de entrada é atualizado com duas colunas adicionais:

* STATUS
* DATA HORA PROCESSAMENTO

Possíveis valores para STATUS:

* Processado
* Não encontrado
* Inválido

---

## Tratamento de erros

A aplicação contempla tratamento para:

* Falha ao acessar o portal do BACEN.
* Timeout durante a navegação.
* Inexistência de diretórios necessários.
* Base de entrada inválida.
* Falha na obtenção da tabela.
* Exceções durante o processamento.

Todos os eventos são registrados no arquivo:

```
app.log
```

---

## Dependências

Instale as dependências executando:

```bash
pip install -r requirements.txt
```

---

## Como executar

Após instalar as dependências:

```bash
python main.py
```

---

## Arquitetura

O projeto foi organizado em módulos para promover a separação de responsabilidades:

* **main.py**

  * Responsável pela orquestração do processo.

* **telas/**

  * Contém as interações com a interface do site do Banco Central utilizando Selenium.

* **uteis/**

  * Contém funções auxiliares utilizadas durante a execução.

Essa estrutura facilita a manutenção e evolução do código, mantendo a lógica de navegação separada das regras de processamento.

---

## Observações

* O projeto utiliza Selenium para navegação automatizada.
* Os diretórios necessários são criados automaticamente caso não existam.
* Os resultados anteriores são preservados na pasta `historico`.
* A automação depende do acesso ao portal oficial do Banco Central e da disponibilidade do serviço.

---

## Autor

**Victor Duarte Venâncio**
