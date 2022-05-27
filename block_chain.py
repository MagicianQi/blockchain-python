# -*- coding: utf-8 -*-

import time
import ecdsa
import hashlib
import requests
import binascii

from typing import Any, Dict, List
from urllib.parse import urlparse

from utils import dict_hash, valid_proof


class Block:
    """
    记录区块信息
    """

    def __init__(self,
                 previous_hash: str,
                 version: str,
                 difficulty: float,
                 transactions: List[Dict[str, Any]]
                 ):
        self.transactions = transactions
        self.headers = {
            "previous_hash": previous_hash,
            "time_stamp": time.strftime("%Y-%m-%d %H:%M", time.localtime()),
            "version": version,
            "nonce": 0,
            "difficulty": difficulty,
            "merkle_root": self.merkle_root()
        }

    def proof_of_work(self):
        """
        工作量证明
        """
        nonce = 0
        while True:
            self.headers["nonce"] = nonce
            if valid_proof(self.headers):
                break
            nonce += 1
        self.headers.update({"nonce": nonce})

    def merkle_root(self):
        """
        计算交易的Merkle根
        """
        if len(self.transactions) == 0:
            return "0000000000000000000000000000000000000000000000000000000000000000"
        hash_list = [dict_hash(x) for x in self.transactions]
        while len(hash_list) > 1:
            last_hash = None
            # 如果是奇数个，则取出最后一个
            if len(hash_list) % 2 == 1:
                last_hash = hash_list.pop()
            # 将hash_list中的元素两两合并算哈希
            hash_list = [hashlib.sha256(
                (x + y).encode()).hexdigest() for x, y in zip(hash_list[0::2], hash_list[1::2])]

            if last_hash:
                hash_list.append(last_hash)
        return hash_list[0]

    def export(self):
        """
        导出区块信息
        """
        return {
            "headers": self.headers,
            "transactions": self.transactions
        }

    def __str__(self):
        return "{}".format(self.export())


class BlockChain:

    def __init__(self):
        self.chain = []
        self.transaction_pool = []
        self.neighbours = set()
        self.mining_block("0000000000000000000000000000000000000000000000000000000000000000")

    def mining_block(self, previous_hash: str):
        """
        挖矿并添加区块
        """
        block = Block(previous_hash,
                      "0x20e00000",
                      31251101365711.12,
                      self.transaction_pool)
        block.proof_of_work()
        self.chain.append(block.export())
        self.transaction_pool = []

    def add_transaction(self, data: Dict[str, Any], signature: str, public_key: str):
        """
        添加交易：
         - 验证交易的签名成功后，添加到交易池
        """
        if self.verify_signature(data, signature, public_key):
            self.transaction_pool.append({
                "data": data,
                "signature": signature,
                "public_key": public_key
            })

    @staticmethod
    def verify_signature(data: Dict[str, Any], signature: str, public_key: str) -> bool:
        """
        验证交易的签名
        """
        # 给矿工奖励的交易，实际不是这么做的
        if signature == "0" and public_key == "0":
            return True
        # 正常的交易
        message = dict_hash(data)
        model = ecdsa.VerifyingKey.from_string(binascii.unhexlify(public_key), curve=ecdsa.SECP256k1)
        try:
            return model.verify(binascii.unhexlify(signature), message.encode())
        except ecdsa.BadSignatureError:
            return False

    def add_neighbour(self, address: str) -> None:
        """
        添加一个节点
        """
        parsed_url = urlparse(address)
        self.neighbours.add(parsed_url.netloc)

    def resolve_conflicts(self) -> bool:
        """
        解决冲突，采用所有邻居节点中最长的链作为自己的链
        """
        neighbours = self.neighbours
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def valid_chain(chain: List[Dict]) -> bool:
        """
        验证区块链是否有效
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['headers']['previous_hash'] != dict_hash(last_block['headers']):
                return False

            if not valid_proof(block['headers']):
                return False

            last_block = block
            current_index += 1

        return True


if __name__ == '__main__':
    pass
