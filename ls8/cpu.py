"""CPU functionality."""

import sys

HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
ADD  = 0b10100000
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
INC  = 0b01100101
DEC  = 0b01100110
PRA  = 0b01001000
AND  = 0b10101000
OR   = 0b10101010
XOR  = 0b10101011
NOT  = 0b01101001
SHL  = 0b10101100
SHR  = 0b10101101
MOD  = 0b10100100

IM = 5 # R5 is reserved as the interrupt mask (IM)
IS = 6 # R6 is reserved as the interrupt status (IS)
SP = 7 # R7 is reserved as the stack pointer (SP)

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.fl = 0
        self.pc = 0

        self.halted = False

    def load(self, filename):
        """Load a program into memory."""
        print(filename)
        address = 0
        with open(filename) as f:
            for line in f:
                comment_split = line.strip().split("#")
                value = comment_split[0].strip()

                # Ignore blank lines
                if value == "":
                    continue

                num = int(value, 2)
                self.ram[address] = num
                address += 1


    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        # elif op == "XOR":
        #     pass
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        # elif op == "SHL":
        #     pass
        # elif op == "SHR":
        #     pass
        # elif op == "MOD"
        #     pass

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while not self.halted:

            ir = self.ram_read(self.pc)
            operand_count = ir >> 6
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                self.halted = True

            elif ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += operand_count + 1

            elif ir == PRN:
                print(self.reg[operand_a])
                self.pc += operand_count + 1

            elif ir == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += operand_count + 1

            elif ir == PUSH:
                # Grab the register argument
                val = self.reg[operand_a]
                # Decrement the SP.
                self.reg[SP] -= 1
                 # Copy the value in the given register to the address pointed to by SP.
                self.ram[self.reg[SP]] = val

                self.pc += operand_count + 1

            elif ir == POP:
                # Grab the value from the top of the stack
                val = self.ram[self.reg[SP]]
                # Copy the value from the address pointed to by SP to the given register.
                self.reg[operand_a] = val
                # Increment the SP.
                self.reg[SP] += 1

                self.pc += operand_count + 1

            elif ir == CALL:
                self.reg[SP] -= 1
                self.ram_write(self.pc + 2, self.reg[SP])

                self.pc = self.reg[operand_a]

            elif ir == RET:
                val = self.ram_read(self.reg[SP])
                self.pc = val

                self.reg[SP] += 1

            elif ir == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += operand_count + 1

            elif ir == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += operand_count + 1

            elif ir == JMP:
                self.pc = self.reg[operand_a]

            elif ir == JEQ:
                # If `equal` flag is set (true), jump to the address stored
                # in the given register.
                if self.fl == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += operand_count + 1

            elif ir == JNE:
                # If `E` flag is clear (false, 0), jump to the address stored
                # in the given register
                if self.fl != 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += operand_count + 1

            elif ir == AND:
                self.alu("AND", operand_a, operand_b)
                self.pc += operand_count + 1

            elif ir == OR:
                self.alu("OR", operand_a, operand_b)
                self.pc += operand_count + 1

            # elif ir == XOR:
            #     self.alu("XOR", operand_a, operand_b)
            #     self.pc += operand_count + 1

            # elif ir == NOT:
            #     self.alu("NOT", operand_a, None)
            #     self.pc += operand_count + 1

            # elif ir == SHL:
            #     self.alu("SHL", operand_a, operand_b)
            #     self.pc += operand_count + 1

            # elif ir == SHR:
            #     self.alu("SHR", operand_a, operand_b)
            #     self.pc += operand_count + 1

            # elif ir == MOD:
            #     self.alu("MOD", operand_a, operand_b)
            #     self.pc += operand_count + 1

