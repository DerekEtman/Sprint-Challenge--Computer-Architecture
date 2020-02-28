"""CPU functionality."""

import sys


# **No longer need these since I label them in the switchbranch**
# LDI = 0b10000010
# PRN = 0b01000111
# HLT = 0b00000001
# MUL = 10100010

# - [x] Add the `CMP` instruction and `equal` flag to your LS-8.
# - [x] Add the `JMP` instruction.
# - [x] Add the `JEQ` and `JNE` instructions.



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # hold up to 256 bytes of memory
        self.ram = [0] * 256
        # * general purpose registers
        self.reg = [0] * 8 
        # Program Counter, Address of the currently executing instruction
        self.pc = 0
        # Sp
        self.sp = 7
        # Memory Address Register, holds the memory address we're reading or writing
        self.mar = 0
        # Memory Data Register, holds the value to write or the value just read
        self.mdr = 0
        # Branch table holding functions an d the IR Opcode value
        self.branchtable = {}
        self.branchtable[0b10000010] = {'instruction_name':'LDI', 'retrieve': self.LDI_handler}
        self.branchtable[0b01000111] = {'instruction_name':'PRN', 'retrieve': self.PRN_handler}
        self.branchtable[0b00000001] = {'instruction_name':'HLT', 'retrieve': self.HLT_handler}
        self.branchtable[0b10100010] = {'instruction_name':'MUL', 'retrieve': self.alu}
        self.branchtable[0b01000101] = {'instruction_name': 'PUSH', 'retrieve': self.push_handler}
        self.branchtable[0b01000110] = {'instruction_name' : 'POP', 'retrieve': self.pop_handler}
        self.branchtable[0b01010000] = {'instruction_name' : 'CALL', 'retrieve': self.CALL_handler}
        self.branchtable[0b00010001] = {'instruction_name' : 'RET', 'retrieve': self.RET_handler}
        self.branchtable[0b10100111] = {'instruction_name' : 'CMP', 'retrieve': self.alu}
        self.branchtable[0b01010100] = {'instruction_name' : 'JMP', 'retrieve': self.JMP_handler}
        self.branchtable[0b01010101] = {'instruction_name' : 'JEQ', 'retrieve': self.JEQ_handler}
        self.branchtable[0b01010110] = {'instruction_name' : 'JNE', 'retrieve': self.JNE_handler}
        self.branchtable[0b10101000] = {'instruction_name': 'JNE', 'retrieve' : self.alu}
        self.E = 0
        self.L = 0
        self.G = 0

    
    def JMP_handler(self,a):
        print(f"\n--JMP--")
        # grab address from mem
        address = self.ram_read(self.pc +1)
        value = self.reg_read(address)
        # Jump(set pc) to the address stored in reg
        self.pc = value

    def JNE_handler(self,a):
        print(f"\n--JNE--")
        # grab the address from mem
        address = self.ram_read(self.pc +1)
        value = self.reg_read(address)
        # if `E` (equal) is false (0)
        print(f"address: {address}, value: {value}")
        if self.E == 0:
            self.pc = value
            # set jump(set pc) to address stored in reg
        else:
            self.pc += 2

    def JEQ_handler(self,a):
        print(f"\n--Running JEQ--")
        address = self.ram_read(self.pc + 1)
        value = self.reg_read(address)
        print(f"address: {address}, value: {value}")
        
        # if `E` is true (1)
        if self.E == 1:
            # Jump to address
            self.pc = value
        else:
            self.pc += 2

    def load(self, filename):
        """Load a program into memory."""
        print(f"---Loading File---\n {filename}")
        try:
            address = 0
            # opening the file
            with open(filename) as f:
                # read through all the lines
                for line in f:
                    # parse out the comments
                    comment_split = line.strip().split("#")

                    # cast the numbers from strings into ints
                    value = comment_split[0].strip()

                    # ignore any blank lines
                    if value == "":
                        continue

                    num = int(value,2)
                    self.ram[address] = num
                    address += 1

        
        # if there is no file
        except FileNotFoundError:
            # return error message
            print("File not found")
            # exit prog
            sys.exit(2)

        # check if file was called for load in
        if len(sys.argv) != 2:
            print(f"Please include file name. Ex/ python -filename-")
            sys.exit(1)

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def RET_handler(self,a):
        # return from the subroutine
        # Pop the value from the top of the stack and store it in the pc
        pass

    def push_handler(self,a):
        print(f"\n--Pushing--")
        self.trace()
        # Grab the register argument
        reg = self.ram_read(self.pc + 1)
        value = self.reg_read(reg)
        print(f"Grabbing value: {value} from register {reg}")

        # Decrement the SP
        self.reg[self.sp] -= 1

        # Copy the value in the given register to the add pointer by the sp
        self.ram[self.reg[self.sp]] = value
        print(f"Placing value: {value} at location {self.ram}")
        self.pc += 2

        # print(f", value: {value},\n  self.reg {self.reg},\n  self.ram{self.ram}") 
        self.trace()

    def CALL_handler(self,a):
        print(f"\n--Calling--")
        self.trace()
        # The address of the instruction directly after call
        # is pushed onto the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2

        print(f" {self.reg[self.sp]}\n{self.ram[self.reg[self.sp]] }")
        # This allows us to return to where we left off
        # when the subroutine finishes executing 
        # the pc is set to the address stored in the given register
        address = self.ram_read(self.pc + 1)
        pc = self.reg_read(address)
        # we jump to that location in ram and execute the first instruction in the subroutine, the pc can move forward or backwards from its current location
        self.trace()



    def pop_handler(self,a):
        print(f"\n--Popping--")
        self.trace()
        # grab the val from the top of the stack
        reg = self.ram_read(self.pc + 1)
        value = self.ram[self.reg[self.sp]]
        # print(f"Grabbing Value {value} from sp Location: {reg}")


        # Copy the value from the address pointed to by `SP` to the given register
        self.reg[reg] = value

        # increment SP
        self.reg[self.sp] += 1
        self.pc += 2

        # print(f"reg: {reg}, value: {value}, updated reg: {self.reg[reg]}")
        self.trace()


    def LDI_handler(self,a):
        print(f"\n--Running LDI--")
        self.trace()
        # print(f"Op_a: {operand_a}, Op b: {operand_b}")
        address = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)

        self.reg_write(address, value)
        self.pc += 3
        self.trace()        

    def PRN_handler(self,a):
        print(f"\n--Printing--")
        address = self.ram_read(self.pc + 1)

        print( self.reg_read(address))
        
        self.pc += 2

    def HLT_handler(self,a):
        print(f"\n--Finished--")
        sys.exit(2)


    def ram_read(self, mar):
        '''
        `ram_read()` should accept the address to read and return the value stored there.
        '''

        # mar holds the Address
        # mdr holds the Value

        return self.ram[mar]


    def ram_write(self,mdr, mar):
       ''' 
       `raw_write()` should accept a value to write, and the address to write it to.
       '''
       self.ram[mar] = mdr
       return self.ram[mar]

    def reg_read(self, mar):
        return self.reg[mar]


    def reg_write(self, mar, mdr):
        self.reg[mar] = mdr
        print(f"{self.reg[mar]}")
        # return self.reg[mar]



    def alu(self, op):
        """ALU operations."""   

        ''' Register Addresses'''
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        ''' Register Values '''
        register_a = self.reg_read(reg_a)
        register_b = self.reg_read(reg_b)
        # print(f"self.reg_read(reg_a): {self.reg_read(self.pc + 1)} * self.reg_read(reg_b): ")

        if op == "ADD":
            print(f"\n--ADD--")
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        # Multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            print(f"\n--Multiplying--")
            value = self.reg_read(reg_a) * self.reg_read(reg_b)
            self.reg_write(reg_a,value)
        elif op == "CMP":
            print(f"\n--Comparing--")
            # if Reg a == reg_b
            print(f"reg a: {reg_a}, reg_b: {reg_b}")
            if register_a == register_b:
                # set the `E` Equal flag to 1
                self.E = 1
                self.L = 0
                self.G = 0
                print(f"a == b, `E` flag is now {self.E}")
            # if reg_A < reg_B 
            elif register_a < register_b:
                # set `L` flag to 1
                # Otherwise set to 0
                self.E = 0
                self.L = 1
                self.G = 0
                print(f"a == b, `L` flag is now {self.L}")
            # if reg_a > reg_b:
            elif register_a > register_b:
                # set `G` flag to 1
                # Otherwise set to 0
                self.E = 0
                self.L = 0
                self.G = 1
                print(f"a == b, `G` flag is now {self.G}")
        elif op == "AND":
            # Bitwise-AND Reg A & B 
            value = register_a & register_b
            # Store in Reg A
            self.reg_write(reg_a, value)
        elif op == "OR":
            pass
        elif op == "XOR":
            pass
        elif op == "NOT":
            pass
        elif op == "SHL":
            pass
        elif op == "SHR":
            pass
        elif op == "MOD":
            pass
        else:
            raise Exception("Unsupported ALU operation")

        self.pc += 3

    def HLT(self):
        sys.exit(0)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X |  %02X %02X %02X | " % (
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

        while True:

            # Grabbing the instructions from RAM
            IR = self.ram[self.pc]
            # print(f"PC at start: {self.pc}, IR: {IR}, operand_a: {operand_a}, operand_b : {operand_b}")
            # print(f"{self.ram}")

            # Grab instructions from branchtable 
            get = self.branchtable[IR]

            # Accessing correct instruction from the branchtable
            # Calling the correct handler from Branchtable
            # Same as calling: 
                # if IR == LDI:
                    # self.LDI_handler()
            get['retrieve'](get["instruction_name"])

            # if IR == LDI:
            #     self.LDI_handler()
            # elif IR == PRN:
            #     print(f"\n--Printing--")
            #     self.reg_read(operand_a)
            #     self.pc += 2
            # elif IR == HLT:
            #     print(f"\n--Stopping--")
            #     sys.exit(0)






