import socket
import math
import random
import string
import sys

# contadores de pacotes recebidos e enviados
counter_received = 0
counter_sent = 0

#contabilizadores de num de bytes enviados e recebidos
counter_bytes_received = 0
counter_bytes_sent = 0

#const para definir a porta do server
SERVER_PORT = 12000

# funcao para gerar string randomica de tamanho especifico
def random_str(chars = string.ascii_letters + string.digits, str_length=10):
	return ''.join(random.choice(chars) for _ in range(str_length))

#AF_INET indica que e um protocolo de endereco IP
#SOCK_STREAM indica que e um protocolo da camada de transporte TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", SERVER_PORT))

server.listen(5)  

while True:
    msg_to_answer = ""
    msg_received_str = ""

    print('Esperando por clientes...')

    socketConnection, address = server.accept()
    print("Servidor recebeu a conexao do cliente com endereco: " + str(address))

    msg_bytes = socketConnection.recv(1024)
    counter_received += 1
    clientHost, clientPort = socketConnection.getpeername()
    msg_received_str = msg_bytes.decode("utf-8")
    counter_bytes_received += sys.getsizeof(msg_received_str)
    msg_received_int = int(msg_received_str)

    if msg_received_str != "":
        integer_length = int(math.log10(msg_received_int))+1
        print("Numero recebido do cliente: " + str(msg_received_int) + 
            " | Ip do cliente: " + str(clientHost) +":"+ str(clientPort) + 
            " | Tamanho do numero recebido do client: " + str(integer_length))
        
        if integer_length >= 10: # se menor qu 10
            msg_to_answer = random_str(str_length = integer_length)

        elif integer_length < 10: # se maior que 10
            if (msg_received_int % 2) == 0:
                msg_to_answer = 'PAR'
            else:
                msg_to_answer = 'IMPAR'

        counter_bytes_sent += sys.getsizeof(msg_to_answer)
        socketConnection.send(msg_to_answer.encode("utf-8"))
        counter_sent += 1
        
        print("Mensagem enviada para o cliente: " +  msg_to_answer)

        msg_bytes = socketConnection.recv(1024)
        counter_received += 1
        msg_received_str = msg_bytes.decode("utf-8")
        counter_bytes_received += sys.getsizeof(msg_received_str)

        print("Mensagem recebida do cliente: " + msg_received_str)
        print("Numero de PACOTES [enviados] | [recebidos]: "+ str(counter_sent) +" | "+ str(counter_received))
        print("Numero de BYTES [enviados] | [recebidos]: " + str(counter_bytes_sent) +" | "+ str(counter_bytes_received))
        print("#"*67)
