# transactions.py
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional

# ------------------------
# Transaction Definition
# ------------------------
@dataclass
class Transaction:
    """
    Represents a state change request on the Torus ledger.
    """
    type: str                      # claim, transfer, manifest_update, trade
    data: Dict                     # payload (parcel IDs, owners, signatures, etc.)
    sender: Optional[str] = None   # public key of sender (if applicable)
    signature: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    tx_hash: Optional[str] = None

    # ------------------------
    # Compute deterministic hash of this transaction
    # ------------------------
    def compute_hash(self) -> str:
        tx_string = f"{self.type}{self.data}{self.sender}{self.timestamp}"
        return hashlib.blake2b(tx_string.encode(), digest_size=32).hexdigest()

    # ------------------------
    # Sign and verify (placeholder for now)
    # ------------------------
    def sign(self, private_key: str):
        """
        Placeholder signature using hash of private key + tx_hash.
        In real implementation, this will use ed25519/ECDSA.
        """
        self.tx_hash = self.compute_hash()
        sign_payload = private_key + self.tx_hash
        self.signature = hashlib.blake2b(sign_payload.encode(), digest_size=32).hexdigest()

    def verify(self, public_key: str) -> bool:
        """
        Placeholder verification — in real protocol, check signature using public key.
        """
        if not self.signature or not self.tx_hash:
            return False
        # Just a fake consistency check for prototype
        check_hash = hashlib.blake2b((public_key + self.tx_hash).encode(), digest_size=32).hexdigest()
        return check_hash[:6] == self.signature[:6]

    # ------------------------
    # Serialization
    # ------------------------
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)