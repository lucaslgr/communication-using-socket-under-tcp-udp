import socket
import random
import time

# contadores de pacotes recebidos e enviados
counter_received = 0
counter_sent = 0

#contabilizadores de num de bytes enviados e recebidos
counter_bytes_received = 0
counter_bytes_sent = 0

#const para definir a porta do server
SERVER_PORT = 16000

#const num de loops
NUM_LOOPS = 20

#const num de delay em segundos
NUM_DELAY_SECONDS = 10

def utf8_str_bytes(str):
    return len(str.encode('utf-8'))

def get_random_number(begin_number, number_of_decimal_places):
    random_integer = random.randrange(begin_number, ((10 ** number_of_decimal_places) - 1)) 
    return random_integer

counter_loop = 0
while True and (counter_loop < NUM_LOOPS):
    msg_to_send = ""
    msg_received_str = ""

    #AF_INET indica que e um protocolo de endereco IP
    #SOCK_DGRAM indica que e um protocolo da camada de transporte UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    random_integer_to_send = get_random_number(
        begin_number = 1, 
        number_of_decimal_places = random.randrange(1,30)
    )

    msg_to_send = str(random_integer_to_send)
    print("Numero randomico gerado enviado para o server: "+ msg_to_send)
    
    counter_bytes_sent += utf8_str_bytes(msg_to_send)
    client.sendto(msg_to_send.encode(), ("localhost", SERVER_PORT)) 
    counter_sent += 1

    msg_received_bytes, address_ip_server = client.recvfrom(2048)
    counter_received += 1
    msg_received_str = msg_received_bytes.decode()
    counter_bytes_received += utf8_str_bytes(msg_received_str)
    print("Mensagem recebida do server: "+ msg_received_str)

    msg_to_send = msg_received_str + " FIM "
    print("Mensagem enviada para o server: " + msg_to_send)
    counter_bytes_sent += utf8_str_bytes(msg_to_send)
    client.sendto(msg_to_send.encode(), ("localhost", SERVER_PORT))
    counter_sent += 1
    
    #fecha o socket e da um delay de 30seg
    client.close()

    print("Numero de PACOTES [enviados] | [recebidos]: "+ str(counter_sent) +" | "+ str(counter_received))
    print("Numero de BYTES [enviados] | [recebidos]: " + str(counter_bytes_sent) +" | "+ str(counter_bytes_received))

    if (counter_loop == (NUM_LOOPS - 1)): break
    for i in range(NUM_DELAY_SECONDS):
        print(str(i+1)+ "seg...")
        time.sleep(1)

    #contador de loop
    counter_loop += 1
