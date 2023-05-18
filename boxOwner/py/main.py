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
 
    def boxOwner(boxId, filepath=None):
        if filepath == None:
            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))
            tree = ErgoTreeContract(inputBox[0].getErgoTree(),  ergo._networkType)
            print(tree.toAddress())
        else:
            f = open(filepath, "w")
            f.write(
                str(
                    ErgoTreeContract(\
                        java.util.Arrays.asList(\
                            ergo._ctx.getBoxesById(\
                                boxId\
                            )\
                        )[0].getErgoTree(), \
                        ergo._networkType
                    ).toAddress()\
                )\
            )
            f.close()

    if len(args) > 1:
        if len(args) > 2:
            boxOwner(args[1], args[2])
            exit()
        boxOwner(args[1])
        exit()

    else:
        print("enter boxId as argument")
