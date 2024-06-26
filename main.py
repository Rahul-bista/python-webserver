import socket
import threading


class Server:
    # Inner class to hold the result of reading headers
    class HeaderResult:
        def __init__(self):
            self.start_header = ""  # The request line (e.g., "GET / HTTP/1.1")
            self.headers = {}  # Dictionary to store header key-value pairs
            self.extra_body = b""  # Any extra data received after the headers

    def __init__(self, port):
        self.port = port  # Initialize server with a port

    def run(self):
        # Create a TCP server socket, set it to reuse the port, and bind to localhost
        with socket.create_server(("127.0.0.1", self.port), reuse_port=True) as server_socket:
            print('Listening on http://127.0.0.1:{}'.format(self.port))
            while True:
                client_socket, address = server_socket.accept()  # Accept a new client connection
                threading.Thread(target=self.handle_client,
                                 args=(client_socket,)).start()  # Handle the client in a new thread

    def handle_client(self, client_socket):
        try:
            # Read the request headers from the client
            self.read_request_header(client_socket)
            # Response content
            content = "Hello world"
            # HTTP response
            response = (
                "HTTP/1.1 200 Ok\r\n"
                "Connection: close\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n"
                f"{content}"
            )
            # Send the response to the client
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(e)  # Print any exception that occurs

    def search_header_end(self, request_buffer):
        # Search for the end of the headers in the request buffer
        for i in range(len(request_buffer) - 3):
            if (request_buffer[i] == 13 and request_buffer[i + 1] == 10
                    and request_buffer[i + 2] == 13 and request_buffer[i + 3] == 10):
                return i  # Return the position where the headers end
        print("not found")
        return -1  # Return -1 if the end of headers is not found

    def read_request_header(self, client_socket):
        print("Reading request header")
        request_buffer = bytearray()  # Buffer to hold the request data
        while True:
            # Search for the end of the headers in the current buffer
            search_header_end = self.search_header_end(request_buffer)
            print("search_header_end: ", search_header_end)
            if search_header_end == -1:
                data = client_socket.recv(1024)  # Receive data from the client
                print("data: ", data)
                if not data:
                    break  # Exit if no data is received
                request_buffer.extend(data)  # Append received data to the buffer
            else:
                break  # Exit the loop if the end of headers is found
        # Extract the headers from the buffer
        header_bytes = request_buffer[:search_header_end]
        # Any extra data after the headers
        extra_body = request_buffer[search_header_end:]
        # Decode the headers from bytes to string and parse them
        headers = header_bytes.decode('utf-8')
        return self.parse_headers(headers, extra_body)

    def parse_headers(self, headers, extra_body):
        header_result = self.HeaderResult()  # Create a HeaderResult object
        header_lines = headers.split('\r\n')  # Split headers by line
        header_result.start_header = header_lines[0]  # First line is the request line
        header_result.extra_body = extra_body  # Store any extra body data

        for line in header_lines[1:]:
            if line:
                parts = line.split(":")  # Split header line into name and value
                if len(parts) >= 2:
                    header_name = parts[0].strip()  # Extract and strip header name
                    header_value = parts[1].strip()  # Extract and strip header value
                    header_result.headers[header_name] = header_value  # Add to headers dictionary
        return header_result  # Return the parsed headers


if __name__ == '__main__':
    server = Server(8080)  # Create a Server object with port 8080
    server.run()  # Run the server
