import pickle
from encryption import EncryptionHandler

class ClientHandler:
    def __init__(self, command_queue, encryption_handler):
        self.command_queue = command_queue
        self.encryption_handler = encryption_handler
        self.public_key = None
        self.session_key = None

    def authenticate_client(self, client_socket):
        # Receive the public key from the client and send the server's public key
        self.public_key = self.encryption_handler.receive_public_key(client_socket)
        self.encryption_handler.send_public_key(client_socket)

        # Receive the encrypted session key from the client and decrypt it
        encrypted_session_key = client_socket.recv(1024)
        self.session_key = self.encryption_handler.decrypt_session_key(encrypted_session_key, self.public_key)

    def handle_commands(self, client_socket):
        # Set up the encryption handler for the session key
        session_encryption_handler = EncryptionHandler(self.session_key)

        try:
            while True:
                command_data = self.receive_command_data(client_socket, session_encryption_handler)
                if command_data is None:
                    break
                output_data = self.execute_command(command_data)
                self.send_output_data(output_data, client_socket, session_encryption_handler)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def receive_command_data(self, client_socket, encryption_handler):
        # Receive and decrypt the command data from the client
        encrypted_command_data = client_socket.recv(1024)
        if not encrypted_command_data:
            return None
        command_data = encryption_handler.decrypt_data(encrypted_command_data)
        command_data = pickle.loads(command_data)
        return command_data

    def execute_command(self, command_data):
        # Execute the command and return the output
        command = command_data['command']
        if command == 'upload':
            filename = command_data['filename']
            return self.upload_file(filename)
        elif command == 'download':
            filename = command_data['filename']
            return self.download_file(filename)
        else:
            return self.run_command(command_data)
    
    def upload_file(self, filename):
        encrypted_file_data = self.client_socket.recv(1024)
        file_data = self.encryption_handler.decrypt_data(encrypted_file_data, self.public_key)
        file_size = int.from_bytes(file_data[:4], byteorder='big')
        file_content = file_data[4:]
        while len(file_content) < file_size:
            encrypted_file_data = self.client_socket.recv(1024)
            decrypted_file_data = self.encryption_handler.decrypt_data(encrypted_file_data, self.public_key)
            file_content += decrypted_file_data

        with open(filename, 'wb') as f:
            f.write(file_content)
        
        return b'File Uploaded successfully'
    
    def download_file(self, filename):
        CHUNK_SIZE = 4096 # read file in 4kb Chunks
        try:
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    encrypted_chunk = self.encryption_handler.encrypt_data(chunk, self.public_key)
                    self.client_socket.send(encrypted_chunk)
            print(f'Successfully downloaded file {filename}')
        except FileNotFoundError:
            print(f'File not found: {filename}')
        except Exception as e:
            print(f'Error downloading file {filename}: {e}')
        return b''                    
