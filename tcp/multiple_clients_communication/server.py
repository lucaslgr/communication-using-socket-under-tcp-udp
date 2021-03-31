import socket
import math
import random
import string
import time
import _thread as thread


def utf8_str_bytes(str):
    return len(str.encode('utf-8'))

# funcao para gerar string randomica de tamanho especifico
def random_str(chars = string.ascii_letters + string.digits, str_length=10):
	return ''.join(random.choice(chars) for _ in range(str_length))

#funcao para gerar um server
def spawn_server():
    Server().waiting_clients()

class Server ():
    """
    Classe para instanciar o servidor para atender multiplos clientes
    """

    #!CONSTANTES
    #const num de bytes para pacotes recebidos
    NUM_BYTES_PACKAGES_RECEIVED = 248

    #constructor
    def __init__(self, server_ip="localhost", server_port=12000, limit_queue_clients = 5):
        #IP do servidor a ser conectado: default 192.168.0.0 || localhost
        self.server_ip = server_ip

        #Porta do servidor a ser acessada: default 12000
        self.server_port = server_port

        #Numero limite de clientes na fila
        self.limit_queue_clients = limit_queue_clients

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
        #Da um delay aleatorio de 1 ate 5 segundos para simular processamentos diferentes para diferentes clientes
        time.sleep(random.randrange(1,5))

        msg_bytes = client_connection.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
        self.counter_received += 1
        client_host, client_port = client_connection.getpeername()
        msg_received_str = msg_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        msg_received_int = int(msg_received_str)
        
        #Checando se a mensagem nao e vazia
        if not msg_bytes: return
        
        integer_length = int(math.log10(msg_received_int))+1
        print("Numero recebido do cliente: " + str(msg_received_int) + 
            " | Ip do cliente: " + str(client_host) +":"+ str(client_port) + 
            " | Tamanho do numero recebido do client: " + str(integer_length))
        
        if integer_length >= 10: # se menor qu 10
            msg_to_answer = random_str(str_length = integer_length)
        elif integer_length < 10: # se maior que 10
            if (msg_received_int % 2) == 0:
                msg_to_answer = 'PAR'
            else:
                msg_to_answer = 'IMPAR'
        self.counter_bytes_sent += utf8_str_bytes(msg_to_answer)
        client_connection.send(msg_to_answer.encode("utf-8"))
        self.counter_sent += 1
        
        print("Mensagem enviada para o cliente: " +  msg_to_answer)
        msg_bytes = client_connection.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
        self.counter_received += 1
        msg_received_str = msg_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        print("Mensagem recebida do cliente: " + msg_received_str)
        print("Numero de PACOTES [enviados] | [recebidos]: "+ str(self.counter_sent) +" | "+ str(self.counter_received))
        print("Numero de BYTES [enviados] | [recebidos]: " + str(self.counter_bytes_sent) +" | "+ str(self.counter_bytes_received))
        print("#"*50)

    #funcao que sera executada para esperar um cliente
    def waiting_clients(self):
        while True:
            msg_to_answer = ""
            msg_received_str = ""

            print('Esperando por clientes...')
            socket_connection, address = self.server.accept()
            print("Servidor recebeu a conexao do cliente com endereco: " + str(address))
            
            #Inicia a nova thread para atender o cliente
            thread.start_new_thread(self.client_resolve, (socket_connection,))
        return
            
#?MAIN
spawn_server()