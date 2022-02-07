import coloredlogs, logging
import sys, getopt
from pathlib import Path
import configparser
import time
import datetime
import random
import re
from modules.brave import Brave
import pytest

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)

serie = 'G'
profileInit = None
codigo = None

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hs:p:c:",["sSerie=","pPerfil=","cCodigo="])
    except getopt.GetoptError:
        print(sys.argv[0] + ' -s <serie> -p <perfil>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(sys.argv[0] + ' -s <serie> -p <perfil>')
            sys.exit()
        elif opt in ("-s", "--sSerie"):
            global serie 
            serie = arg
        elif opt in ("-p", "--pPerfil"):
            global profileInit 
            profileInit = int(arg)
        elif opt in ("-c", "--cCodigo"):
            global codigo 
            codigo = arg

def isLogin():
    if(len(objBrave.driver.find_elements_by_xpath('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[1]/input')) > 0 ):
           return False
    return True

def login():
    
    time.sleep(random.uniform(5, 10))
    
    if(not isLogin()):
        inputEmail = objBrave.driver.find_element_by_xpath('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[1]/input')
        inputPassword = objBrave.driver.find_element_by_xpath('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[2]/input')
        
        inputEmail.clear()
        inputEmail.send_keys('user')
        
        inputPassword.clear()    
        inputPassword.send_keys('pass')
        
        objBrave.driver.find_element_by_xpath('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/button').click()

        time.sleep(random.uniform(5, 10))
        if(objBrave.driver.find_element_by_xpath('/html/body/div[3]').is_displayed()):
            logger.error('Captcha en el LOGIN!!')
            # input("pausa")  
            
    else:
        logger.info('Usuario logado')

def isGirar():
    if(objBrave.driver.find_element_by_xpath('/html/body/main/div/div/div/div/div/div[5]').is_displayed()):
           return True
    return False    
        
def girar():
    time.sleep(random.uniform(5, 10))
    if(isGirar()):
        objBrave.driver.find_element_by_xpath('/html/body/main/div/div/div/div/div/div[5]/button').click()
        time.sleep(random.uniform(5, 10))
        contador = objBrave.driver.find_element_by_xpath('//div[@class="timeout-wrapper"]')
        if(not contador.is_displayed()):
            logger.error('Captcha en el GIRO!!')
            input("pausa")
    return objBrave.driver.find_element_by_xpath('/html/body/main/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]').get_attribute('innerHTML').strip()

def getCoins():
    coins = objBrave.driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[11]/a').get_attribute('innerHTML').strip() 
    return coins

if __name__ == '__main__':
    main(sys.argv[1:])
    
    logger.info('### Inicio de ejecucion Serie: ' + serie)
    logger.info('### Inicio de ejecucion Perfil: ' + str(profileInit))
        
    ###
    config = configparser.RawConfigParser(allow_no_value=True)
    
    if Path("./ini/config_" + serie + ".ini").is_file():
        config.read("./ini/config_" + serie + ".ini")
    else:
        config.read("./ini/config.ini")
    
    
    if (profileInit is None):
        profileInit = config.getint("brave", "profileInit")
    profileMax = config.getint("brave", "profileMax")
    

    timeSleepMin = config.getfloat("brave", "timeSleepMin")
    timeSleepMax = config.getfloat("brave", "timeSleepMax")
    timeSleep = timeSleepMin
    ###
        
    faucets = [
        ['https://freenem.com/', 'XEM', '5'],
        ['https://coinfaucet.io/', 'XRP', '5'],
        ['https://freebitcoin.io/', 'BTC', '0.00020000'],
        ['https://freesteam.io/', 'STEAM', '5'],
        ['https://freetether.com/', 'USDT', '5'],
        ['https://freeusdcoin.com/', 'USDC', '10'],
        ['https://freebinancecoin.com/', 'BNB', '0.03'],
        ['https://freeethereum.com/', 'ETH', '0.005'],
        ['https://free-tron.com/', 'TRX', '40'],
        ['https://freedash.io/', 'DASH', '0.01'],
        ['https://freechainlink.io/', 'LINK', '0.3'],
        ['https://freeneo.io/', 'NEO', '1'],
        ['https://free-ltc.com/', 'LTC', '0.01'],
        ['https://free-doge.com/', 'DOGE', '30']]
    
    while True:
    
        objBrave = Brave(serie, profileInit) 
        
        tiempo = 60
    
        for faucet in faucets:
    
            logger.info('Faucet: ' + faucet[0]) 
            objBrave.driver.get(faucet[0])
            # objBrave.driver.maximize_window()
                
            login()
            acumulado = getCoins()
            logger.info('Saldo(' + faucet[2]+ ' ' + faucet[1] + '): ' + acumulado)
            
            acumulado = re.search(r'(\d*\.?\d+)', acumulado)
            # logger.info(acumulado.group())
            try:
                valorTirada = objBrave.driver.find_element_by_xpath('/html/body/main/div/div/div/div/div/div[2]/div[2]/div[1]/table/tbody/tr[2]/td[3]').get_attribute('innerHTML').strip() 
                logger.info('Valor de la tirada: ' + valorTirada + ', tiradas restantes: ' + 
                        str( (float(faucet[2])-float(acumulado.group()))/float(valorTirada)) )
            except:
                logger.info('No se puede calcular el numero de tiradas restantes')
            
            minutos = girar()
            logger.info('Minutos siguiente giro: ' + minutos)
            if (tiempo > int(minutos)):
                tiempo = int(minutos)
                
            time.sleep(random.uniform(5, 10))
            
            if not (codigo == None):
                objBrave.driver.get(faucet[0])
                objBrave.driver.find_element_by_css_selector('input.form-control').send_keys(codigo)
                objBrave.driver.find_element_by_css_selector('button.btn.main-button-blue-simple.submit-promo').click()
                time.sleep(random.uniform(5, 10))
                objBrave.driver.get(faucet[0])
                time.sleep(random.uniform(5, 10))
                girar()
                time.sleep(random.uniform(5, 10))
                

        # Calculamos el tiempo de la siguiente tirada
        tiempo = tiempo * 60
        now = datetime.datetime.now()
        hora_actual = now.hour
        if (hora_actual > 1 and hora_actual < 7):
            tiempo = (8 - hora_actual) * 3600
        tiempo = random.uniform(tiempo, tiempo + 900)
        logger.info('Tiempo de espera hasta la siguiente tirada: ' + str(tiempo))
      
        codigo = None
        
        objBrave.close()

        time.sleep(tiempo)