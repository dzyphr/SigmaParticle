## Sigma Particle

[![SigmaParticlePicture](https://d2r55xnwy6nx47.cloudfront.net/uploads/2016/11/1_no-glowing.jpg)](https://github.com/dzyphr/SigmaParticle)


**In Development**
# Stage: Alpha

#### Framework for working with the Ergo blockchain utilizing the Ergpy module

###### [Ergpy](https://github.com/mgpai22/ergpy)

 Uses .env file to modulate several parameters including secrets, based on linux filesystem only at the moment

#### Basic Usage:

######  run `./new_Frame yourContractNameHere`

######  `cd` to the contract folder

###### ** edit the `.env` hidden file with the following parameters: **

######  `testnetNode="http://127.0.0.1:9052/"` _if you arent running local node change this, whole project only tested with testnet at the moment_

######  `mnemonic="_your mnemonic seed phrase_"`

######  `mnemonicPass="_your mnemonic password_"` _IF YOU HAVE ONE! If you have one and don't use this transactions will fail_

######  `apiURL="https://tn-ergo-explorer.anetabtc.io/"` _explorer API url, feel free to use this one_

######  `localErgpy=`""  _True or false based on if you need functionality that was added into our local Ergpy repository. If false it will attempt to use an installed version from pip. To keep the repo small we will only ship modifications insead of the whole Ergpy repo. If using a modified ergpy repo just place it into the base folder, the same folder where the new_frame binary is_

######  There is 1 auto-generated variable named `ContractName` which occurs when you run `./new_Frame yourContractNameHere` at the start of the process. You could change this post-build at your own discretion. 

###### After that is set up, write your contract / transaction in `py/main.py` and deploy with `./deploy.sh`
