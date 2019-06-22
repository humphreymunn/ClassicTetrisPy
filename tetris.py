
import tkinter as tk
import time

""" TODO:
    - 3 different frames rather than 1
    - Menubar and title
    - Stop rotation depending on position
    - add more block shapes
"""

GRID_SIZE = 25
block_shapes = {
    'long_block': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),(GRID_SIZE,GRID_SIZE*4-GRID_SIZE),(0,GRID_SIZE*4-GRID_SIZE)],
    'long_block2': [(-GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE*2,GRID_SIZE*3),(-GRID_SIZE*2,GRID_SIZE*3)]
}

class Tetris:
    def __init__(self,master):
        self._master = master
        self._canvas = tk.Canvas(master,width=500,height=500)
        self._canvas.pack(fill='both',expand=True)
        self._blocks = []
        self._block1 = Block(self._canvas,'long_block','red',GRID_SIZE*4)
        self._block2 = Block(self._canvas,'long_block','blue',GRID_SIZE*6)
        self._blocks.extend([self._block1,self._block2])
        self._master.bind('<Key>',self.move_block)
        self._game_speed = 1000
        self.descend_blocks()

    def move_block(self,event):
        key = event.keysym
        if len(self._blocks) > 0:
            if key == "Left":
                self._blocks[0].move((-GRID_SIZE,0))
            elif key == "Right":
                self._blocks[0].move((GRID_SIZE,0))
            elif key == "Down":
                self._blocks[0].move((0,GRID_SIZE))
                #self._canvas.delete(self._blocks[0])
                #del self._blocks[0]
            elif key == 'z' or key == 'x':
                self._blocks[0].rotate(0)
    def descend_blocks(self):
        self._master.after(self._game_speed,self.descend_blocks)
        if len(self._blocks) > 0:
            for block in self._blocks:
                block.move((0,GRID_SIZE))

class Block(object):
    
    def __init__(self,canvas,shape,colour,x_pos):
        self._canvas = canvas
        self._x_pos = x_pos
        self._y_pos = -GRID_SIZE
        self._shape = shape
        self._colour = colour
        self._block_shape = canvas.create_polygon(block_shapes[shape],fill=colour)
        self._canvas.move(self.get_block(),self._x_pos,0)

    def get_block(self):
        return self._block_shape

    def move(self,direction):

        if self._shape == 'long_block2':
            if direction[1] > 0 and self._y_pos >= 425:
                direction = (direction[0],0)
            if (direction[0] > 0 and self._x_pos >= 475) or (direction[0] < 0 and self._x_pos <= 0):
                direction = (0,direction[1])

        else:
            if direction[1] > 0 and self._y_pos >= 400:
                direction = (direction[0],0)
            if (direction[0] > 0 and self._x_pos >= 475) or (direction[0] < 0 and self._x_pos <= 0):
                direction = (0,direction[1])
            
        self._canvas.move(self.get_block(),direction[0],direction[1])
        self.update_position(direction)

    def update_position(self,dpos):
        self._x_pos += dpos[0]
        self._y_pos += dpos[1]
        print(self.get_position())

    def get_position(self):
        return (self._x_pos,self._y_pos)

    def rotate(self,deg):
        
        if self._shape == 'long_block':
            self._canvas.delete(self.get_block())
            self._block_shape = self._canvas.create_polygon(block_shapes['long_block2'],fill=self._colour)
            self._shape = 'long_block2'
            self._canvas.move(self.get_block(),self._x_pos,self._y_pos)


        elif self._shape == 'long_block2':
            self._canvas.delete(self.get_block())
            self._block_shape = self._canvas.create_polygon(block_shapes['long_block'],fill=self._colour)
            self._shape = 'long_block'
            self._canvas.move(self.get_block(),self._x_pos,self._y_pos+GRID_SIZE)
            
if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
