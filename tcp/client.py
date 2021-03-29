import socket
import random
import time
import sys

# contadores de pacotes recebidos e enviados
counter_received = 0
counter_sent = 0

#contabilizadores de num de bytes enviados e recebidos
counter_bytes_received = 0
counter_bytes_sent = 0

#const para definir a porta do server
SERVER_PORT = 12000

def get_random_number(begin_number, number_of_decimal_places):
    #integer_length = (10 ** (int(input("Digite o numero de casas do inteiro randomico: "))) - 1)
    #random_integer_to_send = random.randrange(0, integer_length)
    random_integer = random.randrange(begin_number, ((10 ** number_of_decimal_places) - 1)) 
    return random_integer

counter_loop = 0
while True and (counter_loop < 20):
    msg_to_send = ""
    msg_received_str = ""
    
    random_integer_to_send = get_random_number(
        begin_number = 1, 
        number_of_decimal_places = random.randrange(1,30)
    )

    msg_to_send = str(random_integer_to_send)
    print("Numero randomico gerado enviado para o server: "+ msg_to_send)

    #AF_INET indica que e um protocolo de endereco IP
    #SOCK_STREAM indica que e um protocolo da camada de transporte TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", SERVER_PORT))
    
    counter_bytes_sent += sys.getsizeof(msg_to_send)
    client.send(msg_to_send.encode("utf-8"))
    counter_sent += 1

    msg_received_bytes = client.recv(1024)
    counter_received += 1
    msg_received_str = msg_received_bytes.decode("utf-8")
    counter_bytes_received += sys.getsizeof(msg_received_str)
    print("Mensagem recebida do server: "+ msg_received_str)

    msg_to_send = msg_received_str + " FIM "
    print("Mensagem enviada para o server: " + msg_to_send)
    counter_bytes_sent += sys.getsizeof(msg_to_send)
    client.send(msg_to_send.encode("utf-8"))
    counter_sent += 1

    print("Numero de PACOTES [enviados] | [recebidos]: "+ str(counter_sent) +" | "+ str(counter_received))
    print("Numero de BYTES [enviados] | [recebidos]: " + str(counter_bytes_sent) +" | "+ str(counter_bytes_received))

    #fecha o socket e da um delay de 30seg
    client.close()
    for i in range(10):
        print(str(i+1)+ "seg...")
        time.sleep(1)

    #contador de loop
    counter_loop += 1