# -*- coding: utf-8 -*-

import json
import requests

from address import Address

from utils import dict_hash


def test_mine_api(port):
    response = requests.get("http://127.0.0.1:{}/mine".format(port))
    response.raise_for_status()
    return response.json()


def test_chain_api(port):
    response = requests.get("http://127.0.0.1:{}/chain".format(port))
    response.raise_for_status()
    return response.json()


def test_new_transaction_api(port):
    addr_a = Address('a')
    addr_b = Address('b')

    transaction_data = {
        "sender": addr_a.address,
        "recipient": addr_b.address,
        "amount": 10
    }

    transaction = {
        'sender': addr_a.address,
        'recipient': addr_b.address,
        'amount': 10,
        'signature': addr_a.signature(dict_hash(transaction_data)),
        'public_key': addr_a.public_key
    }
    response = requests.post("http://127.0.0.1:{}/transactions/new".format(port), json=json.dumps(transaction))
    response.raise_for_status()
    return response.json()


def test_register_node_api(port):
    neighbours = {
        "nodes": [
            "http://127.0.0.1:5000",
        ]
    }

    response = requests.post("http://127.0.0.1:{}/nodes/register".format(port), json=json.dumps(neighbours))
    response.raise_for_status()
    return response.json()


def test_resolve_conflicts_api(port):
    response = requests.get("http://127.0.0.1:{}/nodes/resolve".format(port))
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    test_new_transaction_api(5000)
    test_mine_api(5000)
    print(test_chain_api(5000))
    print("------------------")
    test_register_node_api(5001)
    print(test_chain_api(5001))
    print("------------------")
    test_resolve_conflicts_api(5001)
    print(test_chain_api(5001))
