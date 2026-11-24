import struct

import classfile

if __name__ == '__main__':
    def main():
        global cl
        with open('Hello.class', 'rb') as f:
            cl = classfile.ClassFile.from_file(f)

        assert cl.methods[1].name is not None
        assert cl.methods[1].descriptor is not None
        assert (cl.methods[1].name.value + cl.methods[1].descriptor.value) == 'add(II)I'
        code = cl.methods[1].attributes[0].resolve_code()
        assert code is not None
        stack = []
        pc = 0
        bcode = code.code
        while pc < len(bcode):
            op = bcode[pc]
            pc += 1
            match op:
                case 0x10:
                    # bipush
                    a = struct.unpack('>b', bcode[pc:pc+1])[0]
                    pc += 1
                    stack.append(a)
                case 0x1A:
                    # iload 0
                    stack.append(2)
                case 0x1B:
                    # iload 1
                    stack.append(3)
                case 0x60:
                    # iadd
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(a + b)
                case 0x64:
                    # isub
                    b = stack.pop()
                    a = stack.pop()
                    stack.append(a - b)
                case 0xAC:
                    # ireturn
                    a = stack.pop()
                    print(f'ireturn: {a}')
                case _:
                    raise RuntimeError(f'unknown opcode {hex(op)}')
        #print(code)

    main()


