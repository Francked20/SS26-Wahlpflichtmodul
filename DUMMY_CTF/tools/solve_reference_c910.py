"""Reference solver C9 (ElGamal) + C10 (DSA) reused nonce."""
import base64,json,hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
HKDF_INFO=b"kapitel-02-dh-aead-v1"

def parse(path):
    d={}
    for line in open(path,encoding="utf-8"):
        line=line.strip()
        if not line or line.startswith("#"): continue
        if ":" in line:
            k,v=line.split(":",1); d[k.strip()]=v.strip()
    return d

def dec(val,nbytes,nonce_b64,ct_b64):
    key=HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=HKDF_INFO).derive(val.to_bytes(nbytes,"big"))
    return json.loads(AESGCM(key).decrypt(base64.b64decode(nonce_b64),base64.b64decode(ct_b64),None))["flag"]

C9="hiy{elgamal_nonce_reuse_two_ciphertexts_one_secret_a9f0}"
C10="hiy{dsa_nonce_reuse_ps3_style_private_key_recovery_beef}"

print("=== C9 ElGamal ===")
for idx in range(3):
    c=parse(f"custom/assets/0200/{idx}/challenge_9.tcvcap")
    p=int(c["PARAM_P"])
    m1=int(c["MESSAGE1_KNOWN_M1"]); c2_1=int(c["MESSAGE1_C2"]); c2_2=int(c["MESSAGE2_C2"])
    same_c1 = c["MESSAGE1_C1"]==c["MESSAGE2_C1"]     # detection: reused nonce
    m2=(c2_2*m1*pow(c2_1,-1,p))%p                     # recover m2
    nbytes=(p.bit_length()+7)//8
    flag=dec(m2,nbytes,c["RECORD_NONCE_B64"],c["RECORD_CIPHERTEXT_B64"])
    print(f"  [{'OK ' if flag==C9 else 'FAIL'}] var {idx}: same_c1={same_c1}, flag_ok={flag==C9}")

print("=== C10 DSA ===")
for idx in range(3):
    c=parse(f"custom/assets/0200/{idx}/challenge_10.tcvcap")
    q=int(c["PARAM_Q"])
    r=int(c["SIG1_R"]); s1=int(c["SIG1_S"]); s2=int(c["SIG2_S"])
    same_r = c["SIG1_R"]==c["SIG2_R"]
    h1=int.from_bytes(hashlib.sha256(c["SIG1_MESSAGE_UTF8"].encode()).digest(),"big")%q
    h2=int.from_bytes(hashlib.sha256(c["SIG2_MESSAGE_UTF8"].encode()).digest(),"big")%q
    k=((h1-h2)*pow((s1-s2)%q,-1,q))%q
    x=(((s1*k-h1)%q)*pow(r,-1,q))%q
    qbytes=(q.bit_length()+7)//8
    flag=dec(x,qbytes,c["RECORD_NONCE_B64"],c["RECORD_CIPHERTEXT_B64"])
    print(f"  [{'OK ' if flag==C10 else 'FAIL'}] var {idx}: same_r={same_r}, x_recovered=True, flag_ok={flag==C10}")
