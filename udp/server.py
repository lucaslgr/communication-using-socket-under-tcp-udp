import socket
import math
import random
import string

# funcao para gerar string randomica de tamanho especifico
def random_str(chars = string.ascii_letters + string.digits, str_length=10):
	return ''.join(random.choice(chars) for _ in range(str_length))

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("", 12000))

while True:
    print('Esperando por clients...')
    msg_bytes, address_ip_client = server.recvfrom(248)
    msg_received_str = msg_bytes.decode()
    msg_received_int = int(msg_received_str)

    if msg_received_str != "":
        integer_length = int(math.log10(msg_received_int))+1
        print("Numero recebido do client: " + str(msg_received_int) + " | Ip do client: " +str(address_ip_client)+ " | Tamanho do numero recebido do client: " + str(integer_length))
        
        if integer_length > 10: # se menor qu 10
            msg_to_answer = random_str(str_length = integer_length)

        elif integer_length < 10: # se maior que 10
            if (msg_received_int % 2) == 0:
                msg_to_answer = "PAR"
            else:
                msg_to_answer = "IMPAR"

        server.sendto(msg_to_answer.encode(), address_ip_client)
        print("Mensagem enviada para o client: " +  msg_to_answer)

        msg_bytes, address_ip_client = server.recvfrom(248)
        msg_received_str = msg_bytes.decode()
        print("Mensagem recebida do client: " + msg_received_str)
        print("#"*130)
