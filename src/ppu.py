import pygame
import numpy as np
class ppu:

    def __init__(self, cpu, cartridge):
        self.cpu = cpu

        self.VRAM = [np.uint8(0x00)] * 0x10000
        self.SPRRAM = [np.uint8(0x00)] * 0x100

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
        self.VBlank = False
        self.VRAMAddress = 0
        self.VRAMBuffer = 0
        self.firstWrite = True
        self.ppuScrollX = 0
        self.ppuScrollY = 0
        self.ppuStarted = 0

        self.ppuMirroring = 0
        self.addressMirroring = 0

        self.matrix = []

        self.cart = cartridge
        self.initMemory()
        self.setMirroring(self.cart.mirror)

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

    def initMemory(self):
        #for k,v in enumerate(self.cart.chrRomData):
        maxdata = len(self.cart.chrRomData)
        k = 0
        while k < maxdata:
            v=self.cart.chrRomData[k]
            self.dmaVRAMWrite(k, v)
            k+=1
        pygame.init()

        try:
            self.screen = pygame.display.set_mode((256, 240))
            self.layerB = pygame.Surface((256,240))
            self.layerA = pygame.Surface((256,240), pygame.SRCALPHA)
            self.debugLayer = pygame.Surface((256,240), pygame.SRCALPHA)
            self.layerB.fill((0, 0, 0))
            self.layerA.fill((0, 0, 0, 0))
            self.debugLayer.fill((0,0,0,0))
            self.screen.blit(self.layerB, (0,0))
            self.screen.blit(self.layerA, (0,0))
            self.screen.blit(self.debugLayer, (0,0))
            pygame.display.flip()
        except:
            print ("Initialize Video Error")

    def dmaVRAMWrite(self, address, value):
        self.VRAM[address] = value

    def dmaVRAMRead(self, address):
        value = self.VRAM[address]
        return value


    def dmaSPRRAMWrite(self, address, value):
        self.SPRRAM[address] = value

    def dmaSPRRAMRead(self, address):
        value = self.SPRRAM[address]
        return value

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
            self.dmaVRAMWrite(self.VRAMAddress + self.addressMirroring, value)
            self.dmaVRAMWrite(self.VRAMAddress, value)
        # Color Pallete write mirroring.
        elif self.VRAMAddress >= 0x3F00 and self.VRAMAddress < 0x3F20:
            if self.VRAMAddress == 0x3F00 or self.VRAMAddress == 0x3F10:
                self.dmaVRAMWrite(0x3F00, value)
                self.dmaVRAMWrite(0x3F04, value)
                self.dmaVRAMWrite(0x3F08, value)
                self.dmaVRAMWrite(0x3F0C, value)
                self.dmaVRAMWrite(0x3F10, value)
                self.dmaVRAMWrite(0x3F14, value)
                self.dmaVRAMWrite(0x3F18, value)
                self.dmaVRAMWrite(0x3F1C, value)
            else:
                self.dmaVRAMWrite(self.VRAMAddress, value)

        self.VRAMAddress += self.incrementAddress

    # process register 0x2007 (read)
    def readVRAM(self):
        value = 0
        address = self.VRAMAddress & 0x3FFF
        if address >= 0x3F00 and address < 0x4000:
            address = 0x3F00 + (address & 0xF)
            self.VRAMBuffer = self.dmaVRAMRead(address)
            value = self.dmaVRAMRead(address)
        elif address < 0x3F00:
            value = self.VRAMBuffer
            self.VRAMBuffer = self.dmaVRAMRead(address)
        self.VRAMAddress += self.incrementAddress

        return value

    def writeSprRam(self, value):
        self.dmaSPRRAMWrite(self.spriteRamAddr,value)
        self.spriteRamAddr = (self.spriteRamAddr + 1) & 0xFF

    def writeSprRamDMA(self, value):
        address = value * 0x100

        i=0
        while i < 256:
            self.dmaSPRRAMWrite(i, self.cpu.dmaRAMRead(address))
            address += 1
            i+=1

    def readStatusFlag(self):
        value = 0
        value |= (self.vRamWrites << 4)
        value |= (self.scanlineSpriteCount << 5)
        value |= (self.sprite0Hit << 6)
        value |= (int(self.VBlank) << 7)

        self.firstWrite = True
        self.VBlank = False

        return value

    def doScanline(self):

        if self.showBackground:
            self.drawBackground()

        if self.showSprites:
            self.drawSprites()
            

    def drawBackground(self):
        matrix = pygame.PixelArray(self.layerB)
        tileY = int(self.cpu.scanline / 8)
        Y = int(self.cpu.scanline % 8)

        maxTiles = 32
        if (self.ppuScrollX % 8) != 0:
            maxTiles = 33

        currentTile = int(self.ppuScrollX / 8)
        v = int(self.nameTableAddress + currentTile)
        pixel = 0

        i=0 if self.clippingBackground else 1
        while i < maxTiles:

            fromByte = 0
            toByte = 8

            ppuScrollFlag = (self.ppuScrollX %8)
            if ppuScrollFlag != 0:
                if i == 0:
                    toByte = 7 - (ppuScrollFlag)
                if i == (maxTiles - 1):
                    fromByte = 8 - (ppuScrollFlag)

            ptrAddress = self.dmaVRAMRead(v + int(tileY*0x20))
            pattern1 = self.dmaVRAMRead(self.backgroundPatternTable + (ptrAddress*16) + Y)
            pattern2 = self.dmaVRAMRead(self.backgroundPatternTable + (ptrAddress*16) + Y + 8)
            # blockX e blockY sao as coordenadas em relacao ao block
            blockX = i % 4
            blockY = tileY % 4
            block = int(i / 4) + (int(tileY / 4) * 8)
            addressByte = int((v & ~0x001F) + 0x03C0 + block)
            byteAttributeTable = self.dmaVRAMRead(addressByte)
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

            j=fromByte
            while j < toByte:
                bit1 = ((1 << j) & pattern1) >> j
                bit2 = ((1 << j) & pattern2) >> j
                colorIndexFinal = colorIndex
                colorIndexFinal |= ((bit2 << 1) | bit1)

                color = self.colorPallete[self.dmaVRAMRead(colorIndexFinal)]
                x = (pixel + ((j * (-1)) + (toByte - fromByte) - 1))
                y = self.cpu.scanline

                if (color != matrix[x][y]):
                    matrix[x][y] = color
                j+=1

            pixel += toByte - fromByte

            if (v & 0x001f) == 31:
                v &= ~0x001F
                #v ^= self.addressMirroring
                v ^= 0x400
            else:
                v += 1
            
            i+=1
        del matrix


    def drawSprites(self):
        numberSpritesPerScanline = 0
        Y = self.cpu.scanline % 8
        secondaryOAM = [0xFF] * 32
        indexSecondaryOAM = 0

        for currentSprite in range(0, 256, 4):
            spriteY = self.dmaSPRRAMRead(currentSprite)

            if numberSpritesPerScanline == 8:
                break

            if spriteY <= self.cpu.scanline < spriteY + self.spriteSize:
                for i in range(4):
                    secondaryOAM[indexSecondaryOAM + i] = self.dmaSPRRAMRead(currentSprite+i)
                indexSecondaryOAM += 4
                numberSpritesPerScanline += 1

        for currentSprite in range(28, -1, -4):
            spriteX = secondaryOAM[currentSprite + 3]
            spriteY = secondaryOAM[currentSprite]

            if spriteY >= 0xEF or spriteX >= 0xF9:
                continue

            currentSpriteAddress = currentSprite + 2
            flipVertical = secondaryOAM[currentSpriteAddress] & 0x80
            flipHorizontal = secondaryOAM[currentSpriteAddress] & 0x40

            Y = self.cpu.scanline - spriteY

            ptrAddress = secondaryOAM[currentSprite + 1]
            patAddress = self.spritePatternTable + (ptrAddress * 16) + ((7 - Y) if flipVertical else Y)
            pattern1 = self.dmaVRAMRead(patAddress)
            pattern2 = self.dmaVRAMRead(patAddress + 8)
            colorIndex = 0x3F10

            colorIndex |= ((secondaryOAM[currentSprite +2] & 0x3) << 2)

            j=0
            while j < 8:
                if flipHorizontal:
                    colorIndexFinal = (pattern1 >> j) & 0x1
                    colorIndexFinal |= ((pattern2 >> j) & 0x1 ) << 1
                else:
                    colorIndexFinal = (pattern1 >> (7 - j)) & 0x1
                    colorIndexFinal |= ((pattern2 >> (7 - j)) & 0x1) << 1

                colorIndexFinal += colorIndex
                if (colorIndexFinal % 4) == 0:
                    colorIndexFinal = 0x3F00
                color = self.colorPallete[(self.dmaVRAMRead(colorIndexFinal) & 0x3F)]

                # Add Transparency
                if color == self.colorPallete[self.dmaVRAMRead(0x3F10)]:
                    color += (0,)

                pygame.Surface.set_at(self.layerA, (spriteX + j, spriteY + Y), color)

                if self.showBackground and not(self.spriteHitOccured) and currentSprite == 0 and pygame.Surface.get_at(self.layerA, (spriteX + j, spriteY + Y)) == color:
                    self.sprite0Hit = True
                    self.spriteHitOccured = True
                j+=1

    def enterVBlank(self):
        if self.NMI:
            self.cpu.doNMI()

        self.VBlank = True
        self.screen.blit(self.layerB, (0,0))
        self.screen.blit(self.layerA, (0,0))
        self.screen.blit(self.debugLayer, (0,0))
        pygame.display.flip()
    def exitVBlank(self):
        self.VBlank = False
        self.debugLayer.fill((0,0,0,0))
        self.layerA.fill((0,0,0,0))
        self.layerB.fill((0,0,0))
        pygame.display.flip()

    def debugMsg(self, msg):
        self.debugLayer.fill((0,0,0,0))
        font = pygame.font.Font(pygame.font.get_default_font(), 8)
        self.debugLayer.blit(font.render(msg, False, (255, 255, 255, 1), (0,0,0,0)),(4,220))