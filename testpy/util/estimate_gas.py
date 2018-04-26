def estimate_gas(functions, function_name, sender, *args, value=0):
  return functions[function_name](*args).estimateGas({'from': sender, 'value': value})