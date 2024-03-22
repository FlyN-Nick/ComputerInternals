from enum import Enum
import argparse

# guide for my custom assembly language: bitly/nra2130Assembly101

# input kinds
class Inputs(Enum):
    RG = "rg" # register address
    RM = "rm" # ram address
    LN = "ln" # line number (for jumps)
    INTGR = "intgr" # integer literal
    BTWSE = "btwse" # comparison bitwise operation (for conditional jumps)

# operation kinds
class Operations(Enum):
    ADD = "_add_" # addition
    SUB = "_sub_" # subtraction
    GRT = "_grt_" # greater than (comparison)
    EQL = "_eql_" # equals to (comparison)
    JMP = "_jmp_" # jump
    CJP = "_cjp_" # conditional jump
    RST = "_rst_" # register set
    RRD = "_rrd_" # register read
    RCL = "_rcl_" # clear registers
    AND = "_and_" # bitwise and
    BOR = "_bor_" # bitwise or
    XOR = "_xor_" # bitwise xor
    NOT = "_not_" # bitwise not
    RLD = "_rld_" # register load (write from ram to register)
    RMS = "_rms_" # ram set (write to ram)
    INV = "_inv_" # bitwise invert (I have no idea how this is different from NOT)

# inclusive input bounds
RG_ADR_MIN = 0
RG_ADR_MAX = 2**4 - 1
RM_ADR_MIN = 0
RM_ADR_MAX = 2**8 - 1
LN_MIN = 0
LN_MAX = 2**16 - 1
INTGR_MIN = -(2**16)
INTGR_MAX = 2**16 - 1

# binary representations of each assembly operation
casm_to_bnry = {
    Operations.ADD: "0000",
    Operations.SUB: "0001",
    Operations.GRT: "0010",
    Operations.EQL: "0011",
    Operations.JMP: "0100",
    Operations.CJP: "1111",
    Operations.RST: "0101",
    Operations.RRD: "0110",
    Operations.RCL: "0111",
    Operations.AND: "1000",
    Operations.BOR: "1001",
    Operations.XOR: "1010",
    Operations.NOT: "1011",
    Operations.RLD: "1100",
    Operations.RMS: "1101",
    Operations.INV: "1110"
}

# inputs for each command
casm_to_input = {
    Operations.ADD: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.SUB: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.GRT: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.EQL: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.JMP: [Inputs.LN],
    Operations.CJP: [Inputs.LN, Inputs.RG, Inputs.RG, Inputs.BTWSE],
    Operations.RST: [Inputs.RG, Inputs.INTGR],
    Operations.RRD: [Inputs.RG, Inputs.RG],
    Operations.RCL: [],
    Operations.AND: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.BOR: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.XOR: [Inputs.RG, Inputs.RG, Inputs.RG],
    Operations.NOT: [Inputs.RG, Inputs.RG],
    Operations.RLD: [Inputs.RM, Inputs.RG],
    Operations.RMS: [Inputs.RM, Inputs.RG],
    Operations.INV: [Inputs.RG, Inputs.RG]
}

btwse_cmps_ops = [Operations.AND, Operations.BOR, Operations.XOR] # comparison bitwise operations, can be used in conditional jumps

errors = [] # list of errors that occurred during the assembly process

def checkAddress(address: str, address_type: Inputs) -> bool:
    """Check if the address is a valid register or ram address."""
    try:
        val = int(''.join(address[2:])) # first two characters are "rg" or "rm"
    except ValueError:
        return False

    kind = ''.join(address[:2])

    if address_type == Inputs.RG:
        return kind == Inputs.RG.value and (RG_ADR_MIN <= val and val <= RG_ADR_MAX)
    elif address_type == Inputs.RM:
        return kind == Inputs.RM.value and (RM_ADR_MIN <= val and val <= RM_ADR_MAX)
    else:
        return False

def lineValidity(line: str) -> bool:
    """Check if the line number is a valid line number to be jumped to."""
    if not line[:2] == Inputs.LN.value:
        return False
    try:
        val = int(line[2:])
    except ValueError:
        return False
    return val >= LN_MIN and val <= LN_MAX

def numberValidity(number: str) -> bool:
    """Check if the number is a valid integer literal."""
    try:
        val = int(number)
    except ValueError:
        return False
    return val >= INTGR_MIN and val <= INTGR_MAX

def error(input: Operations | str, line_num: int, reason = "None") -> str:
    """Error message creater for invalid operations."""
    errors.append(f"Line #{line_num} is invalid, because '{input}' is invalid. Specified reason: {reason}.")
    return "ERROR"

def input_amount_error(line_num: int, expct_amnt: int, actl_amnt: int) -> str:
    """Error message creater for an operation with too many or too few inputs."""
    # this looks ugly because I wanted the pluralization to be correct
    errors.append(f"Line #{line_num} is invalid, because there {'was' if actl_amnt == 1 else 'were'} {actl_amnt} input" \
        f"{'' if actl_amnt == 1 else 's'}, but {expct_amnt} {'was' if expct_amnt == 1 else 'were'} expected.")
    return "ERROR"


