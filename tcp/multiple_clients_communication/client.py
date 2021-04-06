import socket
import random
import time
import threading

#Classe e funcoes para print no terminal com cores
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def print_error(str_msg):
    print (colors.FAIL + str_msg + colors.ENDC) 
def print_warning(str_msg):
    print (colors.WARNING + str_msg + colors.ENDC)
def print_success(str_msg):
    print (colors.OKGREEN + str_msg + colors.ENDC)
#Converte string em utf-8 para bytes
def utf8_str_bytes(str):
    return len(str.encode('utf-8'))
#Retorna um numero randomico de acordo com os parametros
def get_random_number(begin_number, number_of_decimal_places):
    #integer_length = (10 ** (int(input("Digite o numero de casas do inteiro randomico: "))) - 1)
    #random_integer_to_send = random.randrange(0, integer_length)
    random_integer = random.randrange(begin_number, ((10 ** number_of_decimal_places) - 1)) 
    return random_integer


#Instancia N clientes em N threads
def spawn_clients(number_of_clients = 10):
    for client_id in range(number_of_clients):
        print("Cliente "+str(client_id)+" foi instanciado...")
        #Instanciando os clients e startando as threads de cada um
        Client(client_id).start()

#Classe que define uma instancia de Cliente
class Client (threading.Thread):
    """
    Classe para instanciar os clientes para rodar em threads
    """

    #!CONSTANTES
    #const num de bytes para pacotes recebidos
    NUM_BYTES_PACKAGES_RECEIVED = 248

    #const num de loops
    NUM_LOOPS = 20

    #const num máximo de tentativas
    ATTEMPTS_THRESHOLD = 3

    #const num de delay em segundos
    NUM_DELAY_LOOP_SECONDS = 1

    #constructor
    def __init__(self, client_id, server_ip = "localhost", server_port = 12000):
        #identificador do client
        self.client_id = client_id

        #variavel para armazenar o tempo em segundos para tratamento de erro Timeout
        self.timeout_seconds_limit = 1
        #variavel para armazenar o numero de tentativas ao lidar com erro timeout e/ou outros
        self.socket_erros_count_attempts = 0

        #IP do servidor a ser conectado: default 192.168.0.0 || localhost
        self.server_ip = server_ip

        #Porta do servidor a ser acessada: default 12000
        self.server_port = server_port

        # contadores de pacotes recebidos e enviados
        self.counter_received = 0
        self.counter_sent = 0

        #contabilizadores de num de bytes enviados e recebidos
        self.counter_bytes_received = 0
        self.counter_bytes_sent = 0

        #quantidade de vezes que sera executado a funcao task
        self.counter_loop = 0

        #construindo a instancia da classe mae
        threading.Thread.__init__(self)

    #metodo respectivo a tarefa a ser executada
    def task(self):
        msg_to_send = ""
        msg_received_str = ""

        #AF_INET indica que e um protocolo de endereco IP
        #SOCK_STREAM indica que e um protocolo da camada de transporte TCP
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #setando o limite de timout do cliente
        client.settimeout(self.timeout_seconds_limit)
        
        #!CONECTANDO AO SERVER
        while True:
            try:
                client.connect((self.server_ip, self.server_port))
                break
            except socket.gaierror as error:
                print_error("ERROR: Endereco de IP do server eh invalido ou nao pode ser alcancado")
                #saindo da execucao
                quit() 
            except socket.timeout as error:
                print_error("ERROR: Timeout, o server ultrapassou "+str(self.timeout_seconds_limit)+" segundo(s) para responder a tentativa de conexao")
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " +str(self.ATTEMPTS_THRESHOLD)+ " tentativas de reconexao por erro timeout")
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                client.settimeout(self.timeout_seconds_limit)
            except OSError as error:
                print_error("ERROR: " + str(error))
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de "+str(self.ATTEMPTS_THRESHOLD)+" tentativas de reconexao")
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                #delay de 3 segundos antes de tentar uma reconexao
                time.sleep(3)
            print_warning("Tentando uma nova conexao...")
        self.reset_hadling_errors(client)

        #!ENVIANDO PACOTE AO SERVER
        random_integer_to_send = get_random_number( begin_number=1, number_of_decimal_places=random.randrange(1, 30))
        msg_to_send = str(random_integer_to_send)
        print_success("Cliente: " +str(self.client_id)+ " Numero randomico gerado enviado para o server: " + msg_to_send)
        self.counter_bytes_sent += utf8_str_bytes(msg_to_send)
        while True:
            try:
                client.send(msg_to_send.encode("utf-8"))
                break
            except OSError:
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reenvio de pacote")
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                print_error("ERROR: Erro ao enviar para o server "+str(OSError))
            print_warning("Tentando um novo envio de pacote...")
        self.reset_hadling_errors(client)
        self.counter_sent += 1
        
        #!REQUISITANDO PACOTE AO SERVER
        msg_received_bytes = None
        while True:
            try:
                msg_received_bytes = client.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
            except socket.gaierror as error:
                print_error("ERROR: Endereco de IP do server eh invalido ou nao pode ser alcancado")
                #saindo da execucao
                quit() 
            except socket.timeout as error:
                print_error("ERROR: Timeout, o server ultrapassou "+str(self.timeout_seconds_limit)+" segundo(s) para responder")
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao por erro timeout")
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                client.settimeout(self.timeout_seconds_limit)
            except OSError as error:
                print_error("ERROR: " + str(error))
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao")
                    client.close()
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                #delay de 3 segundos antes de tentar uma reconexao
                time.sleep(3)
            if msg_received_bytes: break
            print_warning("Tentando uma nova requisicao...")
        self.reset_hadling_errors(client)
        self.counter_received += 1
        msg_received_str = msg_received_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        print_success("Mensagem recebida do server: " + msg_received_str)

        #!ENVIANDO PACOTE AO SERVER
        msg_to_send = msg_received_str + " FIM "
        print_success("Mensagem enviada para o server: " + msg_to_send)
        self.counter_bytes_sent += utf8_str_bytes(msg_to_send)
        while True:
            try:
                client.send(msg_to_send.encode("utf-8"))
                break
            except OSError:
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reenvio de pacote")
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                print_error("ERROR: Erro ao enviar para o server "+str(OSError))
            print_warning("Tentando um novo envio de pacote...")
        self.reset_hadling_errors(client)
        self.counter_sent += 1

        #!RESUMO
        print_success("Numero de PACOTES [enviados] | [recebidos]: " +
                str(self.counter_sent) + " | " + str(self.counter_received))
        print_success("Numero de BYTES [enviados] | [recebidos]: " +
                str(self.counter_bytes_sent) + " | " + str(self.counter_bytes_received))

        #fecha o socket e da um delay de 30seg
        client.close()
        if (self.counter_loop == (self.NUM_LOOPS - 1)):
            return
        for i in range(self.NUM_DELAY_LOOP_SECONDS):
            print(str(i+1) + "seg...")
            time.sleep(1)
    
    #metodo herdado de threads, e o metodo chamado ao usar o metodo start na classe mae
    def run(self):
        while True and (self.counter_loop < self.NUM_LOOPS):
            self.task()
            
            #contador de loop
            self.counter_loop += 1
        return

    #metodo para resetar as variaveis de contagem e gerenciamento de erros
    def reset_hadling_errors(self, client_connection):
        self.timeout_seconds_limit = 1
        self.socket_erros_count_attempts = 0
        client_connection.settimeout(self.timeout_seconds_limit)

#?MAIN
spawn_clients(1)