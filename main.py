import sys

from chip8 import *


if __name__=='__main__':
    chip = Chip8()
    chip.load_rom(sys.argv[1])

    while True:
        chip.cycle()
        chip.handle_keys()
        chip.interface.draw(chip.display, chip.mem)
