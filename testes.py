import pyodbc
from datetime import datetime
import os
import ler_arquivo as la
import time
import shutil


def mes_atual():
    return str(datetime.today().month)

def verifica_arquivos():
    files = []
    path = 'C:\Teste'
    for (dirpath, dirnames, filenames) in os.walk(path):
        files.extend(filenames)
        break

    caminho_atual = la.ler_variaveis()['local_bkp_original']
    for i in files:
        if (i[7:9]) != mes_atual():
            diretorio = caminho_atual + (r'\BKP_' + i[7:14])
            print(diretorio)
            if not os.path.exists(diretorio):
                print(diretorio)
                os.makedirs(diretorio)
            caminho_atual_completo = (caminho_atual + i).replace('BKP', '\BKP')
            caminho_novo_completo = (diretorio + i).replace('BKP', '\BKP')
            shutil.move(caminho_atual_completo, caminho_novo_completo)
