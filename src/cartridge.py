from array import array


class romLoader:
    rom = 0

    def __init__(self, romPath):
        self.rom = self.openFile(romPath)

    def openFile(self, romPath):
        try:
            rom = open(romPath, 'rb')
            print("{0} ......LOADED".format(romPath))
        except ValueError:
            print("Invalid Path.")

        return rom

    def load(self):
        # Jump first 4 bytes
        if self.rom.read(3).decode('ascii') != 'NES':
            exit()
        self.rom.seek(4)

        # Read ROM header
        self.prgRomCount = ord(self.rom.read(1))
        self.chrRomCount = ord(self.rom.read(1))
        self.flags6 = ord(self.rom.read(1))
        self.flags7 = ord(self.rom.read(1))
        self.prgRamCount = ord(self.rom.read(1))
        self.flags9 = ord(self.rom.read(1))
        self.flags10 = ord(self.rom.read(1))

        # Compute the mapper
        # Grab the last 4 bits of flags6, do a right shift of 4 bytes and add 4 bits to the last flags7
        self.mapperNumber = ((self.flags6 & 240) >> 4) + (self.flags7 & 240)

        # Adjust the reader to the right position
        self.rom.seek(16)

        # Check and read the Trainer
        if self.flags6 & 4:
            self.trainerData = self.rom.read(0x200)

        self.mirror = self.flags6 & 1

        # Read PRG ROM and CHR ROM and map it to integer arrays
        self.prgRomData = array('B', self.rom.read(0x4000 * self.prgRomCount))
        self.chrRomData = array('B', self.rom.read(0x2000 * self.chrRomCount))
        self.rom.close()

    def printHeader(self):
        print("Mapper Number: {0}".format(self.mapperNumber))
        print("PRG Count: : {0}".format(self.prgRomCount))
        print("CHR Count: : {0}".format(self.chrRomCount))
        print("Flags 6: {0}".format( self.flags6))
        print("Flags 7: {0}".format( self.flags7))
        print("Size of PRG Data: {0}".format(len(self.prgRomData)))
        print("Size of CHR Data: {0}".format(len(self.chrRomData)))
        print("\n")
