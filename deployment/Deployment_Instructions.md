# **Deployment Instructions**


## **Testing**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- You can run `./test.py` for general testing of the crowdsale, or make your own script and `import crowdsale_deployment` to deploy it.
- In the [web3 interface](web3_interface.py) change the provider if needed, and path or url if you are using IPCProvider or HTTPProvider respectively.
- Change configuration data if needed in [config](config.py)

### Deployment

- For Deployment: You can run `./crowdsale_deployment.py test` or `import crowdsale_deployment` from within a script of your own.
- For Configuration: You can run `./set_config.py test`, or `import set_config` from within a script of your own or `from set_config import params` for getting only the parameters for the configuration.


## **MainNet**:

### Before deployment

- Compile contract running `./recompile.sh`. It will make dir 'build' in the current directory 'deployment' and dump the output there.
- In the [web3 interface](web3_interface.py) change the provider if needed, and ipc_path or the URL if you are using IPCProvider or HTTPProvider respectively.
- Change configuration data in [config](config.py)

### Deployment

- For Deployment: Run `./crowdsale_deployment.py`.
  - You will be asked to enter the contract's name and the gas price for deployment.
- For Configuration: Run `./set_config.py`
  - You will be asked to enter the gas price for configuration, approve the configuration parameters and enter the name of the deployment.
