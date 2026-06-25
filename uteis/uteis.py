#Desenvolvedor: VICTOR DUARTE VENANCIO
#Última atualização: 25/06/2024

#Este módulo contém funções gerais úteis para o funcionamento da automação.

import subprocess
import os

#Criação de classe
class Uteis():

    def fechar_subprocesso(self, subprocesso):
        try:
            result = subprocess.run(["tasklist"], text=True)
            if subprocesso in str(result.stdout):
                subprocess.run(["taskkill", "/F", "/IM", subprocesso])

        except Exception as e:
            raise Exception(f"Falha ao encerrar subprocesso {subprocesso}: {e}")

    def conferir_existencia_diretorio(self, diretorio):
        if not os.path.isdir(diretorio):
            os.makedirs(diretorio)
            
        return True