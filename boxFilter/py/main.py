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
    
    def txBoxFilter(address, boxId, filepath=None):
        node = os.getenv('testnetNode')          
        url = node  + "blockchain/transaction/byAddress"
        params = {\
                "limit": 5,\
                "offset": 0\
        }
        headers = {\
            "accept": 'application/json',\
            "Content-type": 'application/json',\
            "api_key": os.getenv('testnetAPIKEY')
        }
        data = str(address)
        response = requests.post(url, params=params, headers=headers, data=data).text
        j = json.loads(response)
        newBoxes = []
        newTxs = []
        for tx in j["items"]:
            if tx["outputs"][0]["boxId"] != boxId:
                newBoxes.append(tx["outputs"][0]["boxId"])
                newTxs.append(tx)
        NoneType = type(None)
        ext = "_tx"
        i = 1
        for tx in newTxs:
            if filepath == None:
                print(json.dumps(tx, indent=2))
            else:
                f = open(filepath + ext + str(i), "w")
                f.write(str(json.dumps(tx, indent=2)))
                f.close()
                i = i + 1

    if len(args) >= 3:
        if len(args) >= 4:
            txBoxFilter(args[1], args[2], filepath=args[3])
            exit()
        txBoxFilter(args[1], args[2])
        exit()
    else:
        print("enter address, boxId, [optional: filepath] as argument")
