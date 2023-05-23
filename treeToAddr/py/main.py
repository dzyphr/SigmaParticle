import sys
import json
import requests
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
    
    def treeToAddr(tree, filepath=None):
        node = os.getenv('testnetNode')          
        url = node  + "utils/ergoTreeToAddress"
        headers = {\
            "accept": 'application/json',\
            "Content-type": 'application/json',\
            "api_key": os.getenv('testnetAPIKEY')
        }
        if tree.startswith("\"") == False:
            tree = "\"" + tree
        if tree.endswith("\"") == False:
            tree = tree + "\""
        data = str(tree)
        try:
            response = requests.post(url, headers=headers, data=data).text
            if filepath != None:
                f = open(filepath, "w")
                addr = json.loads(response)["address"]
                f.write(addr)
                f.close()
            else:
                print(response)
        except Exception as err:
            print("error getting address for: ", tree, "\nerror: ", err)


    if len(args) >= 2:
        if len(args) >= 3:
            treeToAddr(args[1], filepath=args[2])
            exit()
        treeToAddr(args[1])
        exit()
    else:
        print("enter tree [optional: filepath] as argument")
