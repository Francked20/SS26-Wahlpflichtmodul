import os
from fastapi import APIRouter
from Crypto.Cipher import AES

router = APIRouter()

KEYS = [
    bytes.fromhex("00112233445566778899aabbccddeeff"),  # 00
    bytes.fromhex("112233445566778899aabbccddeeff00"),  # 01
    bytes.fromhex("2233445566778899aabbccddeeff0011"),  # 02
    bytes.fromhex("33445566778899aabbccddeeff001122"),  # 03
    bytes.fromhex("445566778899aabbccddeeff00112233"),  # 04
    bytes.fromhex("5566778899aabbccddeeff0011223344"),  # 05
    bytes.fromhex("66778899aabbccddeeff001122334455"),  # 06
    bytes.fromhex("778899aabbccddeeff00112233445566"),  # 07
    bytes.fromhex("8899aabbccddeeff0011223344556677"),  # 08
]

FLAGS = [
    "crypto{3cb_5uck5_4v01d_17_!!!!!}",
    "crypto{ecb_5uck5_4v01d_17_!!!!!}",
    "crypto{3cb_suck5_4v01d_17_!!!!!}",
    "crypto{3cb_5ucks_4v01d_17_!!!!!}",
    "crypto{3cb_5uck5_av01d_17_!!!!!}",
    "crypto{3cb_5uck5_4vo1d_17_!!!!!}",
    "crypto{3cb_5uck5_4v0id_17_!!!!!}",
    "crypto{3cb_5uck5_4v01d_i7_!!!!!}",
    "crypto{3cb_5uck5_4v01d_1t_!!!!!}",
]

def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len

@router.get("/{index}/decrypt/{ciphertext}/")
def decrypt(index: int, ciphertext: str):
    if index < 0 or index >= len(KEYS):
        return {"error": "invalid index"}
    key = KEYS[index]
    ct = bytes.fromhex(ciphertext)
    cipher = AES.new(key, AES.MODE_ECB)
    pt = cipher.decrypt(ct)
    return {"plaintext": pt.hex()}

@router.get("/{index}/encrypt_flag/")
def encrypt_flag(index: int):
    if index < 0 or index >= len(KEYS):
        return {"error": "invalid index"}
    key = KEYS[index]
    flag = FLAGS[index]
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_flag = pkcs7_pad(flag.encode())
    encrypted = cipher.encrypt(padded_flag)
    return {"ciphertext": iv.hex() + encrypted.hex()}
