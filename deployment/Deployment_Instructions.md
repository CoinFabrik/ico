# **Deployment Instructions**


## **Testing**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- You can run `./test.py` for general testing of the crowdsale, or make your own script and `import crowdsale_deployment` to deploy it.
- In [networks](networks.py) change the networks' information accordingly.
- Change configuration data if needed in [test_config](test_config.py)

### Deployment

- For Deployment: You can run `./crowdsale_deployment.py -t` or `import crowdsale_deployment` from within a script of your own.
- For Configuration: You can run `./configurate.py (-a <address> or -d <deployment_name>) -t`, or `import configurate` from within a script of your own or `from configurate import c` for getting only the parameters for the configuration.


## **MainNet**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- In [networks](networks.py) change the networks' information accordingly.
- Change configuration data if needed in [client_config](client_config.py)

### Deployment

- For Deployment: Run `./crowdsale_deployment.py -n mainnet`.
  - You will be asked to enter the contract's name, the gas price and name of the deployment.
- For Configuration: Run `./configurate.py -n mainnet (-a <address> or -d <deployment_name>)`
  - You will be asked to enter the gas price and approve the configuration parameters.