from cartridge import romLoader
from cpu import CPU
from ppu import PPU
import threading
import pygame
import sys


class Console:
    def __init__(self):
        romPath = sys.argv[1]

        self.cartridge = romLoader(romPath)
        self.RENDERER_TYPE = "pygame"
        self.THREAD_MODE = "SINGLE"

        try:
            self.cartridge.load()
        except:
            raise Exception("Couldn't load cartridge")

        try:
            self.CPU = CPU(self)
        except:
            raise Exception("Couldn't initialize CPU") 
        #try:      
        self.PPU = PPU(self)
        #except:
        #    raise Exception("Couldn't initialize PPU")      

    def powerOn(self):
        if self.THREAD_MODE == "SINGLE":
            self.PPU.run()
            self.CPU.run()
        else:
            self.CPU.start()
            self.PPU.start()


if __name__ == '__main__':
    console = Console()
    console.powerOn()