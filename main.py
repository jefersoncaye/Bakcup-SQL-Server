import pyodbc
from datetime import datetime
import os
import ler_arquivo as la
import time
import shutil

"""
        retorno = {'server' : server, 'login' : username, 'senha' : password, 'local_bkp_original' : local_org,
               'database' : database_bck, 'hr_inicio_bkp' : hr_inicio_bkp, 'hr_final_bkp' : hr_final_bkp,
               'tempo_bkp_log' : tempo_bkp_log, 'dias_manter_bkp' : dias_manter_bkp, 'local_bkp' : local_bkp}
"""

hr_inicio_bkp = la.ler_variaveis()['hr_inicio_bkp']
hr_final_bkp = la.ler_variaveis()['hr_final_bkp']

tempo_bkp_log = la.ler_variaveis()['tempo_bkp_log']  # em minutos
ultimo_bkp_log = datetime.today()

dias_manter_bkp = la.ler_variaveis()['dias_manter_bkp']

server = la.ler_variaveis()['server']
database = 'master'
username = la.ler_variaveis()['login']
password = la.ler_variaveis()['senha']
database_bck = la.ler_variaveis()['database']
local_bkp = la.ler_variaveis()['local_bkp']
try:
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                          ';UID=' + username + ';PWD=' + password, autocommit=True)
except:
    raise ValueError('Erro ao conectar no Banco de Dados')


def cursor(cmd):
    cursor = cnxn.cursor()
    cursor.execute(cmd)
    cursor.nextset()
    cursor.close()

def recovery_full():
    try:
        f'USE {database}'
        cursor(f'USE {database}'
                f' ALTER DATABASE {database_bck} SET RECOVERY FULL')
    except:
        raise ValueError('Erro ao Passar a Base para RECOVERY FULL')

def verifica_backup():
    try:
        cursor = cnxn.cursor()
        cursor.execute("RESTORE HEADERONLY  FROM DISK = '"+monta_caminho()+"'")
        resultado = cursor.fetchall()
        return resultado
    except:
        return 0

def monta_caminho():
    caminho = f"{local_bkp}{monta_dt_bkp()}_{database_bck}.BAK"
    dir = la.ler_variaveis()['local_bkp_original']
    if not os.path.exists(dir):
        os.makedirs(dir)
    return caminho

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
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)
            caminho_atual_completo = (caminho_atual + i).replace('BKP', '\BKP')
            caminho_novo_completo = (diretorio + i).replace('BKP', '\BKP')
            shutil.move(caminho_atual_completo, caminho_novo_completo)


def atualiza_banco(tipo_bkp, data_bkp, comando):
    cursor = cnxn.cursor()
    tipo_bkp = str(tipo_bkp)
    data_bkp = str(data_bkp)
    comando = str(comando)
    cursor.execute(" USE ["+database_bck+"] "
    "IF (EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TMP_CONTROLE_BKP')) BEGIN "
    "INSERT INTO TMP_CONTROLE_BKP VALUES ('"+tipo_bkp+"', '"+data_bkp+"', '"+comando+"'); END ELSE BEGIN "
    "CREATE TABLE TMP_CONTROLE_BKP (ID INT IDENTITY(1,1) PRIMARY KEY , TIPO_BKP VARCHAR(1), "
    "DATA_BKP VARCHAR(20), COMANDO_TSQL VARCHAR(200));"
    "INSERT INTO TMP_CONTROLE_BKP VALUES ('"+tipo_bkp+"', '"+data_bkp+"', '"+comando+"'); "
    "END")
    cursor.close()


def data_formatada():
    return str(datetime.today().strftime('%d/%m/%Y %H:%M'))

def monta_dt_bkp():
    return str(datetime.today().strftime('%d_%m_%Y'))

def dia_atual():
    return str(datetime.today().day)

def hora_atual():
    return str(datetime.today().hour)

