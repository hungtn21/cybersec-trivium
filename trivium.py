# Require bitstring package
# pip install bitstring
from collections import deque
from itertools import repeat
from bitstring import BitArray
import argparse

class Trivium:
    def __init__(self, key, iv):
        self.state = None
        self.key = key
        self.iv = iv

        # Initialize state
        init_state = self.key + list(repeat(0, 13))
        init_state += self.iv + list(repeat(0, 4))
        init_state += list(repeat(0, 108)) + [1, 1, 1]

        self.state = deque(init_state)

        # Do 4 Full cycle clock
        for _ in range(4 * 288):
            self.gen_keystream()

    def gen_keystream(self):
        t_1 = self.state[65] ^ self.state[92]
        t_2 = self.state[161] ^ self.state[176]
        t_3 = self.state[242] ^ self.state[287]

        z = t_1 ^ t_2 ^ t_3

        t_1 ^= self.state[90] & self.state[91] ^ self.state[170]
        t_2 ^= self.state[174] & self.state[175] ^ self.state[263]
        t_3 ^= self.state[285] & self.state[286] ^ self.state[68]

        self.state.rotate()
        self.state[0] = t_3
        self.state[93] = t_1
        self.state[177] = t_2

        return z

    def keystream(self, msglen):
        # Generate keystream
        counter = 0
        keystream = []

        while counter < msglen:
            keystream.append(self.gen_keystream())
            counter += 1

        return keystream

def main():
    parser = argparse.ArgumentParser(description='Encrypt text using Trivium stream cipher.')
    parser.add_argument('-k', '--key', action='store', dest='key', type=str,
                        help='An 80 bit key e.g.: 0x0000000000000000')
    parser.add_argument('-iv', action='store', dest='iv', type=str,
                        help='An 80 bit initialization vector e.g.: 0x0000000000000000')
    parser.add_argument('-f', action='store_true', dest='file_input',
                        help='Flag to indicate input from file')
    parser.add_argument('input', help='Input text or input file path')
    args = parser.parse_args()

    # Initialize Trivium
    KEY = BitArray(args.key)
    KEY.byteswap()
    KEY = list(map(int, KEY.bin))
    IV = BitArray(args.iv)
    IV.byteswap()
    IV = list(map(int, IV.bin))
    trivium = Trivium(KEY, IV)

    if args.file_input:
        # Read input from file
        with open(args.input, 'r') as f:
            input_text = f.read().strip()
    else:
        input_text = args.input

    # Print key stream
    keystream = trivium.keystream(len(input_text))
    print('Key Stream:')
    print(''.join(map(str, keystream)))

if __name__ == "__main__":
    main()
