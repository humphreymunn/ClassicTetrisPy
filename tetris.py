
import tkinter as tk
import time
import random

""" TODO:
    - 3 different frames rather than 1
    - Menubar and title
    - add more block shapes
    - score
"""

GRID_SIZE = 25
GAME_SIZE = (500,500)

block_shapes = {
    'long_block': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),(GRID_SIZE,GRID_SIZE*4-GRID_SIZE),(0,GRID_SIZE*4-GRID_SIZE)],
    'long_block_rotate': [(-GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE*2,GRID_SIZE*3),(-GRID_SIZE*2,GRID_SIZE*3)]
}

class Tetris:
    def __init__(self,master):
        self._master = master
        self._canvas = tk.Canvas(master,width=GAME_SIZE[0],height=GAME_SIZE[1]) #Game view canvas
        self._canvas.pack(fill='both',expand=True)
        self._blocks = [] #Blocks currently in the game
        self.add_block('long_block','red',4)
        self._master.bind('<Key>',self.move_block)
        self._game_speed = 1000
        self.descend_blocks()

    def add_block(self,shape,colour,x_pos):
        
        self._blocks.append(Block(self._canvas,shape,colour,GRID_SIZE*x_pos))

    def move_block(self,event):
        key = event.keysym
        if len(self._blocks) > 0:
            block_to_move = False
            for block in self._blocks:
                if block._frozen > 0:
                    block_to_move = block
                    break
            if block_to_move != False:
                if key == "Left":
                    block_to_move.move((-GRID_SIZE,0),self._blocks)
                elif key == "Right":
                    block_to_move.move((GRID_SIZE,0),self._blocks)
                elif key == "Down":
                    block_to_move.move((0,GRID_SIZE),self._blocks)
                    #self._canvas.delete(self._blocks[0])
                    #del self._blocks[0]
                elif key == 'z' or key == 'x':
                    block_to_move.rotate(0,self._blocks)
            else:
                rgb = ''
                for i in range(6):
                    rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
                    
                self.add_block('long_block','#' + rgb, int(random.random()*20))
    def descend_blocks(self):
        self._master.after(self._game_speed,self.descend_blocks)
        block_to_move = False
        for block in self._blocks:
            if block._frozen > 0:
                block_to_move = block
                break
        if block_to_move != False: block_to_move.move((0,GRID_SIZE),self._blocks)
        else:
            rgb = ''
            for i in range(6):
                rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
                
            self.add_block('long_block','#' + rgb, int(random.random()*20))

class Block(object):
    
    def __init__(self,canvas,shape,colour,x_pos):
        self._canvas = canvas
        self._x_pos = x_pos
        self._y_pos = -GRID_SIZE
        self._shape = shape
        self._colour = colour
        self._block_shape = canvas.create_polygon(block_shapes[shape],fill=colour)
        self._canvas.move(self.get_block(),self._x_pos,0)
        self._frozen = 1

    def get_block(self):
        return self._block_shape

    def move(self,direction,blocks):

        dx,dy = direction
        
        if self._shape == 'long_block_rotate':
            if dy > 0 and self._y_pos >= GAME_SIZE[1]-GRID_SIZE*3:
                direction = (0,0)
                if self._frozen > 0: self._frozen -= 1
                
            if (dx > 0 and self._x_pos >= GAME_SIZE[0]-GRID_SIZE*2) or (dx < 0 and self._x_pos-GRID_SIZE*2 <= 0):
                direction = (0,0)

        else:
            if dy > 0 and self._y_pos >= GAME_SIZE[1]-GRID_SIZE*4:
                direction = (0,0)
                if self._frozen > 0: self._frozen -= 1
            if (dx > 0 and self._x_pos >= GAME_SIZE[0]-GRID_SIZE) or (dx < 0 and self._x_pos <= 0):
                direction = (0,0)

        can_move = True 
        if self._shape == 'long_block':
            
            if dy > 0:
                can_move = not(self.check_collision(blocks,(self._x_pos+1,self._y_pos + GRID_SIZE*4)))
                if not can_move and self._frozen > 0:
                    self._frozen -= 1
                    return
                
            elif dx > 0:
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos+GRID_SIZE,self._y_pos + GRID_SIZE*pos))

            elif dx < 0:
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos-GRID_SIZE+1,self._y_pos + GRID_SIZE*pos))
                
        elif self._shape == 'long_block_rotate':
            
            if dx > 0:
                can_move = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*2,self._y_pos + GRID_SIZE*2))
            elif dx < 0:
                can_move = not self.check_collision(blocks,(self._x_pos - GRID_SIZE*3,self._y_pos + GRID_SIZE*2))
            elif dy > 0:
                add = [1,0,0,GRID_SIZE-1] # readjustments
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*(pos-2) + add[pos],self._y_pos + GRID_SIZE*3))
                        
                if not can_move and self._frozen > 0:
                    self._frozen -= 1
                    return
        
        if can_move and self._frozen > 0:
            self._canvas.move(self.get_block(),direction[0],direction[1])
            self.update_position(direction)

    def check_collision(self,blocks,position):
        collision = False
        for block in blocks:
            if block != self:
                if not collision:
                    collision = block.at_position(position)
        return collision
                
    def update_position(self,dpos):
        self._x_pos += dpos[0]
        self._y_pos += dpos[1]

    def get_position(self):
        return (self._x_pos,self._y_pos)

    def at_position(self,position):
        
        if self._shape == 'long_block':

            if position[0] in range(self._x_pos,self._x_pos + GRID_SIZE) and (position[1] in range(self._y_pos,self._y_pos+GRID_SIZE*3+1)): return True
            else: return False
            
        elif self._shape == 'long_block_rotate':
            if position[0] in range(self._x_pos - GRID_SIZE*2,self._x_pos + GRID_SIZE*2+1) and position[1] == self._y_pos + GRID_SIZE*2: return True
            else: return False
                
    def rotate(self,deg,blocks):
        if self._frozen > 0:
            can_rotate = True
            if self._shape == 'long_block' and self._x_pos in range(GRID_SIZE * 2,GAME_SIZE[0]-GRID_SIZE):
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*(pos-2),self._y_pos+GRID_SIZE*2))

                if can_rotate:   
                    self._canvas.delete(self.get_block())
                    self._block_shape = self._canvas.create_polygon(block_shapes['long_block_rotate'],fill=self._colour)
                    self._shape = 'long_block_rotate'
                    self._canvas.move(self.get_block(),self._x_pos,self._y_pos)

            elif self._shape == 'long_block_rotate' and self._y_pos < 425:
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos,self._y_pos + GRID_SIZE*pos))
                if can_rotate:
                    self._canvas.delete(self.get_block())
                    self._block_shape = self._canvas.create_polygon(block_shapes['long_block'],fill=self._colour)
                    self._shape = 'long_block'
                    self._canvas.move(self.get_block(),self._x_pos,self._y_pos+GRID_SIZE)
            
if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
