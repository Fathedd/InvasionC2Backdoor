import os
import pickle
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP


class EncryptionHandler:
    def __init__(self):
        self.public_key, self.private_key = self.generate_key_pair()
        self.symmetric_key = os.urandom(32)

    def generate_key_pair(self):
        key = RSA.generate(2048)
        return key.publickey().export_key(), key.export_key()

    def get_public_key(self):
        return self.public_key

    def get_symmetric_key(self):
        return self.symmetric_key

    def encrypt_data(self, data, key=None):
        if key is None:
            key = self.symmetric_key
        cipher = AES.new(key, AES.MODE_CFB)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(data)
        return pickle.dumps((iv, encrypted_data))

    def decrypt_data(self, data, key=None):
        if key is None:
            key = self.symmetric_key
        iv, encrypted_data = pickle.loads(data)
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data

    def serialize_public_key(self):
        return self.public_key

    def deserialize_public_key(self, data):
        return RSA.import_key(data)

    def serialize_private_key(self):
        return self.private_key

    def deserialize_private_key(self, data):
        return RSA.import_key(data)

    def encrypt_symmetric_key(self, public_key):
        cipher_rsa = PKCS1_OAEP.new(public_key)
        encrypted_key = cipher_rsa.encrypt(self.symmetric_key)
        return encrypted_key

    def decrypt_symmetric_key(self, private_key, encrypted_key):
        cipher_rsa = PKCS1_OAEP.new(private_key)
        symmetric_key = cipher_rsa.decrypt(encrypted_key)
        return symmetric_key
