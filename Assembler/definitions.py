from enum import StrEnum, auto

# https://jwodder.github.io/kbits/posts/multi-value-enum/

class Input(StrEnum):
    """Assembly input types and their bounds."""
    
    RG = (auto(), 0, 2**4)             # register address, unsigned 4-bit
    RM = (auto(), 0, 2**8)             # RAM address, unsigned 8-bit
    LN = (auto(), 0, 2**16)            # line number, unsigned 16-bit, used for jumps
    INTGR = (auto(), -(2**15), 2**15)  # integer immediate, signed 16-bit, RAM and registers hold these values
    BTWSE = (auto(), None, None)       # comparison bitwise operation, used for conditional jumps
    
    _value_: str  # string representation of the input type, used for validation
    min_: int     # min value, inclusive
    max_: int     # max value, exclusive
    
    def __new__(cls, value: str, min_: int, max_: int) -> "Input":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.min_ = min_
        obj.max_ = max_
        return obj
    
    def within_bounds(self, value: int) -> bool:
        """Check if a value is within the input kind's bounds."""
        return self.min_ <= value < self.max_


class Operation(StrEnum):
    """Assembly operations, their binary representations, and required inputs."""
    
    ADD = ("_add_", "0000", [Input.RG, Input.RG, Input.RG])              # addition
    SUB = ("_sub_", "0001", [Input.RG, Input.RG, Input.RG])              # subtraction
    GRT = ("_grt_", "0010", [Input.RG, Input.RG, Input.RG])              # greater than
    EQL = ("_eql_", "0011", [Input.RG, Input.RG, Input.RG])              # equal to
    JMP = ("_jmp_", "0100", [Input.LN])                                  # jump
    CJP = ("_cjp_", "1111", [Input.LN, Input.RG, Input.RG, Input.BTWSE]) # conditional jump
    RST = ("_rst_", "0101", [Input.RG, Input.INTGR])                     # register set
    RRD = ("_rrd_", "0110", [Input.RG, Input.RG])                        # register read
    RCL = ("_rcl_", "0111", [])                                          # register clear
    AND = ("_and_", "1000", [Input.RG, Input.RG, Input.RG])              # bitwise and
    BOR = ("_bor_", "1001", [Input.RG, Input.RG, Input.RG])              # bitwise or
    XOR = ("_xor_", "1010", [Input.RG, Input.RG, Input.RG])              # bitwise exclusive or
    NOT = ("_not_", "1011", [Input.RG, Input.RG])                        # bitwise not
    RLD = ("_rld_", "1100", [Input.RM, Input.RG])                        # register load (write from RAM to register)
    RMS = ("_rms_", "1101", [Input.RM, Input.RG])                        # RAM set (write from register to RAM)
    INV = ("_inv_", "1110", [Input.RG, Input.RG])                        # negate (bitwise not + 1)
    
    _value_: str         # assembly representation of operation
    bnry: str            # binary representation of operation
    inputs: list[Input]  # inputs required for operation
    
    def __new__(cls, value: str, bnry: str, inputs: list[Input]) -> "Operation":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.bnry = bnry
        obj.inputs = inputs
        return obj
    
    def is_btwse_cmps_op(self) -> bool:
        """Check if the operation is a bitwise comparison operation, which can be used for conditional jumps."""
        return self in [Operation.AND, Operation.BOR, Operation.XOR]
