#!/usr/bin/env python3
"""Standalone, self-checking verification for the export-cipher crypto engine.

No test framework is wired up in this repo, so this is a plain script: proves
the crafted TLS bytes for one variant are genuinely decryptable using only the
recovered RSA factors and the capture-visible wire bytes (never touching any
precomputed "expected" value directly), and sanity-checks the per-stage answer
comparators. Run manually:

    cd custom/challengebackend && python3 scripts/verify_export_cipher_crypto.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.export_cipher_crypto import decrypt_as_attacker
from utils.export_cipher_pool import (
    generate_variant, check_factor256, check_factor512, check_master_secret, check_flag,
)


def main():
    print("Generating variant #0 ...")
    variant = generate_variant(0)

    assert variant.n256 == variant.p256 * variant.q256
    assert variant.n512 == variant.p512 * variant.q512
    print(f"  256-bit N bit length: {variant.n256.bit_length()} "
          f"(p={variant.p256.bit_length()}b, q={variant.q256.bit_length()}b)")
    print(f"  512-bit N bit length: {variant.n512.bit_length()} "
          f"(p={variant.p512.bit_length()}b, q={variant.q512.bit_length()}b)")

    print("Decrypting as an attacker would (only p512, q512, and wire bytes) ...")
    recovered_master_secret, recovered_flag = decrypt_as_attacker(
        variant.client_flight_1, variant.server_flight_1, variant.client_flight_2, variant.server_flight_2,
        variant.p512, variant.q512,
    )

    assert recovered_master_secret == variant.master_secret, "master secret mismatch"
    assert recovered_flag == variant.flag.encode(), "flag mismatch"
    print(f"  Recovered master secret: {recovered_master_secret.hex()}")
    print(f"  Recovered flag: {recovered_flag.decode()}")

    print("Checking answer comparators ...")
    assert check_factor256(str(variant.p256), str(variant.q256), f"{variant.p256},{variant.q256}")
    assert check_factor256(str(variant.p256), str(variant.q256), f"{variant.q256}, {variant.p256}")
    assert not check_factor256(str(variant.p256), str(variant.q256), f"{variant.p256},{variant.p256}")
    assert check_factor512(str(variant.q512), str(variant.q512))
    assert not check_factor512(str(variant.q512), str(variant.p512))
    assert check_master_secret(recovered_master_secret.hex(), recovered_master_secret.hex().upper())
    assert not check_master_secret(recovered_master_secret.hex(), "00" * 48)
    assert check_flag(variant.flag, variant.flag)
    assert not check_flag(variant.flag, "crypto{wrong}")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
