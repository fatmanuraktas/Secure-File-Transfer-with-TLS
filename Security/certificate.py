from cryptography import x509
from cryptography.hazmat.backends import default_backend 
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
import socket
import ipaddress

server_IP = '192.168.0.16'  # Get the server's IP address
hostname = '192.168.0.16'  # Get the hostname of the server
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, server_IP),
])
alternative_names = [
    #x509.DNSName(hostname),
    #x509.DNSName(server_IP),
    x509.IPAddress(ipaddress.ip_address(server_IP))
    
]

basic_contraints = x509.BasicConstraints(ca=False, path_length=None)
now = datetime.utcnow()
cert = x509.CertificateBuilder().subject_name(
    name
).issuer_name(
    name
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    now
).not_valid_after(
    now + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName(alternative_names),
    critical=False,
).add_extension(
    basic_contraints,
    critical=True,
).sign(key, hashes.SHA256(), default_backend())

my_cert_pem = cert.public_bytes(serialization.Encoding.PEM)
my_key_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
with open('server.crt', 'wb') as cert_file:
    cert_file.write(my_cert_pem)
with open('server.key', 'wb') as key_file:
    key_file.write(my_key_pem)