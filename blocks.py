# blocks.py
import hashlib
import time
from typing import List, Optional
from dataclasses import dataclass, field
from torus_core import ledger, Parcel, claim_parcel, transfer_parcel, update_manifest, trade_parcels

# ------------------------
# Block Definition
# ------------------------
@dataclass
class Transaction:
    type: str               # "claim", "transfer", "manifest_update", "trade"
    data: dict              # payload for the transaction
    timestamp: float = field(default_factory=time.time)

@dataclass
class Block:
    index: int
    prev_hash: str
    timestamp: float = field(default_factory=time.time)
    transactions: List[Transaction] = field(default_factory=list)
    nonce: int = 0
    merkle_root: Optional[str] = None
    block_hash: Optional[str] = None

    def compute_merkle_root(self):
        # Simple concatenation hash for prototype
        tx_str = "".join(str(tx) for tx in self.transactions)
        return hashlib.blake2b(tx_str.encode(), digest_size=32).hexdigest()

    def compute_hash(self):
        block_header = f"{self.index}{self.prev_hash}{self.timestamp}{self.nonce}{self.merkle_root}"
        return hashlib.blake2b(block_header.encode(), digest_size=32).hexdigest()

# ------------------------
# Blockchain Definition
# ------------------------
class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(index=0, prev_hash="0")
        genesis.merkle_root = genesis.compute_merkle_root()
        genesis.block_hash = genesis.compute_hash()
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions: List[Transaction], nonce: int = 0):
        block = Block(
            index=len(self.chain),
            prev_hash=self.last_block.block_hash,
            transactions=transactions,
            nonce=nonce
        )
        block.merkle_root = block.compute_merkle_root()
        block.block_hash = block.compute_hash()
        if self.validate_block(block):
            self.chain.append(block)
            self.apply_transactions(block.transactions)
            return block
        else:
            return None

    # ------------------------
    # Basic Block Validation
    # ------------------------
    def validate_block(self, block: Block) -> bool:
        # Check previous hash
        if block.prev_hash != self.last_block.block_hash:
            print("Invalid prev_hash")
            return False
        # Check Merkle root
        if block.merkle_root != block.compute_merkle_root():
            print("Invalid merkle_root")
            return False
        # Add additional validation rules later (nonce, difficulty, signatures)
        return True

    # ------------------------
    # Apply Transactions to Ledger
    # ------------------------
    def apply_transactions(self, transactions: List[Transaction]):
        for tx in transactions:
            if tx.type == "claim":
                claim_parcel(**tx.data)
            elif tx.type == "transfer":
                transfer_parcel(**tx.data)
            elif tx.type == "manifest_update":
                update_manifest(**tx.data)
            elif tx.type == "trade":
                trade_parcels(**tx.data)