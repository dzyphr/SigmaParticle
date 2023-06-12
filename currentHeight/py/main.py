import os
import sys
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
    
    def height():
        sys.stdout.write(str(ergo._ctx.getHeight()))

    def height_filepath(filepath):
        height = str(ergo._ctx.getHeight())
        f = open(filepath, "w")
        f.write(height)
        f.close()



    if len(args) > 1:
        height_filepath(args[1])
    else:
        height()
