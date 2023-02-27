import coincurve
from coincurve._libsecp256k1 import ffi, lib

### compat with secp256k1 python lib

class PublicKey:
    def __init__(self, pubkey=None, raw=False):
        self.cc = coincurve.PublicKey(pubkey) if pubkey else None
        self.__compressed = None

    def serialize(self, compressed=True):
        if compressed:
            if not self.__compressed:
                self.__compressed = self.cc.format(compressed=True)
            return self.__compressed
        else:
            return self.cc.format(compressed=False)
    
    def ecdh(self, scalar, hashfn=ffi.NULL, hasharg=ffi.NULL):
        priv = coincurve.PrivateKey(scalar)
        result = ffi.new('char [32]')
        res = lib.secp256k1_ecdh(
            priv.context.ctx, result, self.cc.public_key, priv.secret, hashfn, hasharg
        )
        if not res:
            raise Exception(f'invalid scalar ({res})')
        return bytes(ffi.buffer(result, 32))

    def schnorr_verify(self, msg, schnorr_sig, bip340tag, raw=False):
        assert bip340tag is None
        assert raw
        pk = coincurve.PublicKeyXOnly(self.serialize()[1:])
        try:
            return pk.verify(schnorr_sig, msg)
        except ValueError:
            return False

class PrivateKey:
    def __init__(self, privkey=None, raw=True):
        if not raw:
            self.cc = coincurve.PrivateKey.from_der(privkey)
        else:
            self.cc = coincurve.PrivateKey(privkey)

        self.pubkey = PublicKey()
        self.pubkey.cc = coincurve.PublicKey.from_valid_secret(self.cc.secret)

    def schnorr_sign(self, hash, bip340tag, raw=True):
        assert bip340tag is None
        assert raw
        return self.cc.sign_schnorr(hash)
