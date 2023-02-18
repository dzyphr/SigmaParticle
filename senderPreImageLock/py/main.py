import hashlib
import os
import time
import random
import jpype
from jpype import *
import java.lang
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    sender = senderAddress[0]
    castedSender = ergo.castAddress(senderAddress[0])
    depositAmount = 1
    senderPreImageLockScript = "sender && sigmaProp(INPUTS(0).R4[Coll[Byte]].get == blake2b256(OUTPUTS(0).R4[Coll[Byte]].get))"
    preImage = os.getenv('senderPreImage') #make sure to set this .env variable, it can be any string! make sure it is large for real life use cases, as this can prevent even someone who stole your private key from spending the output!  (because they wont know the preImage, a small one like a pin or common password can be brute forced)
    hasher = hashlib.blake2b(digest_size=32)
    hasher.update(bytes(preImage, 'utf-8'))
    hashedPreImage =  hasher.digest()
    cb = ConstantsBuilder.create()
    senderPubK = Address.create(sender).getPublicKey()
    senderPreImageLockContract = ergo._ctx.compileContract(cb.item("sender", senderPubK).build(), senderPreImageLockScript)
    tb = ergo._ctx.newTxBuilder()
    senderPreImageLockBox = tb.outBoxBuilder().value(depositAmount * Parameters.OneErg + Parameters.MinFee).contract(senderPreImageLockContract).build()
    largeinput_boxes = ergo.getInputBox(sender_address=castedSender, amount_list=[depositAmount], tokenList=None)
    senderPreImageLockBox = tb.outBoxBuilder() \
        .value(Parameters.OneErg * depositAmount + Parameters.MinFee) \
        .registers(
        [ \
            ErgoValue.of(hashedPreImage) \
        ] \
        ).contract(senderPreImageLockContract).build()
    senderPreImageLockTx = ergo.buildUnsignedTransaction(
        input_box=largeinput_boxes, outBox=[senderPreImageLockBox],
        sender_address=ergo.castAddress(senderAddress[0])
    )
    WM = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
    senderPreImageLockTxSigned = ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(senderPreImageLockTx)
    ergo.txId(senderPreImageLockTxSigned) #DEPOSIT
    senderErgoTree = ErgoTreeContract(ergo.castAddress(senderAddress[0]).getErgoAddress().script(), ergo._networkType)
    preImageBytes = scalaPipe.getBytes(preImage)
    withdrawBox = tb.outBoxBuilder().value(Parameters.OneErg * depositAmount - Parameters.MinFee)  \
        .registers(
            [ \
                ErgoValue.of(preImageBytes ) \
            ] \
        ).contract(senderErgoTree).build()
    ioBox: InputBox = senderPreImageLockTxSigned.getOutputsToSpend(index_for_outbox=0)
    ioBox = coinSelection.pruneToIndex(0, ioBox)
    withdrawTx = ergo.buildUnsignedTransaction(
           input_box=ioBox, outBox=[withdrawBox],
           sender_address=ergo.castAddress(senderAddress[0]),
    )
    waits.waitForBlockHeight(ergo, ergo._ctx.getHeight(), 1)
    withdrawTxSigned =  ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(withdrawTx)
    ergo._ctx.sendTransaction(withdrawTxSigned) #WITHDRAW 
