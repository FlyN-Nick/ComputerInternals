from enum import StrEnum, auto

# https://jwodder.github.io/kbits/posts/multi-value-enum/

# While the docstrings throughout do interrupt the code flow, they provide helpful documentation and intellisense.
# However, I may change my mind in the future about the tradeoff between readability and documentation, and replace them with inline comments.
class Input(StrEnum):
    """Assembly input types and their bounds."""
    
    RG = (auto(), 0, 2**4)
    """Register address, unsigned 4-bit"""
    RM = (auto(), 0, 2**8)
    """Ram address, unsigned 8-bit"""
    LN = (auto(), 0, 2**16)
    """Line number, unsigned 16-bit, used for jumps"""
    INTGR = (auto(), -(2**15), 2**15)
    """Integer value, signed 16-bit, RAM and registers hold these values"""
    BTWSE = (auto(), None, None) 
    """Comparison bitwise operation, used for conditional jumps"""
    
    value: str
    """String representation of the input type, used for validation"""
    min_: int
    """Minimized value, inclusive"""
    max_: int
    """Maximized value, exclusive"""
    
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
    
    ADD = ("_add_", "0000", [Input.RG, Input.RG, Input.RG]) # addition
    """Addition"""
    SUB = ("_sub_", "0001", [Input.RG, Input.RG, Input.RG])
    """Subtraction"""
    GRT = ("_grt_", "0010", [Input.RG, Input.RG, Input.RG])
    """Greater than (comparison)"""
    EQL = ("_eql_", "0011", [Input.RG, Input.RG, Input.RG])
    """Equal to (comparison)"""
    JMP = ("_jmp_", "0100", [Input.LN])
    """Jump"""
    CJP = ("_cjp_", "1111", [Input.LN, Input.RG, Input.RG, Input.BTWSE])
    """Conditional jump"""
    RST = ("_rst_", "0101", [Input.RG, Input.INTGR])
    """Register set"""
    RRD = ("_rrd_", "0110", [Input.RG, Input.RG])
    """Register read"""
    RCL = ("_rcl_", "0111", [])
    """Register clear"""
    AND = ("_and_", "1000", [Input.RG, Input.RG, Input.RG])
    """Bitwise and"""
    BOR = ("_bor_", "1001", [Input.RG, Input.RG, Input.RG])
    """Bitwise or"""
    XOR = ("_xor_", "1010", [Input.RG, Input.RG, Input.RG])
    """Bitwise xor"""
    NOT = ("_not_", "1011", [Input.RG, Input.RG])
    """Bitwise not"""
    RLD = ("_rld_", "1100", [Input.RG, Input.RG])
    """Register load (write from ram to register)"""
    RMS = ("_rms_", "1101", [Input.RG, Input.RG])
    """Ram set."""
    INV = ("_inv_", "1110", [Input.RG, Input.RG])
    """Bitwise invert (negate?)."""
    
    value: str
    """Assembly representation of operation."""
    bnry: str
    """Binary representation of operation."""
    inputs: list[Input]
    """Inputs required for operation."""
    
    def __new__(cls, value: str, bnry: str, inputs: list[Input]) -> "Operation":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.bnry = bnry
        obj.inputs = inputs
        return obj
    
    def is_btwse_cmps_op(self) -> bool:
        """Check if the operation is a bitwise comparison operation, which can be used for conditional jumps."""
        return self in [Operation.AND, Operation.BOR, Operation.XOR]
