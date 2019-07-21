"""
Author: Humphrey Munn
2019
"""

import tkinter as tk
import time
import random

from tkinter import messagebox

""" TODO:
    - Start/Game over screens?
    - sounds
    - Glitch some blocks dont fall on row completion
    - Improved look
"""

GRID_SIZE = 25
GAME_SIZE = (300,500)
GAME_SPEED_START = 200

shape_types = ('i_block','i_block_r1','o_block',\
               'l_block','l_block_r1','l_block_r2','l_block_r3',\
               'j_block','j_block_r1','j_block_r2','j_block_r3',\
               'z_block','z_block_r1','s_block','s_block_r1',\
               't_block','t_block_r1','t_block_r2','t_block_r3') # Shape type constants

gs = GRID_SIZE # for drawing polygons (less text)
# Polygon points (top left is (0,0))
block_shapes = {
    
    'i_block': [(0,-gs),(gs,-gs),\
                   (gs,gs*4-gs),(0,gs*4-gs)],
    
    'i_block_r1': [(-gs*2,gs*2),(gs*2,gs*2),\
                          (gs*2,gs*3),(-gs*2,gs*3)],
    
    'o_block': [(0,-gs),(gs*2,-gs),\
                     (gs*2,gs*2 - gs),(0,gs*2 - gs)],

    'l_block': [(0,-gs),(gs,-gs),\
                    (gs,gs*2-gs),(gs*2,gs*2-gs),\
                        (gs*2,gs*3-gs),(0,gs*3-gs)],
    
    'l_block_r1': [(-gs,0),(gs*2,0),\
                   (gs*2,gs),(0,gs),\
                   (0,gs*2),(-gs,gs*2)],

    'l_block_r2': [(-gs,-gs),(gs,-gs),\
                       (gs,gs*3-gs),(0,gs*3-gs),\
                           (0,0),(-gs,0)],

    'l_block_r3': [(-gs,gs),(gs,gs),\
                   (gs,0),(gs*2,0),\
                   (gs*2,gs*2),(-gs,gs*2)],

    'j_block': [(0,-gs),(gs,-gs),\
                (gs,gs*3-gs),(-gs,gs*3-gs),\
                (-gs,gs*2-gs),(0,gs*2-gs)],
    
    'j_block_r1': [(-gs,-gs),(0,-gs),\
                   (0,0),(gs*2,0),\
                   (gs*2,gs),(-gs,gs)],
    
    'j_block_r2': [(0,-gs),(gs*2,-gs),\
                   (gs*2,0),(gs,0),\
                   (gs,gs*2),(0,gs*2)],
    
    'j_block_r3': [(-gs,-gs),(gs*2,-gs),\
                   (gs*2,gs),(gs,gs),\
                   (gs,0),(-gs,0)],
    
    'z_block': [(-gs,0),(gs,0),\
                (gs,gs),(gs*2,gs),\
                (gs*2,gs*2),(0,gs*2),\
                (0,gs),(-gs,gs)],

    'z_block_r1': [(0,-gs),(gs,-gs),\
                   (gs,gs),(0,gs),\
                   (0,gs*2),(-gs,gs*2),\
                   (-gs,0),(0,0)],
    
    's_block': [(0,0),(gs*2,0),\
                (gs*2,gs),(gs,gs),\
                (gs,gs*2),(-gs,gs*2),\
                (-gs,gs),(0,gs)],

    's_block_r1': [(0,-gs),(gs,-gs),\
                   (gs,0),(gs*2,0),\
                   (gs*2,gs*2),(gs,gs*2),\
                   (gs,gs),(0,gs)],

    't_block': [(-gs,0),(gs*2,0),\
                (gs*2,gs),(gs,gs),\
                (gs,gs*2),(0,gs*2),\
                (0,gs),(-gs,gs)],

    't_block_r1': [(gs,-gs),(gs,gs*2),\
                   (0,gs*2),(0,gs),\
                   (-gs,gs),(-gs,0),\
                   (0,0),(0,-gs)],

    't_block_r2': [(gs*2,gs),(-gs,gs),\
                   (-gs,0),(0,0),\
                   (0,-gs),(gs,-gs),\
                   (gs,0),(gs*2,0)],

    't_block_r3': [(0,-gs),(0,gs*2),\
                   (gs,gs*2),(gs,gs),\
                   (gs*2,gs),(gs*2,0),\
                   (gs,0),(gs,-gs)]
}

