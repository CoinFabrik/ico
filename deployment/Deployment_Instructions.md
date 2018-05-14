# **Deployment Instructions**


## **Testing**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- You can run `./test.py` for general testing of the crowdsale, or make your own script and `import crowdsale_deployment` to deploy it.
- In [networks](networks.json) change the networks' information accordingly.
- Change configuration data if needed in [test_config](test_config.py)

### Deployment

- For Deployment: You can run `./crowdsale_deployment.py [-n NETWORK] [-p PROVIDER] [-t]` or `import crowdsale_deployment` from within a script of your own.
  - Options for NETWORK: {mainnet, ropsten, poanet}. Defaults to poanet.
  - Options for PROVIDER: {http, ws, ipc}. Defaults to http.
- For Configuration: You can run `./configurate.py [-n NETWORK] [-p PROVIDER] [-a ADDRESS] [-d DEPLOYMENT_NAME] [-t]`, or `import configurate` from within a script of your own or `from configurate import c` for getting only the parameters for the configuration. Make sure you pass the ADDRESS **or** the DEPLOYMENT_NAME as parameter.


## **MainNet**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- In [networks](networks.json) change the networks' information accordingly (host and port).
- Change configuration data if needed in [client_config](client_config.py)

### Deployment

- For Deployment: Run `./crowdsale_deployment.py [-n NETWORK] [-p PROVIDER]`.
  - Options for NETWORK: {mainnet, ropsten, poanet}. Defaults to poanet.
  - Options for PROVIDER: {http, ws, ipc}. Defaults to http.
  - You will be asked to enter the contract's name, the gas price and name of the deployment. The hash and the address will be printed.
- For Configuration: Run `./configurate.py [-n NETWORK] [-p PROVIDER] [-a ADDRESS] [-d DEPLOYMENT_NAME]`. Make sure you pass the ADDRESS **or** the DEPLOYMENT_NAME as parameter. 
  - You will be asked to enter the gas price and approve the configuration parameters.