# test cases for the different aseembly operations, key is the command,
# value is "VALUE" if the command is valid or "ERROR" if the operation is invalid
test_cases = {
    "_add_ rg4 rg5 rg3": "VALUE",
    "_sub_": "ERROR", # no inputs
    "_cjp_ ln5 rg5 rg3 _and_": "VALUE",
    "_cjp_ ln12345 rg15 rg0 _xor_": "VALUE",
    "_cjp_ ln98765 rg15 rg16 _xor_": "ERROR", # too big of a line number
    "_sub_ rm5": "ERROR", # too few inputs and wrong type of input
    "_grt_ rg5 rg6": "ERROR", # too few inputs
    "_eql_ rg1 rg0 rg2": "VALUE",
    "_jmp_ ln": "ERROR", # missing an integer literal after ln
    "_rst_ rm5 00": "ERROR", # wrong type of input and 00 is not a valid integer literal
    "_rrd_ gr5 gr5": "ERROR", # wrong type of input (not even a valid input)
    "_rcl_": "VALUE",
    "_and_ rg5 rm5 gr4": "ERROR", # wrong type of input (not even a valid input)
    "_bor_ rg5 rg9 rg11": "VALUE",
    "_xor_ rm5 rg5 rg6": "ERROR", # wrong type of input
    "_not_ rg5 rg4 rg3": "ERROR", # too many inputs
    "_nat_ rg5 rg4": "ERROR", # not a valid operation
    "_rld_ rm255 rg6": "VALUE",
    "_rms_ rm256 rg 16": "ERROR", # ram adress is too large
    "_inv_ rg15 rg14": "VALUE"
}

parser = argparse.ArgumentParser(description='Assemble your assembly code into binary!')
parser.add_argument('-t','--test', help='run the test cases instead of assembling user input', required=False, action='store_true')
parser.add_argument('-i','--input', help='input text file to read multiple lines of assembly code', required=False)
parser.add_argument('-o','--output', help='output text file to write the multiple lines of assembled code to (default is output.txt)', required=False, default='output.txt')
args = vars(parser.parse_args())

if __name__ == "__main__":
    testing = args["test"]
    input_file = args["input"]
    assembly_code = []
    if testing:
        print("Running test cases...")
        for test_op in test_cases.keys():
            assembly_code.append(test_op)
    elif input_file:
        with open(input_file, "r") as f:
            assembly_code = f.readlines()
    else:
        print("Please enter your line of assembly code:", end=" ")
        assembly_code.append(input())

    assembled_code = [] # the final assembled code, each element is a line of binary code (as a string)
    line_num = 0

    for line in assembly_code:
        line_num += 1
        inputs = line.split()
        operation = inputs[0]
        inputs.pop(0)

        try:
            operation = Operations(operation)
        except ValueError:
            assembled_code.append(error(operation, line_num, "invalid operation"))
            continue

        binary = casm_to_bnry[operation]

        expected_inputs = casm_to_input[operation]
        expctd_amnt = len(expected_inputs)
        actl_amnt = len(inputs)
        if actl_amnt > expctd_amnt or actl_amnt < expctd_amnt:
            assembled_code.append(input_amount_error(line_num, expctd_amnt, actl_amnt))
            continue
        index = 0
        # the following for loop checks the validity of the inputs depending on the operation
        for input in inputs:
            input_type = expected_inputs[index]
            if input_type == Inputs.RG:
                binary += f'{int(input[2:]):04b}' if checkAddress(input, Inputs.RG) else error(input, line_num, "invalid register address")
            elif input_type == Inputs.INTGR:
                binary += f'{int(input):016b}' if numberValidity(input) else error(input, line_num, "invalid number")
            elif input_type == Inputs.LN:
                binary += f'{int(input[2:]):016b}' if lineValidity(input) else error(input, line_num, "invalid line number")
            elif input_type == Inputs.RM:
                binary += f'{int(input[2:]):08b}' if checkAddress(input, Inputs.RM) else error(input, line_num, "invalid ram address")
            elif input_type == Inputs.BTWSE:
                try:
                    input = Operations(input)
                    if input not in btwse_cmps_ops:
                        raise ValueError
                    binary += casm_to_bnry[input]
                except ValueError:
                    binary += error(input, line_num, "invalid bitwise operation")

            index += 1

        # length of binary code should be 32, we need to add zero padding if it's not
        padding = 32 - len(binary)
        binary += "0"*padding

        if not "ERROR" in binary:
            if not testing:
                assembled_code.append(hex(int(binary, 2)))
            else:
                assembled_code.append("VALUE")
        else:
            assembled_code.append("ERROR")

    print('\n'+'\n'.join(errors))
    print("\nOutput: {}".format(assembled_code))

    if input_file:
        with open(args["output"], "w+") as output:
            output.write("\nOutput: {}".format(assembled_code))

    if testing:
        expected_array = list(test_cases.values())
        print("Expctd: {}".format(expected_array))
        if expected_array == assembled_code:
            print("\nTest Results: Assembler working properly 😊")
        else:
            print("\nTest Results: Assembler working improperly 🫠")

