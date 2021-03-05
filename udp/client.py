import socket
import random

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    integer_length = (10 ** (int(input("Digite o numero de casas do inteiro randomico: "))) - 1)
    random_integer_to_send = random.randrange(0, integer_length)

    msg_to_send = str(random_integer_to_send)
    print("Número randomico gerado enviado para o server: "+ msg_to_send)
    
    client.sendto(msg_to_send.encode(), ("localhost", 12000))
    msg_received_bytes, address_ip_server = client.recvfrom(2048)
    msg_received_str = msg_received_bytes.decode()
    print("Mensagem recebida do server: "+ msg_received_str + " NA ")

    msg_to_send = msg_received_str + " FIM "
    print("Mensagem enviada para o server: " + msg_to_send)
    client.sendto(msg_to_send.encode(), ("localhost", 12000))
    client.close()