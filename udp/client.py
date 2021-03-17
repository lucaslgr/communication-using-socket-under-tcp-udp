import socket
import random
import time
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def get_random_number(begin_number, number_of_decimal_places):
    #integer_length = (10 ** (int(input("Digite o numero de casas do inteiro randomico: "))) - 1)
    #random_integer_to_send = random.randrange(0, integer_length)
    random_integer = random.randrange(begin_number, ((10 ** number_of_decimal_places) - 1)) 
    return random_integer

def send_to_server():
    random_integer_to_send = get_random_number(
        begin_number = 1, 
        number_of_decimal_places = 30
    )
    msg_to_send = str(random_integer_to_send)
    print("Número randomico gerado enviado para o server: "+ msg_to_send)
    client.sendto(msg_to_send.encode(), ("localhost", 12000))

def check_arrived():
    msg_received_bytes, address_ip_server = client.recvfrom(2048)
    msg_received_str = msg_received_bytes.decode()
    print("Mensagem recebida do server: "+ msg_received_str)
    msg_to_send = msg_received_str + " FIM "
    print("Mensagem enviada para o server: " + msg_to_send)
    client.sendto(msg_to_send.encode(), ("localhost", 12000))
    
    #fecha o socket e da um delay de 30seg
    #client.close()
    
set_interval(send_to_server, 30)
set_interval(check_arrived, 1)
send_to_server()