class Tetris:
    def __init__(self,master):
        
        self._master = master
        master.title("Tetris")
        master.geometry("+250+100")
        # Menubar: File -> *New Game *Help
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File",menu=file_menu)
        file_menu.add_command(label="New Game",command=self.restart_game)
        file_menu.add_command(label="Help",command=self.show_help)

        # Highscores
        try:
            # Read highscores and high score names if file exists
            txt_file = open('highscores.txt','r')
            self.high_score = int(txt_file.readline())
            self.high_score_name = txt_file.readline()             
            txt_file.close()

        except:
            # Create file if it doesnt exist
            txt_file = open('highscores.txt','w')
            txt_file.write("0\nPlayer 1")
            self.high_score = 0
            self.high_score_name = "Player 1"
            txt_file.close()

        # Side frame background
        self.background = tk.PhotoImage(file="TetrisBackground.png")
        
        # Left frame
        self._lf = tk.Canvas(master,width = 200,height = GAME_SIZE[1],bg='#BBBBBB')
        self._lf.pack(side=tk.LEFT,expand=True,fill='both')
        self.bg_left = self._lf.create_image(0,0,anchor=tk.N,image=self.background)
        
        # Game canvas
        self._canvas = tk.Canvas(master,width=GAME_SIZE[0],height=GAME_SIZE[1],bg='#111111') #Game view canvas
        self._canvas.pack(side=tk.LEFT,anchor=tk.S)

        # Pause text
        self.pause_txt = tk.Label(self._master,text="",font=("MS Gothic",40),bg='#111111',fg='#DDDDDD')
        self.pause_txt.place(x=GAME_SIZE[0]//2+120,y=GAME_SIZE[1]//2-30)

        # Right frame
        self._rf = tk.Canvas(master,width = 200,height = GAME_SIZE[1],bg='#BBBBBB')
        self._rf.pack(side=tk.RIGHT,expand=True,fill='both')
        self.bg_right = self._rf.create_image(500,0,anchor=tk.NE,image=self.background)
        
        # Score text
        self._score_label = tk.Label(self._rf, text="Score: 0", font=("Arial Black", 18),bg='#333333',fg='#DDDDDD',width=12)
        self._score_label.pack(side=tk.TOP,expand=True)

        # Highscore text
        self._hs_label = tk.Label(self._rf, text=("High Score\n"+self.high_score_name+ ": " +str(self.high_score)), font=("Arial Black", 18),bg='#333333',fg='#DDDDDD',width=12)
        self._hs_label.pack(side=tk.TOP,expand=True)
        
        self._master.bind('<Key>',self.move_block)
        
        self.new_game()

        self.descend_blocks() # Start moving the blocks downwards each step
            
    def new_game(self):
        """ Initialises game."""
        self._blocks = [] #Blocks currently in the game
        self._paused = False
        self._game_over = False
        self.add_block()
        self._score = 0
        self._score_label.configure(text="Score: " + str(self._score))
        self.update_game_speed()
        txt_file = open('highscores.txt','r')
        self.high_score = int(txt_file.readline())
        self.high_score_name = txt_file.readline()             
        txt_file.close()
        self._hs_label.configure(text="High Score\n"+self.high_score_name + ": "+str(self.high_score))

    def restart_game(self):
        """ Restarts game by removing blocks then reinitialising game."""
        for block in self._blocks:
            self._canvas.delete(block.get_block())
        self.new_game()

    def pause(self):
        """Toggles pause."""
        self._paused = not self._paused
        if self._paused:
            self.pause_txt.configure(text="PAUSED")
        else:
            self.pause_txt.configure(text="")

    def show_help(self):
        """ Show pop up explaining aim of game and controls."""
        self.pause()
        
        message = "AIM: \nComplete (fill) as many rows \
as you can. When a row is completed, all blocks will be removed in that row. \
The rows you complete are added to your overall score. \n\n\
CONTROLS: \nArrow keys (left, right, down): move current block. \n\
z/x: rotate the block clockwise"
        
        if messagebox.showinfo("TETRIS - HELP", message):
            self.pause()

    def update_game_speed(self):
        """Increases game speed by 12 steps every 5 scores."""
        self._game_speed = GAME_SPEED_START - 12*(self._score//5)
        # Cap game speed at 20
        if self._game_speed < 20: self._game_speed = 20

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
            if messagebox.showinfo("TETRIS", "GAME OVER"):
                if self._score > self.high_score:
                    high_score_name_popup = highScorePopup(self._master,self)

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

        shape = random.choice([0,2,3,7,11,13,15]) # All non-rotated blocks
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
                elif key == 'Z':
                    block_to_move.rotate(0,self._blocks)
                elif key == 'X':
                    block_to_move.rotate(1,self._blocks)        
                    
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
            self.add_block()

    def check_rows(self):
        """ Checks each row in the game and removes each block
            in rows that are full, then adds to player's
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
            # Update score, score text and game speed
            self._score += rows_full
            self.update_game_speed()
            self._score_label.configure(text="Score: " + str(self._score))
            # Delete all blocks in full rows
            for deleted_block in blocks_to_delete:
                if deleted_block in self._blocks:
                    deleted_block._canvas.delete(deleted_block.get_block())
                    del self._blocks[self._blocks.index(deleted_block)]
                    
            # descend all blocks but disable control of the blocks
            for block in self._blocks:
                block._frozen = 1
                block._control = False
                block.move((0,GRID_SIZE),self._blocks)
             
class highScorePopup(object):
    def __init__(self,master,tetris_obj):
        self.name = "Player 1"
        self.window = tk.Toplevel(master)
        self.window.geometry("300x150+"+str(GAME_SIZE[0]//2 + 304) + "+"+str(GAME_SIZE[1]//2 + 100))
        self.high_score_txt = tk.Label(self.window,text="You got a highscore! Please enter your name.")
        self.high_score_txt.pack(pady = 20)
        self.name_entry = tk.Entry(self.window)
        self.name_entry.pack(ipady = 5)
        self.save_btn = tk.Button(self.window,text="Save",command=self.close)
        self.save_btn.pack(ipadx = 10,ipady = 5)
        self._tetris_obj = tetris_obj
    
    def close(self):
        self.name = self.name_entry.get()
        with open("highscores.txt",'w') as file:
            file.write(str(self._tetris_obj._score))
            file.write("\n" + self.name)
        self._tetris_obj.restart_game()
        self.window.destroy()

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
            Parameters:
                x_bounds (tuple): (dx,x_bound1,x_bound2)
                    [dx (int): x direction
                    [x_bound1 (int): left side of screen pos
                    [x_bound2 (int): right side of screen pos
                y_bounds (tuple): (dy,y_bound)
                    [dy (int): y direction
                    [y_bound (int): bottom side of screen pos
        """
        # If checking below and y pos is greater than y boundary, stop & freze
        if y_bounds[0] > 0 and self._y_pos >= y_bounds[1]:
            if self._frozen > 0: self._frozen -= 1
            return (0,0)

        # If checking left or right and x pos is outside x boundaries, stop
        elif (x_bounds[0] < 0 and self._x_pos <= x_bounds[1]) or \
             (x_bounds[0] > 0 and self._x_pos >= x_bounds[2]):
            return (0,0)

    def check_block_collisions(self,blocks,loop,dec_frozen,x_adj,y_adj,x_adj2,y_adj2,x_adj3,y_adj3,add, rotation):
        """ Check collisions around block when moving.
            Parameters:
                blocks (list): blocks in the game
                loop (int): amount of times to loop over collision checks
                dec_frozen (bool): if checking dy, this should be true so it will decrement frozen by 1
                x_adj (int): constant amount to adjust the x position
                y_adj (int): constant amount to adjust the y position
                x_adj2 (int): 0 or 1, 1 if looping horizontally through blocks (GRID_SIZE*pos), 0 otherwise 
                y_adj2 (int): 0 or 1, 1 if looping vertically through blocks (GRID_SIZE*pos), 0 otherwise
                x_adj3 (int): 0 or 1, 1 if using adjustment list (add)
                y_adj3 (int): 0 or 1, 1 if using adjustment list (add)
                add (list): List of x/y adjustments based on loops
                rotation (bool): If true, adjustment list will be 2 dimensional
            Returns:
                0: if frozen decremented (this means block can't move)
                True: If block can move
                False: If block can't move
        """
            
        can_move = True
        # Fill adjustment list with 0's if empty list passed
        if add == [] and not rotation:
            for i in range(loop):
                add.append(0)
        elif add == [] and rotation:
            for i in range(loop):
                add.append((0,0))
                
        # Loop through each block position based on parameters above and
        # check if there is a collision at this position.
        for pos in range(loop):
            if can_move:
                if not rotation:
                    can_move = not self.check_collision(blocks,(self._x_pos + x_adj + x_adj2*GRID_SIZE*pos + x_adj3*add[pos],\
                                                                self._y_pos + y_adj + y_adj2*GRID_SIZE*pos + y_adj3*add[pos]))
                else:
                    can_move = not self.check_collision(blocks,(self._x_pos + x_adj + x_adj2*GRID_SIZE*pos + x_adj3*add[pos][0],\
                                                                self._y_pos + y_adj + y_adj2*GRID_SIZE*pos + y_adj3*add[pos][1]))
                
        # Decrement self._frozen if dec_frozen = True (if checking collisions below blocks)
        if dec_frozen:
            if not can_move and self._frozen > 0:
                self._frozen -= 1
                return 0
            
        return can_move

    def move(self,direction,blocks):
        """ collision stuff >:( """
        
        dx,dy = direction

        # If block is on edge of game screen, don't move, and make frozen if block reached bottom of game screen.

        if self._shape == shape_types[0]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE),(dy,GAME_SIZE[1]-GRID_SIZE*4)
            
        elif self._shape == shape_types[1]:
            x_bound,y_bound = (dx,GRID_SIZE*2,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*4)

        elif self._shape == shape_types[2]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*2)

        elif self._shape in [shape_types[3],shape_types[9],shape_types[14],shape_types[18]]:
            x_bound,y_bound = (dx,0,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[4],shape_types[6]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[5],shape_types[7],shape_types[12],shape_types[16]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE),(dy,GAME_SIZE[1]-GRID_SIZE*3)

        elif self._shape in [shape_types[8],shape_types[10],shape_types[17]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*2)

        elif self._shape in [shape_types[11],shape_types[13],shape_types[15]]:
            x_bound,y_bound = (dx,GRID_SIZE,GAME_SIZE[0]-GRID_SIZE*2),(dy,GAME_SIZE[1]-GRID_SIZE*3)
            
        else:
            x_bound,y_bound = (0,0,0),(0,0)

        if self.check_boundaries(x_bound,y_bound) == (0,0): direction = (0,0)

        can_move = True

        # Test if blocks are in the way of new position (where block is moving). If so, set can_move = False
        # and if there is a block underneath, freeze block.

        # L block
        if self._shape == shape_types[0]:
            if dy > 0:
                can_move = self.check_block_collisions(blocks,1,True,1,GRID_SIZE*4,0,0,0,0,[],False)
                if can_move == 0: return
            elif dx > 0:
                can_move = self.check_block_collisions(blocks,4,False,GRID_SIZE,0,0,1,0,0,[],False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,4,False,-GRID_SIZE+1,0,0,1,0,0,[],False)
        # L block rotated       
        elif self._shape == shape_types[1]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,1,False,GRID_SIZE*2,GRID_SIZE*3,0,0,0,0,[],False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,1,False,-GRID_SIZE*3+1,GRID_SIZE*3,0,0,0,0,[],False)
            elif dy > 0:
                add = [1,0,0,GRID_SIZE-1] # readjustments
                can_move = self.check_block_collisions(blocks,4,True,-GRID_SIZE*2,GRID_SIZE*4,1,0,1,0,add,False)
                if can_move == 0: return
        # O block
        elif self._shape == shape_types[2]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,0,0,1,0,0,[],False) 
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,0,0,1,0,0,[],False)
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1,GRID_SIZE*2,1,0,0,0,[],False)
                if can_move == 0: return
        # L block
        elif self._shape == shape_types[3]:
            if dx > 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add,False)        
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,0,0,[],False)
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1,GRID_SIZE*3,1,0,0,0,[],False)
                if can_move == 0: return
        # L block rotated 1              
        elif self._shape == shape_types[4]:
            if dx > 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add,False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2 + 1, GRID_SIZE,0,1,0,0,[],False)
            elif dy > 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1 - GRID_SIZE,GRID_SIZE*2,1,0,0,1,add,False)
                if can_move == 0: return
        # L block rotated 2
        elif self._shape == shape_types[5]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,0,0,[],False)
            elif dx < 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,1,0,add,False)                           
            elif dy > 0:
                add = [GRID_SIZE,GRID_SIZE*3] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,-GRID_SIZE+1,0,1,0,0,1,add,False)
                if can_move == 0: return
        # L block rotated 3
        elif self._shape == shape_types[6]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,0,0,[],False)
            elif dx < 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,0,GRID_SIZE,0,1,1,0,add,False)
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*3,1,0,0,0,[],False)
                if can_move == 0: return
        # J block
        elif self._shape == shape_types[7]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,0,0,[],False)        
            elif dx < 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,1,0,add,False)
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,2,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,0,[],False)
                if can_move == 0: return
        # J block rotated 1
        elif self._shape == shape_types[8]:
            if dx > 0:
                add = [0,-GRID_SIZE*2] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add,False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2 + 1, GRID_SIZE,0,1,0,0,[],False) 
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*2,1,0,0,0,[],False)
                if can_move == 0: return
        # J block rotated 2
        elif self._shape == shape_types[9]:
            if dx > 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add,False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE+1,0,0,1,0,0,[],False)                         
            elif dy > 0:
                add = [GRID_SIZE*3,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,0,0,1,0,0,1,add,False)
                if can_move == 0: return
        # J block rotated 3        
        elif self._shape == shape_types[10]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,0,0,[],False)
            elif dx < 0:
                add = [-GRID_SIZE*2,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,0,GRID_SIZE,0,1,1,0,add,False)
            elif dy > 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1 - GRID_SIZE,GRID_SIZE,1,0,0,1,add,False)
                if can_move == 0: return
        # Z block      
        elif self._shape == shape_types[11]:
            if dx > 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add,False)
            elif dx < 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,GRID_SIZE,0,1,1,0,add,False)
            elif dy > 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add,False)
                if can_move == 0: return
        # Z block rotated
        elif self._shape == shape_types[12]:
            if dx > 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add,False)
            elif dx < 0:
                add = [GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE*2,0,0,1,1,0,add,False)
            elif dy > 0:
                add = [0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add,False)
                if can_move == 0: return
        # S block
        elif self._shape == shape_types[13]:
            if dx > 0:
                add = [GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE,GRID_SIZE,0,1,1,0,add,False)
            elif dx < 0:
                add = [0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE,GRID_SIZE,0,1,1,0,add,False)
            elif dy > 0:
                add = [0,0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,1-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add,False)
                if can_move == 0: return
        # S block rotated
        elif self._shape == shape_types[14]:
            if dx > 0:
                add = [-GRID_SIZE,0,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE*2,0,0,1,1,0,add,False)
            elif dx < 0:
                add = [0,0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,1,0,add,False)
            elif dy > 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,True,0,GRID_SIZE*3,1,0,0,1,add,False)
                if can_move == 0: return
        # T block
        elif self._shape == shape_types[15]:
            if dx > 0:
                add = [0,-GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,GRID_SIZE,0,1,1,0,add,False)
            elif dx < 0:
                add = [0,GRID_SIZE] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2,GRID_SIZE,0,1,1,0,add,False)
            elif dy > 0:
                add = [0,GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*2,1,0,0,1,add,False)
                if can_move == 0: return
        # T block rotated 1
        elif self._shape == shape_types[16]:
            if dx > 0:
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,0,0,[],False)
            elif dx < 0:
                add = [0,-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,1,0,add,False)
            elif dy > 0:
                add = [-GRID_SIZE,0]
                can_move = self.check_block_collisions(blocks,2,True,-GRID_SIZE,GRID_SIZE*3,1,0,0,1,add,False)
                if can_move == 0: return
        # T block rotated 2
        elif self._shape == shape_types[17]:
            if dx > 0:
                add = [-GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,GRID_SIZE*2,0,0,1,1,0,add,False)
            elif dx < 0:
                add = [GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,2,False,-GRID_SIZE*2,0,0,1,1,0,add,False)
            elif dy > 0:
                can_move = self.check_block_collisions(blocks,3,True,-GRID_SIZE,GRID_SIZE*2,1,0,0,0,[],False)
                if can_move == 0: return
        # T block rotated 3
        elif self._shape == shape_types[18]:
            if dx > 0:
                add = [0,GRID_SIZE,0] # readjustments
                can_move = self.check_block_collisions(blocks,3,False,GRID_SIZE,0,0,1,1,0,add,False)
            elif dx < 0:
                can_move = self.check_block_collisions(blocks,3,False,-GRID_SIZE,0,0,1,0,0,[],False)
            elif dy > 0:
                add = [0,-GRID_SIZE]
                can_move = self.check_block_collisions(blocks,2,True,0,GRID_SIZE*3,1,0,0,1,add,False)
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
            Parameters:
                position (tuple x,y): Game position to check.
        """
        x,y = position
        # bounds for each shape to check, size of 4 only checks one rectangle, size of 8 checks two rectangles of the shape
        # e.g. the L block will check the 3 vertical squares then the bottom right square
        BOUNDS = {
            shape_types[0]: (0,GRID_SIZE,0,GRID_SIZE*4),
            shape_types[1]: (-GRID_SIZE*2,GRID_SIZE*2,GRID_SIZE*3,GRID_SIZE*4),
            shape_types[2]: (0,GRID_SIZE*2,0,GRID_SIZE*2),
            shape_types[3]: (0,GRID_SIZE,0,GRID_SIZE*3,GRID_SIZE,GRID_SIZE*2,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[4]: (-GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,-GRID_SIZE,0,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[5]: (0,GRID_SIZE,0,GRID_SIZE*3,-GRID_SIZE,0,0,GRID_SIZE),
            shape_types[6]: (-GRID_SIZE,GRID_SIZE*2,GRID_SIZE*2,GRID_SIZE*3,GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2),
            shape_types[7]: (0,GRID_SIZE,0,GRID_SIZE*3,-GRID_SIZE,0,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[8]: (-GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,-GRID_SIZE,0,0,GRID_SIZE),
            shape_types[9]: (0,GRID_SIZE,0,GRID_SIZE*3,GRID_SIZE,GRID_SIZE*2,0,GRID_SIZE),
            shape_types[10]:(-GRID_SIZE,GRID_SIZE*2,0,GRID_SIZE,GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2),
            shape_types[11]:(-GRID_SIZE,GRID_SIZE,GRID_SIZE,GRID_SIZE*2,0,GRID_SIZE*2,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[12]:(0,GRID_SIZE,0,GRID_SIZE*2,-GRID_SIZE,0,GRID_SIZE,GRID_SIZE*3),
            shape_types[13]:(0,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,-GRID_SIZE,GRID_SIZE,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[14]:(0,GRID_SIZE,0,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*3),
            shape_types[15]:(-GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,0,GRID_SIZE,GRID_SIZE*2,GRID_SIZE*3),
            shape_types[16]:(0,GRID_SIZE,0,GRID_SIZE*3,-GRID_SIZE,0,GRID_SIZE,GRID_SIZE*2),
            shape_types[17]:(-GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2,0,GRID_SIZE,0,GRID_SIZE),
            shape_types[18]:(0,GRID_SIZE,0,GRID_SIZE*3,GRID_SIZE,GRID_SIZE*2,GRID_SIZE,GRID_SIZE*2)
        }
        try:
            shape_bounds = BOUNDS[self._shape]
        except:
            shape_bounds = []
            
        if len(shape_bounds) == 4:
            if (x in range(self._x_pos + shape_bounds[0], self._x_pos + shape_bounds[1]))\
               and (y in range(self._y_pos + shape_bounds[2], self._y_pos + shape_bounds[3])): return True
            else: return False
        elif len(shape_bounds) == 8:
            if (x in range(self._x_pos + shape_bounds[0], self._x_pos + shape_bounds[1])\
               and y in range(self._y_pos + shape_bounds[2], self._y_pos + shape_bounds[3])) or \
               (x in range(self._x_pos + shape_bounds[4], self._x_pos + shape_bounds[5])\
               and y in range(self._y_pos + shape_bounds[6], self._y_pos + shape_bounds[7])): return True
            else: return False

            
    def rotate(self,deg,blocks):
        """ Rotate block left/right depending on deg (degree), if there is no collision at the rotated position.
            Parameters:
                deg (int): 0 if clockwise, 1 if anti-clockwise
                blocks (list): List of blocks in the game.
        """
        
        if self._frozen > 0:
            can_rotate = True
            
            # Check collision with I block rotated
            if self._shape == shape_types[0] and self._x_pos in range(GRID_SIZE * 2,GAME_SIZE[0]-GRID_SIZE):
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE*2,GRID_SIZE*3,1,0,0,0,[],True)
                new_shape = shape_types[1]

            # Check collision with I block
            elif self._shape == shape_types[1] and self._y_pos < 425:
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,0,0,[],True)
                new_shape = shape_types[0]

            # Check collision with L block rotated 1
            elif ((self._shape == shape_types[3] and deg == 0)\
                 or (self._shape == shape_types[5] and deg == 1)) and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(0,0),(-3*GRID_SIZE,GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE*2,1,0,1,1,add,True)
                new_shape = shape_types[4]

            # Check collision with L block rotated 2
            elif (self._shape == shape_types[4] and deg == 0) or (self._shape == shape_types[6] and deg == 1):
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-3*GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[5]

            # Check collision with L block rotated 3
            elif ((self._shape == shape_types[5] and deg == 0)\
                 or (self._shape == shape_types[3] and deg == 1)) and self._x_pos <= GAME_SIZE[0]-GRID_SIZE*2:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE*2,1,0,1,1,add,True)
                new_shape = shape_types[6]

            # Check collision with L block
            elif (self._shape == shape_types[6] and deg == 0) or (self._shape == shape_types[4] and deg == 1):
                add = [(0,0),(0,0),(0,0),(GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[3]

            # Check collision with J block rotated 1
            elif ((self._shape == shape_types[7] and deg == 0)\
                 or (self._shape == shape_types[9] and deg == 1)) and self._x_pos <= GAME_SIZE[0]-GRID_SIZE*2:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE*2,1,0,1,1,add,True)
                new_shape = shape_types[8]

            # Check collision with J block rotated 2
            elif ((self._shape == shape_types[8] and deg == 0)\
                 or (self._shape == shape_types[10] and deg == 1)) and self._y_pos <= GAME_SIZE[1]-GRID_SIZE*3:
                add = [(0,0),(0,0),(0,0),(GRID_SIZE,-3*GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[9]

            # Check collision with J block rotated 3
            elif ((self._shape == shape_types[9] and deg == 0)\
                 or (self._shape == shape_types[7] and deg == 1)) and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE*2,1,0,1,1,add,True)
                new_shape = shape_types[10]

            # Check collision with J block
            elif ((self._shape == shape_types[10] and deg == 0)\
                 or (self._shape == shape_types[8] and deg == 1)) and self._y_pos <= GAME_SIZE[1]-GRID_SIZE*3:
                add = [(0,0),(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[7]

            # Check collision with Z block rotated
            elif self._shape == shape_types[11]:
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(-GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[12]

            # Check collision with Z block
            elif self._shape == shape_types[12] and self._x_pos <= GAME_SIZE[0]-GRID_SIZE*2:
                add = [(0,0),(0,0),(-GRID_SIZE,GRID_SIZE),(-GRID_SIZE,GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE,1,0,1,1,add,True)
                new_shape = shape_types[11]

            # Check collision with S block rotated
            elif self._shape == shape_types[13]:
                add = [(0,0),(0,0),(GRID_SIZE,-GRID_SIZE),(GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,0,0,1,1,1,add,True)
                new_shape = shape_types[14]

            # Check collision with S block
            elif self._shape == shape_types[14] and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(-GRID_SIZE,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE*2,1,0,1,1,add,True)
                new_shape = shape_types[13]

            # Check collision with T block rotated 1
            elif (self._shape == shape_types[15] and deg == 0) or (self._shape == shape_types[17] and deg == 1):
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(0,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,-GRID_SIZE,0,1,1,1,add,True)
                new_shape = shape_types[16]

            # Check collision with T block rotated 2
            elif ((self._shape == shape_types[16] and deg == 0)\
                 or (self._shape == shape_types[18] and deg == 1)) and self._x_pos <= GAME_SIZE[0] - GRID_SIZE*2:
                add = [(0,0),(0,0),(-GRID_SIZE,-GRID_SIZE),(-GRID_SIZE,0)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE,1,0,1,1,add,True)
                new_shape = shape_types[17]

            # Check collision with T block rotated 3
            elif (self._shape == shape_types[17] and deg == 0) or (self._shape == shape_types[15] and deg == 1):
                add = [(0,0),(0,0),(GRID_SIZE,-GRID_SIZE),(0,-GRID_SIZE)]
                can_rotate = self.check_block_collisions(blocks,4,False,0,-GRID_SIZE,0,1,1,1,add,True)
                new_shape = shape_types[18]

            # Check collision with T block
            elif ((self._shape == shape_types[18] and deg == 0)\
                 or (self._shape == shape_types[16] and deg == 1)) and self._x_pos >= GRID_SIZE:
                add = [(0,0),(0,0),(-GRID_SIZE,GRID_SIZE),(-GRID_SIZE,0)]
                can_rotate = self.check_block_collisions(blocks,4,False,-GRID_SIZE,GRID_SIZE,1,0,1,1,add,True)
                new_shape = shape_types[15]
                
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
