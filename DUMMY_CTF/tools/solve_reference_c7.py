"""Reference solver for C7 — walks the generated ECDH capture as a student would."""
import base64, json, math
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HKDF_INFO = b"kapitel-02-dh-aead-v1"
EXPECT = "hiy{ecdh_small_curve_order_bsgs_on_the_curve_e11c}"

def parse(path):
    d={}
    for line in open(path,encoding="utf-8"):
        line=line.strip()
        if not line or line.startswith("#"): continue
        if ":" in line:
            k,v=line.split(":",1); d[k.strip()]=v.strip()
    return d

def ec_add(a,p,P,Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2 and (y1+y2)%p==0: return None
    if x1==x2 and y1==y2:
        if y1%p==0: return None
        lam=(3*x1*x1+a)*pow(2*y1,-1,p)%p
    else:
        lam=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(lam*lam-x1-x2)%p; y3=(lam*(x1-x3)-y1)%p
    return (x3,y3)

def ec_mul(a,p,k,P):
    R=None
    if k<0: k=-k; P=(P[0],(-P[1])%p)
    while k>0:
        if k&1: R=ec_add(a,p,R,P)
        P=ec_add(a,p,P,P); k>>=1
    return R

def neg(p,P): return None if P is None else (P[0],(-P[1])%p)

def dlog_bsgs(a,p,G,Q,n):
    m=int(math.isqrt(n))+1
    table={}; R=None
    for j in range(m):
        if R not in table: table[R]=j
        R=ec_add(a,p,R,G)
    nmG=neg(p,ec_mul(a,p,m,G)); gamma=Q
    for i in range(m):
        if gamma in table: return i*m+table[gamma]
        gamma=ec_add(a,p,gamma,nmG)
    return None

import time
for idx in range(3):
    c=parse(f"custom/assets/0200/{idx}/challenge_7.tcvcap")
    a=int(c["CURVE_A"]); b=int(c["CURVE_B"]); p=int(c["CURVE_P"]); n=int(c["CURVE_ORDER_N"])
    G=(int(c["GENERATOR_GX"]),int(c["GENERATOR_GY"]))
    A=(int(c["ALICE_PUBLIC_AX"]),int(c["ALICE_PUBLIC_AY"]))
    B=(int(c["BOB_PUBLIC_BX"]),int(c["BOB_PUBLIC_BY"]))
    t=time.time()
    a_sec=dlog_bsgs(a,p,G,A,n)        # ECDLP via BSGS
    dt=time.time()-t
    S=ec_mul(a,p,a_sec,B)            # secret partagé = a*B
    nbytes=(p.bit_length()+7)//8
    ikm=S[0].to_bytes(nbytes,"big")
    key=HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=HKDF_INFO).derive(ikm)
    nonce=base64.b64decode(c["RECORD_NONCE_B64"]); ct=base64.b64decode(c["RECORD_CIPHERTEXT_B64"])
    pt=AESGCM(key).decrypt(nonce,ct,None)
    flag=json.loads(pt)["flag"]
    ok = flag==EXPECT
    print(f"[{'OK ' if ok else 'FAIL'}] variante {idx}: curve_idx={idx%12} bits_p={p.bit_length()} bsgs={dt:.1f}s flag_ok={ok}")
    if not ok: print("   got:",flag)
