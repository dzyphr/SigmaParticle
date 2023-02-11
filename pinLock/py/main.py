from ergpy import helper_functions, appkit
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress):
    print("Running", contractName)
    pinLockScript = "sigmaProp(INPUTS(0).R4[Coll[Byte]].get == blake2b256(OUTPUTS(0).R4[Coll[Byte]].get))"
    pinLockContract = ergo.compile_proxy_contract(pinLockScript)
    print(pinLockContract)
