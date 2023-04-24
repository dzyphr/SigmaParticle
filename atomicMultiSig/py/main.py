import hashlib
import datetime
import random
import os
import time
import random
import choice
import jpype
from jpype import *
import java.lang
from sigmastate.interpreter.CryptoConstants import dlogGroup
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe 

'''
.env variables:
    senderEIP3Secret
    receiverEIP3Secret
    receiverAddress
    receiverMnemonic
'''

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
    # in practice this needs to be set as large as possible to encourage
    # the swap to happen optimistically and resist needing to resort to claiming the funds after time lock
    # it also makes it less likely that the other party will be able to delay the tx long enough to force a claim
    atomicLockScript = \
            "(sigmaProp(receiver && INPUTS(0).R4[Coll[Byte]].get == blake2b256(OUTPUTS(0).R4[Coll[Byte]].get))) || (sigmaProp(INPUTS(0).R4[Coll[Byte]].get == OUTPUTS(0).R4[Coll[Byte]].get && HEIGHT > lockHeight && sender))"
    minPreImage = pow(2, 64) #give a lower bound to prevent accidental small blinding value pre-images that could be quickly brute forced
    maxPreImage = pow(2, 256) #upper bound for preimage blinding value 
    randPreImage = random.randrange(minPreImage, maxPreImage) #here is our scalar random blinding value the most important part 
    
    currentBlockHeight = ergo._ctx.getHeight()
    currentHeightHex = hex(currentBlockHeight)[2:]
    time_stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    time_stamp_hex = hex(int(time_stamp))[2:]
    value = depositAmount * Parameters.OneErg
    valuehex = hex(value)[2:]
    messageScript = atomicLockScript.replace("receiver", receiver).replace("sender", sender).replace("lockHeight", str(lockHeight))
    messageScriptHex = messageScript.encode('utf-8').hex()
    publicMessage = currentHeightHex + time_stamp_hex + valuehex + messageScriptHex
    preImage = publicMessage + hex(randPreImage)[2:] #now we have a collision resistant value which includes a large scalar random
                                                
    hasher = hashlib.blake2b(digest_size=32)
    hasher.update(bytes(preImage, 'utf-8'))
    hashedPreImage =  hasher.digest()
    cb = ConstantsBuilder.create()
    atomicLockContract =  ergo._ctx.compileContract(cb.item("receiver", receiverPubK).item("sender", senderPubK).item("lockHeight", lockHeight).build(), atomicLockScript)
    tb = ergo._ctx.newTxBuilder()
    atomicLockBox = tb.outBoxBuilder() \
        .value(depositAmount * Parameters.OneErg + Parameters.MinFee) \
        .registers(
            [
                ErgoValue.of(hashedPreImage) #use the hashed pre image as the R4 value
            ]
        ).contract(atomicLockContract).build()
    largeinput_boxes = ergo.getInputBox(sender_address=castedSender, amount_list=[depositAmount], tokenList=None)
    WM = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
    senderAtomicLockTx = ergo.buildUnsignedTransaction(
        input_box=largeinput_boxes, outBox=[atomicLockBox],
        sender_address=castedSender
    )
    senderAtomicLockTxSigned = ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(senderEIP3Secret).build().sign(senderAtomicLockTx)
    ergo.txId(senderAtomicLockTxSigned) #DEPOSIT
    receiverWithdraws = bool(random.getrandbits(1)) #
    if receiverWithdraws == True:
        receiverErgoTree = ErgoTreeContract(castedReceiver.getErgoAddress().script(), ergo._networkType)
        receiverWithdrawBox = tb.outBoxBuilder() \
            .value(depositAmount * Parameters.OneErg - Parameters.MinFee) \
            .registers(
                [
                      ErgoValue.of(scalaPipe.getBytes(preImage)) #provide the preImage as bytes (get through pedersend commitment)
                ]
            ).contract(receiverErgoTree).build()
        atomicOutputsToSpend = senderAtomicLockTxSigned.getOutputsToSpend(index_for_outbox=0)
        coinSelection.pruneToIndex(0, atomicOutputsToSpend) 
        receieverWithdrawTx =  ergo.buildUnsignedTransaction(
            input_box=atomicOutputsToSpend, outBox=[receiverWithdrawBox],
            sender_address=castedReceiver
        )
        receiverWM = ergo.getMnemonic(os.getenv('receiverMnemonic')) 
        receiverWithdrawTxSigned = ergo._ctx.newProverBuilder().withMnemonic(receiverWM[0]).withEip3Secret(receiverEIP3Secret).build().sign(receieverWithdrawTx)
        waits.waitForBlockHeight(ergo, ergo._ctx.getHeight()) #wait for one block confirmation 
        print("receiver attempting to withdraw!")
        ergo._ctx.sendTransaction(receiverWithdrawTxSigned)
    elif receiverWithdraws == False:
        waits.waitForBlockHeight(ergo, lockHeight) #wait for the lock height 
        node_url = os.getenv('testnetNode') 
        api_url = os.getenv('apiURL')
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        senderErgoTree = ErgoTreeContract(castedSender.getErgoAddress().script(), ergo._networkType)
        senderWithdrawBox = tb.outBoxBuilder() \
            .value(depositAmount * Parameters.OneErg - Parameters.MinFee) \
            .registers(
                [
                    ErgoValue.of(hashedPreImage) #provide the hash as alt path for sender re-claiming un swapped coins
                ]
            ).contract(senderErgoTree).build()
        atomicOutputsToSpend = senderAtomicLockTxSigned.getOutputsToSpend(index_for_outbox=0)
        coinSelection.pruneToIndex(0, atomicOutputsToSpend)
        senderWithdrawTx = ergo.buildUnsignedTransaction(
            input_box=atomicOutputsToSpend, outBox=[senderWithdrawBox],
            sender_address=castedSender
        )
        senderWithdrawTxSigned = ergo._ctx.newProverBuilder().withMnemonic(WM[0]).withEip3Secret(senderEIP3Secret).build().sign(senderWithdrawTx)
        print("sender is re-claiming their funds because the receiver is not cooperating and block height", lockHeight, "was reached")
        ergo.txId(senderWithdrawTxSigned)









