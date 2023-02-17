import os
import time
import jpype
import random
from jpype import *
import java.lang
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
'''
This script uses these extra .env variables:
    senderEIP3Secret
    p2EIP3Secret
    p2Address
    p2Mnemonic
'''
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    senderEIP3Secret = int(os.getenv('senderEIP3Secret'))
    p2EIP3Secret = int(os.getenv('p2EIP3Secret'))
    p1 = Address.create(senderAddress[0]).getPublicKey()
    p2Address = os.getenv('p2Address')
    p2 = Address.create(p2Address).getPublicKey() #nautilus testnet addr 2
    depositAmount = 10
    timedFundScript = "p1 && sigmaProp(HEIGHT > deadline) || p2 && sigmaProp(HEIGHT <= deadline)" 
    #this script requires p1 to get a new instance of the appkit inorder for them to publish a valid signature when claiming 
    #p2 just needs to claim before the deadline (after at least one block confirmation of the timedFundTx) 
    #and doesn't need to update their local instance to sign for the block height..? 
    #that is my interpretation based on debugging and this is open to discussion. 
    deadline = ergo._ctx.getHeight() + 5
    cb = ConstantsBuilder.create()
    timedFundContract = ergo._ctx.compileContract(cb.item("p1", p1).item("p2", p2).item("deadline", deadline).build(), timedFundScript) #must run constantsBuilder.build() in here
    tb = ergo._ctx.newTxBuilder()
    timedFundBox = tb.outBoxBuilder().value(depositAmount * Parameters.OneErg + Parameters.MinFee).contract(timedFundContract).build()
    largeinput_boxesp1 = ergo.getInputBox(sender_address=ergo.castAddress(senderAddress[0]), amount_list=[depositAmount], tokenList=None)
    timedFundTxp1 = ergo.buildUnsignedTransaction(
        input_box=largeinput_boxesp1, outBox=[timedFundBox],
        sender_address=ergo.castAddress(senderAddress[0])
    )
    p1WM = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
    p2WM = ergo.getMnemonic(os.getenv('p2Mnemonic'))
    timedFundTxSignedp1 = ergo._ctx.newProverBuilder().withMnemonic(p1WM[0]).withEip3Secret(senderEIP3Secret).build().sign(timedFundTxp1)
    ergo.txId(timedFundTxSignedp1) #send initial funding tx
    p2Withdraws =True# bool(random.getrandbits(1)) #random bool
    if p2Withdraws == True:
        p2ErgoTree = ErgoTreeContract(ergo.castAddress(p2Address).getErgoAddress().script(), ergo._networkType)
        p2WithdrawBox = tb.outBoxBuilder().value(depositAmount * Parameters.OneErg - Parameters.MinFee).contract(p2ErgoTree).build()
        timedOutputsToSpend = timedFundTxSignedp1.getOutputsToSpend(index_for_outbox=0) #make sure to get this from starting party
        coinSelection.pruneToIndex(0, timedOutputsToSpend)
        p2WithdrawTx =  ergo.buildUnsignedTransaction(
            input_box=timedOutputsToSpend, outBox=[p2WithdrawBox],
            sender_address=ergo.castAddress(p2Address)
        )
        p2WM = ergo.getMnemonic(os.getenv('p2Mnemonic'))
        p2WithdrawTxSigned =  ergo._ctx.newProverBuilder().withMnemonic(p2WM[0]).withEip3Secret(p2EIP3Secret).build().sign(p2WithdrawTx)
        waits.waitForBlockHeight(ergo, ergo._ctx.getHeight()) #wait for ~one block
        print("\np2 attempting to withdraw\n") #if the deadline is one block and you wait one block this will fail
        ergo._ctx.sendTransaction(p2WithdrawTxSigned)
    else:
        waits.waitForBlockHeight(ergo, deadline) #waits for deadline + mod
        node_url = os.getenv('testnetNode') # MainNet or TestNet
        api_url = os.getenv('apiURL')
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        ergo._ctx
        p1ErgoTree = ErgoTreeContract(ergo.castAddress(senderAddress[0]).getErgoAddress().script(), ergo._networkType)
        p1WithdrawBox =  tb.outBoxBuilder().value(depositAmount * Parameters.OneErg - Parameters.MinFee).contract(p1ErgoTree).build()
        timedOutputsToSpend = timedFundTxSignedp1.getOutputsToSpend(index_for_outbox=0)
        coinSelection.pruneToIndex(0, timedOutputsToSpend)
        p1WithdrawTx = ergo.buildUnsignedTransaction(
                input_box=timedOutputsToSpend, outBox=[p1WithdrawBox],
            sender_address=ergo.castAddress(senderAddress[0])
        )
        prover = ergo._ctx.newProverBuilder().withMnemonic(p1WM[0]).withEip3Secret(senderEIP3Secret).build()
        p1WithdrawTxSigned =  prover.sign(p1WithdrawTx)
        print("\np1 attempting to withdraw\n")
        ergo._ctx.sendTransaction(p1WithdrawTxSigned)

        
