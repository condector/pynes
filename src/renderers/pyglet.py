# not working just here
import pyglet
from pyglet.gl import *
import numpy as np

class PygletRenderer:
    class NormalLayer:
        def __init__(self):
            self.matrix = np.zeros([256,240], dtype=object)
            self.layer = pyglet.image.ImageData(256, 240, "RGB", bytes(self.matrix))
            
        def clear(self):
            self.matrix = np.zeros([256,240], dtype=object)

        def blit(self, element=None, position=(0,0), color=(0,0,0)):
            self.layer = pyglet.image.ImageData(256, 240, "RGB", bytes(self.matrix))

        def read(self, x, y):
            value = self.matrix[x,y]
            return value

        def write(self, x, y, value):
            self.matrix[x,y] = value

    class AlphaLayer:
        def __init__(self):
            self.matrix = np.empty([256,240], dtype=object)
            self.clear()
            self.layer = pyglet.image.ImageData(256, 240, "RGBA", bytes(self.matrix))
            
        def clear(self):
            for k,v in np.ndenumerate(self.matrix):
                self.matrix[k] = (0,0,0,0)

        def blit(self, element=None, position=(0,0), color=(0,0,0,0)):
            self.layer = pyglet.image.ImageData(256, 240, "RGBA", bytes(self.matrix))

        def text(self, message=""):
            label = pyglet.text.Label(message,
                          font_size=8,
                          x=4, y=220,
                          anchor_x='left', anchor_y='center')
            label.draw()

        def read(self, x, y):
            value = self.matrix[x,y]
            return value

        def write(self, x, y, value):
            self.matrix[x,y] = value

    def __init__(self):
        self.layers = ["LAYER_B", "LAYER_A", "DEBUG_LAYER"]

        #try:
        self.SCREEN = pyglet.window.Window()
        self.SCREEN.set_size(256, 240)
        self.SCREEN.set_visible(True)
        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.LAYER_B = PygletRenderer.NormalLayer()
        self.LAYER_A = PygletRenderer.AlphaLayer()
        self.DEBUG_LAYER = PygletRenderer.AlphaLayer()
        #except:
           #print ("Initialize Video Error with Pygame as Renderer")
        super(PygletRenderer, self).__init__()

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
        #self.SCREEN.clear()

    def blit(self):
        self.LAYER_B.blit(0,0,0)
        self.LAYER_B.layer.blit(0,0,0)
        self.SCREEN.flip()
        #self.LAYER_A.blit(0,0,-0.1)
        #self.DEBUG_LAYER.blit(0,0,0)
        