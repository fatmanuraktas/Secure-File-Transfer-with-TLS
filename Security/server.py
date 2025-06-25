import socket
import ssl
from cryptography.fernet import Fernet
import os


PORT = 9090
HOST = '192.168.0.16'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Load the server's certificate and private key
context.load_cert_chain(certfile='server.crt', keyfile='server.key')
# Load system's trusted CA certificates
context.load_default_certs()

if not os.path.exists('filekey.key'):
    key = Fernet.generate_key()
    with open('filekey.key', 'wb') as key_file:
        key_file.write(key)

with open('filekey.key', 'rb') as key_file:
    key = key_file.read()
fernet = Fernet(key)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
   

    while True:
        conn, addr = sock.accept()
        print(f"Connection from {addr}")
        
        
        try:
            with context.wrap_socket(conn, server_side=True) as ssock:
                print(ssock.version())

                try:
                        request = ssock.recv(1024).decode('utf-8')
                except UnicodeDecodeError:
                        print("[SERVER] Received non-UTF8 command. Dropping connection.")
                        continue
                print(f"Received request:\n{request}")
                
                if request.startswith("SEND "):
                    filename = request.split()[1]
                    if not filename.isalnum() and not filename.replace('.', '', 1).isalnum():
                            print("[SERVER] Unsafe filename detected. Rejecting.")
                            ssock.sendall(b'ERROR: Invalid filename')
                            continue
                    print(f"Receiving file: {filename}")
                    
                    with open(filename, 'wb') as f:
                        while True:
                            data = ssock.recv(1024)
                            if data == b'EOF':
                                break
                            token = fernet.encrypt(data)
                            f.write(token + b'\n')  # Write encrypted data with newline
                    print(f"File {filename} received successfully.")
                elif request.startswith("RECEIVE "):
                     filename = request.split()[1]
                     if not filename.isalnum() and not filename.replace('.', '', 1).isalnum():
#                       
                        print("[SERVER] Unsafe filename detected. Rejecting.")
                        ssock.sendall(b'ERROR: Invalid filename')
                        continue
                     try:
                         with open(filename, 'rb') as f:
                             for line in f:
                                 decrypted_data = fernet.decrypt(f.readline().strip())
                                 ssock.sendall(decrypted_data)                                 
                                 
                         ssock.sendall(b'EOF')
                         print(f"File {filename} decrypted and sent successfully.")
                     except FileNotFoundError:
                        print(f"[SERVER] File {filename} not found.")
                        ssock.sendall(b'ERROR: File not found')
                    
                    
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
        except Exception as e:
            print(f"Error: {e}")    