from definitions import Input, Operation
import argparse

# guide for my custom assembly language: bit.ly/nra2130Assembly101

errors = [] # list of string descriptions of errors that occurred during the assembly process

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
    """Check if the inputted number is a valid integer immediate."""
    try:
        val = int(number)
    except ValueError:
        return False
    return Input.INTGR.within_bounds(val)

def error(input: Operation | str, line_num: int, reason = "none") -> str:
    """Generic error message creator for invalid operations."""
    errors.append(f"Line #{line_num} is invalid, because '{input}' is invalid. Specified reason: {reason}.")
    return "ERROR"

def input_amount_error(line_num: int, expct_amnt: int, actl_amnt: int) -> str:
    """Specialized error message creator for an operation with too many or too few inputs."""
    # this looks ugly because I wanted the pluralization to be correct
    errors.append(f"Line #{line_num} is invalid, because there {'was' if actl_amnt == 1 else 'were'} {actl_amnt} input"
        f"{'' if actl_amnt == 1 else 's'}, but {expct_amnt} {'was' if expct_amnt == 1 else 'were'} expected.")
    return "ERROR"


# some test cases for the different aseembly operations

test_cases = {
    "_add_ rg1 rg2 rg3": "VALUE",
    "_sub_ rg4 rg5 rg6": "VALUE",
    "_grt_ rg7 rg8 rg9": "VALUE",
    "_eql_ rg10 rg11 rg12": "VALUE",
    "_jmp_ ln0": "VALUE",
    "_cjp_ ln65535 rg13 rg14 _eql_": "VALUE",
    "_rst_ rg15 12345": "VALUE",
    "_rrd_ rg14 rg13": "VALUE",
    "_rcl_": "VALUE",
    "_and_ rg12 rg11 rg10": "VALUE",
    "_bor_ rg9 rg8 rg7": "VALUE",
    "_xor_ rg6 rg5 rg4": "VALUE",
    "_not_ rg3 rg1": "VALUE",
    "_rld_ rm255 rg0": "VALUE",
    "_rms_ rm0 rg15": "VALUE",
    "_inv_ rg0 rg0": "VALUE",
    "_sub_": "ERROR",                      # missing three inputs
    "_jmp_ ln65536": "ERROR",              # too large of a line number
    "_cjp_ ln0 rg13 rg14 _and_": "ERROR",  # invalid comparison operation for conditional jump
    "_sub_ rm100 rg5 rg4": "ERROR",        # wrong type of input, should be register not RAM address
    "_grt_ rg5 rg6": "ERROR",              # missing one input
    "_jmp_ ln": "ERROR",                   # missing an integer immediate after ln (invalid input)
    "_rst_ rm5 0": "ERROR",                # wrong type of input, should be register not RAM address
    "_rrd_ gr5 gr5": "ERROR",              # wrong type of input (invalid input prefix)
    "_and_ rg5 rg5 gr4": "ERROR",          # wrong type of input (invalid input prefix)
    "_xor_ rg5 rg4 rg16": "ERROR",         # too large of a register address
    "_not_ rg5 rg4 rg3": "ERROR",          # too many inputs
    "_nat_ rg5 rg4": "ERROR",              # invalid operation
    "_rms_ rm256 rg15": "ERROR",           # too large of a RAM address
}

parser = argparse.ArgumentParser(description='Assemble your assembly code into binary!')
parser.add_argument('-t','--test', help='run the test cases instead of assembling user input', required=False, action='store_true')
parser.add_argument('-i','--input', help='input text file to read multiple lines of assembly code', required=False)
parser.add_argument('-o','--output', help='output text file to write the multiple lines of assembled code to (default is output.txt)', required=False, default='output.txt')
args = vars(parser.parse_args())

if __name__ == "__main__":
    testing = args["test"]
    input_file = args["input"]
    output_file = args["output"]
    assembly_code = []
    if testing:
        print("Running test cases...")
        assembly_code = list(test_cases)
    elif input_file:
        with open(input_file, "r") as f:
            assembly_code = f.readlines()
    else:
        assembly_code = [input("Please enter your line of assembly code: ")]

    assembled_code = [] # the final assembled code, each element is a line of binary code (as a string)

    for line_num, line in enumerate(assembly_code, 1):
        inputs = line.split()

        try:
            operation = inputs.pop(0)
        except IndexError:
            assembled_code.append("ERROR")
            error("", line_num, "no operation")
            continue

        try:
            operation = Operation(operation)
        except ValueError:
            assembled_code.append("ERROR")
            error(operation, line_num, "invalid operation")
            continue

        binary = operation.bnry
        
        # remove comments
        for i, input in enumerate(inputs):
            if input[0] == "#":
                inputs = inputs[:i]
                break

        expctd_amnt = len(operation.inputs)
        actl_amnt = len(inputs)
        if actl_amnt != expctd_amnt:
            assembled_code.append("ERROR")
            input_amount_error(line_num, expctd_amnt, actl_amnt)
            continue
        # check the validity of the inputs depending on the operation
        for input, input_type in zip(inputs, operation.inputs):
            if input_type == Input.RG:
                binary += f'{int(input[2:]):04b}' if check_address(input, Input.RG) else error(input, line_num, "invalid register address")
            elif input_type == Input.INTGR:
                # https://stackoverflow.com/questions/63274885/converting-an-integer-to-signed-2s-complement-binary-string
                # bitmask to grab the last 16 bits of the integer
                binary += f'{int(input) & ((1 << 16) - 1):016b}' if check_integer(input) else error(input, line_num, "invalid number")
            elif input_type == Input.LN:
                binary += f'{int(input[2:]):016b}' if check_address(input, Input.LN) else error(input, line_num, "invalid line number")
            elif input_type == Input.RM:
                binary += f'{int(input[2:]):08b}' if check_address(input, Input.RM) else error(input, line_num, "invalid ram address")
            elif input_type == Input.BTWSE:
                try:
                    input = Operation(input) # this may throw a ValueError
                    if input not in input.bitwise_cmps():
                        raise ValueError
                    binary += input.bnry
                except ValueError:
                    binary += error(input, line_num, "invalid bitwise operation")


        # length of binary code should be 32, we need to add zero padding if it's not
        padding = 32 - len(binary)
        binary += "0"*padding

        if "ERROR" not in binary:
            if not testing:
                assembled_code.append(hex(int(binary, 2)))
            else:
                assembled_code.append("VALUE")
        else:
            assembled_code.append("ERROR")

    if errors:
        print('\n'+'\n'.join(errors))
    if not testing:
        print("\nOutput:\n" + '\n'.join(assembled_code))

    if input_file:
        with open(output_file, "w+") as output:
            output.write("v2.0 raw\n")
            for i, code in enumerate(assembled_code):
                if i == 0:
                    output.write(f"{code[2:]}")
                elif i % 8 == 0:
                    output.write(f"\n{code[2:]}")
                else:
                    output.write(f" {code[2:]}")

    if testing:
        expected_array = list(test_cases.values())
        if expected_array == assembled_code:
            print("\nTest Results: Assembler working properly 😊")
        else:
            for i, (line, expected, actual) in enumerate(zip(assembly_code, expected_array, assembled_code)):
                if expected != actual:
                    print(f"Failed case #{i}: {line}")
            print("\nTest Results: Assembler working improperly 🫠")
