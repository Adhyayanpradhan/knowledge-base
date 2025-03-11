import socket
import ssl
import threading
import os
import datetime
import mimetypes


class SimpleHTTPServer:
    def __init__(self, host="0.0.0.0", port=8080, document_root="./www"):
        """
        Initialize the HTTP server with configurable host, port, and document root.

        :param host: Server host address
        :param port: Server port number
        :param document_root: Directory to serve files from
        """
        self.host = host
        self.port = port
        self.document_root = document_root
        self.server_socket = None

        # Ensure document root exists
        os.makedirs(document_root, exist_ok=True)

    def _handle_request(self, client_socket):
        """
        Handle incoming HTTP request

        :param client_socket: Connected client socket
        """
        try:
            # Receive request data
            request_data = client_socket.recv(1024).decode("utf-8")

            # Parse request
            request_lines = request_data.split("\n")
            request_method = request_lines[0].split()[0]
            request_path = request_lines[0].split()[1]

            # Construct file path
            file_path = os.path.join(self.document_root, request_path.lstrip("/"))

            # Default to index.html if path is a directory
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, "index.html")

            # Determine content type
            content_type = mimetypes.guess_type(file_path)[0] or "text/plain"

            # Response construction
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    file_content = f.read()

                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Server: SimpleHTTPServer\r\n"
                    f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Content-Length: {len(file_content)}\r\n\r\n"
                ).encode("utf-8") + file_content
            else:
                response = (
                    f"HTTP/1.1 404 Not Found\r\n"
                    f"Server: SimpleHTTPServer\r\n"
                    f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
                    f"Content-Type: text/plain\r\n\r\n"
                    "404 File Not Found"
                ).encode("utf-8")

            client_socket.send(response)
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()

    def start(self):
        """
        Start the HTTP server and listen for connections
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"HTTP Server running on http://{self.host}:{self.port}")

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_request, args=(client_socket,)
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()


class SimpleHTTPSServer(SimpleHTTPServer):
    def __init__(
        self,
        host="0.0.0.0",
        port=8443,
        document_root="./www",
        certfile="server.crt",
        keyfile="server.key",
    ):
        """
        Initialize the HTTPS server with SSL support

        :param certfile: SSL certificate file path
        :param keyfile: SSL private key file path
        """
        super().__init__(host, port, document_root)
        self.certfile = certfile
        self.keyfile = keyfile

        # Generate self-signed certificate if not exists
        if not (os.path.exists(certfile) and os.path.exists(keyfile)):
            self._generate_self_signed_cert()

    def _generate_self_signed_cert(self):
        """
        Generate a self-signed SSL certificate if not present
        """
        os.system(
            f"openssl req -x509 -newkey rsa:4096 -keyout {self.keyfile} "
            f"-out {self.certfile} -days 365 -nodes -subj '/CN=localhost'"
        )

    def start(self):
        """
        Start the HTTPS server with SSL context
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        # Wrap socket with SSL
        secure_socket = context.wrap_socket(self.server_socket, server_side=True)

        print(f"HTTPS Server running on https://{self.host}:{self.port}")

        try:
            while True:
                client_socket, address = secure_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_request, args=(client_socket,)
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            if secure_socket:
                secure_socket.close()


def main():
    # Create a sample index.html in the document root
    os.makedirs("./www", exist_ok=True)
    with open("./www/index.html", "w") as f:
        f.write(
            """
        <!DOCTYPE html>
        <html>
        <head><title>Simple HTTP/HTTPS Server</title></head>
        <body>
            <h1>Welcome to the Simple HTTP/HTTPS Server!</h1>
            <p>This server is running from scratch.</p>
        </body>
        </html>
        """
        )

    # Start HTTP server
    http_server = SimpleHTTPServer(port=8080)
    http_thread = threading.Thread(target=http_server.start)
    http_thread.start()

    # Start HTTPS server
    https_server = SimpleHTTPSServer(port=8443)
    https_thread = threading.Thread(target=https_server.start)
    https_thread.start()


if __name__ == "__main__":
    main()
