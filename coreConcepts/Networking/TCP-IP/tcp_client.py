import socket
import sys


def send_message_to_tcp_server(message, host="localhost", port=9999):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((host, port))

        # Send data to the server
        client_socket.sendall(message.encode("utf-8"))

        # Receive a response from the server
        response = client_socket.recv(1024)
        print(f"Response from server: {response.decode('utf-8')}")
    finally:
        # Close the connection
        client_socket.close()


if __name__ == "__main__":
    while True:
        message = input("Enter the message to send: ")
        send_message_to_tcp_server(message)
        user_input = input("Do you want to send another message? (yes/no): ")
        if user_input.lower() != "yes":
            break
