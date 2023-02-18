import ast
import subprocess
import time
import hashlib
import jpype
from jpype import *
import java.lang
from ergpy import helper_functions, appkit
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    pinLockScript = "sigmaProp(INPUTS(0).R4[Coll[Byte]].get == blake2b256(OUTPUTS(0).R4[Coll[Byte]].get))"
    pinLockContract = ergo.compile_proxy_contract(pinLockScript)
    rawPin = "9728"
    hasher = hashlib.blake2b(digest_size=32)
    hasher.update(bytes(rawPin, 'utf-8'))
    hashedPin = hasher.digest()
    tb = ergo._ctx.newTxBuilder()
    ergoAmount = 1 #amount in ergos 1 = 1 erg
    largeinput_boxes = BoxOperations \
        .createForSender(ergo.castAddress(senderAddress[0]), ergo._ctx) \
        .withAmountToSpend(jpype.JLong(Parameters.OneErg * ergoAmount)) \
        .withInputBoxesLoader(ExplorerAndPoolUnspentBoxesLoader()) \
        .loadTop()
    pinLockBox = tb.outBoxBuilder()  \
        .value(Parameters.OneErg * ergoAmount + Parameters.MinFee) \
        .registers( 
            [ \
                ErgoValue.of(hashedPin) \
            ] \
        ).contract(pinLockContract).build()
    depositTx = ergo.buildUnsignedTransaction(
       input_box=largeinput_boxes, outBox=[pinLockBox], 
       sender_address=ergo.castAddress(senderAddress[0])
    )
    WM = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
    depositTxSigned = ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(depositTx) 
    ergo.txId(depositTxSigned) #DEPOSIT CALL
    senderErgoTree = ErgoTreeContract(ergo.castAddress(senderAddress[0]).getErgoAddress().script(), ergo._networkType)
    pinBytes = scalaPipe.getBytes(rawPin) #important to grab the scala getBytes format, this function handles it
                                                    #view how the function works in py/scalaPipe.py
    withdrawBox = tb.outBoxBuilder().value(Parameters.OneErg * ergoAmount - Parameters.MinFee)  \
        .registers( 
            [ \
                ErgoValue.of(pinBytes ) \
            ] \
        ).contract(senderErgoTree).build()
    pinOut: InputBox = depositTxSigned.getOutputsToSpend(index_for_outbox=0)
    pinOut = coinSelection.pruneToIndex(0, pinOut)
    withdrawTx = ergo.buildUnsignedTransaction(
           input_box=pinOut, outBox=[withdrawBox],
           sender_address=ergo.castAddress(senderAddress[0]),
    )
    waits.waitForBlockHeight(ergo, ergo._ctx.getHeight(), 1)
    withdrawTxSigned =  ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(withdrawTx)
    ergo._ctx.sendTransaction(withdrawTxSigned) #WITHDRAW CALL
