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
from sigmastate.interpreter.CryptoConstants import *
import java.math.BigInteger
import scala.math.BigInt as BigInt
from java.math import BigInteger
interpreterClasspath = \
    "/home/" + os.getlogin() + "/Downloads/sigmastate-interpreter-5.0.7/target/scala-2.12/sigma-state_2.12-HEAD-20230423-1639.jar"
jpype.addClassPath(interpreterClasspath)
from sigmastate.eval.package import ecPointToGroupElement
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress, args):
    print("Running", contractName)
    def scalarLockDeposit():
        sender = senderAddress[0]
        castedSender = ergo.castAddress(senderAddress[0])
        senderPubkey = Address.create(sender).getPublicKey()
        senderWalletMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
        senderEIP3Secret = int(os.getenv('senderEIP3Secret'))
        senderProver = ergo._ctx.newProverBuilder().withMnemonic(senderWalletMnemonic[0]).withEip3Secret(senderEIP3Secret).build()
        ergoAmountRaw = 10
        ergoAmount = ergoAmountRaw * Parameters.OneErg#should be automated irl
        ergoAmountFeeIncluded = ergoAmount + Parameters.MinFee
        ECC_Generator = dlogGroup().generator().getEncoded(True)
        x = BigInteger(os.getenv('x'))
        xG = dlogGroup().generator().multiply(x)
        ScalarLockScript = \
        "\
            {\
            val xBYTES = OUTPUTS(0).R4[Coll[Byte]].get;\
            val x = byteArrayToBigInt(xBYTES);\
            val G = decodePoint(generator);\
              sigmaProp(\
                receiver &&\
                G.exp(x) == xG\
              )\
            }\
        "
        ScalarContract = ergo._ctx.compileContract( \
                ConstantsBuilder.create()\
                .item("receiver", senderPubkey)\
                .item("xG", xG)\
                .item("generator", ECC_Generator)\
                .build(),
                ScalarLockScript)
        inputBoxes =  ergo.getInputBox(sender_address=castedSender, amount_list=[ergoAmountRaw], tokenList=None)
        ScalarLockBox = ergo._ctx.newTxBuilder().outBoxBuilder() \
            .value(ergoAmountFeeIncluded) \
            .contract(ScalarContract)\
            .build()
        unsignedTx = ergo.buildUnsignedTransaction(\
            input_box = inputBoxes, outBox=[ScalarLockBox],\
            sender_address=castedSender\
        )
        signedTx = senderProver.sign(unsignedTx)
        print(ergo.txId(signedTx)) #DEPOSIT
        signedTxJSON = senderProver.sign(unsignedTx).toJson(True)
        print(signedTxJSON)

    def receiverClaim():
        sender = senderAddress[0] #sender is receiver for example
        receiver = Address.create(sender).getPublicKey()
        castedReceiver =  ergo.castAddress(sender)
        receiverEIP3 = int(os.getenv('senderEIP3Secret'))
        receiverMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
        receiverProver = ergo._ctx.newProverBuilder().withMnemonic(receiverMnemonic[0]).withEip3Secret(receiverEIP3).build()
        scalarBoxID = os.getenv('scalarBox')
        ergoAmount = Parameters.OneErg * 10
        ergoAmountFeeSubtracted = ergoAmount - Parameters.MinFee

        x = BigInteger(os.getenv('x'))
        xBYTES = BigInt.javaBigInteger2bigInt(x).toByteArray()
        ev_xBYTES = ErgoValue.of(xBYTES)
        receiverErgoTree = ErgoTreeContract(castedReceiver.getErgoAddress().script(), ergo._networkType)
        unlockBox = ergo._ctx.newTxBuilder().outBoxBuilder() \
            .value(ergoAmountFeeSubtracted) \
            .contract(receiverErgoTree)\
            .registers([ev_xBYTES])\
            .build() 
        inputBoxes = java.util.Arrays.asList(ergo._ctx.getBoxesById(scalarBoxID)) 
        unsignedTx = ergo.buildUnsignedTransaction(\
            input_box = inputBoxes, outBox=[unlockBox],\
            sender_address=castedReceiver\
        )
        signedTx = receiverProver.sign(unsignedTx)
        print(ergo.txId(signedTx)) #CLAIM
        signedTxJSON = receiverProver.sign(unsignedTx).toJson(True)
        print(signedTxJSON)

    if len(args) > 1:
        if args[1] == "deposit":
            scalarLockDeposit()
        elif args[1] == "receiverClaim":
            receiverClaim()
        else:
            print("unknown arg.\nchoices: deposit, receiverClaim")
    else:
        print("enter argument.\nchoices: deposit, receiverClaim")
