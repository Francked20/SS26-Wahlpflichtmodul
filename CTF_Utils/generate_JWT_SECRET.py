import secrets

def generate_jwt_secret(hex_length=256):
    """Erzeugt einen zufaelligen JWT_SECRET Hex-String"""
    if hex_length % 2 != 0:
        raise ValueError("hex_length muss eine gerade Zahl sein (2 Hex = 1 Byte).")

    # hex_length/2 Bytes → hex_length Hex-Zeichen
    return secrets.token_hex(hex_length // 2)

# Beispiel: 512 Hex-Zeichen (~256 Byte)
secret = generate_jwt_secret(256)
print(secret)
