# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress,  ak = connect() #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, ak)

from cleanup import *
cleanup()

if __name__ == "__main__":
    main()
