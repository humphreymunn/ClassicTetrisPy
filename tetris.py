"""
Author: Humphrey Munn
2019

"""

import tkinter as tk
import time
import random

from tkinter import messagebox

""" TODO:
    - add T block
    - display score
    - Start/Game over screens?
    - Help pop up
    - improve keyboard input (e.g. down arrow slow)
    - Game over change ??
    - sounds
    - Glitch some blocks dont fall on row completion
    - Fix tkinter bind when window expand
"""

GRID_SIZE = 25
GAME_SIZE = (300,500)
GAME_SPEED_START = 200

shape_types = ('i_block','i_block_r1','o_block',\
               'l_block','l_block_r1','l_block_r2','l_block_r3',\
               'j_block','j_block_r1','j_block_r2','j_block_r3',\
               'z_block','z_block_r1','s_block','s_block_r1') # Shape type constants

# Polygon points (top left is (0,0))
block_shapes = {
    
    'i_block': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                   (GRID_SIZE,GRID_SIZE*4-GRID_SIZE),(0,GRID_SIZE*4-GRID_SIZE)],
    
    'i_block_r1': [(-GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE*2,GRID_SIZE*2),\
                          (GRID_SIZE*2,GRID_SIZE*3),(-GRID_SIZE*2,GRID_SIZE*3)],
    
    'o_block': [(0,-GRID_SIZE),(GRID_SIZE*2,-GRID_SIZE),\
                     (GRID_SIZE*2,GRID_SIZE*2 - GRID_SIZE),(0,GRID_SIZE*2 - GRID_SIZE)],

    'l_block': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                    (GRID_SIZE,GRID_SIZE*2-GRID_SIZE),(GRID_SIZE*2,GRID_SIZE*2-GRID_SIZE),\
                        (GRID_SIZE*2,GRID_SIZE*3-GRID_SIZE),(0,GRID_SIZE*3-GRID_SIZE)],
    
    'l_block_r1': [(-GRID_SIZE,0),(GRID_SIZE*2,0),\
                   (GRID_SIZE*2,GRID_SIZE),(0,GRID_SIZE),\
                   (0,GRID_SIZE*2),(-GRID_SIZE,GRID_SIZE*2)],

    'l_block_r2': [(-GRID_SIZE,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                       (GRID_SIZE,GRID_SIZE*3-GRID_SIZE),(0,GRID_SIZE*3-GRID_SIZE),\
                           (0,0),(-GRID_SIZE,0)],

    'l_block_r3': [(-GRID_SIZE,GRID_SIZE),(GRID_SIZE,GRID_SIZE),\
                   (GRID_SIZE,0),(GRID_SIZE*2,0),\
                   (GRID_SIZE*2,GRID_SIZE*2),(-GRID_SIZE,GRID_SIZE*2)],

    'j_block': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                (GRID_SIZE,GRID_SIZE*3-GRID_SIZE),(-GRID_SIZE,GRID_SIZE*3-GRID_SIZE),\
                (-GRID_SIZE,GRID_SIZE*2-GRID_SIZE),(0,GRID_SIZE*2-GRID_SIZE)],
    
    'j_block_r1': [(-GRID_SIZE,-GRID_SIZE),(0,-GRID_SIZE),\
                   (0,0),(GRID_SIZE*2,0),\
                   (GRID_SIZE*2,GRID_SIZE),(-GRID_SIZE,GRID_SIZE)],
    
    'j_block_r2': [(0,-GRID_SIZE),(GRID_SIZE*2,-GRID_SIZE),\
                   (GRID_SIZE*2,0),(GRID_SIZE,0),\
                   (GRID_SIZE,GRID_SIZE*2),(0,GRID_SIZE*2)],
    
    'j_block_r3': [(-GRID_SIZE,-GRID_SIZE),(GRID_SIZE*2,-GRID_SIZE),\
                   (GRID_SIZE*2,GRID_SIZE),(GRID_SIZE,GRID_SIZE),\
                   (GRID_SIZE,0),(-GRID_SIZE,0)],
    
    'z_block': [(-GRID_SIZE,0),(GRID_SIZE,0),\
                (GRID_SIZE,GRID_SIZE),(GRID_SIZE*2,GRID_SIZE),\
                (GRID_SIZE*2,GRID_SIZE*2),(0,GRID_SIZE*2),\
                (0,GRID_SIZE),(-GRID_SIZE,GRID_SIZE)],

    'z_block_r1': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                   (GRID_SIZE,GRID_SIZE),(0,GRID_SIZE),\
                   (0,GRID_SIZE*2),(-GRID_SIZE,GRID_SIZE*2),\
                   (-GRID_SIZE,0),(0,0)],
    
    's_block': [(0,0),(GRID_SIZE*2,0),\
                (GRID_SIZE*2,GRID_SIZE),(GRID_SIZE,GRID_SIZE),\
                (GRID_SIZE,GRID_SIZE*2),(-GRID_SIZE,GRID_SIZE*2),\
                (-GRID_SIZE,GRID_SIZE),(0,GRID_SIZE)],

    's_block_r1': [(0,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE),\
                   (GRID_SIZE,0),(GRID_SIZE*2,0),\
                   (GRID_SIZE*2,GRID_SIZE*2),(GRID_SIZE,GRID_SIZE*2),\
                   (GRID_SIZE,GRID_SIZE),(0,GRID_SIZE)]
}

