
import tkinter as tk
import time
import random

""" TODO:
    - 3 different frames rather than 1 (pack frame to right and left of canvas)
    - Menubar and title (obvious)
    - add more block shapes (add to block_shapes and test in tetris __init__ self.add_block())
    - score (obvious)
"""

GRID_SIZE = 25
GAME_SIZE = (500,500)

# Polygon points (top left is (0,0))
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
        self._game_speed = 100
        self.descend_blocks() # Start moving the blocks downwards each step

    def add_block(self,shape,colour,x_pos):
        """ Adds block object into game.
        Parameters:
            shape (str): the key for which block_shape to select.
            colour (str): colour of block
            x_pos (int): Which grid x position to spawn block (e.g. x_pos = 1 will spawn at the first grid)
        """
        self._blocks.append(Block(self._canvas,shape,colour,GRID_SIZE*x_pos))

    def move_block(self,event):
        """ Moves/rotates block that is not frozen. Also checks if block is frozen and then creates a new block
        with random hex colour.
        Parameters: event (key): Key event to move or rotate block.
        """
        key = event.keysym # change key event into a string containing key character
        if len(self._blocks) > 0:
            
            block_to_move = False
            # selects oldest block created that isn't frozen
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
                    #del self._blocks[0]
                elif key == 'z' or key == 'x':
                    block_to_move.rotate(0,self._blocks)
                    
            # If all blocks are frozen, create new block
            else:
                rgb = ''
                for i in range(6):
                    rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
                    
                self.add_block('long_block','#' + rgb, int(random.random()*20))
                
    def descend_blocks(self):
        """ Lowers block that isnt frozen by one grid position every step. """

        # Call this function to itself every step (game_speed)
        self._master.after(self._game_speed,self.descend_blocks)
        
        block_to_move = False
        # selects oldest block created that isn't frozen
        for block in self._blocks:
            if block._frozen > 0:
                block_to_move = block
                break
        # Move block down one grid pos
        if block_to_move != False: block_to_move.move((0,GRID_SIZE),self._blocks)
        # If all blocks frozen create a new one
        else:
            rgb = ''
            for i in range(6):
                rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
                
            self.add_block('long_block','#' + rgb, int(random.random()*20))

