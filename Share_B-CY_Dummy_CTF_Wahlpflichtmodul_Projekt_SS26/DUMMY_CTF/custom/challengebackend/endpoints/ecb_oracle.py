import os
from fastapi import APIRouter
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

router = APIRouter()

KEYS = [
    bytes.fromhex("00112233445566778899aabbccddeeff"),
    bytes.fromhex("112233445566778899aabbccddeeff00"),
    bytes.fromhex("2233445566778899aabbccddeeff0011"),
    bytes.fromhex("33445566778899aabbccddeeff001122"),
    bytes.fromhex("445566778899aabbccddeeff00112233"),
    bytes.fromhex("5566778899aabbccddeeff0011223344"),
    bytes.fromhex("66778899aabbccddeeff001122334455"),
    bytes.fromhex("778899aabbccddeeff00112233445566"),
    bytes.fromhex("8899aabbccddeeff0011223344556677"),
    bytes.fromhex("99aabbccddeeff001122334455667788"),
]

FLAGS = [
    "crypto{p1n6u1n3_h4553n_3cb}",
    "crypto{pin6u1n3_h4553n_3cb}",
    "crypto{p1ngu1n3_h4553n_3cb}",
    "crypto{p1n6uin3_h4553n_3cb}",
    "crypto{p1n6u1ne_h4553n_3cb}",
    "crypto{p1n6u1n3_ha553n_3cb}",
    "crypto{p1n6u1n3_h4s53n_3cb}",
    "crypto{p1n6u1n3_h45s3n_3cb}",
    "crypto{p1n6u1n3_h455en_3cb}",
    "crypto{p1n6u1n3_h4553n_ecb}",
]

@router.get("/{index}/encrypt/{plaintext}/")
def encrypt(index: int, plaintext: str):
    """
    ECB Oracle: prepends the secret flag to user input and encrypts with AES-ECB.
    """
    if index < 0 or index >= len(KEYS):
        return {"error": "invalid index"}

    key = KEYS[index]
    flag = FLAGS[index]

    try:
        pt = bytes.fromhex(plaintext)
    except ValueError:
        return {"error": "plaintext must be hex-encoded"}

    # Flag wird hinten angehängt
    padded = pad(pt + flag.encode(), 16)
    cipher = AES.new(key, AES.MODE_ECB)

    try:
        encrypted = cipher.encrypt(padded)
    except ValueError as e:
        return {"error": str(e)}

    return {"ciphertext": encrypted.hex()}
