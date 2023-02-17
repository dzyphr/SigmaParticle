import time
import hashlib
import jpype
from jpype import *
import java.lang
from ergpy import helper_functions, appkit
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    pinLockScript = "sigmaProp(INPUTS(0).R4[Coll[Byte]].get == blake2b256(OUTPUTS(0).R4[Coll[Byte]].get))"
    pinLockContract = ergo.compile_proxy_contract(pinLockScript)
    userParty = senderAddress
    pinNumber = b'9728'
    
    hasher = hashlib.blake2b(digest_size=32)
    hasher.update(pinNumber)
    hashedPin = hasher.digest()
    
     
    print("pin:", pinNumber,  "\npinHash: ", hashedPin.hex())
    tb = ergo._ctx.newTxBuilder()
    ergoAmount = 2 #amount in ergos 1 = 1 erg
    print("ergo amount", ergoAmount)
    largeinput_boxes = ergo.getInputBox(sender_address=ergo.castAddress(senderAddress[0]), amount_list=[ergoAmount], tokenList=None)
    print(largeinput_boxes)
    collected_value = 0
    boxVals = []
    boxIndexes = []
    pinHashByteArray = bytearray(hashedPin.hex(), 'utf-8')
    pinHashByteInt = int(pinHashByteArray, 16)
    javaPinHashByteInt = jpype.JByte(pinHashByteInt)
    pinLockBox = tb.outBoxBuilder() \
        .value(Parameters.OneErg * ergoAmount) \
        .registers( \
                [ \
                    ErgoValue.of(pinHashByteArray) \
                ] \
        ).contract(pinLockContract).build()
    print("getval:", ErgoValue.of(hashedPin).getValue()) 
    print("outputValue:", pinLockBox.getValue())
    depositTx = ergo.buildUnsignedTransaction(
       input_box=largeinput_boxes, outBox=[pinLockBox],
       sender_address=ergo.castAddress(senderAddress[0])
    )
    WM = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
    depositTxSigned = ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(depositTx) #sign with prover index 0 because 1 party
    ergo.txId(depositTxSigned) #DEPOSIT CALL
    senderErgoTree = ErgoTreeContract(ergo.castAddress(senderAddress[0]).getErgoAddress().script(), ergo._networkType)
#    senderErgoTree = ErgoTreeContract(pinLockContract.getErgoTree(), ergo._networkType)

    JPin =  jpype.JByte(int(pinNumber.hex(), 16))
    print(JPin)
    withdrawBox = tb.outBoxBuilder().value(Parameters.OneErg * ergoAmount - Parameters.MinFee) \
            .registers( \
                [ \
                    ErgoValue.of(b'9728') \
                ] \
            ).contract(senderErgoTree).build()
    pinOut: InputBox = depositTxSigned.getOutputsToSpend(index_for_outbox=0)
    print(pinOut)
    print(withdrawBox.getValue())
    boxVals = []
    boxIndexes = []
    outVal = 0
    chosen = []
    pinOutFull = pinOut
    pinOutVals = []
    for i in pinOut:
        pinOutVals.append(i.getValue())
    while outVal < withdrawBox.getValue() + 10000000:
        outVal += max(pinOutVals)
        print(max(pinOutVals))
        pinOut.pop(pinOut.index(max(pinOutVals)))
    print(pinOut)
    withdrawTx = ergo.buildUnsignedTransaction(
           input_box=pinOut, outBox=[withdrawBox],
           sender_address=ergo.castAddress(senderAddress[0]),
    )
    withdrawTxSigned =  ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(0).build().sign(withdrawTx)
    ergo.txId(depositTxSigned) #WITHDRAW CALL
