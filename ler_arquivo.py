from datetime import datetime
import os
def escreve_arquivo(server, username, password, database_bck, local_bkp, hr_inicio_bkp, hr_final_bkp,
                    tempo_bkp_log, dias_manter_bkp):
    try:
        arq = open('dados.txt', 'w')
        arq.write(f'INSTANCIA: {server}\n'
                  f'LOGIN: {username}\n'
                  f'SENHA: {password}\n'
                  f'DATABASE: {database_bck}\n'
                  f'CAMINHO: {local_bkp}\n'
                  f'HORA INICIAR BKP: {hr_inicio_bkp}\n'
                  f'HORA PARA BKP: {hr_final_bkp}\n'
                  f'TEMPO ENTRE BKP: {tempo_bkp_log}\n'
                  f'DIAS MANTER BACKUP: {dias_manter_bkp}\n')
        arq.close()
    except:
        raise RuntimeError('Erro ao Abrir ou Salvar o Arquivo')

def ler_variaveis():
    arq = open('dados.txt', 'r')
    try:
        for i in arq:
            if 'INSTANCIA:' in i:
                instancia = i
            if 'LOGIN:' in i:
                login = i
            if 'SENHA:' in i:
                senha = i
            if 'CAMINHO:' in i:
                caminho = i
            if 'DATABASE:' in i:
                database_bkp = i
            if 'HORA INICIAR BKP:' in i:
                hr_inicio_bkp = i
            if 'HORA PARA BKP:' in i:
                hr_final_bkp = i
            if 'TEMPO ENTRE BKP:' in i:
                tempo_bkp_log = i
            if 'DIAS MANTER BACKUP:' in i:
                dias_manter_bkp = i
    except:
        raise ValueError('Alguma Variavel não foi encontrada')
    arq.close()
    server = instancia
    server = server[10:].strip()
    username = login
    username = username[6:].strip()
    password = senha
    password = password[6:].strip()
    database_bck = database_bkp
    database_bck = database_bck[9:].strip()
    local_bkp = caminho
    local_org = local_bkp[8:].strip()
    local_bkp = local_org + '\BKP_'
    hr_inicio_bkp = hr_inicio_bkp[17:].strip()
    hr_final_bkp = hr_final_bkp[14:].strip()
    tempo_bkp_log = tempo_bkp_log[16:].strip()
    dias_manter_bkp = dias_manter_bkp[19:].strip()
    database = 'master'
    retorno = {'server' : server, 'login' : username, 'senha' : password, 'local_bkp_original' : local_org,
               'database' : database_bck, 'hr_inicio_bkp' : hr_inicio_bkp, 'hr_final_bkp' : hr_final_bkp,
               'tempo_bkp_log' : tempo_bkp_log, 'dias_manter_bkp' : dias_manter_bkp, 'local_bkp' : local_bkp}
    return retorno

def cria_log(msg):
    #nome = str(nome)
    try:
        arq = open(monta_caminho_log(), 'a')
        arq.write('\n' + msg)
        arq.close()
    except:
        raise ValueError('Erro ao Criar o Arquivo De Log')

def le_log():
    try:
        arq = open(monta_caminho_log(), 'a')
        arq.close()
        arq = open(monta_caminho_log(), 'r')
        log = arq.read()
        arq.close()
        return log
    except:
        raise ValueError('Não Foi Possivel Ler o Arquivo de Log')

def monta_caminho_log():
    data = str(datetime.today().strftime('\%d_%m_%Y'))
    dir = ler_variaveis()['local_bkp_original']
    dir = (dir + f'\LOGS')
    caminho = f"{dir}{data}.txt"
    if not os.path.exists(dir):
        os.makedirs(dir)
    return caminho