class Block(object):
    """ this is a B l o c c"""
    def __init__(self,canvas,shape,colour,x_pos):
        """ Parameters:
                canvas (tk.Canvas): game canvas to draw block into.
                shape (str): the key for which block_shape to select.
                colour (str): colour of block
                x_pos (int): Which x position to spawn block
        """
        self._canvas = canvas
        self._x_pos = x_pos
        self._y_pos = -GRID_SIZE # Top of game window
        self._shape = shape
        self._colour = colour
        self._block_shape = canvas.create_polygon(block_shapes[shape],fill=colour)
        self._canvas.move(self.get_block(),self._x_pos,0)
        self._frozen = 2 # 2 when unfrozen, 1 when 1 step, <= 0 if frozen

    def get_block(self):
        return self._block_shape #polygon shape

    def move(self,direction,blocks):
        """ Disgusting collision stuff >:( """
        
        dx,dy = direction

        # If block is on edge of game screen, don't move and make frozen if block reached bottom y value.
        
        if self._shape == 'long_block_rotate':
            if dy > 0 and self._y_pos >= GAME_SIZE[1]-GRID_SIZE*3:
                direction = (0,0)
                if self._frozen > 0: self._frozen -= 1
                
            if (dx > 0 and self._x_pos >= GAME_SIZE[0]-GRID_SIZE*2) or (dx < 0 and self._x_pos-GRID_SIZE*2 <= 0):
                direction = (0,0)

        elif self._shape == 'long_block':
            if dy > 0 and self._y_pos >= GAME_SIZE[1]-GRID_SIZE*4:
                direction = (0,0)
                if self._frozen > 0: self._frozen -= 1
            if (dx > 0 and self._x_pos >= GAME_SIZE[0]-GRID_SIZE) or (dx < 0 and self._x_pos <= 0):
                direction = (0,0)

        
        can_move = True

        # Test if blocks are in the way of new position (where block is moving). If so, set can_move = False
        # and if there is a block underneath, freeze block.
        
        if self._shape == 'long_block':
            
            if dy > 0:
                # Test position below the long block, and if there is something there then freeze block.
                can_move = not(self.check_collision(blocks,(self._x_pos+1,self._y_pos + GRID_SIZE*4)))
                if not can_move and self._frozen > 0:
                    self._frozen -= 1
                    return
                
            elif dx > 0:
                # Test position to the right of each of the 4 squares that make up the long block.
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos+GRID_SIZE,self._y_pos + GRID_SIZE*pos))

            elif dx < 0:
                # Test position to the left of each of the 4 squares that make up the long block.
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos-GRID_SIZE+1,self._y_pos + GRID_SIZE*pos))
                
        elif self._shape == 'long_block_rotate':
            
            if dx > 0:
                # Test position to the right of the long block.
                can_move = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*2,self._y_pos + GRID_SIZE*2))

            elif dx < 0:
                # Test position to the left of the long block.
                can_move = not self.check_collision(blocks,(self._x_pos - GRID_SIZE*3,self._y_pos + GRID_SIZE*2))

            elif dy > 0:
                add = [1,0,0,GRID_SIZE-1] # readjustments
                # Test position below each of the 4 squares that make up the long block.
                # Readjustments used to make collisions more accurate.
                for pos in range(4):
                    if can_move:
                        can_move = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*(pos-2) + add[pos],self._y_pos + GRID_SIZE*3))

                # if something is below the block, freeze block.
                if not can_move and self._frozen > 0:
                    self._frozen -= 1
                    return

        # If block will not collide and isn't frozen, move it in specified direction.
        if can_move and self._frozen > 0:
            self._canvas.move(self.get_block(),direction[0],direction[1])
            self.update_position(direction)

    def check_collision(self,blocks,position):
        """ Loops through each block and checks if there is a collision with the given position.
            Parameters:
                blocks (list): List of blocks in the game to iterate over.
                position (tuple x,y): Game position to check.
        """
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
        """ Returns True if current block is at a given position.
            Parameters: position (tuple x,y): Game position to check.
        """
        x,y = position
        if self._shape == 'long_block':

            if x in range(self._x_pos,self._x_pos + GRID_SIZE)\
               and y in range(self._y_pos,self._y_pos+GRID_SIZE*3+1): return True
            
            else: return False
            
        elif self._shape == 'long_block_rotate':
            
            if x in range(self._x_pos - GRID_SIZE*2,self._x_pos + GRID_SIZE*2+1)\
               and y == self._y_pos + GRID_SIZE*2: return True

            else: return False
                
    def rotate(self,deg,blocks):
        """ Rotate block left/right depending on deg (degree), if there is no collision at the rotated position.
            Parameters:
                deg (int): 0 if anti-clockwise, 1 if clockwise
                blocks (list): List of blocks in the game.
        """
        
        if self._frozen > 0:
            can_rotate = True
            # If long block rotated is within the game boundaries
            if self._shape == 'long_block' and self._x_pos in range(GRID_SIZE * 2,GAME_SIZE[0]-GRID_SIZE):
                # Check if there is collision with the 4 squares of the rotated long block
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*(pos-2),self._y_pos+GRID_SIZE*2))

                # If no colision, undraw current polygon and redraw rotated
                if can_rotate:   
                    self._canvas.delete(self.get_block())
                    self._block_shape = self._canvas.create_polygon(block_shapes['long_block_rotate'],fill=self._colour)
                    self._shape = 'long_block_rotate'
                    self._canvas.move(self.get_block(),self._x_pos,self._y_pos)
                    # ^ This is used as rotated block auto generates at (0,0)

            # If long block is within the game boundaries
            elif self._shape == 'long_block_rotate' and self._y_pos < 425:
                # Check if there is collision with the 4 squares of the long block
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos,self._y_pos + GRID_SIZE*pos))

                # If no collision, undraw current polygon and redraw rotated
                if can_rotate:
                    self._canvas.delete(self.get_block())
                    self._block_shape = self._canvas.create_polygon(block_shapes['long_block'],fill=self._colour)
                    self._shape = 'long_block'
                    self._canvas.move(self.get_block(),self._x_pos,self._y_pos+GRID_SIZE)
                    # ^ This is used as rotated block auto generates at (0,0)

           
if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
