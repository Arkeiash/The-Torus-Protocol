# network.py
import threading
import time
from typing import List
from blocks import Blockchain, Block, Transaction

# ------------------------
# Node Definition
# ------------------------
class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.peers: List[Node] = []

    # Connect to another node
    def connect_peer(self, peer_node: 'Node'):
        if peer_node not in self.peers:
            self.peers.append(peer_node)
            peer_node.peers.append(self)

    # Broadcast a block to all peers
    def broadcast_block(self, block: Block):
        for peer in self.peers:
            peer.receive_block(block)

    # Receive a block from a peer
    def receive_block(self, block: Block):
        if self.blockchain.validate_block(block):
            self.blockchain.chain.append(block)
            self.blockchain.apply_transactions(block.transactions)

    # Mine a new block (prototype PoW)
    def mine_block(self, transactions: List[Transaction], difficulty: int = 1):
        nonce = 0
        while True:
            block = Block(
                index=len(self.blockchain.chain),
                prev_hash=self.blockchain.last_block.block_hash,
                transactions=transactions,
                nonce=nonce
            )
            block.merkle_root = block.compute_merkle_root()
            block_hash = block.compute_hash()
            # Simple difficulty: block_hash must start with '0' * difficulty
            if block_hash.startswith('0' * difficulty):
                block.block_hash = block_hash
                self.blockchain.add_block(transactions, nonce=nonce)
                print(f"[{self.node_id}] Mined block {block.index} with nonce {nonce}")
                self.broadcast_block(block)
                break
            nonce += 1

# ------------------------
# Example: network simulation
# ------------------------
if __name__ == "__main__":
    # Create nodes
    node_a = Node("NodeA")
    node_b = Node("NodeB")
    node_c = Node("NodeC")

    # Connect peers
    node_a.connect_peer(node_b)
    node_b.connect_peer(node_c)

    # Simulate a transaction
    tx1 = Transaction(type="claim", data={"block_header":"header1","pubkey":"pubA","manifest_cid":"cidA"})
    tx2 = Transaction(type="claim", data={"block_header":"header2","pubkey":"pubB","manifest_cid":"cidB"})

    # Start mining in threads
    threading.Thread(target=node_a.mine_block, args=([tx1], 1)).start()
    threading.Thread(target=node_b.mine_block, args=([tx2], 1)).start()

    # Let threads run a bit
    time.sleep(5)

    # Print ledgers
    print("\n--- NodeA Ledger ---")
    for idx, parcel in node_a.blockchain.chain[-1].transactions:
        print(parcel)