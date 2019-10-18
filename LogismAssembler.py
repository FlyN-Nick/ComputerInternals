import numpy

# variables to check if inputs are within the limits 
rgst_min = 0
rgst_max = 15
rm_min = 0
rm_max = 255
ln_min = 0
ln_max = 65535
ornum_min = -65536
ornum_max = 65535

testing = False # default False, True if you are testing the test cases

casm_to_bnry = {  # commands, assembly to binary
  "_add_": "0000",
  "_sub_": "0001",
  "_grt_": "0010",
  "_eql_": "0011",
  "_jmp_": "0100",
  "_cjp_": "1111",
  "_rst_": "0101",
  "_rrd_": "0110",
  "_rcl_": "0111",
  "_and_": "1000",
  "_bor_": "1001",
  "_xor_": "1010",
  "_not_": "1011",
  "_rld_": "1100",
  "_rms_": "1101",
  "_inv_": "1110"
}

casm_to_input = {  # inputs for each command
  "_add_": ["num", "num", "rg"],
  "_sub_": ["num", "num", "rg"],
  "_grt_": ["num", "num", "rg"],
  "_eql_": ["num", "num", "rg"],
  "_jmp_": ["lineNum"],
  "_cjp_": ["lineNum", "num", "num", "btwse"], #btwse stands for bitwise operation
  "_rst_": ["rg", "ornum"],
  "_rrd_": ["rg", "rg"],
  "_rcl_": [],
  "_and_": ["num", "num", "rg"],
  "_bor_": ["num", "num", "rg"],
  "_xor_": ["num", "num", "rg"],
  "_not_": ["num", "rg"],
  "_rld_": ["rm", "rg"],
  "_rms_": ["rm", "rg"],
  "_inv_": ["num", "rg"]
}

zero_padding = { # the amount of zeros that needed to be added after the line when using this command
  "_add_": "0000000000000000",
  "_sub_": "0000000000000000",
  "_grt_": "0000000000000000",
  "_eql_": "0000000000000000",
  "_jmp_": "000000000000",
  "_cjp_": "",
  "_rst_": "00000000",
  "_rrd_": "00000000000000000000",
  "_rcl_": "0000000000000000000000000000",
  "_and_": "0000000000000000",
  "_bor_": "0000000000000000",
  "_xor_": "0000000000000000",
  "_not_": "00000000000000000000",
  "_rld_": "0000000000000000",
  "_rms_": "0000000000000000",
  "_inv_": "00000000000000000000"
}

errors = [] # this stores information about all the errors that occurs

anyErrors = False # whether or not there were any errors

alu_ops = ["_add_", "_sub_", "_grt_", "_eql_"] # ALU operations
btwse_ops = ["_and_", "_bor_", "_xor_", "_not_", "_inv_"] # bitwise operations
btwse_ops_special = ["_and_", "_bor_", "_xor_"] # bitwise operations that take in two inputs
rgst_ops = ["_rrd_", "_rst_", "_rcl_", "_rld_"] # register operations
rm_ops = ["_rms_"] # ram operations
jmp_ops = ["_jmp_", "_cjp_"] # jump operations
ops = [alu_ops, btwse_ops, rgst_ops, rm_ops, jmp_ops] # all the different operations

test_cases = {
"_add_ rg4 rg5 rg3": "Value",
"_sub_": "Error", # no inputs
"_cjp_ ln5 rg5 rg3 _and_": "Value",
"_cjp_ ln42069 rg15 rg0 _xor_": "Value",
"_cjp_ ln69420 rg15 rg16 _xor_": "Error", # too big of a line number
"_sub_ rm5": "Error", # too little inputs and wrong type of input
"_grt_ rg5 rg6": "Error", # too little inputs
"_eql_ rg1 rg0 rg2": "Value",
"_jmp_ ln": "Error", # missing a number after ln
"_rst_ rm5 00": "Error", # wrong type of input and 00 is not a valid number
"_rrd_ gr5 gr5": "Error", # wrong type of input (not even an input)
"_rcl_": "Value",
"_and_ rg5 rm5 gr4": "Error", # wrong type of input (not even an input)
"_bor_ rg5 rg9 rg11": "Value",
"_xor_ rm5 rg5 rg6": "Error", # wrong type of input
"_not_ rg5 rg4 rg3": "Error", # too many inputs
"_nat_ rg5 rg4": "Error", # not a valid operation
"_rld_ rm255 rg6": "Value",
"_rms_ rm256 rg 16": "Error", # numbers too large
"_inv_ rg15 rg14": "Value"
}

def checkCommand(command): # check assembly command validity
  value = False
  for i in ops:
    if command in i:
      value = True
      break 
  return value

