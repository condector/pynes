import pygame
from pygame import gfxdraw

class PygameRenderer:
    class NormalLayer:
        def __init__(self):
            self.layer = pygame.Surface((256,240))
            matrix = pygame.PixelArray(self.layer)
            matrix[:] = (255, 0, 0)
            del matrix            

        def clear(self):
            matrix = pygame.PixelArray(self.layer)
            matrix[:] = (0, 0, 0)
            del matrix

        def blit(self, element=None, position=(0,0), color=(0,0,0)):
            self.layer.blit(element, position, color)

        def read(self, x, y):
            matrix = pygame.PixelArray(self.layer)
            value = matrix[x,y]
            del matrix
            return value

        def write(self, x, y, value):
            gfxdraw.pixel(self.layer, x, y, value)

    class AlphaLayer:
        def __init__(self):
            self.layer = pygame.Surface((256,240), pygame.SRCALPHA) 
            matrix = pygame.PixelArray(self.layer)
            matrix[:] = (255, 0, 0, 0)
            del matrix            

        def clear(self):
            matrix = pygame.PixelArray(self.layer)
            matrix[:] = (0, 0, 0, 0)
            del matrix

        def blit(self, element=None, position=(0,0), color=(0,0,0,0)):
            self.layer.blit(element, position, color)

        def text(self, message=""):
            self.clear()
            font = pygame.font.Font(pygame.font.get_default_font(), 8)
            self.layer.blit(font.render(message, False, (255, 255, 255, 1), (0,0,0,0)),(4,220))

        def read(self, x, y):
            matrix = pygame.PixelArray(self.layer)
            value = matrix[x,y]
            del matrix
            return value

        def write(self, x, y, value):
            gfxdraw.pixel(self.layer, x, y, value)

    def __init__(self):
        self.layers = ["LAYER_B", "LAYER_A", "DEBUG_LAYER"]

        #try:
        pygame.init()   
        self.SCREEN = pygame.display.set_mode((256, 240))
        self.LAYER_B = PygameRenderer.NormalLayer()
        self.LAYER_A = PygameRenderer.AlphaLayer()
        self.DEBUG_LAYER = PygameRenderer.AlphaLayer()
        self.reset()
        #except:
        #   print ("Initialize Video Error with Pygame as Renderer")
        super(PygameRenderer, self).__init__()

    def reset(self):
        self.clear()
        self.blit()
        
    def clear(self):
        tl = self.layers.__len__()
        i=0
        while i < tl:
            l=getattr(self, self.layers[i])
            l.clear()
            del l
            i+=1

    def blit(self):
        tl = self.layers.__len__()
        i=0
        while i < tl:
            l=getattr(self, self.layers[i])
            self.SCREEN.blit(l.layer, (0,0))
            del l
            i+=1
        pygame.display.update()
        