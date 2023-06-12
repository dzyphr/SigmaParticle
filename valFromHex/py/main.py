import os
import time
import random
import jpype
import sigmastate
from sigmastate.interpreter.CryptoConstants import *
from java.math import BigInteger
from jpype import *
import java.lang
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress, args):

    def intVal(hx, filepath=None):
        coll = ErgoValue.fromHex(hx).getValue()
        array = coll.toArray()
        decoded = BigInteger(array)
        if filepath is None:
            print(decoded)
        else:
            f = open(filepath, "w")
            f.write(str(decoded))
            f.close()


    if len(args) >= 2:
        if len(args) >= 3:
            intVal(args[1], filepath=args[2])
            exit()
        intVal(args[1])
        exit()
    else:
        print("enter hex, [optional: filepath] as argument") 





#0e200fe3ac722831c0e09e54f55ec842654d70ab97557af2758b598acfb802b7a7a0
