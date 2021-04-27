import socket
import math
import random
import string
import time
import _thread as thread

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
# funcao para gerar string randomica de tamanho especifico
def random_str(chars = string.ascii_letters + string.digits, str_length=10):
	return ''.join(random.choice(chars) for _ in range(str_length))


#funcao para gerar um server
def spawn_server():
    Server().waiting_clients()

#Classe que define uma instancia de Servidor
class Server ():
    """
    Classe para instanciar o servidor para atender multiplos clientes
    """

    #!CONSTANTES
    #const num de bytes para pacotes recebidos
    NUM_BYTES_PACKAGES_RECEIVED = 248

    #const num máximo de tentativas
    ATTEMPTS_THRESHOLD = 3

    #constructor
    def __init__(self, server_ip="localhost", server_port=12000, limit_queue_clients = 5):
        #IP do servidor a ser conectado: default 192.168.0.0 || localhost
        self.server_ip = server_ip

        #Porta do servidor a ser acessada: default 12000
        self.server_port = server_port

        #Numero limite de clientes na fila
        self.limit_queue_clients = limit_queue_clients

        #variavel para armazenar o tempo em segundos para tratamento de erro Timeout
        self.timeout_seconds_limit = 1
        #variavel para armazenar o numero de tentativas ao lidar com erro timeout e/ou outros
        self.socket_erros_count_attempts = 0

        # contadores de pacotes recebidos e enviados pelo server
        self.counter_received = 0
        self.counter_sent = 0

        #contabilizadores de num de bytes enviados e recebidos pelo server
        self.counter_bytes_received = 0
        self.counter_bytes_sent = 0

        #AF_INET indica que e um protocolo de endereco IP
        #SOCK_STREAM indica que e um protocolo da camada de transporte TCP
        self.server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #inicializa o servidor
        self.run()

        super().__init__()

    #funcao que sera executada para incializar o server
    def run(self):
        self.server.bind((self.server_ip, self.server_port))
        
        #numero maximo de clientes que poderao esperar na fila
        self.server.listen(self.limit_queue_clients)

    #funcao que sera executada para atender um cliente
    def client_resolve(self, client_connection):
        
        #?Da um delay aleatorio de 1 ate 5 segundos para simular processamentos diferentes para diferentes clientes
        time.sleep(random.randrange(1,5))

        client_connection.settimeout(self.timeout_seconds_limit)

        #!RECEBENDO PACOTE DO CLIENTE
        msg_bytes = None
        while True:
            try:
                msg_bytes = client_connection.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
            except socket.gaierror as error:
                print_error("ERROR: Endereco de IP do cliente eh invalido ou nao pode ser alcancado")
                client_connection.close()                 
                quit()
            except socket.timeout as error:
                print_error("ERROR: Timeout, o cliente ultrapassou "+str(self.timeout_seconds_limit)+" segundo(s) para responder")
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao por erro timeout")
                    client_connection.close()                    
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                client_connection.settimeout(self.timeout_seconds_limit)
            except socket.error as error:
                print_error("ERROR" + str(error))
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao")
                    client_connection.close()                    
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                #delay de 3 segundos antes de tentar uma reconexao
                time.sleep(3)
            if msg_bytes: break
            print_warning("Tentando uma nova requisicao...")
        self.reset_hadling_errors(client_connection)
        self.counter_received += 1
        client_host, client_port = client_connection.getpeername()
        msg_received_str = msg_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        msg_received_int = int(msg_received_str)
        integer_length = int(math.log10(msg_received_int))+1
        print_success("Numero recebido do cliente: " + str(msg_received_int) + 
            " | Ip do cliente: " + str(client_host) +":"+ str(client_port) + 
            " | Tamanho do numero recebido do client: " + str(integer_length))
        
        #!PROCESSANDO MENSAGEM RECEBIDA
        if integer_length >= 10: # se menor qu 10
            msg_to_answer = random_str(str_length = integer_length)
        elif integer_length < 10: # se maior que 10
            if (msg_received_int % 2) == 0:
                msg_to_answer = 'PAR'
            else:
                msg_to_answer = 'IMPAR'
        
        #!ENVIANDO PACOTE AO CLIENTE
        self.counter_bytes_sent += utf8_str_bytes(msg_to_answer)
        while True:
            try:
                client_connection.send(msg_to_answer.encode("utf-8"))
                break
            except OSError:
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reenvio de pacote")
                    client_connection.close()                    
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                print_error("ERROR: Erro ao enviar para o cliente "+str(OSError))
            print_warning("Tentando um novo envio de pacote...")
        self.reset_hadling_errors(client_connection)
        self.counter_sent += 1
        print_success("Mensagem enviada para o cliente: " +  msg_to_answer)
        
        #!RECEBENDO PACOTE DO CLIENTE
        msg_bytes = None
        while True:
            try:
                msg_bytes = client_connection.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
            except socket.gaierror as error:
                print_error("ERROR: Endereco de IP do cliente eh invalido ou nao pode ser alcancado")
                client_connection.close()                
                quit()
            except socket.timeout as error:
                print_error("ERROR: Timeout, o cliente ultrapassou "+str(self.timeout_seconds_limit)+" segundo(s) para responder")
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao por erro timeout")
                    client_connection.close()                    
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                client_connection.settimeout(self.timeout_seconds_limit)
            except socket.error as error:
                print_error("ERROR" + str(error))
                #Verificando se atingiu o número máximo de tentativas
                if(self.socket_erros_count_attempts > self.ATTEMPTS_THRESHOLD):
                    print_error("Foi alcancado o numero maximo de " + str(self.ATTEMPTS_THRESHOLD) + " tentativas de reconexao")
                    client_connection.close()                    
                    quit()
                #Contabilizando +1 tentativa de reconexao por timeout
                self.socket_erros_count_attempts += 1
                #Aumentando o tempo de timeout +1 seg
                self.timeout_seconds_limit += 1
                #delay de 3 segundos antes de tentar uma reconexao
                time.sleep(3)
            if msg_bytes: break
            print_warning("Tentando uma nova requisicao...")
        self.reset_hadling_errors(client_connection)
        self.counter_received += 1
        msg_received_str = msg_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        print_success("Mensagem recebida do cliente: " + msg_received_str)

        #!RESUMO
        print_success("Numero de PACOTES [enviados] | [recebidos]: "+ str(self.counter_sent) +" | "+ str(self.counter_received))
        print_success("Numero de BYTES [enviados] | [recebidos]: " + str(self.counter_bytes_sent) +" | "+ str(self.counter_bytes_received))
        client_connection.close()
        print("#"*50)
        quit()

    #funcao que sera executada para esperar um cliente
    def waiting_clients(self):
        while True:
            msg_to_answer = ""
            msg_received_str = ""

            print('Esperando por clientes...')
            socket_connection, address = self.server.accept()
                
            print_success("Servidor recebeu a conexao do cliente com endereco: " + str(address))
            #Inicia a nova thread para atender o cliente
            thread.start_new_thread(self.client_resolve, (socket_connection,))
        return
            
    #metodo para resetar as variaveis de contagem e gerenciamento de erros
    def reset_hadling_errors(self, socket_connection):
        self.timeout_seconds_limit = 1
        self.socket_erros_count_attempts = 0
        socket_connection.settimeout(self.timeout_seconds_limit)

#?MAIN
spawn_server()