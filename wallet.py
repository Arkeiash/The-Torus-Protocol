# wallet.py
from ecdsa import SigningKey, SECP256k1

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def sign(self, message: str):
        return self.private_key.sign(message.encode()).hex()

    def get_address(self):
        return self.public_key.to_string().hex()