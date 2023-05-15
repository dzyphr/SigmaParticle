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
 
    def boxVal(boxId):
        inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId)) 
        print(inputBox[0].getValue())

    if len(args) > 1:
        boxVal(args[1])
    else:
        print("enter boxId as argument")

