import tkinter as tk
import socket
import threading

class ServerGUI:
    def __init__(self):
        super().__init__()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8000))
        self.server_socket.listen()

        self.clients = {}

        self.root = tk.Tk()
        self.root.title("Server GUI")

        self.clients_frame = tk.Frame(self.root)
        self.clients_frame.pack(side=tk.LEFT)

        self.commands_frame = tk.Frame(self.root)
        self.commands_frame.pack(side=tk.RIGHT)

        self.add_client_button = tk.Button(self.clients_frame, text="Add client", command=self.add_client)
        self.add_client_button.pack()
        self.send_command_button = tk.Button(self.commands_frame, text="Send command", command=self.send_command)
        self.send_command_button.pack()

        self.command_entry = tk.Entry(self.commands_frame)
        self.command_entry.pack()

        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            client_socket, address = self.server_socket.accept()
            client_name = f"Client {len(self.clients) + 1}"
            self.clients[client_name] = client_socket
            client_label = tk.Label(self.clients_frame, text=client_name)
            client_label.pack()

    def add_client(self):
        client_socket, address = self.server_socket.accept()
        client_name = f"Client {len(self.clients) + 1}"
        self.clients[client_name] = client_socket
        client_label = tk.Label(self.clients_frame, text=client_name)
        client_label.pack()

    def send_command(self):
        command = self.command_entry.get()
        for client_socket in self.clients.values():
            client_socket.sendall(command.encode())

    def run(self):
        self.root.mainloop()

gui = ServerGUI()
gui.run()