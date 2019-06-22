
import tkinter as tk
import time



GRID_SIZE = 25
block_shapes = {
    'long_block': [0,0,GRID_SIZE,0,GRID_SIZE,GRID_SIZE*4,0,GRID_SIZE*4]
}

class Tetris:
    def __init__(self,master):
        self._master = master
        self._canvas = tk.Canvas(master,width=500,height=500)
        self._canvas.pack(fill='both',expand=True)
        self._blocks = []
        self._block1 = Block(self._canvas,'long_block','red')
        self._block2 = Block(self._canvas,'long_block','blue')
        self._blocks.extend([self._block1,self._block2])
        self._master.bind('<Key>',self.move_block)
        self._game_speed = 1000
        self.descend_blocks()

    def move_block(self,event):
        key = event.keysym
        if len(self._blocks) > 0:
            if key == "Left":
                self._canvas.move(self._blocks[0].get_block(),-GRID_SIZE,0)
            elif key == "Right":
                self._canvas.move(self._blocks[0].get_block(),GRID_SIZE,0)
            elif key == "Down":
                self._canvas.move(self._blocks[0].get_block(),0,GRID_SIZE)
                #self._canvas.delete(self._blocks[0])
                #del self._blocks[0]

    def descend_blocks(self):
        print('Block lowered')
        self._master.after(self._game_speed,self.descend_blocks)
        if len(self._blocks) > 0:
            for block in self._blocks:
                self._canvas.move(block.get_block(),0,30)

class Block(object):
    
    def __init__(self,canvas,shape,colour):
        self._block_shape = canvas.create_polygon(block_shapes[shape],fill=colour)

    def get_block(self):
        return self._block_shape


if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
