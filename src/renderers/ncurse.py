# not working yet just here

from asciimatics.scene import Scene
from asciimatics.screen import Screen
import numpy as np

class NcurseRenderer:
    class NormalLayer:
        def __init__(self):
            self.layer = np.zeros([256,240], dtype=object)
                     
        def clear(self):
            self.layer = np.zeros([256,240], dtype=object)

        def blit(self, element='#', position=(0,0), color=(0,0,0)):
            pass

        def read(self, x, y):
            value = self.layer[x][y]
            return value

        def write(self, x, y, value):
            self.layer[x][y]=value

    def __init__(self):
        self.layer_order = ['LAYER_B', 'LAYER_A', 'DEBUG_LAYER']
        try:
            self.LAYER_B = NcurseRenderer.NormalLayer()
            self.LAYER_A = NcurseRenderer.NormalLayer()
            self.DEBUG_LAYER = NcurseRenderer.NormalLayer()
            self.layers = [
                asciimatics.Cycle(
                    self.SCREEN,
                    self.LAYER_B,
                    0
                ),
                asciimatics.Cycle(
                    self.SCREEN,
                    self.LAYER_A,
                    0
                ),
                asciimatics.Cycle(
                    self.SCREEN,
                    self.DEBUG_LAYER,
                    0
                )
            ]  
        except:
           print ("Initialize Video Error with Ncurse as Renderer")
        super(NcurseRenderer, self).__init__()
    
    def main(self, screen):
        self.SCREEN = screen   
        self.reset()

    def reset(self):
        self.clear()
        self.blit()
        
    def clear(self):
        Screen.wrapper(self.main, catch_interrupt=False)

    def blit(self):
        tl = self.layer_order.__len__()
        i=0
        while i < tl:
            l=getattr(self, self.layer_order[i])
            for k,v in np.ndenumerate(l):
                self.SCREEN.print_at('#', k[0], k[1], colour=v, bg=0)
            del l
            i+=1        
        self.SCREEN.refresh()
        self.SCREEN.play(Scene(self.layers, 500))

        