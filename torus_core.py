import hashlib
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math

WORLD_CAP = 4096  # total parcels in prototype
DIFFICULTY = 2**256 // 100_000  # toy difficulty for testing

@dataclass
class Parcel:
    index: int
    owner_pubkey: str
    manifest_cid: str

ledger: Dict[int, Parcel] = {}  # parcel_index -> Parcel

def hash_proof(block_header: str, pubkey: str, nonce: int) -> int:
    h = hashlib.blake2b(f"{block_header}{pubkey}{nonce}".encode(), digest_size=32).hexdigest()
    return int(h, 16)

def claim_parcel(block_header: str, pubkey: str, manifest_cid: str) -> Optional[Parcel]:
    nonce = 0
    while True:
        h = hash_proof(block_header, pubkey, nonce)
        if h < DIFFICULTY:
            parcel_index = h % WORLD_CAP
            if parcel_index not in ledger:
                parcel = Parcel(parcel_index, pubkey, manifest_cid)
                ledger[parcel_index] = parcel
                return parcel
        nonce += 1
        if nonce > 1_000_000:  # safety stop for prototype
            return None
def transfer_parcel(parcel_index: int, new_owner: str) -> bool:
    if parcel_index in ledger:
        ledger[parcel_index].owner_pubkey = new_owner
        return True
    return False

def uv_to_theta_phi(u: float, v: float) -> Tuple[float, float]:
    theta = 2 * math.pi * u  # wrap around main circle
    phi = 2 * math.pi * v    # wrap around tube
    return theta, phi

def update_manifest(parcel_index: int, new_cid: str) -> bool:
    if parcel_index in ledger:
        ledger[parcel_index].manifest_cid = new_cid
        return True
    return False

def trade_parcels(trade_offers: List[Tuple[str, List[int]]]) -> bool:
    # trade_offers = [(owner_pubkey, [parcel_index,...]), ...]
    # simplistic atomic check: all owners own their parcels
    for owner, parcels in trade_offers:
        for p in parcels:
            if p not in ledger or ledger[p].owner_pubkey != owner:
                return False
    # execute trade
    new_owners = [offer[0] for offer in trade_offers[::-1]]  # rotate owners
    for (owner, parcels), new_owner in zip(trade_offers, new_owners):
        for p in parcels:
            ledger[p].owner_pubkey = new_owner
    return True

def parcel_coordinates(parcel_index: int) -> Tuple[float, float]:
    root = math.sqrt(WORLD_CAP)
    u = (parcel_index % root) / root
    v = (parcel_index // root) / root
    return uv_to_theta_phi(u, v)

def print_ledger():
    for idx, parcel in ledger.items():
        print(f"Parcel {idx}: Owner={parcel.owner_pubkey}, CID={parcel.manifest_cid}")