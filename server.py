import socket
import threading
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init()

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345

clients = {}  # เก็บ client_socket เป็น key และ hostname เป็น value

def handle_client(client_socket):
    client_hostname = clients[client_socket]
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"{Fore.CYAN}[*] {Fore.WHITE}{client_hostname}: {message}{Style.RESET_ALL}")
                broadcast_message(message, client_socket)
            else:
                remove_client(client_socket)
                break
        except ConnectionResetError:
            remove_client(client_socket)
            break

def broadcast_message(message, client_socket):
    client_hostname = clients[client_socket]
    for client in list(clients):  # ใช้ list(clients) เพื่อป้องกันการเปลี่ยนแปลง dict ระหว่างการ iterate
        if client != client_socket and client.fileno() != -1:  # ตรวจสอบว่า client ยังเชื่อมต่ออยู่หรือไม่
            try:
                client.send(f"{client_hostname}: {message}".encode('utf-8'))
            except ConnectionError:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        client_hostname = clients.pop(client_socket)
        client_socket.close()
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{Fore.RED}[-] {Fore.WHITE}{client_hostname} disconnected at {current_time}{Style.RESET_ALL}")
        except OSError as e:
            print(f"{Fore.RED}[-] {Fore.WHITE}Client disconnected unexpectedly{Style.RESET_ALL}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    print(f"{Fore.YELLOW}[+] {Fore.WHITE}Listening on {SERVER_HOST}:{SERVER_PORT}{Style.RESET_ALL}")

    while True:
        client_socket, client_address = server_socket.accept()
        try:
            client_hostname = socket.gethostbyaddr(client_address[0])[0]
        except socket.herror as e:
            print(f"Error resolving hostname: {e}")
            client_hostname = client_address[0]  # ใช้ IP Address แทนชื่อโฮสต์

        print(f"{Fore.GREEN}[+] {Fore.WHITE}Accepted connection from {client_address[0]}:{client_address[1]} ({client_hostname}){Style.RESET_ALL}")

        clients[client_socket] = client_hostname

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

except KeyboardInterrupt:
    print(f"\n{Fore.RED}[+] Keyboard Interrupted, Exiting...{Style.RESET_ALL}")

finally:
    for client_socket in list(clients):
        client_socket.close()

    server_socket.close()
