# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress= connect() #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress)

from cleanup import *
cleanup()


