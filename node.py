# -*- coding: utf-8 -*-

import json

from flask import Flask, jsonify, request

from block_chain import BlockChain
from address import Address

from utils import dict_hash

app = Flask(__name__)

# 模拟钱包地址
addr = Address("random string")

# 初始化本地区块链
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    transaction_data = {
            "sender": "0",
            "recipient": addr.address,
            "amount": 6
        }

    blockchain.add_transaction(
        data=transaction_data,
        signature="0",
        public_key="0"
    )
    last_block = blockchain.chain[-1]
    blockchain.mining_block(dict_hash(last_block['headers']))
    block = blockchain.chain[-1]

    response = {
        'message': "New Block Forged",
        'index': len(blockchain.chain),
        'transactions': block['transactions'],
        'proof': block['headers']['nonce'],
        'previous_hash': block['headers']['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = json.loads(request.get_json())

    # 检查POST数据
    required = ['sender', 'recipient', 'amount', 'signature', 'public_key']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction

    transaction_data = {
        "sender": values['sender'],
        "recipient": values['recipient'],
        "amount": values['amount']
    }
    blockchain.add_transaction(
        data=transaction_data,
        signature=values['signature'],
        public_key=values['public_key']
    )

    response = {'message': f'Transaction will be added to BlockChain'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [block for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = json.loads(request.get_json())

    nodes = values['nodes']
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.add_neighbour(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.neighbours),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