class Tetris:
    def __init__(self,master):
        
        self._master = master
        master.title("Tetris")
        
        # Menubar: File -> *New Game *Help
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File",menu=file_menu)
        file_menu.add_command(label="New Game",command=self.restart_game)
        file_menu.add_command(label="Help")

        # Left frame
        self._lf = tk.Frame(master,width = 200,height = GAME_SIZE[1],bg='#BBBBBB')
        self._lf.pack(side=tk.LEFT)
        
        # Game canvas
        self._canvas = tk.Canvas(master,width=GAME_SIZE[0],height=GAME_SIZE[1]) #Game view canvas
        self._canvas.pack(side=tk.LEFT,fill='both',expand=True)

        # Right frame
        self._rf = tk.Frame(master,width = 200,height = GAME_SIZE[1],bg='#BBBBBB')
        self._rf.pack(side=tk.LEFT)
        
        self._master.bind('<Key>',self.move_block)

        self._paused = False
        self._game_over = False
        self.new_game()
        
        self.descend_blocks() # Start moving the blocks downwards each step
        
    def new_game(self):
        """ Initialises game."""
        self._blocks = [] #Blocks currently in the game
        self._paused = False
        self._game_over = False
        self.add_block()
        self._score = 0
        self.update_game_speed()

    def restart_game(self):
        """ Restarts game by removing blocks then reinitialising game."""
        for block in self._blocks:
            self._canvas.delete(block.get_block())
        self.new_game()

    def pause(self):
        """Toggles pause."""
        self._paused = not self._paused

    def update_game_speed(self):
        """Increases game speed by 4 steps every 10 scores."""
        self._game_speed = GAME_SPEED_START - 15*(self._score//5)
        # Cap game speed at 25
        if self._game_speed < 25: self._game_speed = 25

    def check_game_over(self):
        """ Check if any frozen blocks exist in the top row."""
        for block in self._blocks:
            for column in range(0,(GAME_SIZE[0])//GRID_SIZE):
                if not self._game_over:
                    if block._frozen == 0 and block.at_position((column*GRID_SIZE,0)):
                        self._game_over = True
                        self._paused = True
                        break
        if self._game_over:
            if messagebox.showinfo("Tetris", "GAME OVER"):
                self.restart_game()
                
        return self._game_over
            
    def add_block(self):
        """ Adds block object into game."""

        # Make sure there are no full rows and it is not game over
        self.check_rows()
        if not self._game_over: self.check_game_over()
        
        # Create block with random rgb colour and random shape
        rgb = '#'
        for i in range(6):
            rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])

        shape = random.choice([0,2,3,7,11,13])
        shape = shape_types[shape]
        colour = rgb

        # Chose random x position within game field
        x_pos = GRID_SIZE*int(random.random()*((GAME_SIZE[0]-GRID_SIZE*2) // GRID_SIZE)) + GRID_SIZE

        # Create block
        self._blocks.append(Block(self._canvas,shape,colour,x_pos))

    def move_block(self,event):
        """ Moves/rotates block that is not frozen. Also checks if block is frozen and then creates a new block
        with random hex colour.
        Parameters:
            event (key): Key event to move or rotate block.
        """
        if self.check_game_over(): return
        key = (event.keysym).upper() # change key event into a string containing key character

        if key == 'P':
            self.pause()
            print('pause',self._paused)
            return
        
        elif self._paused: return
        
        if len(self._blocks) > 0:
            
            block_to_move = False
            # selects oldest block created that isn't frozen
            for block in self._blocks:
                if block._frozen > 0:
                    block_to_move = block
                    break
                
            if block_to_move != False and block_to_move._control:
                if key == "LEFT":
                    block_to_move.move((-GRID_SIZE,0),self._blocks)
                elif key == "RIGHT":
                    block_to_move.move((GRID_SIZE,0),self._blocks)
                elif key == "DOWN":
                    block_to_move.move((0,GRID_SIZE),self._blocks)
                elif key == 'Z' or key == 'X':
                    block_to_move.rotate(0,self._blocks)
                    
            # If all blocks are frozen, create new block
            elif not block_to_move:
                self.add_block()
                
    def descend_blocks(self):
        """ Lowers blocks that arent frozen by one grid position every step. """
        
        # Call this function to itself every step (game_speed)
        self._master.after(self._game_speed,self.descend_blocks)

        if self._paused: return
        if self.check_game_over(): return
        
        blocks_to_move = [] # Descend all blocks that aren't frozen
        
        # adds unfrozen blocks to list
        for block in self._blocks:
            if block._frozen > 0:
                blocks_to_move.append(block)

        # Move each block down one grid pos
        if blocks_to_move != []:
            for block in blocks_to_move:
                block.move((0,GRID_SIZE),self._blocks)
        # If all blocks frozen create a new one
        else:
            rgb = ''
            for i in range(6):
                rgb += random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
                
            self.add_block()

    def check_rows(self):
        """ Checks each row in the game and removes each block in rows that are full, then adds to player's
            score depending on how many rows are cleared. """

        if len(self._blocks) == 0: return

        rows_full = 0 # Used to add to score, e.g. 2 rows full adds 2 to score
        blocks_to_delete = [] # Blocks that are in full rows
        
        # Loop through each row and column
        for row in range(0,GAME_SIZE[1]//GRID_SIZE):
            blocks_in_row = []
            row_columns_full = True # Originally set to true, and will stay true if all columns filled in row
            
            for column in range(0,(GAME_SIZE[0])//GRID_SIZE):
                if row_columns_full:
                    column_full = False # Check current column and set to true if there is a block at this position
                    for block in self._blocks:
                        block_at_position = block.at_position((column*GRID_SIZE,row*GRID_SIZE))
                        # If block is in row add it to blocks_in_row
                        if block_at_position and block not in blocks_in_row: blocks_in_row.append(block)

                        # If there is any block at this position, set column_full to True
                        if not column_full:
                            column_full = block_at_position
                            

                    # If no blocks are at this column, set columns_full false
                    if not column_full:
                        row_columns_full = False

            # If every column is full in row...
            if row_columns_full:
                rows_full += 1
                blocks_to_delete.extend(blocks_in_row)
                #print('row',row+1,'full')

        # If there are full rows, increase score, delete each block in those rows,
        # then descend each block
        if rows_full > 0:
            self._score += rows_full
            self.update_game_speed()
            print('score:',self._score)

            for deleted_block in blocks_to_delete:
                if deleted_block in self._blocks:
                    deleted_block._canvas.delete(deleted_block.get_block())
                    del self._blocks[self._blocks.index(deleted_block)]

            for block in self._blocks:
                block._frozen = 1
                block._control = False
                block.move((0,GRID_SIZE),self._blocks)

                    
                    
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
        self._control = True

    def get_block(self):
        return self._block_shape #polygon shape

    def check_boundaries(self,x_bounds,y_bounds):
        """ Check if a collision will occur with the edge of the game.
            Params:
                x_bounds (tuple): (dx,x_bound1,x_bound2)
                    dx (int): x direction
                    x_bound1 (int): left side of screen pos
                    x_bound2 (int): right side of screen pos
                y_bounds (tuple): (dy,y_bound)
                    dy (int): y direction
                    y_bound (int): bottom side of screen pos
        """
        if y_bounds[0] > 0 and self._y_pos >= y_bounds[1]:
            if self._frozen > 0: self._frozen -= 1
            return (0,0)
        
        elif (x_bounds[0] < 0 and self._x_pos <= x_bounds[1]) or \
             (x_bounds[0] > 0 and self._x_pos >= x_bounds[2]):
            return (0,0)

    def check_block_collisions(self,blocks,loop,dec_frozen,x_adj,y_adj,x_adj2,y_adj2,x_adj3,y_adj3,add):
        """ Check collisions around block when moving.
            Parameters:    F :(
                blocks (list): blocks in the game
                loop (int): amount of times to loop over collision checks
                dec_frozen (bool): if checking dy, this should be true so it will decrement frozen by 1
                x_adj (int): constant amount to adjust the x position
                y_adj (int): constant amount to adjust the y position
                x_adj2 (int): 0 or 1, ... linear amount to adjust the x position based on loops
                y_adj2 (int): linear amount to adjust the y position based on loops
                x_adj3 (int): 0 or 1, 1 if using adjustment list (add)
                y_adj3 (int): 0 or 1, 1 if using adjustment list (add)
                add (list): List of x/y adjustments based on loops
            Returns:
                0: if frozen decremented
                True: If block can move
                False: If block can't move
        """
            
        can_move = True
        if add == []:
            for i in range(loop):
                add.append(0)
        #print(add)
        
        for pos in range(loop):
            if can_move:
                can_move = not self.check_collision(blocks,(self._x_pos + x_adj + x_adj2*GRID_SIZE*pos + x_adj3*add[pos],\
                                                            self._y_pos + y_adj + y_adj2*GRID_SIZE*pos + y_adj3*add[pos]))
        if dec_frozen:
            if not can_move and self._frozen > 0:
                self._frozen -= 1
                return 0
            
        return can_move

    def move(self,direction,blocks):
        """ collision stuff >:( """
        
        dx,dy = direction

        # If block is on edge of game screen, don't move, and make frozen if block reached bottom y value.

        if self._shape == shape_types[0]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE),(dy,GAME_SIZE[1]-GRID_SIZE*4)
            
        elif self._shape == shape_types[1]:
            x_bound,y_bound = (dx,GRID_SIZE*2,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*4)

        elif self._shape == shape_types[2]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*2)

        elif self._shape in [shape_types[3],shape_types[9],shape_types[14]]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[4],shape_types[6]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[5],shape_types[7],shape_types[12]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[8],shape_types[10]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*2)

        elif self._shape in [shape_types[11],shape_types[13]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        else:
            x_bound,y_bound = (0,0,0),(0,0)

        if self.check_boundaries(x_bound,y_bound) == (0,0): direction = (0,0)

        can_move = True

        # Test if blocks are in the way of new position (where block is moving). If so, set can_move = False
        # and if there is a block underneath, freeze block.
        
        if self._shape == shape_types[0]:
            
            if dy > 0:
                can_move = self.check_block_collisions(blocks,1,True,1,GRID_SIZE*4,0,0,0,0,[])
                if can_move == 0: return
                
            elif dx > 0:
                can_move = self.check_block_collisions(blocks,4,False,GRID_SIZE,0,0,1,0,0,[])

            elif dx < 0:
                can_move = self.check_block_collisions(blocks,4,False,-GRID_SIZE+1,0,0,1,0,0,[])
                
        elif self._shape == shape_types[1]:
            
            if dx > 0:
                can_move = self.check_block_collisions(blocks,1,False,GRID_SIZE*2,GRID_SIZE*3,0,0,0,0,[])

            elif dx < 0:
                can_move = self.check_block_collisions(blocks,1,False,-GRID_SIZE*3+1,GRID_SIZE*3,0,0,0,0,[])

            elif dy > 0:
                add = [1,0,0,GRID_SIZE-1] # readjustments
                can_move = self.check_block_collisions(blocks,4,True,-GRID_SIZE*2,GRID_SIZE*4,1,0,1,0,add)
                if can_move == 0: return

        elif self._shape == shape_types[2]:

            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,0,0,1,0,0,[])
                
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,0,0,1,0,0,[])

            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1,GRID_SIZE*2,1,0,0,0,[])
                if can_move == 0: return

        elif self._shape == shape_types[3]:
            if dx > 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add)
                        
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,0,0,[])

            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1,GRID_SIZE*3,1,0,0,0,[])
                if can_move == 0: return
                        
        elif self._shape == shape_types[4]:
            if dx > 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add)
                
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2 + 1, GRID_SIZE,0,1,0,0,[])
                
            elif dy > 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1 - GRID_SIZE,GRID_SIZE*2,1,0,0,1,add)
                if can_move == 0: return

        elif self._shape == shape_types[5]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,0,0,[])

            elif dx < 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,1,0,add)
                                        
            elif dy > 0:
                add = [GRID_SIZE,GRID_SIZE*3] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,-GRID_SIZE+1,0,1,0,0,1,add)
                if can_move == 0: return

        elif self._shape == shape_types[6]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,0,0,[])

            elif dx < 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,0,GRID_SIZE,0,1,1,0,add)

            elif dy > 0:
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*3,1,0,0,0,[])
                if can_move == 0: return

        elif self._shape == shape_types[7]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,0,0,[])
                        
            elif dx < 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,1,0,add)

            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,0,[])
                if can_move == 0: return

        elif self._shape == shape_types[8]:
            if dx > 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add)
                
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2 + 1, GRID_SIZE,0,1,0,0,[])
                
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*2,1,0,0,0,[])
                if can_move == 0: return

        elif self._shape == shape_types[9]:
            if dx > 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add)

            elif dx < 0:
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,0,0,[])
                                        
            elif dy > 0:
                add = [GRID_SIZE*3,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,0,0,1,0,0,1,add)
                if can_move == 0: return
                
        elif self._shape == shape_types[10]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,0,0,[])

            elif dx < 0:
                add = [-GRID_SIZE*2,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,0,GRID_SIZE,0,1,1,0,add)

            elif dy > 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1 - GRID_SIZE,GRID_SIZE,1,0,0,1,add)
                if can_move == 0: return
                
        elif self._shape == shape_types[11]:
            if dx > 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add)

            elif dx < 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,GRID_SIZE,0,1,1,0,add)

            elif dy > 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add)
                if can_move == 0: return

        elif self._shape == shape_types[12]:
            if dx > 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add)

            elif dx < 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE*2,0,0,1,1,0,add)

            elif dy > 0:
                add = [0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add)
                if can_move == 0: return

        elif self._shape == shape_types[13]:
            if dx > 0:
                add = [GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE,GRID_SIZE,0,1,1,0,add)

            elif dx < 0:
                add = [0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,GRID_SIZE,0,1,1,0,add)

            elif dy > 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add)
                if can_move == 0: return

        elif self._shape == shape_types[14]:
            if dx > 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE*2,0,0,1,1,0,add)

            elif dx < 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,1,0,add)

            elif dy > 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,0,GRID_SIZE*3,1,0,0,1,add)
                if can_move == 0: return
                
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
        
        if self._shape == shape_types[0]:
            if x in range(self._x_pos,self._x_pos + GRID_SIZE)\
               and y in range(self._y_pos,self._y_pos+GRID_SIZE*4): return True
            
            else: return False
            
        elif self._shape == shape_types[1]:
            if x in range(self._x_pos - GRID_SIZE*2,self._x_pos + GRID_SIZE*2)\
               and y in range(self._y_pos + GRID_SIZE*3,self._y_pos + GRID_SIZE*4): return True

            else: return False

        elif self._shape == shape_types[2]:
            if x in range(self._x_pos,self._x_pos + GRID_SIZE*2) \
               and y in range(self._y_pos,self._y_pos+GRID_SIZE*2): return True
            
            else: return False

        elif self._shape == shape_types[3]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
               and y in range(self._y_pos,self._y_pos+GRID_SIZE*3)) or \
               (x in range(self._x_pos+GRID_SIZE,self._x_pos+GRID_SIZE*2)\
                and y in range(self._y_pos + GRID_SIZE*2,self._y_pos + GRID_SIZE*3)): return True
            
            else: return False

        elif self._shape == shape_types[4]:
            if (x in range(self._x_pos-GRID_SIZE,self._x_pos + GRID_SIZE*2)\
                and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos-GRID_SIZE,self._x_pos)\
                 and y in range(self._y_pos+GRID_SIZE*2,self._y_pos+GRID_SIZE*3)): return True

            else: return False

        elif self._shape == shape_types[5]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
                and y in range(self._y_pos,self._y_pos+GRID_SIZE*3)) or \
                (x in range(self._x_pos-GRID_SIZE,self._x_pos)\
                 and y in range(self._y_pos,self._y_pos + GRID_SIZE)): return True

            else: return False

        elif self._shape == shape_types[6]:
            if (x in range(self._x_pos-GRID_SIZE,self._x_pos + GRID_SIZE*2)\
                and y in range(self._y_pos+GRID_SIZE*2,self._y_pos+GRID_SIZE*3)) or \
                (x in range(self._x_pos+GRID_SIZE,self._x_pos+GRID_SIZE*2)\
                 and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)): return True
            
            else: return False

        elif self._shape == shape_types[7]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
               and y in range(self._y_pos,self._y_pos+GRID_SIZE*3)) or \
               (x in range(self._x_pos-GRID_SIZE,self._x_pos)\
                and y in range(self._y_pos + GRID_SIZE*2,self._y_pos + GRID_SIZE*3)): return True
            
            else: return False

        elif self._shape == shape_types[8]:
            if (x in range(self._x_pos-GRID_SIZE,self._x_pos + GRID_SIZE*2)\
                and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos-GRID_SIZE,self._x_pos)\
                 and y in range(self._y_pos,self._y_pos+GRID_SIZE)): return True

            else: return False

        elif self._shape == shape_types[9]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
                and y in range(self._y_pos,self._y_pos+GRID_SIZE*3)) or \
                (x in range(self._x_pos+GRID_SIZE,self._x_pos+GRID_SIZE*2)\
                 and y in range(self._y_pos,self._y_pos + GRID_SIZE)): return True

            else: return False

        elif self._shape == shape_types[10]:
            if (x in range(self._x_pos-GRID_SIZE,self._x_pos + GRID_SIZE*2)\
                and y in range(self._y_pos,self._y_pos+GRID_SIZE)) or \
                (x in range(self._x_pos+GRID_SIZE,self._x_pos+GRID_SIZE*2)\
                 and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)): return True

            else: return False

        elif self._shape == shape_types[11]:
            if (x in range(self._x_pos-GRID_SIZE,self._x_pos + GRID_SIZE)\
                and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos,self._x_pos+GRID_SIZE*2)\
                 and y in range(self._y_pos+GRID_SIZE*2,self._y_pos+GRID_SIZE*3)): return True

            else: return False

        elif self._shape == shape_types[12]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
                and y in range(self._y_pos,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos-GRID_SIZE,self._x_pos)\
                 and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*3)): return True

            else: return False

        elif self._shape == shape_types[13]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE*2)\
                and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos-GRID_SIZE,self._x_pos+GRID_SIZE)\
                 and y in range(self._y_pos+GRID_SIZE*2,self._y_pos+GRID_SIZE*3)): return True

            else: return False

        elif self._shape == shape_types[14]:
            if (x in range(self._x_pos,self._x_pos + GRID_SIZE)\
                and y in range(self._y_pos,self._y_pos+GRID_SIZE*2)) or \
                (x in range(self._x_pos+GRID_SIZE,self._x_pos+GRID_SIZE*2)\
                 and y in range(self._y_pos+GRID_SIZE,self._y_pos+GRID_SIZE*3)): return True

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
            if self._shape == shape_types[0] and self._x_pos in range(GRID_SIZE * 2,GAME_SIZE[0]-GRID_SIZE):
                # Check if there is collision with the 4 squares of the rotated long block
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos + GRID_SIZE*(pos-2),self._y_pos+GRID_SIZE*3))
                new_shape = shape_types[1]

            # If long block is within the game boundaries
            elif self._shape == shape_types[1] and self._y_pos < 425:
                # Check if there is collision with the 4 squares of the long block
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos,self._y_pos + GRID_SIZE*pos))
                new_shape = shape_types[0]

            # as above
            elif self._shape == shape_types[3] and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(0,0),(-3*GRID_SIZE,GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+GRID_SIZE*(pos-1)+add[pos][0],self._y_pos + add[pos][1] + GRID_SIZE*2))
                new_shape = shape_types[4]

            elif self._shape == shape_types[4]:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-3*GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos+GRID_SIZE*pos+add[pos][1]))
                new_shape = shape_types[5]

            elif self._shape == shape_types[5] and self._x_pos <= GAME_SIZE[0]-GRID_SIZE*2:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+GRID_SIZE*(pos-1)+add[pos][0],self._y_pos+add[pos][1]+GRID_SIZE*2))
                new_shape = shape_types[6]

            elif self._shape == shape_types[6]:
                add = [(0,0),(0,0),(0,0),(GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos + GRID_SIZE*pos + add[pos][1]))
                new_shape = shape_types[3]

            elif self._shape == shape_types[7] and self._x_pos <= GAME_SIZE[0]-GRID_SIZE*2:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+GRID_SIZE*(pos-1)+add[pos][0],self._y_pos + add[pos][1] + GRID_SIZE*2))
                new_shape = shape_types[8]

            elif self._shape == shape_types[8] and self._y_pos <= GAME_SIZE[1]-GRID_SIZE*3:
                add = [(0,0),(0,0),(0,0),(GRID_SIZE,-3*GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos+GRID_SIZE*pos+add[pos][1]))
                new_shape = shape_types[9]

            elif self._shape == shape_types[9] and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+GRID_SIZE*(pos-1)+add[pos][0],self._y_pos+add[pos][1]+GRID_SIZE*2))
                new_shape = shape_types[10]

            elif self._shape == shape_types[10] and self._y_pos <= GAME_SIZE[1]-GRID_SIZE*3:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos + GRID_SIZE*pos + add[pos][1]))
                new_shape = shape_types[7]

            elif self._shape == shape_types[11]:
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(-GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos + GRID_SIZE*pos + add[pos][1]))  
                new_shape = shape_types[12]

            elif self._shape == shape_types[12] and self._x_pos <= GAME_SIZE[1]-GRID_SIZE:
                add = [(0,0),(0,0),(-GRID_SIZE,GRID_SIZE),(-GRID_SIZE,GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos-GRID_SIZE+GRID_SIZE*pos+add[pos][0],self._y_pos + GRID_SIZE + add[pos][1]))     
                new_shape = shape_types[11]

            elif self._shape == shape_types[13]:
                add = [(0,0),(0,0),(GRID_SIZE,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos+add[pos][0],self._y_pos + GRID_SIZE*pos + add[pos][1]))  
                new_shape = shape_types[14]

            elif self._shape == shape_types[14] and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(-GRID_SIZE,-GRID_SIZE)]
                for pos in range(4):
                    if can_rotate:
                        can_rotate = not self.check_collision(blocks,(self._x_pos-GRID_SIZE+GRID_SIZE*pos+add[pos][0],self._y_pos + GRID_SIZE*2 + add[pos][1]))     
                new_shape = shape_types[13]
                
            else:
                new_shape = shape_types[0]
                can_rotate = False

            # If no colision, undraw current polygon and redraw rotated
            if can_rotate:   
                self._canvas.delete(self.get_block())
                self._block_shape = self._canvas.create_polygon(block_shapes[new_shape],fill=self._colour)
                self._shape = new_shape
                self._canvas.move(self.get_block(),self._x_pos,self._y_pos+GRID_SIZE)
                # ^ This is used as rotated block auto generates at (0,0)
                    
if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
