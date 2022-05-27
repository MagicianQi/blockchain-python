# -*- coding: utf-8 -*-

import ecdsa
import base58
import hashlib
import binascii


class Address:
    """
    按照比特币的地址规则生成地址
    """

    def __init__(self, random_string: str):
        self.private_key, self.public_key, self.address, others = self.generate(random_string)
        self.source_private_key, self.source_public_key, self.compressed_private_key, self.compressed_public_key = others

    @staticmethod
    def generate(random_string: str):
        """
        根据随机字符串生成私钥和公钥
        """
        # --------------------------generate keys--------------------------

        source_private_key = hashlib.sha256(random_string.encode()).hexdigest()
        source_private_key = bytes(source_private_key, 'utf-8')
        source_private_key_ascii = binascii.unhexlify(source_private_key)
        source_public_key_ascii = ecdsa.SigningKey.from_string(source_private_key_ascii,
                                                               curve=ecdsa.SECP256k1).get_verifying_key().to_string()
        source_public_key = binascii.hexlify(source_public_key_ascii)

        # --------------------------transfer private key--------------------------

        private_key = str(source_private_key, 'utf-8')
        # add version number
        private_key = "80" + private_key[:64]
        # Add 32 bit checksum
        checksum = hashlib.sha256(hashlib.sha256(private_key.encode()).digest()).hexdigest()[:8]
        compressed_private_key = private_key + checksum
        compressed_private_key = base58.b58encode(bytes.fromhex(compressed_private_key))

        # --------------------------transfer public key--------------------------

        public_key = str(source_public_key, 'utf-8')
        # 通过最后一个字符的奇偶来判断 y 的正负
        if int(public_key[-1], 16) % 2 == 0:
            compressed_public_key = "02" + public_key[:64]
        else:
            compressed_public_key = "03" + public_key[:64]

        public_key = "04" + public_key

        # --------------------------transfer address--------------------------

        hashed_public_key = hashlib.new('sha256', public_key.encode()).digest()
        encrypted_public_key = hashlib.new('ripemd160', hashed_public_key).hexdigest()
        # 增加主网标识
        encrypted_public_key = "00" + encrypted_public_key
        checksum = hashlib.sha256(hashlib.sha256(encrypted_public_key.encode()).digest()).hexdigest()[:8]
        encrypted_public_key = encrypted_public_key + checksum
        address = base58.b58encode(bytes.fromhex(encrypted_public_key))

        return private_key, public_key, address.decode(), (source_private_key, source_public_key, compressed_private_key, compressed_public_key)

    def signature(self, message: str) -> str:
        """
        使用生成的私钥对消息进行签名
        :param message: 需要签名的消息
        :return: 签名
        """
        model = ecdsa.SigningKey.from_string(binascii.unhexlify(self.source_private_key), curve=ecdsa.SECP256k1)
        return binascii.hexlify(model.sign(message.encode())).decode()

    def verify_signature(self, signature: str, message: str) -> bool:
        """
        验证签名
        :param signature: 签名
        :param message: 消息
        :return: 验证结果
        """
        model = ecdsa.VerifyingKey.from_string(binascii.unhexlify(self.source_public_key), curve=ecdsa.SECP256k1)
        try:
            return model.verify(binascii.unhexlify(signature), message.encode())
        except ecdsa.BadSignatureError:
            return False
