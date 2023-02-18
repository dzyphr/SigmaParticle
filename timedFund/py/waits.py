import time
import os
from ergpy import helper_functions, appkit
def waitForBlockHeight(ergo, height, mod=None):
    if mod == None:
        mod = 0
    node_url = os.getenv('testnetNode') # MainNet or TestNet
    api_url = os.getenv('apiURL')
    currentHeight = ergo._ctx.getHeight()
    while height + mod >= currentHeight:
        print("deadline:", height + mod, ">=", "current_height:", currentHeight)
        time.sleep(40)
        newergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        currentHeight = newergo._ctx.getHeight()

