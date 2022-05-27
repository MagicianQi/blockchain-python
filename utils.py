
import json
import hashlib

from typing import Any, Dict


def dict_hash(dict_item: Dict[str, Any]):
    """
    计算字典的哈希值
    """
    block_string = json.dumps(dict_item, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def valid_proof(headers: Dict) -> bool:
    """
    验证工作量证明
    """
    guess_hash = dict_hash(headers)
    # 取前多少位为0，应该是难度确定的，为了维持10分钟一个区块
    if guess_hash[:4] == "0000":
        return True
    return False
