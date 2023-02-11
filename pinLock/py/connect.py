import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()
import sys 
if bool(os.getenv('localErgpy')) == True:
    sys.path.insert(0, '../ergpy') #prefer local version
from ergpy import appkit, helper_functions
def connect():
    load_dotenv()
    node_url = os.getenv('testnetNode') # MainNet or TestNet
    api_url = os.getenv('apiURL')
    ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
    wallet_mnemonic = os.getenv('mnemonic')
    mnemonic_password = os.getenv('mnemonicPass')
    if mnemonic_password != "":
        usingMnemonicPass = True
    else:
        usingMnemonicPass = False

    if usingMnemonicPass == True:
        #WITH MNEMONIC PASSWORD
        senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic, mnemonic_password=mnemonic_password)
    else:
        #WITHOUT MNEMONIC PASSWORD
        senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic)
    return ergo, wallet_mnemonic, mnemonic_password, senderAddress
