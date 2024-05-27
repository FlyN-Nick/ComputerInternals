import argparse
from definitions import *

# guide for my custom assembly language: bitly/nra2130Assembly101

errors = [] # list of errors that occurred during the assembly process

def check_address(address: str, address_type: Input) -> bool:
    """Check if the inputted address is a valid register, ram address, or line number (to jump to)."""
    if not address[:2] == address_type:
        return False
    
    try:
        val = int(address[2:])
    except ValueError:
        return False

    return address_type.within_bounds(val)

def check_integer(number: str) -> bool:
    """Check if the inputted number is a valid integer literal."""
    try:
        val = int(number)
    except ValueError:
        return False
    return Input.INTGR.within_bounds(val)

def error(input: Operation | str, line_num: int, reason = "None") -> str:
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

        try:
            operation = inputs.pop(0)
        except IndexError:
            assembled_code.append(error("", line_num, "no operation"))
            continue

        try:
            operation = Operation(operation)
        except ValueError:
            assembled_code.append(error(operation, line_num, "invalid operation"))
            continue

        binary = operation.bnry

        expctd_amnt = len(operation.inputs)
        actl_amnt = len(inputs)
        if actl_amnt > expctd_amnt or actl_amnt < expctd_amnt:
            assembled_code.append(input_amount_error(line_num, expctd_amnt, actl_amnt))
            continue
        index = 0
        # the following for loop checks the validity of the inputs depending on the operation
        for input in inputs:
            input_type = operation.inputs[index]
            if input_type == Input.RG:
                binary += f'{int(input[2:]):04b}' if check_address(input, Input.RG) else error(input, line_num, "invalid register address")
            elif input_type == Input.INTGR:
                # https://stackoverflow.com/questions/63274885/converting-an-integer-to-signed-2s-complement-binary-string
                binary += f'{int(input) & ((1 << 16) - 1):016b}' if check_integer(input) else error(input, line_num, "invalid number")
            elif input_type == Input.LN:
                binary += f'{int(input[2:]):016b}' if check_address(input, Input.LN) else error(input, line_num, "invalid line number")
            elif input_type == Input.RM:
                binary += f'{int(input[2:]):08b}' if check_address(input, Input.RM) else error(input, line_num, "invalid ram address")
            elif input_type == Input.BTWSE:
                try:
                    input = Operation(input)
                    if not input.is_btwse_cmps_op():
                        raise ValueError
                    binary += input.bnry
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