def mes_atual():
    return str(datetime.today().month)

def verifica_data_tbl():
    try:
        cursor = cnxn.cursor()
        cursor.execute("USE ["+database_bck+"]")
        cursor.execute("IF (EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TMP_CONTROLE_BKP')) "
                       "BEGIN "
                       "SELECT DATA_BKP FROM TMP_CONTROLE_BKP "
                       "END")
        dia = cursor.fetchall()
        cursor.close()
        dia = dia[-1][0][:5]
        return str(dia)
    except:
        return dia_atual()


def reinicia_tabela():
    if mes_atual() != verifica_data_tbl()[3:5]:
        cursor("IF (EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TMP_CONTROLE_BKP')) "
               "BEGIN "
               "DROP TABLE TMP_CONTROLE_BKP "
               "END")


def verifica_horario():
    if int(hora_atual()) >= int(hr_inicio_bkp) and int(hora_atual()) <= int(hr_final_bkp):
        return 0
    else:
        return 1

def tempo_log():
    d2 = datetime.today()
    diff = d2 - ultimo_bkp_log
    seconds = diff.seconds
    minutes, seconds = seconds // 60, seconds % 60
    if minutes >= int(tempo_bkp_log):
        return 0
    else:
        return 1

def condicao_bkp_inicial():
    return verifica_backup() == 0 and verifica_horario() == 0

def condicao_bkp_diferencial():
    return verifica_backup()[-1][2] == 2 and verifica_backup()[-2][2] == 2 and verifica_backup()[-3][2] == 2 \
        and verifica_backup()[-4][2] == 2 and verifica_backup()[-5][2] != 2 and verifica_horario() == 0

def condicao_bkp_log():
    return (verifica_backup()[-1][2] == 1 or verifica_backup()[-1][2] == 2 or verifica_backup()[-1][2] == 5) \
        and verifica_horario() == 0 and tempo_log() == 0


def faz_backup():
    while verifica_horario() == 0:
        if condicao_bkp_inicial():
            verifica_arquivos()
            reinicia_tabela()
            try:
                la.cria_log(f'Fazendo Backup Inicial {data_formatada()}')
                backup_inicial = (
                            "BACKUP DATABASE [" + database_bck + "] TO DISK = '"+monta_caminho()+"' WITH INIT")
                cursor(backup_inicial)
                la.cria_log(f'Backup Inicial Feito com Sucesso em {data_formatada()}\n{backup_inicial}')
                atualiza_banco('1', data_formatada(), backup_inicial.replace("'", ''))
            except:
                la.cria_log('Erro ao fazer o Backup Inicial')

        elif condicao_bkp_diferencial():
            try:
                la.cria_log(f'Fazendo Backup Diferencial {data_formatada()}')
                backup_diferencial = (
                            "BACKUP DATABASE [" + database_bck + "] TO DISK = '" +monta_caminho()+ "' WITH DIFFERENTIAL")
                cursor(backup_diferencial)
                la.cria_log(f'Backup Inicial Feito com Sucesso em {data_formatada()}\n{backup_diferencial}')
                atualiza_banco('5', data_formatada(), backup_diferencial.replace("'", ''))
            except:
                la.cria_log('Erro ao Fazer Backup Diferencial')

        elif condicao_bkp_log():
            try:
                la.cria_log(f'Fazendo Backup Log {data_formatada()}')
                backup_log = (
                            "BACKUP LOG ["+database_bck+"] TO DISK = '"+monta_caminho()+"' WITH NOINIT")
                cursor(backup_log)
                la.cria_log(f'Backup Log Feito com Sucesso em {data_formatada()}\n{backup_log}')
                atualiza_banco('2', data_formatada(), backup_log.replace("'", ''))
                ultimo_bkp_log = datetime.today()
            except:
                la.cria_log('Erro ao fazer Backup Log')

        time.sleep((int(tempo_bkp_log) * 60)+60)

