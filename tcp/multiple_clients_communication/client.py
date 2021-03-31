import socket
import random
import time
import threading

def utf8_str_bytes(str):
    return len(str.encode('utf-8'))

def get_random_number(begin_number, number_of_decimal_places):
    #integer_length = (10 ** (int(input("Digite o numero de casas do inteiro randomico: "))) - 1)
    #random_integer_to_send = random.randrange(0, integer_length)
    random_integer = random.randrange(begin_number, ((10 ** number_of_decimal_places) - 1)) 
    return random_integer

def spawn_clients(number_of_clients = 10):
    for client_id in range(number_of_clients):
        print("Cliente "+str(client_id)+" foi instanciado...")
        #Instanciando os clients e startando as threads de cada um
        Client(client_id).start()

class Client (threading.Thread):
    """
    Classe para instanciar os clientes para rodar em threads
    """

    #!CONSTANTES
    #const num de bytes para pacotes recebidos
    NUM_BYTES_PACKAGES_RECEIVED = 248

    #const num de loops
    NUM_LOOPS = 1

    #const num de delay em segundos
    NUM_DELAY_SECONDS = 1

    #constructor
    def __init__(self, client_id, server_ip = "localhost", server_port = 12000):
        #identificador do client
        self.client_id = client_id

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
        client.settimeout(100)

        client.connect((self.server_ip, self.server_port))

        random_integer_to_send = get_random_number(
            begin_number=1,
            number_of_decimal_places=random.randrange(1, 30)
        )

        msg_to_send = str(random_integer_to_send)
        print("Cliente: " +str(self.client_id)+ " Numero randomico gerado enviado para o server: " + msg_to_send)

        self.counter_bytes_sent += utf8_str_bytes(msg_to_send)
        client.send(msg_to_send.encode("utf-8"))
        self.counter_sent += 1

        msg_received_bytes = client.recv(self.NUM_BYTES_PACKAGES_RECEIVED)
        self.counter_received += 1
        msg_received_str = msg_received_bytes.decode("utf-8")
        self.counter_bytes_received += utf8_str_bytes(msg_received_str)
        print("Mensagem recebida do server: " + msg_received_str)

        msg_to_send = msg_received_str + " FIM "
        print("Mensagem enviada para o server: " + msg_to_send)
        self.counter_bytes_sent += utf8_str_bytes(msg_to_send)
        client.send(msg_to_send.encode("utf-8"))
        self.counter_sent += 1

        print("Numero de PACOTES [enviados] | [recebidos]: " +
                str(self.counter_sent) + " | " + str(self.counter_received))
        print("Numero de BYTES [enviados] | [recebidos]: " +
                str(self.counter_bytes_sent) + " | " + str(self.counter_bytes_received))

        #fecha o socket e da um delay de 30seg
        client.close()
        if (self.counter_loop == (self.NUM_LOOPS - 1)):
            return
        for i in range(self.NUM_DELAY_SECONDS):
            print(str(i+1) + "seg...")
            time.sleep(1)
    
    #metodo herdado de threads, e o metodo chamado ao usar o metodo start na classe mae
    def run(self):
        while True and (self.counter_loop < self.NUM_LOOPS):
            self.task()
            
            #contador de loop
            self.counter_loop += 1
        return

#?MAIN
spawn_clients(1)