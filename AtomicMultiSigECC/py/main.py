import secrets  
import numpy as np
import hashlib
import ECC
from ECC import *
import os
import json
import base64
import time
import random
import jpype
from jpype import *
import org.bouncycastle.math.ec.custom.sec
import org.ergoplatform
import scala
import scala.collection
import sigmastate
from sigmastate import SGroupElement
import sigmastate.basics
import sigmastate.serialization
import sigmastate.utils
import sigmastate.utxo
import special.sigma.GroupElement as GroupElement
from jpype import JProxy
import typing
import java.lang
from java.util import *;
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from org.bouncycastle.math.ec import *
from org.bouncycastle.math.ec.ECPoint import *
from sigmastate.interpreter.CryptoConstants import * ##
from java.math import BigInteger
from jpype import JClass
from java.math import BigInteger
from java.security import KeyPairGenerator, KeyPair, PublicKey
from java.security.spec import ECGenParameterSpec, ECPoint
from org.bouncycastle.math.ec.custom.sec import SecP256K1Curve, SecP256K1Point
from ergo_python_appkit.appkit import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
#    print("Running", contractName)
    curve = dlogGroup()
#    print("curveorder:",curve.order())
    javaBigIntegerMAX = 57896044618658097711785492504343953926634992332820282019728792003956564819968
    #ERGO ECC ADD point.add(point)
    #ERGO ECC MULTIPLY G dlogGroup().generator().multiply(scalar)
    message = "1000000000" #some public change output
    sha256 = hashlib.sha256()
    n =  int(str(curve.order()))
    g = ECC.curve.g
    rs = random.randrange(0, n)
    rs = rs % n
    rs = rs % javaBigIntegerMAX
    rsERGO = BigInteger(str(rs))
    ks = random.randrange(0, n)
    ks = ks % n
    ks = ks % javaBigIntegerMAX
    ksERGO = BigInteger(str(ks))
    rsGERGO = dlogGroup().generator().multiply(rsERGO).normalize()
    ksG = scalar_mult(ks, g)
    ksGERGO = dlogGroup().generator().multiply(ksERGO).normalize()
#    print("\np1 picks secret randoms rs and ks and multiplies them by the curve generator and sends to p2")
#    print("\nrs:", rs, "rsG:", rsGERGO)
    print("ksGX-ERGO:", int(str(ksGERGO.getXCoord().toBigInteger())),\
           "\nksGY-ERGO:", int(str(ksGERGO.getYCoord().toBigInteger())))
    rr = random.randrange(0, n)
    rr = rr % n
    rr = rr % javaBigIntegerMAX
    rrERGO = BigInteger(str(rr))
    kr = random.randrange(0, n)
    kr = kr % n
    kr = kr % javaBigIntegerMAX
    krERGO = BigInteger(str(kr))
    krGERGO = dlogGroup().generator().multiply(krERGO).normalize()
    print("\nkrGX-ERGO:", int(str(krGERGO.getXCoord().toBigInteger())), "krGY-ERGO:", int(str(krGERGO.getYCoord().toBigInteger())))
    krG = scalar_mult(kr, g)
    rrG = scalar_mult(rr, g)
    hashContent = message.encode() + str(ksGERGO.add(krGERGO)).encode()
    sha256.update(hashContent)
    e = int(sha256.digest().hex(), 16)
    e = e % n
    e = e % javaBigIntegerMAX
    eERGO = BigInteger(str(int(sha256.digest().hex(), 16)))
#    print("\ne:", e)
    sr = kr + (e * rr)
    def gen_sr(kr, e, rr):
        sr = kr + (e * rr)
        sr = sr % n
        sr = sr % javaBigIntegerMAX
        while sr > javaBigIntegerMAX:
            rr = random.randrange(0, n)
            sr = kr + (e * rr)
            sr = sr % n
            sr = sr % javaBigIntegerMAX
            if sr < javaBigIntegerMAX:
                return sr
            else: 
                continue
        return sr 
    sr = gen_sr(kr, e, rr)
    srERGO = BigInteger(str(sr))
    print("\np2 creates their multisig value sr:", sr)
    x = secrets.randbits(256)
    x = x % n
    x = x % javaBigIntegerMAX
    xERGO = BigInteger(str(x))
    print("\np2 creates a 256bit secret preimage x:", x)
    #xGERGO = dlogGroup().generator().multiply(xERGO).normalize()
    #print("\nxGXERGO:", xGERGO.getXCoord().toBigInteger(), "\nxGYERGO:", xGERGO.getYCoord().toBigInteger())
    srGERGO = dlogGroup().generator().multiply(srERGO).normalize()#sr is on ERGO
    srG = scalar_mult(sr, g)
    xG = scalar_mult(x, g)#x is on EVM chain
    print("xG:", xG)
    print("\nsrGX-ERGO:", int(str(srGERGO.getXCoord().toBigInteger())), "srGY-ERGO:", int(str(srGERGO.getYCoord().toBigInteger())))
    #print("\np2 multiplies the preimage by secp256k1 generator G to get xG:", xG)
    sr_ = sr + x
    sr_ = sr_  
 #   print("\np2 computes a partial equation for p1 sr_ = sr - x. \n\nsr_:", sr_)
 #   print("\np2 sends sr_ and xG along with srG to p1")
    check = add_points(srG, xG) #P1 CHECKS WITH ECC
    sr_G = scalar_mult(sr_, g)
   # print("\np1 checks that srG + xG == sr_G", check, "==", sr_G, "and that xG are locking funds in contract")
    assert(check == sr_G)
   # print("\np1 locks funds to contract that checks that the inputed sr and ss are == to srG and ssG as well as include krG and ksG in the second half of the conditions")
    ss = ks + e * rs
    ss = ss % n
    ss = ss % javaBigIntegerMAX
    ssERGO = BigInteger(str(ss))
    ssGERGO = dlogGroup().generator().multiply(ssERGO).normalize()
#    print("create ergo script locked to ", srGERGO, ssGERGO, krGERGO, ksGERGO)
 #   print("\np1 computes their part of the signature ss = ks + e * rs:", ss, "and sends result to p2" )
    print("\nss: ", ss)
#    print("ss:", ss, "ssGERGO", ssGERGO)
    print("\nssGX-ERGO:", int(str(ssGERGO.getXCoord().toBigInteger())), "ssGY-ERGO:", int(str(ssGERGO.getYCoord().toBigInteger())))
    #print("\np2 computes their part of the signature sr = kr + e *rr:", sr)
    Q = sr + ss
    #print("\nthe contract can check for the combined sig:", Q, "obtained by doing assert([input]ss*G + sr*G == [spending condition]ssG + srG)")
    #print("\np1 sees that p2 broadcasted Q on chain and can then use it to compute sr")
    p1sr = Q - ss
    #print("\nsr:", sr,"==", "p1sr:", p1sr)
    assert(sr == p1sr )
    p1x = sr_ - sr  #p1 discovers x this way
    #print("\np1 discovers sr_ - sr = x", p1x)
    assert(p1x == x)
    #print("p1 can now spend value locked to hash/public pair xG with x and their signature")






