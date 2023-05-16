import sys
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
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress, args):
 
    def boxVal(boxId, filepath=None):
        if filepath == None:
            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))
    #       sys.stdout.write(str(inputBox[0].getValue()))
            print(str(inputBox[0].getValue()))
        else:
            value = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getValue()
            print(value)
            f = open(filepath, "w")
            f.write(str(value))
            f.close()

    if len(args) > 1:
        if len(args) > 2:
            boxVal(args[1], args[2])
            exit()
        boxVal(args[1])
        exit()

    else:
        print("enter boxId as argument")
