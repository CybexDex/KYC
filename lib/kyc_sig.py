import json,cybex,config
from collections import OrderedDict
from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId
)
from graphenebase.objects import GrapheneObject, isArgsThisClass
from graphenebase.ecdsa import sign_message, verify_message
from graphenebase.account import PublicKey
import hashlib
from binascii import unhexlify, hexlify
cybex.cybex.cybex_debug_config(config.chain_id)
inst = cybex.Cybex(config.ws_conn)


class Tx(GrapheneObject):
    def __init__(self, *args, **kwargs):
    # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('account', String(kwargs["account"])),
            ])) 

def build_tx(account, WIF):
    op = Tx(**{
            'account': account,
        })
    message = bytes(op)
    digest = hashlib.sha256(message).digest()
    signature = Signature(sign_message(message, WIF))
    d = op.json()
    d['signature'] = hexlify(signature.data).decode('ascii')
    return d
def verify_tx(d):
    sig = d['signature']
    name = d['account']
    account = cybex.account.Account(name , cybex_instance = inst)
    del d['signature']
    op = Tx(**d)
    message = bytes(op)
    p = verify_message(message, unhexlify(sig))
    pkey = PublicKey(hexlify(p).decode('ascii'), prefix = 'CYB')
    print(str(pkey))
    _pubkey = account['active']['key_auths'][0][0]
    if str(pkey) == _pubkey:
        return True
    return False


if __name__ == '__main__':
    m = build_tx('sunxiaoqi-01', '5KWTrrQMyD7Ez62viB36r75ur9ZJ6DPu3qkSa2eDcpE99XfD8ye')
    print(m)
    res = verify_tx(m)
    print(res)
