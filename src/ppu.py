import threading
import multiprocessing
import time
from array import array

from renderer import RendererManager

class PPU:

    class VolatileMemory:
        def __init__(self, size):
            self.ram = array('B', [0x00] * size)

        def read(self, a=0x0):
            return self.ram[a]

        def write(self, a=0x0, v=0x0):
            self.ram[a] = v

    class VBlank:
        def __init__(self, console):
            self.status = False
            self._console = console
        
        def enter(self):
            if self._console.PPU.NMI:
                self._console.CPU.InterruptRequest = 0x4E # N
            self.status = True
            while True:
                try:
                    self._console.PPU.renderer.display.blit()
                    break
                except:
                    pass

        def exit(self):
            self.status = False
            self._console.PPU.renderer.display.clear()

    def __init__(self, console=None):
        print("Initializing PPU...")
        self.console = console

        self.nameTableAddress = 0
        self.incrementAddress = 1
        self.spritePatternTable = 0
        self.backgroundPatternTable = 0
        self.spriteSize = 8
        self.NMI = False
        self.colorMode = True
        self.clippingBackground = False
        self.clippingSprites = False
        self.showBackground = False
        self.showSprites = False
        self.colorIntensity = 0

        self.spriteRamAddr = 0
        self.vRamWrites = 0
        self.scanlineSpriteCount = 0
        self.sprite0Hit = 0
        self.spriteHitOccured = False
        self.VRAMAddress = 0
        self.VRAMBuffer = 0
        self.firstWrite = True
        self.ppuScrollX = 0
        self.ppuScrollY = 0
        self.ppuStarted = 0

        self.ppuMirroring = 0
        self.addressMirroring = 0

        self.colorPallete = [(0x75, 0x75, 0x75),
                             (0x27, 0x1B, 0x8F),
                             (0x00, 0x00, 0xAB),
                             (0x47, 0x00, 0x9F),
                             (0x8F, 0x00, 0x77),
                             (0xAB, 0x00, 0x13),
                             (0xA7, 0x00, 0x00),
                             (0x7F, 0x0B, 0x00),
                             (0x43, 0x2F, 0x00),
                             (0x00, 0x47, 0x00),
                             (0x00, 0x51, 0x00),
                             (0x00, 0x3F, 0x17),
                             (0x1B, 0x3F, 0x5F),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0xBC, 0xBC, 0xBC),
                             (0x00, 0x73, 0xEF),
                             (0x23, 0x3B, 0xEF),
                             (0x83, 0x00, 0xF3),
                             (0xBF, 0x00, 0xBF),
                             (0xE7, 0x00, 0x5B),
                             (0xDB, 0x2B, 0x00),
                             (0xCB, 0x4F, 0x0F),
                             (0x8B, 0x73, 0x00),
                             (0x00, 0x97, 0x00),
                             (0x00, 0xAB, 0x00),
                             (0x00, 0x93, 0x3B),
                             (0x00, 0x83, 0x8B),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0xFF, 0xFF, 0xFF),
                             (0x3F, 0xBF, 0xFF),
                             (0x5F, 0x97, 0xFF),
                             (0xA7, 0x8B, 0xFD),
                             (0xF7, 0x7B, 0xFF),
                             (0xFF, 0x77, 0xB7),
                             (0xFF, 0x77, 0x63),
                             (0xFF, 0x9B, 0x3B),
                             (0xF3, 0xBF, 0x3F),
                             (0x83, 0xD3, 0x13),
                             (0x4F, 0xDF, 0x4B),
                             (0x58, 0xF8, 0x98),
                             (0x00, 0xEB, 0xDB),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0xFF, 0xFF, 0xFF),
                             (0xAB, 0xE7, 0xFF),
                             (0xC7, 0xD7, 0xFF),
                             (0xD7, 0xCB, 0xFF),
                             (0xFF, 0xC7, 0xFF),
                             (0xFF, 0xC7, 0xDB),
                             (0xFF, 0xBF, 0xB3),
                             (0xFF, 0xDB, 0xAB),
                             (0xFF, 0xE7, 0xA3),
                             (0xE3, 0xFF, 0xA3),
                             (0xAB, 0xF3, 0xBF),
                             (0xB3, 0xFF, 0xCF),
                             (0x9F, 0xFF, 0xF3),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00),
                             (0x00, 0x00, 0x00)]

        #try:
        self.renderer = RendererManager(self.console.RENDERER_TYPE)
        #except:
        #    print ("Cannot initialize Renderer")

        self.VBLANK = self.VBlank(self.console)
        self.VRAM = self.VolatileMemory(0x10000)
        self.SPRRAM = self.VolatileMemory(0x100)

        self.load_vram_data()
        self.setMirroring(self.console.cartridge.mirror)

        super(PPU, self).__init__()

    def load_vram_data(self):
        maxdata = self.console.cartridge.chrRomData.__len__()
        k = 0
        while k < maxdata:
            v = self.console.cartridge.chrRomData[k]
            self.VRAM.write(k, v)
            k += 1
        self.renderer.display.reset()

    def setMirroring(self, mirroring):
        # 0 = horizontal mirroring
        # 1 = vertical mirroring
        self.ppuMirroring = mirroring
        self.addressMirroring = 0x400 << self.ppuMirroring

    def processControlReg1(self, value):
        # Check bits 0-1
        aux = value & 0x3
        if aux == 0:
            self.nameTableAddress = 0x2000
        elif aux == 1:
            self.nameTableAddress = 0x2400
        elif aux == 2:
            self.nameTableAddress = 0x2800
        else:
            self.nameTableAddress = 0x2C00

        # Check bit 2
        if value & (1 << 2):
            self.incrementAddress = 32
        else:
            self.incrementAddress = 1

        # Check bit 3
        if value & (1 << 3):
            self.spritePatternTable = 0x1000
        else:
            self.spritePatternTable = 0x0000

        # Check bit 4
        if value & (1 << 4):
            self.backgroundPatternTable = 0x1000
        else:
            self.backgroundPatternTable = 0x0000

        # Check bit 5
        if value & (1 << 5):
            self.spriteSize = 16
        else:
            self.spriteSize = 8

        # Bit 6 not used
        # Check bit 7
        if value & (1 << 7):
            self.NMI = True
        else:
            self.NMI = False

    def processControlReg2(self, value):
        # Check bit 0
        if value & 1:
            self.colorMode = True
        else:
            self.colorMode = False

        # Check bit 1
        if value & (1 << 1):
            self.clippingBackground = True
        else:
            self.clippingBackground = False

        # Check bit 2
        if value & (1 << 2):
            self.clippingSprites = True
        else:
            self.clippingSprites = False

        # Check bit 3
        if value & (1 << 3):
            self.showBackground = True
        else:
            self.showBackground = False

        # Check bit 4
        if value & (1 << 4):
            self.showSprites = True
        else:
            self.showSprites = False

        # Check bits 5-7
        self.colorIntensity = value >> 5

    # process register 0x2005
    def processPPUSCROLL(self, value):
        if self.firstWrite:
            self.ppuScrollX = value
            self.firstWrite = False
        else:
            self.ppuScrollY = value
            self.firstWrite = True

    # process register 0x2006
    def processPPUADDR(self, value):
        if self.firstWrite:
            self.VRAMAddress = (value & 0xFF) << 8
            self.firstWrite = False
        else:
            self.VRAMAddress += (value & 0xFF)
            self.firstWrite = True

    # process register 0x2007 (write)
    def writeVRAM(self, value):
        #Todo: Verificar se esta certo
        # NameTable write mirroring.
        if self.VRAMAddress >= 0x2000 and self.VRAMAddress < 0x3F00:
            self.VRAM.write(self.VRAMAddress + self.addressMirroring, value)
            self.VRAM.write(self.VRAMAddress, value)
        # Color Pallete write mirroring.
        elif self.VRAMAddress >= 0x3F00 and self.VRAMAddress < 0x3F20:
            if self.VRAMAddress == 0x3F00 or self.VRAMAddress == 0x3F10:
                self.VRAM.write(0x3F00, value)
                self.VRAM.write(0x3F04, value)
                self.VRAM.write(0x3F08, value)
                self.VRAM.write(0x3F0C, value)
                self.VRAM.write(0x3F10, value)
                self.VRAM.write(0x3F14, value)
                self.VRAM.write(0x3F18, value)
                self.VRAM.write(0x3F1C, value)
            else:
                self.VRAM.write(self.VRAMAddress, value)

        self.VRAMAddress += self.incrementAddress

    # process register 0x2007 (read)
    def readVRAM(self):
        value = 0
        address = self.VRAMAddress & 0x3FFF
        if address >= 0x3F00 and address < 0x4000:
            address = 0x3F00 + (address & 0xF)
            self.VRAMBuffer = self.VRAM.read(address)
            value = self.VRAM.read(address)
        elif address < 0x3F00:
            value = self.VRAMBuffer
            self.VRAMBuffer = self.VRAM.read(address)
        self.VRAMAddress += self.incrementAddress

        return value

    def writeSprRam(self, value):
        self.SPRRAM.write(self.spriteRamAddr,value)
        self.spriteRamAddr = (self.spriteRamAddr + 1) & 0xFF

    def writeSprRamDMA(self, value):
        address = value * 0x100

        i = 0
        while i < 256:
            self.SPRRAM.write(i, self.console.CPU.RAM.read(address))
            address += 1
            i += 1

    def readStatusFlag(self):
        value = 0
        value |= (self.vRamWrites << 4)
        value |= (self.scanlineSpriteCount << 5)
        value |= (self.sprite0Hit << 6)
        value |= (int(self.VBLANK.status) << 7)

        self.firstWrite = True
        self.VBLANK.exit()

        return value

    def doScanline(self):

        if self.showBackground:
            self.drawBackground(self.console.CPU.scanline)

        if self.showSprites:
            self.drawSprites(self.console.CPU.scanline)
            

    def drawBackground(self, scanline):
        tileY = int(scanline / 8)
        Y = int(scanline % 8)

        maxTiles = 32
        if (self.ppuScrollX % 8) != 0:
            maxTiles = 33

        currentTile = int(self.ppuScrollX / 8)
        v = int(self.nameTableAddress + currentTile)
        pixel = 0

        first = 0 if self.clippingBackground else 1
        tiles = array('B', list(range(first, maxTiles)))
        for i in tiles:

            fromByte = 0
            toByte = 8

            ppuScrollFlag = (self.ppuScrollX %8)
            if ppuScrollFlag != 0:
                if i == 0:
                    toByte = 7 - (ppuScrollFlag)
                if i == (maxTiles - 1):
                    fromByte = 8 - (ppuScrollFlag)

            ptrAddress = self.VRAM.read(v + int(tileY*0x20))
            pattern1 = self.VRAM.read(self.backgroundPatternTable + (ptrAddress*16) + Y)
            pattern2 = self.VRAM.read(self.backgroundPatternTable + (ptrAddress*16) + Y + 8)
            # blockX e blockY sao as coordenadas em relacao ao block
            blockX = i % 4
            blockY = tileY % 4
            block = int(i / 4) + (int(tileY / 4) * 8)
            addressByte = int((v & ~0x001F) + 0x03C0 + block)
            byteAttributeTable = self.VRAM.read(addressByte)
            colorIndex = 0x3F00

            if blockX < 2:
                if blockY >= 2:
                    colorIndex |= ((byteAttributeTable & 0b110000) >> 4) << 2
                else:
                    colorIndex |= (byteAttributeTable & 0b11) << 2
            elif blockX >= 2 and blockY < 2:
                colorIndex |= ((byteAttributeTable & 0b1100) >> 2) << 2
            else:
                colorIndex |= ((byteAttributeTable & 0b11000000) >> 6) << 2

            k = array('B', list(range(fromByte, toByte)))
            for j in k:
                bit1 = ((1 << j) & pattern1) >> j
                bit2 = ((1 << j) & pattern2) >> j
                colorIndexFinal = colorIndex
                colorIndexFinal |= ((bit2 << 1) | bit1)

                color = self.colorPallete[self.VRAM.read(colorIndexFinal)]
                x = (pixel + ((j * (-1)) + (toByte - fromByte) - 1))
                y = scanline

                if (bytes(color) != self.renderer.display.LAYER_B.read(x, y)):
                    self.renderer.display.LAYER_B.write(x, y, color)
                j += 1

            pixel += toByte - fromByte

            if (v & 0x001f) == 31:
                v &= ~0x001F
                #v ^= self.addressMirroring
                v ^= 0x400
            else:
                v += 1
            del k
        del tiles

    def drawSprites(self, scanline):
        numberSpritesPerScanline = 0
        Y = scanline % 8
        secondaryOAM = array('B', [0xFF] * 32)
        indexSecondaryOAM = 0

        k = array('B', list(range(0, 256, 4)))
        for currentSprite in k:
            spriteY = self.SPRRAM.read(currentSprite)

            if numberSpritesPerScanline == 8:
                break

            if spriteY <= scanline < spriteY + self.spriteSize:
                sprloop = array('B', list(range(4)))
                for i in sprloop:
                    secondaryOAM[indexSecondaryOAM + i] = self.SPRRAM.read(currentSprite+i)
                indexSecondaryOAM += 4
                numberSpritesPerScanline += 1
                del sprloop
        del k

        k = array('B', list(range(28, -1, -4)))
        for currentSprite in k:
            spriteX = secondaryOAM[currentSprite + 3]
            spriteY = secondaryOAM[currentSprite]

            if spriteY >= 0xEF or spriteX >= 0xF9:
                continue

            currentSpriteAddress = currentSprite + 2
            flipVertical = secondaryOAM[currentSpriteAddress] & 0x80
            flipHorizontal = secondaryOAM[currentSpriteAddress] & 0x40

            Y = scanline - spriteY

            ptrAddress = secondaryOAM[currentSprite + 1]
            patAddress = self.spritePatternTable + (ptrAddress * 16) + ((7 - Y) if flipVertical else Y)
            pattern1 = self.VRAM.read(patAddress)
            pattern2 = self.VRAM.read(patAddress + 8)
            colorIndex = 0x3F10

            colorIndex |= ((secondaryOAM[currentSprite +2] & 0x3) << 2)

            sprloop = array('B', range(8))
            for j in sprloop:
                if flipHorizontal:
                    colorIndexFinal = (pattern1 >> j) & 0x1
                    colorIndexFinal |= ((pattern2 >> j) & 0x1 ) << 1
                else:
                    colorIndexFinal = (pattern1 >> (7 - j)) & 0x1
                    colorIndexFinal |= ((pattern2 >> (7 - j)) & 0x1) << 1

                colorIndexFinal += colorIndex
                if (colorIndexFinal % 4) == 0:
                    colorIndexFinal = 0x3F00
                color = self.colorPallete[(self.VRAM.read(colorIndexFinal) & 0x3F)]

                # Add Transparency
                if color == self.colorPallete[self.VRAM.read(0x3F10)]:
                    color += (0,)

                self.renderer.display.LAYER_A.write(spriteX + j, spriteY + Y, color)
                checkColor=self.renderer.display.LAYER_A.read(spriteX + j, spriteY + Y)
                if self.showBackground and not(self.spriteHitOccured) and currentSprite == 0 and checkColor == bytes(color):
                    self.sprite0Hit = True
                    self.spriteHitOccured = True
            del sprloop
        del k

    def run(self):
        print("PPU OK")
        if self.console.THREAD_MODE == "SINGLE":
            pass
        else:
            self.console.CPU = self.console.CPU
            while True:
                self.console.CPU.end.wait()
                self.console.CPU.end.clear()
                print(self.console.CPU.scanline)
                self.renderer.display.blit()
                self.console.CPU.scanline = 0