def addressValidity(address, address_type): # check address validity
  try:
    int(''.join(address[2:]))
  except ValueError:
    return False
  if address_type == "rg":
    if not ''.join(address[0:2]) == "rg":
      return False
    if rgst_min <= int(''.join(address[2:])) and int(''.join(address[2:])) <= rgst_max:
      return True
    else:
      return False
  elif address_type == "rm":
    if not ''.join(address[0:2]) == "rm":
        return False
    if rm_min <= int(address[2:]) and int(address[2:]) <= rm_max:
      return True
    else:
      return False
  else:
    return False

def lineValidity(line): # check line number validity
  if not line[0:2] == "ln":
    return False
  try:
    int(line[2:])
  except ValueError:
    return False
  if int(line[2:]) >= ln_min and int(line[2:]) <= ln_max:
    return True
  else:
    return False

def numberValidity(number):# check number validity
  try:
    int(number)
  except ValueError:
    return False
  if int(number) >= ornum_min and int(number) <= ornum_max:
    return True
  else:
    return False

def error(command, line_num, reason = "None"): # to make an error
  errors.append("Line " + str(line_num) + " is invalid, because " + command + " is invalid. Specified Reason: " + reason)
  anyErrors = True
  return "ERROR"

def input_amount_error(line_num, expct_amnt, actl_amnt): # if there were too many or too little inputs for an operation
  # if statements because grammar
  if actl_amnt == 1:
    errors.append("Line " + str(line_num) + " is invalid, because there was {} input, but {} were expected.".format(actl_amnt, expct_amnt))
  elif expct_amnt == 1:
    errors.append("Line " + str(line_num) + " is invalid, because there are {} inputs, but {} was expected.".format(actl_amnt, expct_amnt))
  else:
    errors.append("Line " + str(line_num) + " is invalid, because there are {} inputs, but {} were expected.".format(actl_amnt, expct_amnt))
  anyErrors = True

if __name__ == '__main__': # the beginning of the actual code
  if testing:
    code = '\n'.join(test_cases.keys())
  else:
    code = input()
  sep_code = code.splitlines()
  assembledCode = []
  lineNum = 0

  for line in sep_code:
    lineNum = lineNum + 1
    commands = line.split()
    origCom = commands[0]
    commands.remove(origCom)

    binary_commands = numpy.empty(len(commands)+2, dtype=object) # +2 because the original command was removed and the last item is zero padding
    # binary_commands are the commands/inputs in the line represented as binary
    if checkCommand(origCom):
      binary_commands[0] = casm_to_bnry.get(origCom)
    else:
      binary_commands[0] = error(origCom, lineNum, "invalid operation")
      assembledCode.append("Error")
      continue
    
    # expctd_amnt is the number of inputs an operation (origCom) should have gotten
    expctd_amnt = len(casm_to_input.get(origCom))
    if len(commands) > expctd_amnt or len(commands) < expctd_amnt:
      input_amount_error(lineNum, expctd_amnt, len(commands))
      binary_commands[0] = "ERROR"
      assembledCode.append("Error")
      continue
    index = 0
    # the following for loop checks the validity of the inputs depending on the operation (origCom)
    # it checks for x input, for the operation, what type of input it should have gotten and whether or not it is satisfied
    for command in commands:
      input_type = (casm_to_input.get(origCom))[index]
      if input_type == "num" or input_type == "rg":
        if addressValidity(command, "rg"):
          binary_commands[index+1] = f'{int(command[2:]):04b}'
        else:
          binary_commands[index+1] = error(command, lineNum, "invalid register address")
      elif input_type == "ornum":
        if numberValidity(command):
          binary_commands[index+1] = f'{int(command):016b}'
        else:
          binary_commands[index+1] = error(command, lineNum, "invalid number")
      elif input_type == "lineNum":
        if lineValidity(command):
          binary_commands[index+1] = f'{int(command[2:]):016b}'
        else:
          binary_commands[index+1] = error(command, lineNum, "invalid line number")
      elif input_type == "rm":
        if addressValidity(command, "rm"):
          binary_commands[index+1] = f'{int(command[2:]):08b}'
        else:
          binary_commands[index+1] = error(command, lineNum, "invalid ram address")
      elif input_type == "btwse":
        if command in btwse_ops_special:
          binary_commands[index+1] = casm_to_bnry.get(command)
        else:
          binary_commands[index+1] = error(command, lineNum, "invalid bitwise operation")
      index = index + 1

    binary_commands[len(binary_commands)-1] = zero_padding.get(origCom) # zero padding is added to the end
    if not "ERROR" in binary_commands:
      if not testing:
        the_line = ''.join(binary_commands)
        assembledCode.append(hex(int(the_line, 2)))
      else:
        assembledCode.append("Value")
    else:
      assembledCode.append("Error")
  print("\n"+'\n'.join(errors))
  print("\nOutput: {}".format(assembledCode))
  if testing:
    expected_array = []
    for value in test_cases.values():
      expected_array.append(value)
    print("Expected output: \n{}".format(expected_array))
    if expected_array == assembledCode:
      print("\nTest Results: Assembler working properly")
    else:
      print("\nTest Results: Assembler working improperly")


