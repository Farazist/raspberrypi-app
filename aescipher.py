import hashlib
import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        try:
            if len(enc) == 64:
                enc = base64.b64decode(enc)
                iv = enc[:16]
                cipher = AES.new(self.key, AES.MODE_CBC, iv)
                result = self.unpad(cipher.decrypt(enc[16:])).decode('utf8')
        except:
            result = 'QRCode is not valid'
        
        return result

    def unpad(self, s):
        return s[0:-ord(s[-1:])]

    def pad(self, s):
        return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')

