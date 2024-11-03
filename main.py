from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import logging
import traceback
import json
import datetime
import sys
import os
from colorama import Fore, Style

data_atual = datetime.datetime.now().strftime('%Y-%m-%d')
os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=f'logs/app_{data_atual}.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

class Main:
     
    def carregar_dados(self):
        print(Fore.CYAN + '|- Carregando dados' + Style.RESET_ALL)
        try:
            logging.info('Carregando dados...')
            with open('config.json', 'r') as file:
                dados = json.load(file)
                self.cpf = dados['cpf']
                self.consorcio = dados['consorcio_type']
                self.step = dados['step']
                self.timer = dados['timer']
                self.ver_chrome = dados['ver_chrome']
                self.consorcio = self.consorcio.upper()
                self.MaximoPraDireita = 129
                self.contadoMaximo = 0
            with open('mensagem.txt', 'r') as msg:
                self.mensagem = msg.read()
            if (self.step % 5000) != 0:
                a = input('O "step" deve ser multiplo de 5000, aperte ENTER e reconfigure ')
                sys.exit()
            
        except Exception as error:
            logging.error(f'Carregar dados: {error}')
            raise Exception('Erro ao carregar dados')

    def start(self):        
        print(Fore.BLUE + 'Iniciando Tela..' + Style.RESET_ALL)
        try:
            logging.info('|- Abrindo tela')
            self.options = uc.ChromeOptions()
            self.options.add_argument("--start-maximized")
            self.options.add_argument("--disable-infobars")
            self.options.add_argument("--disable-extensions")
            self.options.add_argument("--no-sandbox")
            if not self.ver_chrome:
                self.options.add_argument("--headless")
                # self.options.add_argument("--disable-gpu")
            service = ChromeService(ChromeDriverManager().install())
            self.driver = uc.Chrome(service=service, options=self.options)                
            self.driver.set_window_size(960, 1080)
            self.driver.set_window_position(0, 0)
            self.driver.get("https://mycotas.mycon.com.br")
        except Exception as error:
                logging.error(f'Abrindo tela: {error}')
                raise Exception('Erro ao abrir tela')

    def login(self):        
        print(Fore.BLUE + '|- Fazendo login' + Style.RESET_ALL)
        try:
            logging.info('Fazendo login...')
            try: self.driver.find_element(By.CSS_SELECTOR, '.accept-policy').click()
            except: pass
            self.driver.execute_script('validateLead()')
            sleep(2)
            self.driver.find_element(By.CSS_SELECTOR, '#Login').click() 
            sleep(1)
            for i in self.cpf:
                self.driver.find_element(By.CSS_SELECTOR, '#Login').send_keys(i)
                sleep(0.2)
            self.driver.execute_script('login()') 
        except Exception as error:
            logging.error(f'Fazendo login: {error}')
            raise Exception('Erro ao fazer login')

    def escolher_consorcio(self):
        print(Fore.BLUE + '|- Iniciando Tela' + Style.RESET_ALL)
        try:
            logging.info('Escolhendo consorcio...')
            sleep(4)
            itens = self.driver.find_elements(By.CSS_SELECTOR, '.item')
            if self.consorcio == 'IMÓVEL' or self.consorcio == 'IMOVEL':
                itens[0].click()
            elif self.consorcio == 'CARRO':
                itens[1].click()
            elif self.consorcio == 'MOTOS':
                itens[2].click()
            elif self.consorcio == 'SERVIÇOS' or self.consorcio == 'SERVICOS':
                itens[3].click()
        except Exception as error:
            logging.error(f'Escolhendo consorcio: {error}')
            raise Exception('Erro ao escolher consorcio')

    def config_input_baixo(self):
        print(Fore.BLUE + '|- Configurando valor' + Style.RESET_ALL)
        try:
            logging.info('Configurando o input')
            #botar o valor mais baixo no input
            sleep(1)
            input = self.driver.find_element(By.CSS_SELECTOR, '.irs-slider.single')
            actions = ActionChains(self.driver)
            numeroDeVezesMaximoPraEleSempreChegarNaEsquerda = 7
            for i in range(0, numeroDeVezesMaximoPraEleSempreChegarNaEsquerda):
                actions.click_and_hold(input).move_by_offset(-30, 0).release().perform()
        except Exception as error:
            logging.error(f'Configurando o input: {error}')
            raise Exception('Erro ao configurar o input')

                    
    def config_input_cima(self):
        print(Fore.BLUE + '|- Aumentando valor' + Style.RESET_ALL)
        try:
            logging.info('Configurando o input')
            sleep(1)
            input = self.driver.find_element(By.CSS_SELECTOR, '.irs-slider.single')
            actions = ActionChains(self.driver)
            VezesPraFrente = self.step / 5000
            for i in range(0, int(VezesPraFrente)):
                sleep(1)
                actions.click_and_hold(input).move_by_offset(3, 0).release().perform()
                self.contadoMaximo += 1
                if self.contadoMaximo == self.MaximoPraDireita:
                    self.buscar_oferta()
            self.buscar_oferta()
        except Exception as error:
            logging.error(f'Configurando o input: {error}')
            logging.error('Traceback: %s', traceback.format_exc())
            raise Exception('Erro ao configurar o input para cima')

    def buscar_oferta(self):
        print(Fore.BLUE + '|- Escolhendo consórcios' + Style.RESET_ALL)
        try:
            valor = self.driver.find_element(By.CSS_SELECTOR, '.irs-single').text
            valor = valor.replace('R$', '').replace('.', '').strip()
            valor = float(valor)
            logging.info(f'Buscando ofertas na faixa de {valor}...')
            sleep(2)
            try:
                print(f'Buscando valor na faixa de {valor}')
            except: pass
            self.driver.execute_script('filter()')
            sleep(7)
            tbody = self.driver.find_element(By.TAG_NAME, 'tbody')
            linhas = tbody.find_elements(By.TAG_NAME, 'tr')
            sleep(2)
            if len(linhas) :            
                for linha in linhas:
                    sleep(2)
                    colunas = linha.find_elements(By.TAG_NAME, 'td')
                    credito = colunas[0].text
                    credito = credito.replace('.', '').replace(',', '.')
                    credito = float(credito)
                    porcentagem = credito * 0.30
                    entrada = colunas[1]
                    entrada = entrada.text
                    entrada = entrada.replace('.', '').replace(',', '.')
                    entrada = float(entrada)
                    if entrada <= porcentagem:
                        try:
                            logging.info(f'Oportunidade encontrada na faixa de {valor}...')
                            self.driver.execute_script("arguments[0].scrollIntoView();", linha)                            
                            print(Fore.YELLOW + '|- Oportunidade encontrada' + Style.RESET_ALL)
                            sleep(2)
                            btn = colunas[6].find_element(By.TAG_NAME, 'a')
                            self.driver.execute_script('arguments[0].click();', btn)
                            sleep(5)
                            if not len(self.driver.find_elements(By.CSS_SELECTOR, '#Message')): continue
                            self.driver.find_element(By.CSS_SELECTOR, '#Message').click()
                            sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, '#Message').clear()
                            sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, '#Message').send_keys(self.mensagem)
                            print(Fore.GREEN + '|- Escolhendo consórcios' + Style.RESET_ALL)
                            self.driver.execute_script('sendContact()') 
                            sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, 'button#btCloseModal').click()
                            logging.info('Mensagem enviada com sucesso...')
                        except: pass
                #try:
                #    self.driver.find_element(By.CSS_SELECTOR, '#responsive-data-table_next').click()
                #    self.buscar_oferta()
                #except: pass
                self.driver.execute_script("arguments[0].scrollIntoView();", linhas[0])
                self.driver.execute_script('navigateToTabSearch()')
            sleep(2)
            if valor == 700000.00:
                self.esperar()    
            else:
                self.config_input_cima()
        except Exception as error:
            logging.error(f'Erro no processo de buscar oferta: {error}')
            logging.error('Traceback: %s', traceback.format_exc())
            raise Exception('Erro no processo de buscar oferta')
           
    def esperar(self):
        print('Esperando...')
        try:
            logging.info('Esperando...')
            tempo = self.timer * 60
            self.driver.quit()
            sleep(tempo)
            self.main()
        except Exception as error:
            logging.error(f'Esperando: {error}')
            raise Exception('Erro ao esperar')

    def main(self):
        try:
            self.carregar_dados()
            self.start()
            self.login()
            self.escolher_consorcio()
            self.config_input_baixo()
            self.buscar_oferta()
        except:
            self.driver.quit()

if __name__ == '__main__':
    main = Main()
    main.main()