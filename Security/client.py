import socket
import ssl
import os
import time

PORT = 9090
#HOST = socket.gethostbyname(socket.gethostname())
MODE = 'SEND'  # 'SEND' or 'RECEIVE'
HOST = '192.168.0.16'
# PROTOCOL_TLS_CLIENT requires valid cert chain and hostname
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# Load system's trusted CA certificates
#context.load_default_certs()
context.load_verify_locations('server.crt')  # Load the server's certificate
context.check_hostname = False  # Enable hostname checking
context.verify_mode = ssl.CERT_REQUIRED  # Require certificate verification

start_time = time.time()

filename = 'test.txt'
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.connect((HOST, 9090))
        
        # Wrap the socket with SSL
        with context.wrap_socket(sock, server_hostname='192.168.0.16') as ssock:
            print(ssock.version())

            if MODE == 'RECEIVE':
                ssock.sendall(f"RECEIVE {filename}".encode())
                print(f"Requesting file: {filename}")

                with open(filename, 'wb') as f:
                    while True:
                        data = ssock.recv(1024)
                        if data == b'EOF':
                            break
                        f.write(data)
                print(f"Data received and written to {filename}")
            elif MODE == 'SEND':
                file = os.path.join(os.path.dirname(__file__), 'test.txt')
                
                ssock.sendall(f"SEND {filename}".encode())

                with open(filename, 'rb') as f:
                    
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        ssock.sendall(data)
                ssock.sendall(b'EOF')  # Indicate end of file transfer
                print(f"Data written to {filename}")
            

except ssl.SSLError as e:
    print(f"SSL error: {e}")
except FileNotFoundError:
    print(f"File {filename} not found.")
except Exception as e:
    print(f"An error occurred: {e}")
end_time = time.time()
duration = end_time - start_time

file_size_bytes = os.path.getsize(filename)
file_size_bits = file_size_bytes * 8
throughput_bps = file_size_bits / duration
throughput_mbps = throughput_bps / 1_000_000
print(f"[TLS CLIENT] File sent in {duration:.4f} seconds")
print(f"[TLS CLIENT] File size: {file_size_bytes} bytes")
print(f"[TLS CLIENT] Throughput: {throughput_mbps:.2f} Mbps")