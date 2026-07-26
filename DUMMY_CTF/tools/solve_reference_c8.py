"""Reference solver C8 — Invalid Curve Attack, as a student would."""
import base64,json,math
from functools import reduce
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
HKDF_INFO=b"kapitel-02-dh-aead-v1"
EXPECT="hiy{invalid_curve_bob_forgot_to_check_the_point_cr7}"

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
    if Q is None: return 0
    m=int(math.isqrt(n))+1; table={}; R=None
    for j in range(m):
        if R not in table: table[R]=j
        R=ec_add(a,p,R,G)
    nmG=neg(p,ec_mul(a,p,m,G)); gamma=Q
    for i in range(m):
        if gamma in table: return i*m+table[gamma]
        gamma=ec_add(a,p,gamma,nmG)
    return None
def crt(res,mod):
    N=reduce(lambda x,y:x*y,mod); x=0
    for r,m in zip(res,mod):
        Ni=N//m; x+=r*Ni*pow(Ni,-1,m)
    return x%N
def on_curve(a,b,p,P):
    x,y=P; return (y*y-(x*x*x+a*x+b))%p==0

import time
for idx in range(3):
    c=parse(f"custom/assets/0200/{idx}/challenge_8.tcvcap")
    a=int(c["CURVE_A"]); b=int(c["CURVE_B"]); p=int(c["CURVE_P"]); n=int(c["CURVE_ORDER_N"])
    nprobes=int(c["N_PROBES"])
    res=[]; mod=[]
    t=time.time()
    for i in range(nprobes):
        q=int(c[f"PROBE_{i}_Q"])
        P=(int(c[f"PROBE_{i}_PX"]),int(c[f"PROBE_{i}_PY"]))
        rx=int(c[f"PROBE_{i}_RX"]); ry=int(c[f"PROBE_{i}_RY"])
        R=None if (rx==0 and ry==0) else (rx,ry)   # (0,0) = point à l'infini = d≡0 mod q
        # d mod q via BSGS in the order-q subgroup (on curve E'(b'), same a)
        di=dlog_bsgs(a,p,P,R,q)
        res.append(di%q); mod.append(q)
    d=crt(res,mod)
    dt=time.time()-t
    # decrypt traffic on real curve: S = d * A_eph
    A_eph=(int(c["ALICE_EPH_AX"]),int(c["ALICE_EPH_AY"]))
    S=ec_mul(a,p,d,A_eph)
    nbytes=(p.bit_length()+7)//8
    key=HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=HKDF_INFO).derive(S[0].to_bytes(nbytes,"big"))
    nonce=base64.b64decode(c["RECORD_NONCE_B64"]); ct=base64.b64decode(c["RECORD_CIPHERTEXT_B64"])
    flag=json.loads(AESGCM(key).decrypt(nonce,ct,None))["flag"]
    # detection check: is PROBE_0 point on the real curve E?
    P0=(int(c["PROBE_0_PX"]),int(c["PROBE_0_PY"]))
    p0_on_E=on_curve(a,b,p,P0)
    ok=flag==EXPECT
    print(f"[{'OK ' if ok else 'FAIL'}] variante {idx}: {nprobes} sondes, CRT+BSGS={dt:.2f}s, "
          f"P0_sur_E={p0_on_E} (attendu False), flag_ok={ok}")
    if not ok: print("   got:",flag)
