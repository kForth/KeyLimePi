#!/usr/bin/env python
import sys
import time

NULL = chr(0)
DEVICE = '/dev/hidg0'
TO_CODE = lambda c: ord(c) - 93

def write(str):
    with open(DEVICE, 'rb+') as kb:
        kb.write(str.encode())

def write_code(code, shift=False):
    write((chr(32) if shift else NULL) + NULL + chr(code) + NULL * 5)

def write_key(char, shift=False):
    write_code(TO_CODE(char), shift=shift)

def main(args):
    while True:
        write_key('k')
        write_code(0)
        time.sleep(1)
    
if __name__ == "__main__":
    main(sys.argv)