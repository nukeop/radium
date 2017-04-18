import pygame
import random

from interface import Interface


KEY_MAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xc,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xd,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xe,
    pygame.K_z: 0xa,
    pygame.K_x: 0x0,
    pygame.K_c: 0xb,
    pygame.K_v: 0xf
}


class Chip8:


    def __init__(self):
        self.key_inputs = [0]*16
        self.display = [0]*64*32
        self.mem = [0]*4096

        self.opcode = 0
        self.vx = 0
        self.vy = 0

        self.registers = [0]*16
        self.sound_timer = 0
        self.delay_timer = 0
        self.index = 0
        self.pc = 0x200

        self.key_wait = False

        self.stack = []

        self.fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
                      0x20, 0x60, 0x20, 0x20, 0x70, # 1
                      0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
                      0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
                      0x90, 0x90, 0xF0, 0x10, 0x10, # 4
                      0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
                      0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
                      0xF0, 0x10, 0x20, 0x40, 0x40, # 7
                      0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
                      0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
                      0xF0, 0x90, 0xF0, 0x90, 0x90, # A
                      0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
                      0xF0, 0x80, 0x80, 0x80, 0xF0, # C
                      0xE0, 0x90, 0x90, 0x90, 0xE0, # D
                      0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
                      0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        self.funcmap = {
            0x0000: self._0ZZZ,
            0x00e0: self._0ZZ0,
            0x00ee: self._0ZZE,
            0x1000: self._1ZZZ,
            0x2000: self._2ZZZ,
            0x3000: self._3ZZZ,
            0x4000: self._4ZZZ,
            0x5000: self._5ZZZ,
            0x6000: self._6ZZZ,
            0x7000: self._7ZZZ,
            0x8000: self._8ZZZ,
            0x8FF0: self._8ZZ0,
            0x8ff1: self._8ZZ1,
            0x8ff2: self._8ZZ2,
            0x8ff3: self._8ZZ3,
            0x8ff4: self._8ZZ4,
            0x8ff5: self._8ZZ5,
            0x8ff6: self._8ZZ6,
            0xA000: self._AZZZ,
            0xB000: self._BZZZ,
            0xC000: self._CZZZ,
            0xD000: self._DZZZ,
            0xE000: self._EZZZ,
            0xE00E: self._EZZE,
            0xE001: self._EZZ1,
            0xF000: self._FZZZ,
            0xF007: self._FZ07,
            0xF00A: self._FZ0A,
            0xF015: self._FZ15,
            0xF018: self._FZ18,
            0xF01E: self._FZ1E,
            0xF029: self._FZ29,
            0xF033: self._FZ33,
            0xF055: self._FZ55,
            0xF065: self._FZ65
        }

        for i in range(80):
            self.mem[i] = self.fonts[i]

        self.interface = Interface(64, 32, 10)


    def load_rom(self, rom_path):
        print("Loading {}...".format(rom_path))
        binary = open(rom_path, 'rb').read()

        for i in range(len(binary)):
            self.mem[i+0x200] = binary[i]

        print("ROM loaded.")


    def cycle(self):
        self.opcode = (self.mem[self.pc] << 8) | self.mem[self.pc + 1]

        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4

        self.pc += 2

        extracted_opcode = self.opcode & 0xf000
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Unknown opcode: {0:x}".format(self.opcode))


        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

            if self.sound_timer == 0:
                pass
            #play sounds here


    def _0ZZZ(self):
        extracted_opcode = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Unknown opcode: {0:x}".format(self.opcode))

    def _0ZZ0(self):
        """Clears the screen.
        """
        self.display_buffer = [0]*64*32


    def _0ZZE(self):
        """Returns from subroutine.
        """
        self.pc = self.stack.pop()


    def _1ZZZ(self):
        """JMP instruction.

        NNN specifies an address.
        """
        self.pc = self.opcode & 0x0fff


    def _2ZZZ(self):
        """Calls a subroutine at NNN.
        """
        self.stack.append(self.pc)
        self.pc = self.opcode & 0x0fff


    def _3ZZZ(self):
        """Skips the next instruction if VX equals NN.
        """
        if self.registers[self.vx] == (self.opcode & 0x00ff):
            self.pc += 2


    def _4ZZZ(self):
        """Skips the next instruction if VX doesn't equal NN.
        """
        if self.registers[self.vx] != (self.opcode & 0x00ff):
            self.pc += 2


    def _5ZZZ(self):
        """Skips the next instruction if VX equals VY.
        """
        if self.registers[self.vx] == self.registers[self.vy]:
            self.pc += 2


    def _6ZZZ(self):
        """Sets VX to NN.
        """
        self.registers[self.vx] = self.opcode & 0x00ff


    def _7ZZZ(self):
        """Adds NN to VX.
        """
        self.registers[self.vx] += self.opcode & 0xff


    def _8ZZZ(self):
        extracted_opcode = self.opcode & 0xf00f
        extracted_opcode += 0xff0
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Unknown opcode: {0:x}".format(self.opcode))


    def _AZZZ(self):
        """Sets I to the address NNN.
        """
        self.index = self.opcode & 0x0fff


    def _BZZZ(self):
        """Jumps to the address NNN plus V0.
        """
        self.pc = (self.opcode & 0x0fff) + self.registers[0]


    def _CZZZ(self):
        """Sets VX to a random number and NN.
        """
        r = int(random.random() * 0xff)
        self.registers[self.vx] = r & (self.opcode & 0x00ff)
        self.registers[self.vx] &= 0xff


    def _8ZZ0(self):
        """Sets VX to the value of VY.
        """
        self.registers[self.vx] = self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ1(self):
        """Sets VX to VX or VY.
        """
        self.registers[self.vx] |= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ2(self):
        """Sets VX to VX and VY.
        """
        self.registers[self.vx] &= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ3(self):
        """Sets VX to VX xor VY.
        """
        self.registers[self.vx] ^= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ4(self):
        """Adds VX to VY. VF is set to 1 when there's a carry, 0 otherwise.
        """
        if self.registers[self.vx] + self.registers[self.vy] > 0xff:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        self.registers[self.vx] += self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ5(self):
        """Subtracts VY from VX. VF is set to 0 when there's a borrow, 1
        otherwise.
        """
        if self.registers[self.vy] > self.registers[self.vx]:
            self.registers[0xf] = 0
        else:
            self.registers[0xf] = 1

        self.registers[self.vx] -= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8ZZ6(self):
        """Rightshift VX by one. VF is set to the value of the least
        significant bit of VX before the shift.
        """
        self.registers[0xf] = self.registers[self.vx] & 0x0001
        self.registers[self.vx] = self.registers[self.vx] >> 1


    def _DZZZ(self):
        """Draws a sprite.
        """
        self.registers[0xf] = 0
        x = self.registers[self.vx] & 0xff
        y = self.registers[self.vy] & 0xff
        height = self.opcode & 0x000f

        for row in range(height):
            curr_row = self.mem[row + self.index]

            pixel_offset = 0
            while pixel_offset < 8:
                loc = x + pixel_offset + ((y+row)*64)
                pixel_offset += 1
                if (y + row) >= 32 or (x + pixel_offset - 1) >= 64:
                    continue
                mask = 1 << 8-pixel_offset
                curr_pixel = (curr_row & mask) >> (8-pixel_offset)
                self.display[loc] ^= curr_pixel
                if self.display[loc] == 0:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0


    def _EZZZ(self):
        extracted_opcode = self.opcode & 0xf00f
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Unknown opcode: {0:x}".format(self.opcode))


    def _EZZE(self):
        """Skips the next instruction if the key stored in VX is pressed.
        """
        key = self.registers[self.vx] & 0xf
        if self.key_inputs[key] == 1:
            self.pc += 2


    def _EZZ1(self):
        """Skips the next instruction if the key stored in VX isn't pressed.
        """
        key = self.registers[self.vx] & 0xf
        if self.key_inputs[key] == 0:
            self.pc += 2


    def _FZZZ(self):
        extracted_opcode = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Unknown opcode: {0:x}".format(self.opcode))


    def _FZ07(self):
        """Sets VX to the value of the delay timer.
        """
        self.registers[self.vx] = self.delay_timer


    def _FZ0A(self):
        """A key press is awaited and then stored in VX.
        """
        ret = self.get_key()
        if ret >= 0:
            self.registers[self.vx] = ret
        else:
            self.pc -= 2


    def _FZ15(self):
        """Sets the delay timer to VX.
        """
        self.delay_timer = self.registers[self.vx]


    def _FZ18(self):
        """Sets the sound timer to VX.
        """
        self.sound_timer = self.registers[self.vx]


    def _FZ1E(self):
        """Adds VX to I. If overflow, VF = 1
        """
        self.index += self.registers[self.vx]
        if self.index > 0xfff:
            self.registers[0xf] = 1
            self.index &= 0xfff
        else:
            self.registers[0xf] = 0


    def _FZ29(self):
        """Set index to point to a character.
        """
        self.index = (5*(self.registers[self.vx])) & 0xfff


    def _FZ33(self):
        """Store a number as BCD.
        """
        self.mem[self.index] = self.registers[self.vx] // 100
        self.mem[self.index+1] = (self.registers[self.vx] % 100) // 10
        self.mem[self.index+2] = self.registers[self.vx] % 10


    def _FZ55(self):
        """Stores V0 to VX in memory starting at address I.
        """
        for i in range(self.vx):
            self.mem[self.index+i] = self.registers[i]
        self.index += self.vx + 1


    def _FZ65(self):
        """Fills V0 to VX with values from memory starting at address I.
        """
        for i in range(self.vx):
            self.registers[i] = self.mem[self.index + i]
        self.index += (self.vx) + 1


    def handle_keys(self):
        events = self.interface.handle_events()
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.on_key_press(event)
            elif event.type == pygame.KEYUP:
                self.on_key_release(event)


    def get_key(self):
        for i in range(0xf):
            if self.key_inputs[i] == 1:
                return i
        return -1


    def on_key_press(self, event):
        #print("Key pressed: {}".format(event.key))
        if event.key in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[event.key]] = 1
            if self.key_wait:
                self.key_wait = False


    def on_key_release(self, event):
        #print("Key released: {}".format(event.key))
        if event.key in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[event.key]] = 0
