import socket
import smtplib


def start_tcp_server(host="localhost", port=9999):
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )  # create TCP/IP socket
    server_socket.bind((host, port))  # bind socket to host and port

    server_socket.listen(5)  # listen on port 5 for incoming connections
    print(f"TCP server started on {host}:{port}")

    while True:
        # wait for connection
        print("waiting for connection...")
        client_socket, client_address = server_socket.accept()
        print(f"connection established with {client_address}")

        try:
            # receive data from client
            data = client_socket.recv(1024)
            print(f"received data: {data.decode('utf8')}")

            # send response back to the client
            response = "Messag received by TCP server"
            client_socket.sendall(response.encode("utf8"))

        finally:
            client_socket.close()
            print(f"connection with {client_address} closed")


if __name__ == "__main__":
    start_tcp_server()
