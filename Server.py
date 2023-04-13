import tkinter as tk
from tkinter import messagebox
import socket
import threading
import pickle
import time
import traceback

class Server:
    def __init__(self):
        self.host = 'localhost'
        self.port = 10223
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stopped = True
        self.clients = {}
        self.gui = None

    def start(self):
        self.gui = ServerGUI(self)
        self.gui.mainloop()

    def accept_clients(self):
        while not self.stopped:
            try:
                if self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except socket.error as e:
                print(f"Error accepting connection: {str(e)}")
                continue
            
    def handle_client(self, client_socket, client_address):
        client_data = client_socket.recv(1024)
        if client_data:
            client_data = pickle.loads(client_data)
            if client_data['type'] == 'register':
                self.clients[client_data['name']] = client_socket
                self.broadcast(f"{client_data['name']} has joined the chat!")
            elif client_data['type'] == 'message':
                self.broadcast(f"{client_data['name']}: {client_data['message']}")
            elif client_data['type'] == 'command':
                self.send_command(client_data['name'], client_data['command'])
            else:
                print(f"Unknown data received from {client_address}: {client_data}")

    def send_command(self, client_name, command):
        if client_name in self.clients:
            client_socket = self.clients[client_name]
            client_socket.sendall(pickle.dumps({'type': 'command', 'command': command}))
        else:
            print(f"No client found with name {client_name}")

    def stop(self):
        for client_socket in self.clients.values():
            client_socket.close()
        if self.server_socket is not None:
            self.server_socket.close()
        print("Server stopped")

class ServerGUI(tk.Tk):
    def __init__(self, server):
        super().__init__()
        self.title("Invasion")
        self.server = server
        self.geometry("400x400")
        self.resizable(False, False)

        # Start button
        self.start_button = tk.Button(self, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=20)

        # Stop button
        self.stop_button = tk.Button(self, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Client listbox
        self.client_listbox = tk.Listbox(self)
        self.client_listbox.pack(fill=tk.BOTH, expand=True)

    def start_server(self):
        try:
            self.server.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.server_socket.bind((self.server.host, self.server.port))
            self.server.server_socket.listen(5)
            threading.Thread(target=self.server.accept_clients).start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Server Started", f"Server started at {self.server.host}:{self.server.port}")
            self.update_client_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")

    def stop_server(self):
        self.server.stop()
        while not self.server.stopped:
            time.sleep(0.1)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_client_list()

    def update_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for client in self.server.clients:
            status = "Connected" if client.is_connected() else "Disconnected"
            self.client_listbox.insert(tk.END, f"{client.address[0]}:{client.address[1]} ({status})")
        self.after(10000, self.update_client_list())
        #Updates GUI Client List
def start_gui_update():
    gui.update_client_list()
    gui.after(10000, start_gui_update)

if __name__ == '__main__':
    server = Server()
    server.start()
    gui = ServerGUI(server)
    gui.after(10000, start_gui_update)
    gui.mainloop()

