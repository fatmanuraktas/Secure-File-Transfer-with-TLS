import socket
import os

PORT = 8080
HOST = '127.0.0.1'  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = sock.accept()
        print(f"Connection from {addr}")
        with conn:
            try:
                request = conn.recv(1024).decode('utf-8')
                print(f"Received request: {request}")

                if request.startswith("SEND "):
                    filename = request.split()[1]
                    if not filename.isalnum() and not filename.replace('.', '', 1).isalnum():
                        conn.sendall(b'ERROR: Invalid filename')
                        continue

                    print(f"Receiving file: {filename}")
                    with open(filename, 'wb') as f:
                        while True:
                            data = conn.recv(1024)
                            if data == b'EOF':
                                break
                            f.write(data)
                    print(f"File {filename} received successfully.")

                elif request.startswith("RECEIVE "):
                    filename = request.split()[1]
                    if not filename.isalnum() and not filename.replace('.', '', 1).isalnum():
                        conn.sendall(b'ERROR: Invalid filename')
                        continue

                    try:
                        with open(filename, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    break
                                conn.sendall(data)
                        conn.sendall(b'EOF')
                        print(f"File {filename} sent successfully.")
                    except FileNotFoundError:
                        print(f"File {filename} not found.")
                        conn.sendall(b'ERROR: File not found')

                else:
                    conn.sendall(b'ERROR: Unknown command')

            except Exception as e:
                print(f"Error: {e}")
