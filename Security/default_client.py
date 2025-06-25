import socket
import os
import time

PORT = 8080
HOST = '127.0.0.1'
MODE = 'SEND'  
filename = 'test.txt'

start_time = time.time()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        if MODE == 'RECEIVE':
            sock.sendall(f"RECEIVE {filename}".encode())
            print(f"Requesting file: {filename}")

            with open(filename, 'wb') as f:
                while True:
                    data = sock.recv(1024)
                    if data == b'EOF':
                        break
                    f.write(data)
            print(f"Data received and written to {filename}")

        elif MODE == 'SEND':
            sock.sendall(f"SEND {filename}".encode())
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    sock.sendall(data)
            sock.sendall(b'EOF')  # Dosya aktarımının bittiğini belirt

            print(f"Data sent from {filename}")

        else:
            print("Invalid MODE. Use 'SEND' or 'RECEIVE'.")

except FileNotFoundError:
    print(f"File {filename} not found.")
except Exception as e:
    print(f"An error occurred: {e}")

end_time = time.time()
duration = end_time - start_time

if os.path.exists(filename):
    file_size_bytes = os.path.getsize(filename)
    file_size_bits = file_size_bytes * 8
    throughput_bps = file_size_bits / duration
    throughput_mbps = throughput_bps / 1_000_000
    print(f"File transfer completed in {duration:.4f} seconds")
    print(f"File size: {file_size_bytes} bytes")
    print(f"Throughput: {throughput_mbps:.2f} Mbps")
