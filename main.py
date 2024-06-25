import socket
import threading


class Server:
    class HeaderResult:
        def __init__(self):
            self.start_header = ""
            self.headers = {}
            self.extra_body = b""

    def __init__(self, port):
        self.port = port

    def run(self):
        with socket.create_server(("127.0.0.1", self.port), reuse_port=True) as server_socket:
            print('Listening on http://127.0.0.1:{}'.format(self.port))
            while True:
                client_socket, address = server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            header_result = self.read_request_header(client_socket)
            content = "Hello world"
            response = (
                "HTTP/1.1 200 Ok\r\n"
                "Connection: close\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n"
                f"{content}"
            )
            client_socket.send(response.encode('utf-8'))
            print(header_result)
        except Exception as e:
            print(e)

    def search_header_end(self, request_buffer):
        for i in range(len(request_buffer) - 3):
            if (request_buffer[i] == 13 and request_buffer[i + 1] == 10
                    and request_buffer[i + 2] == 13 and request_buffer[i + 3] == 10):
                return i
        print("not found")
        return -1

    def read_request_header(self, client_socket):
        print("Reading request header")
        request_buffer = bytearray()
        while True:
            search_header_end = self.search_header_end(request_buffer)
            print("search_header_end: ", search_header_end)
            if search_header_end == -1:
                data = client_socket.recv(1024)
                print("data: ", data)
                if not data:
                    break
                request_buffer.extend(data)
            else:
                break
        header_bytes = request_buffer[:search_header_end]
        extra_body = request_buffer[search_header_end:]
        headers = header_bytes.decode('utf-8')
        return self.parse_headers(headers, extra_body)

    def parse_headers(self, headers, extra_body):
        header_result = self.HeaderResult()
        header_lines = headers.split('\r\n')
        header_result.start_header = header_lines[0]
        header_result.extra_body = extra_body

        for line in header_lines[1:]:
            if line:
                parts = line.split(":")
                if len(parts) >= 2:
                    header_name = parts[0].strip()
                    header_value = parts[1].strip()
                    header_result.headers[header_name] = header_value
        return header_result


if __name__ == '__main__':
    server = Server(8080)
    server.run()
