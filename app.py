import time
import threading
from hashlib import sha256
from flask import Flask, jsonify, request, render_template

MAX_NONCE = 100000000000

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.mine_block()
        
    def SHA256(self, text):
        return sha256(text.encode("ascii")).hexdigest()
    
    def mine_block(self):
        target_letter = 'bee'  # Ethereum-like difficulty, looking for a hash starting with 'm'
        for nonce in range(MAX_NONCE):
            block_content = str(self.index) + str(self.transactions) + self.previous_hash + str(nonce)
            block_hash = self.SHA256(block_content)
            if block_hash.startswith(target_letter):
                self.nonce = nonce
                return block_hash
        raise Exception("Mining failed!")
    
    def __repr__(self):
        return f"Block(Index: {self.index}, Hash: {self.hash}, Nonce: {self.nonce}, Transactions: {self.transactions}, Timestamp: {self.timestamp})"


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
    
    def create_genesis_block(self):
        return Block(0, ["Genesis Block"], "0")
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        if "contract" in transaction.lower():
            self.execute_smart_contract(transaction)
    
    def execute_smart_contract(self, transaction):
        print(f"Executing smart contract for transaction: {transaction}")
    
    def mine_pending_transactions(self):
        while True:
            if self.pending_transactions:
                last_block = self.get_last_block()
                new_block = Block(last_block.index + 1, self.pending_transactions[:], last_block.hash)
                self.chain.append(new_block)
                self.pending_transactions = []
                print(f"\nNew block mined: {new_block}")
            else:
                print("No transactions to mine, waiting for more transactions...")
            
            time.sleep(12)  # Simulate Ethereum-like block interval (12 seconds)

# Initialize the blockchain
blockchain = Blockchain()

# Start mining thread in the background
mining_thread = threading.Thread(target=blockchain.mine_pending_transactions)
mining_thread.daemon = True  # Allows program to exit even if the thread is still running
mining_thread.start()

# Flask Web Application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Route to get all mined blocks
@app.route('/blocks', methods=['GET'])
def get_blocks():
    chain_data = []
    for block in blockchain.chain:
        block_info = {
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'hash': block.hash
        }
        chain_data.append(block_info)
    return jsonify({'chain': chain_data, 'length': len(blockchain.chain)}), 200

# Route to add a new transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    if not data or 'transaction' not in data:
        return jsonify({'message': 'Invalid transaction data!'}), 400

    transaction = data['transaction']
    blockchain.add_transaction(transaction)
    return jsonify({'message': f'Transaction added: {transaction}'}), 201

if __name__ == '__main__':
    app.run(debug=True)
