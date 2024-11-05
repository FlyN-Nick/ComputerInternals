
from definitions import *
import argparse

def hex_to_bin(hex: str) -> str:
    """Convert a hexadecimal string (8 hex digits) to a 32-bit binary string."""
    return f"{int(hex, 16):032b}"

def decode_instruction(binary_instruction: str) -> str:
    """Decodes a single 32-bit binary instruction into assembly language."""
    
    # extract the opcode (first 4 bits)
    opcode_binary = binary_instruction[:4]
    operation = None
    
    # find the matching operation based on the binary opcode
    for op in Operation:
        if op.bnry == opcode_binary:
            operation = op
            break

    if operation is None:
        raise ValueError(f"Unknown opcode: {opcode_binary}")

    assembly_line = operation._value_
    index = 4
    for input_type in operation.inputs:
        if input_type == Input.RG:
            # register is 4 bits
            reg_value = int(binary_instruction[index:index+4], 2)
            assembly_line += f" rg{reg_value}"
            index += 4
        elif input_type == Input.RM:
            # RAM address is 8 bits
            ram_value = int(binary_instruction[index:index+8], 2)
            assembly_line += f" rm{ram_value}"
            index += 8
        elif input_type == Input.LN:
            # line number is 16 bits
            line_value = int(binary_instruction[index:index+16], 2)
            assembly_line += f" ln{line_value}"
            index += 16
        elif input_type == Input.INTGR:
            # integer immediate is 16 bits signed
            int_value = int(binary_instruction[index:index+16], 2) # first assume that it's an unsigned 16-bit niteger
            # convert to 16-bit signed integer
            if int_value >= (1 << 15): # if it's >= 2^15, the MSB is 1 and it's actually a negative number
                int_value -= (1 << 16) # convert to signed integer by subtracting 2^16 (two's complement)
            assembly_line += f" {int_value}"
            index += 16
        elif input_type == Input.BTWSE:
            # bitwise comparison operation (4 bits for opcode)
            found = False
            for btwse_cmp_opcode in Operation.bitwise_cmps():
                if binary_instruction[index:index+4] == btwse_cmp_opcode.bnry:
                    assembly_line += f" {btwse_cmp_opcode._value_}"
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Unknown bitwise comparison opcode: {binary_instruction[index:index+4]}")
            index += 4

    return assembly_line

def disassemble(hex_instructions: list[str]) -> list[str]:
    """Disassemble a list of hexadecimal instructions into assembly language."""
    assembly_code = []
    for hex_instruction in hex_instructions:
        # convert hex to binary
        binary_instruction = hex_to_bin(hex_instruction.strip())
        # decode the binary instruction to assembly language
        assembly_line = decode_instruction(binary_instruction)
        assembly_code.append(assembly_line)
    return assembly_code

parser = argparse.ArgumentParser(description="Disassemble binary instructions into assembly language.")
parser.add_argument("input", type=str, help="Input file containing hexadecimal instructions.")
parser.add_argument("-o", "--output", type=str, help="Output file to write the disassembled assembly code to (default is output.txt)", default="output.txt")
args = vars(parser.parse_args())

if __name__ == "__main__":
    input_file = args["input"]
    output_file = args["output"]
    with open(input_file, "r") as f:
        hex_instructions = " ".join(f.readlines()[1:]).split()
        assembly_code = disassemble(hex_instructions)
        with open(output_file, "w+") as out:
            for assembly_line in assembly_code:
                out.write(f"{assembly_line}\n")
                print(assembly_line)
