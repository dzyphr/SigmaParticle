import secrets
import hashlib
from ECC import *
import os
import time
import random
import jpype
from jpype import *
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
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    sender = senderAddress[0] #sender will be the one who generates the hash preimage
    castedSender = ergo.castAddress(senderAddress[0])
    senderPubK = Address.create(sender).getPublicKey()
    senderEIP3Secret = int( os.getenv('senderEIP3Secret'))
    receiverEIP3Secret = int(os.getenv('receiverEIP3Secret'))
    receiver = os.getenv('receiverAddress')
    castedReceiver = ergo.castAddress(receiver)
    receiverPubK = Address.create(receiver).getPublicKey()
    depositAmount = 50
    lockHeight = ergo._ctx.getHeight() + 3
    #ERGO ECC ADD point.add(point)
    #ERGO ECC MULTIPLY G dlogGroup().generator().multiply(scalar)
    message = "1000000000" #some public change output
    sha256 = hashlib.sha256()
    rs = random.randrange(0, curve.n)
    rsERGO = BigInteger(str(random.randrange(0, curve.n)))
    ks = random.randrange(0, curve.n)
    ksERGO = BigInteger(str(ks))
    rsG = dlogGroup().generator().multiply(rsERGO)
    ksG = scalar_mult(ks, curve.g)
    ksGERGO = dlogGroup().generator().multiply(ksERGO)
    print("\np1 picks secret randoms rs and ks and multiplies them by the curve generator and sends to p2")
    print("\nrs:", rs, "rsG:", rsG)
    print("\nks:", ks, "ksG:", ksG)
    rr = random.randrange(0, curve.n)
    rrERGO = BigInteger(str(rr))
    kr = random.randrange(0, curve.n)
    krERGO = BigInteger(str(kr))
    krGERGO = dlogGroup().generator().multiply(krERGO)
    krG = scalar_mult(kr, curve.g)
    rrG = scalar_mult(rr, curve.g)
    hashContent = message.encode() + str(ksGERGO.add(krGERGO)).encode()
    sha256.update(hashContent)
    e = int(sha256.digest().hex(), 16)
    eERGO = BigInteger(str(int(sha256.digest().hex(), 16)))
    print("e:", e)
    sr = kr + (e * rr)
    srERGO = BigInteger(str(sr))
    print("\np2 creates their multisig value sr:", sr)
    x = secrets.randbits(256)
    print("\np2 creates a 256bit secret preimage x:", x)
    srGERGO = dlogGroup().generator().multiply(srERGO)#sr is on ERGO
    srG = scalar_mult(sr, curve.g)
    xG = scalar_mult(x, curve.g)#x is on EVM chain
    print("srG:", srG)
    print("\np2 multiplies the preimage by secp256k1 generator G to get xG:", xG)
    sr_ = sr + x
    print("\np2 computes a partial equation for p1 sr_ = sr - x. \n\nsr:", sr_)
    print("\np2 sends sr_ and xG along with srG to p1")
    #end p2 activity
    #start p1 activity
    check = add_points(srG, xG) #P1 CHECKS WITH ECC
    sr_G = scalar_mult(sr_, curve.g)
    print("\np1 checks that srG + xG == sr_G", check, "==", sr_G, "and that xG are locking funds in contract")
    assert(check == sr_G, "check != sr_G")
    #p1 also check that xG is locking up funds
    #if so p1 locks their coins into a box that requires (sr + ss, krG + ksG) to spend or can redeem after lockheight
    print("\np1 locks funds to contract that checks that the inputed sr and ss are == to srG and ssG as well as include krG and ksG in the second half of the conditions")
    ss = ks + e * rs
    ssERGO = BigInteger(str(ss))
    print("\np1 computes their part of the signature ss = ks + e * rs:", ss, "and sends result to p2" )
    ssG = scalar_mult(ss, curve.g)
    ssGERGO = dlogGroup().generator().multiply(ssERGO)
    print("create ergo script locked to ", srGERGO, ssGERGO, krGERGO, ksGERGO)
    AtomicScript = \
            "{val ss = SELF.R4[BigInt].get} {val sr = SELF.R5[BigInt].get} {val _ksG = SELF.R6[GroupElement].get} {val _krG = SELF.R7[GroupElement].get} {sigmaProp(receiver && dlogGroup.generator.multiply(ss) == ssG && dlogGroup.generator.multiply(sr) == srG && _ksG == ksG && _krG == krG)}"
    cb = ConstantsBuilder.create()

    AtomicContract = ergo._ctx.compileContract(cb.item("receiver", receiverPubK).item("sender", senderPubK).item("ssG", ssGERGO).item("srG", srGERGO).item("krG", krGERGO).item("ksG", ksGERGO).item("lockHeight", lockHeight).build(), AtomicScript)
    tb = ergo._ctx.newTxBuilder()
    atomicLockBox = tb.outBoxBuilder().value(depositAmount * Parameters.OneErg + Parameters.MinFee).contract(AtomicContract).build()
    







    '''
    ss = ks + e * rs
    print("\np1 computes their part of the signature ss = ks + e * rs:", ss, "and sends result to p2" )
    ssG = scalar_mult(ss, curve.g)
    print("ss:", ss, "ssG", ssG)
    #p1 sends e and ss to p2
    #end p1 activity
    #start p2 activity
    sr = kr + e * rr
    print("\np2 computes their part of the signature sr = kr + e *rr:", sr)
    Q = sr + ss
    print("\nthe contract can check for the combined sig:", Q, "obtained by doing assert([input]ss*G + sr*G == [spending condition]ssG + srG)")

    #p2 claims with Q which implicitly broadcasts the value of Q on chain, they also use krG and ksG as 2nd half of the sig
    #end p2 activity
    #start p1 activity
    print("\np1 sees that p2 broadcasted Q on chain and can then use it to compute sr")
    p1sr = Q - ss
    print("\nsr:", sr,"==", "p1sr:", p1sr)
    assert(sr == p1sr)
    p1x = sr_ - sr #p1 discovers x this way
    print("\np1 discovers sr_ - sr = x", p1x)
    assert(p1x == x)
    print("p1 can now spend value locked to hash/public pair xG with x and their signature")
    #p1 can now spend value locked to hash xG with x and their signature
    #end atomic swap
    '''






    

























#   testPoint = ECPoint.getInstance(java.math.BigInteger("39060997197745157058762928031222231134846049427130642227436188562396358129972"), java.math.BigInteger("39060997197745157058762928031222231134846049427130642227436188562396358129972"))
    
    srGx = BigInteger("97647752661427826410974688393180336368548694536803785018906672917340715918188") #DOUBLE CHECK BIGINTS !!!
    srGy = BigInteger("101418408571438157600997957708631538565383173915608244268740934935529141489124")
    srG = ErgoValue.of(dlogGroup().curve().createPoint(srGx, srGy))
    print(srG)
#    srGGE = dlogGroup().curve().createPoint(srG.getValue().value().getXCoord().toBigInteger(), srG.getValue().value().getYCoord().toBigInteger())

    #x = point.getXCoord().toBigInteger()
    #y = point.getYCoord().toBigInteger()

