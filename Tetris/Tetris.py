#-------------------------------------------------------------------------------
# Name:        Tetris
# Purpose:     A Tetris clone
#
# Author:      Will Taplin
#
# Created:     21/10/2010
#
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys
import pygame
from pygame.locals import *
import random
import os

# Globals
block_drop_delay = 1200
block_shapes = []
flashing_anim = ['whiteblock.bmp',
                 'transblock.bmp',]

# Resource handling
def load_image(name, colorkey = None):
    fullname = os.path.join('Data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey =  image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_animated_images(image_list):
    images = []
    for name in image_list:
        fullname = os.path.join('Data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image:', name
            raise SystemExit, message
        image = image.convert()
        image.set_colorkey((255,0,255), RLEACCEL)
        images.append(image)
    return images

def load_sound(name):
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', name
        raise SystemExit, message
    sound.set_volume(0.5)
    return sound


def init_blocks():
    global block_shapes

    #block_shapes[shape_type and color][rotate_state][grid_y][grid_x]

    t_block = [[[0,0,0,0],     # initial rotation
                [0,1,1,1],
                [0,0,1,0],
                [0,0,0,0]],
               [[0,0,1,0],     # 2nd rotation, 90 degrees counter-clockwise
                [0,0,1,1],
                [0,0,1,0],
                [0,0,0,0]],
               [[0,0,1,0],     # 3rd rotation
                [0,1,1,1],
                [0,0,0,0],
                [0,0,0,0]],
               [[0,0,1,0],     # 4th rotation
                [0,1,1,0],
                [0,0,1,0],
                [0,0,0,0]]]

    sq_block = [[[0,0,0,0],
                 [0,1,1,0],
                 [0,1,1,0],
                 [0,0,0,0]]]

    i_block = [[[0,1,0,0],
                [0,1,0,0],
                [0,1,0,0],
                [0,1,0,0]],
               [[0,0,0,0],
                [0,0,0,0],
                [1,1,1,1],
                [0,0,0,0]]]

    l_block = [[[0,0,0,0],
                [0,1,1,1],
                [0,1,0,0],
                [0,0,0,0]],
               [[0,0,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,0]],
               [[0,0,0,1],
                [0,1,1,1],
                [0,0,0,0],
                [0,0,0,0]],
               [[0,1,1,0],
                [0,0,1,0],
                [0,0,1,0],
                [0,0,0,0]]]

    j_block = [[[0,0,0,0],
                [0,1,1,1],
                [0,0,0,1],
                [0,0,0,0]],
               [[0,0,1,1],
                [0,0,1,0],
                [0,0,1,0],
                [0,0,0,0]],
               [[0,1,0,0],
                [0,1,1,1],
                [0,0,0,0],
                [0,0,0,0]],
               [[0,0,1,0],
                [0,0,1,0],
                [0,1,1,0],
                [0,0,0,0]]]

    s_block = [[[0,0,0,0],
                [0,0,1,1],
                [0,1,1,0],
                [0,0,0,0]],
               [[0,0,1,0],
                [0,0,1,1],
                [0,0,0,1],
                [0,0,0,0]]]

    z_block = [[[0,0,0,0],
                [0,1,1,0],
                [0,0,1,1],
                [0,0,0,0]],
               [[0,0,0,1],
                [0,0,1,1],
                [0,0,1,0],
                [0,0,0,0]]]

    # add all blocks to block_shapes list
    block_shapes.append(t_block)
    block_shapes.append(sq_block)
    block_shapes.append(i_block)
    block_shapes.append(l_block)
    block_shapes.append(j_block)
    block_shapes.append(s_block)
    block_shapes.append(z_block)


class Flashing_Square(pygame.sprite.Sprite):
    global flashing_anim

    def __init__(self, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self.flashing = True
        self.images = load_animated_images(flashing_anim)
        self.start = pygame.time.get_ticks()
        self.delay = 1000 / fps
        self.last_update = 0
        self.frame = 0
        self.update(pygame.time.get_ticks())
        self.flashing = False

    def update(self, t):
        if self.flashing:
            if t - self.last_update > self.delay:
                self.frame += 1
                if self.frame > len(self.images) - 1 :
                    self.frame = 0
                self.image = self.images[self.frame]
                self.last_update = t


class Square(Flashing_Square):
    """ A single square object """
    def __init__(self, color, x, y, grid):
        Flashing_Square.__init__(self)
        if color == 0:
            self.image  = load_image('redblock.bmp')
        elif color == 1:
            self.image = load_image('purpleblock.bmp')
        elif color == 2:
            self.image = load_image('greenblock.bmp')
        elif color == 3:
            self.image = load_image('greyblock.bmp')
        elif color == 4:
            self.image = load_image('blueblock.bmp')
        elif color == 5:
            self.image = load_image('dgreenblock.bmp')
        elif color == 6:
            self.image = load_image('dblueblock.bmp')
        else:
            print "Invalid color choice"

        self.rect = self.image.get_rect()
        self.color = color
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.grid = grid
        self.row = -1  # keeps track of which row in the grid the square is in
                       # 0 = top row, 19 = bottom row

    def shift_down(self):
        # shifts a square down one cell for each line made
        # updates the square's row
        self.rect.bottom = self.rect.bottom + 30
        x_grid, y_grid = self.get_grid()
        self.row = y_grid


    def get_grid(self):
        # convert on-screen pixel position
        # to 10x20 grid coords
        x_grid = (self.rect.left - 270) / 30
        y_grid = self.rect.top / 30
        return x_grid, y_grid


class Block(pygame.sprite.Sprite):
    """ A full Tetris Block Object
        which is a list of four square objects """
    global block_drop_delay

    def __init__(self, color, x, y, grid):
        pygame.sprite.Sprite.__init__(self)
        self.x_pos = x
        self.y_pos = y
        self.color = color
        self.rotate_state = 0
        self.rotate_sound = load_sound('rotate.wav')
        self.slide = 0  # sliding state 0 = not sliding
        self.slide_delay = 0
        self.start_drop_timer = pygame.time.get_ticks()
        self.drop_delay = block_drop_delay  # speed of falling blocks
        self.grid = grid
        self.squares = self.build_block()

    def build_block(self):
        color = self.color
        rotate_state = self.rotate_state
        new_block = []   # List of new squares that make up a tetris block
        for i in range(0,4):
            for j in range(0,4):
                grid = block_shapes[color][rotate_state][i][j]  #process the 4x4 array
                if grid > 0:      # If array element is a "filled" space
                    grid_x = self.x_pos + (j * self.grid.cellsize)    # Assign an x,y coord based on the array element index
                    grid_y = self.y_pos + (i * self.grid.cellsize)   # times the square width, added to the initial "0,0" given
                    new_square = Square(color, grid_x, grid_y, self.grid)    # Create a new square object with the new x,y
                    new_block.append(new_square)   # add it to the list of block pieces to blit
        return new_block

    def try_rotate(self):
        # attempts to rotate the block. If rotation will put the block out
        # of bounds or cause two or more squares to collide, the rotation function
        # will revert the block back to its' previous state

        self.rotate_state = self.rotate_state + 1  #increment the state for every call

        # Rotate the block based on the current rotate state
        if self.squares[3].rect.bottom < 600:  # if block has not hit bottom
            self.rotation()

        # if rotation puts block out of bounds, revert back to
        # previous rotate state
        for square in self.squares:
            if square.rect.left < 270:
                self.rotation(rev_rotate = True)
            elif square.rect.right > 570:
                self.rotation(rev_rotate = True)

        # if rotated block collides with another block
        # rotate the block back to the previous state
        for square in self.squares:
            x_grid, y_grid = square.get_grid()
            if self.grid.tiles[y_grid][x_grid] > 0:  # if filled space
                self.rotation(rev_rotate = True)

    def rotation(self, rev_rotate = False):
        # handles the actual block rotation.
        # the block will either rotate or revert to its' previous state
        # if try_rotate function detects a collision
        self.rotate_sound.play()
        next_square = 0 # index for squares in block
        color = self.color
        prev_state =  self.rotate_state - 1  # save previous state before rotating

        # keep it spinnin'
        if color == 0 or color == 3 or color == 4:  # "T","L","J" blocks
            if self.rotate_state == 4:   # if last state
                self.rotate_state = 0    # start again from original state
        elif color == 2 or color == 5 or color == 6: # "I","S","Z" blocks
            if self.rotate_state == 2:
                self.rotate_state = 0
        elif color == 1: # square block
            self.rotate_state = 0  # square block does not rotate

        for i in range(0,4):
            for j in range(0,4):
                if rev_rotate:  # if rotation collision, use previous state
                    rotate_grid = block_shapes[color][prev_state][i][j]
                else:
                    rotate_grid = block_shapes[color][self.rotate_state][i][j]
                if rotate_grid > 0:  # if array element is a "filled" space
                    grid_x = self.x_pos + (j*30)
                    grid_y = self.y_pos + (i*30)
                    self.squares[next_square].rect.x = grid_x  # set new x,y for each square in block
                    self.squares[next_square].rect.y = grid_y
                    next_square = next_square + 1

        if rev_rotate:  # if rotation collision, reset the rotate state
            self.rotate_state = self.rotate_state - 1  # reset the value for rotate state


    def in_bounds(self, checking_bound):
        # only move if these blocks are in bounds
        # checking this combination of squares ensures all block shapes
        # stay in bounds
        if checking_bound == "left":
            if self.squares[0].rect.left > 270 and\
               self.squares[1].rect.left > 270 and\
               self.squares[2].rect.left > 270:
                return True
        elif checking_bound == "right":
            if self.squares[1].rect.right < 570 and\
               self.squares[2].rect.right < 570 and\
               self.squares[3].rect.right < 570:
                return True
        elif checking_bound == "bottom":
            if self.squares[1].rect.bottom < 600 and\
               self.squares[2].rect.bottom < 600 and\
               self.squares[3].rect.bottom < 600:
                return True
        elif checking_bound == "square_left":  # check if space to left is empty
            open_grid = True  # assume grid space is empty
            for square in self.squares:
                x_grid, y_grid = square.get_grid()
                if self.grid.tiles[y_grid][x_grid - 1] == 1:
                    open_grid = False  # tell piece the grid space is filled
            return open_grid
        elif checking_bound == "square_right": # check if space to right is empty
            open_grid = True
            for square in self.squares:
                x_grid, y_grid = square.get_grid()
                if self.grid.tiles[y_grid][x_grid + 1] == 1:
                    open_grid = False
            return open_grid
        elif checking_bound == "square_below":
            open_grid = True
            for square in self.squares:
                x_grid, y_grid = square.get_grid()
                if self.grid.tiles[y_grid + 1][x_grid] == 1:
                    open_grid = False
            return open_grid

    def move_left(self):
        if self.in_bounds("left") and self.in_bounds("square_left"):
            for square in self.squares:
                square.rect.left = square.rect.left - 30 # move one cell to the left
            self.x_pos = self.x_pos - 30  # update x_pos
            self.slide_delay = 0  # reset the delay for sliding

    def move_right(self):
        if self.in_bounds("right") and self.in_bounds("square_right"):
            for square in self.squares:
                square.rect.left = square.rect.left + 30  # move one cell to the right
            self.x_pos = self.x_pos + 30  # update x_pos
            self.slide_delay = 0  # reset the delay for sliding

    def move_down(self):
        if self.in_bounds("bottom") and self.in_bounds("square_below"):
            for square in self.squares:
                square.rect.bottom = square.rect.bottom + 30 # move one cell down
            self.y_pos = self.y_pos + 30 # update y_pos
            self.slide_delay = 0  # reset the delay for sliding

    def break_and_freeze(self, block_group, frozen_group):
        # stops the block and removes square objects from block
        # group and puts them in the frozen squares group.
        # sets the squares' row to the y grid coord.
        # increments the number of squares in each row.
        for square in self.squares:
            x_grid, y_grid = square.get_grid()
            square.row = y_grid
            frozen_group.add(square)
            block_group.remove(square)
        self.grid.track_squares(frozen_group)

    def is_collided(self):
        # checks for collisions with other squares and
        # the bottom of the screen
        for square in self.squares:
            x_grid, y_grid = square.get_grid()  # get grid x,y coords for every square
            if square.rect.bottom >= 600:  # if block hit bottom
                return True
            elif self.grid.tiles[y_grid + 1][x_grid] == 1:  # if space below current square
                return True                                 # is 'filled'

    def update(self, t):
        #keep the drop delay updated for level up
        global block_drop_delay
        self.drop_delay = block_drop_delay

        # allow blocks to slide if key held
        if self.slide == -1:  # if holding left
            if self.slide_delay < 6:  # slow down sliding
                self.slide_delay += 1
            else:
                self.move_left()
        elif self.slide == 1:  # if holding right
            if self.slide_delay < 6:
                self.slide_delay += 1
            else:
                self.move_right()
        elif self.slide == 2:  # if holding down
            if self.slide_delay < 3:
                self.slide_delay += 1
            else:
                self.move_down()
        # falling blocks
        if t - self.start_drop_timer > self.drop_delay:
            self.move_down()
            self.start_drop_timer = t

class Tetris_Grid(object):
    """ A 10 X 20 2D list to keep track of the game board """
    def __init__(self, x = 10, y = 20):
        self.x = x
        self.y = y
        self.tiles = self.build_grid()
        self.squares_in_row = self.build_rows()
        self.left = 270
        self.right = 570
        self.top = 0
        self.bottom = 600
        self.cellsize = 30

    def build_grid(self):   # create a new 2D list filled with 0's
        grid = [[0 for i in range(self.x)] for j in range(self.y)]
        return grid

    def build_rows(self):
        # a 20 element array that keeps track of how many squares are in
        # each row of the grid
        rows = [0 for i in range(20)]
        return rows

    def track_squares(self, frozen_squares):
        # adds frozen squares to the 2D grid array
        for i in range(self.y):     # reset all cells to empty
            for j in range(self.x):
                self.tiles[i][j] = 0

        for row in range(0,20):     # reset all rows to empty
            self.squares_in_row[row] = 0

        for square in frozen_squares:   # update the coll.grid and row array
            x_grid, y_grid = square.get_grid()
            self.tiles[y_grid][x_grid] = 1
            self.squares_in_row[y_grid] += 1

class Game_Stats(object):
    """ updates and displays all the textual
        info used in the game """
    def __init__(self, screen):
        self.font = pygame.font.Font(os.path.join('data', 'Retroville NC.ttf'), 24)
        self.color = (252,248,252)
        self.screen = screen
        self.level = 0
        self.score = 0
        self.lines = 2
        self.high_score_text = self.load_score()
        self.high_score = int(self.high_score_text)

    def render_text(self):
        # update and render all text
        render_level = self.font.render(str(self.level), 0, self.color)
        render_score = self.font.render(str(self.score), 0, self.color)
        render_lines = self.font.render(str(self.lines), 0, self.color)
        render_high_score = self.font.render(str(self.high_score), 0, self.color)
        self.screen.blit(render_level, (180,150))
        self.screen.blit(render_score, (30,240))
        self.screen.blit(render_high_score, (30,300))
        self.screen.blit(render_lines, (180,390))

    def load_score(self):
        # load the high score from file
        file = open(os.path.join('data','highscore.txt'), "r")
        score = file.readline()
        file.close()
        return score

    def new_high_score(self):
        # update file with new high score
        file = open(os.path.join('data','highscore.txt'), "w")
        file.write(str(self.high_score))
        file.close

def main():
    # Initialize game, display the game screen
    pygame.init()
    screen = pygame.display.set_mode((800,600), pygame.FULLSCREEN)
    fullscreen = True
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('TETRIS')
    splash_screen = load_image('splash.bmp')
    play_music('intro.wav')
    clock = pygame.time.Clock()


    # Splash screen mode
    game_over = True
    while game_over:
        clock.tick(60)
        screen.blit(splash_screen, (0,0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:   # quit
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_f:    # toggle fullscreen
                    if not fullscreen:
                        pygame.mouse.set_visible(False)
                        screen = pygame.display.set_mode((800,600), pygame.FULLSCREEN)
                        fullscreen = True
                    else:
                        pygame.mouse.set_visible(True)
                        screen = pygame.display.set_mode((800,600))
                        fullscreen = False
                elif event.key == K_RETURN:  # start game
                    game_over = False

    # game mode
    # start music, initialize timers and timer toggles
    play_music("song.wav")
    break_delay = 0 # timer for block collision
    shift_delay = 0 # timer for dropping the stack after a line
    delete_delay = 0
    get_line = None   # line_indicator
    line_made = False # toggle for the shifting function
    line_deleted = False
    flash_effect = False
    paused = False

    # load non block images
    gamescreen = load_image('background.bmp')
    game_over_screen = load_image('gameover.bmp', -1)
    pause_screen = load_image('pause.bmp', -1)

    # load sounds
    lock_sound = load_sound('lock.wav')
    line_sound = load_sound('line.wav')
    game_over_sound = load_sound('gameover.wav')
    level_up = load_sound('levelup.wav')

    # Inintialize block shapes
    init_blocks()

    # create the grid and stat keeper
    grid = Tetris_Grid()
    stats = Game_Stats(screen)

    # drop a block, get the next block
    block_sprite, block, next_block_sprite, next_block_type = choose_piece(grid, random.randint(0,6))

    # create a sprite list for collided blocks
    frozen_squares = pygame.sprite.RenderPlain()

    # Draw the screen
    block_sprite.draw(screen)
    next_block_sprite.draw(screen)
    screen.blit(gamescreen, (0,0))
    stats.render_text()
    pygame.display.flip()


    # Game Loop
    while not game_over:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            # controls
            elif event.type == KEYDOWN:
                if event.key == K_UP:  # up arrow rotates the block counter-clockwise
                    block.try_rotate()
                elif event.key == K_LEFT: # left key slides the block to the left
                    block.move_left()
                    block.slide = -1
                elif event.key == K_RIGHT: # right key slides the block to the right
                    block.move_right()
                    block.slide = 1
                elif event.key == K_DOWN:  # down key for fast drop
                    block.move_down()
                    block.slide = 2
                elif event.key == K_SPACE:  # pause game
                    paused = True
                    pygame.mixer.music.pause()
                elif event.key == K_f:      # toggle fullscreen
                    if not fullscreen:
                        pygame.mouse.set_visible(False)
                        screen = pygame.display.set_mode((800,600), pygame.FULLSCREEN)
                        fullscreen = True
                    else:
                        pygame.mouse.set_visible(True)
                        screen = pygame.display.set_mode((800,600))
                        fullscreen = False
                elif event.key == K_ESCAPE:   # quit
                    if stats.score == stats.high_score: # save high score on exit
                        stats.new_high_score()
                    return

            elif event.type == KEYUP:    # releasing key stops the piece
                if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN:
                    block.slide = 0

        # pause mode
        while paused:
            clock.tick(60)
            screen.blit(pause_screen, (360,220))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        paused = False
                        pygame.mixer.music.unpause()
                    elif event.key == K_f:      # toggle fullscreen
                        if not fullscreen:
                            pygame.mouse.set_visible(False)
                            screen = pygame.display.set_mode((800,600), pygame.FULLSCREEN)
                            fullscreen = True
                        else:
                            pygame.mouse.set_visible(True)
                            screen = pygame.display.set_mode((800,600))
                            fullscreen = False
                    elif event.key == K_ESCAPE:   # quit
                        if stats.score == stats.high_score: # save high score on exit
                            stats.new_high_score()
                        return

        # check for collisions, break blocks up into squares,
        # use the grid to track position of squares(for coll. detection) , and
        # how many squares in each row (for line detection)
        if block.is_collided():
            if break_delay < 18:  # delay allows for short sliding over blocks
                break_delay += 1
            else:
                lock_sound.play()
                block.break_and_freeze(block_sprite, frozen_squares)  #break up the block
                block_sprite, block, next_block_sprite, next_block_type = choose_piece(grid, next_block_type)  # drop a new block
                if grid.squares_in_row[0] > 8:  # if stack reaches top, Game Over
                    if stats.score == stats.high_score:  # save high score
                        stats.new_high_score()
                    game_over_sound.play()
                    screen.blit(game_over_screen, (270, 220))
                    pygame.display.flip()
                    pygame.mixer.music.stop()
                    pygame.time.wait(5000)
                    game_over = True
                break_delay = 0

        get_line = detect_lines(grid)  # check for lines
        if get_line is not None:   # get_line holds the row number of the line
            line_sound.play()
            line_made = True  # start delete line timer
            line_at = get_line  # store the line row number for delete and shift function
            # make lines flash
            for square in frozen_squares:
                if square.row == line_at:
                    square.flashing = True
                    frozen_squares.update(pygame.time.get_ticks())
                    frozen_squares.draw(screen)
                    pygame.display.flip()

        if line_made:
            if delete_delay < 13:
                delete_delay += 1
            else:
                update_game(block, stats, level_up)
                delete_lines(grid, frozen_squares, line_at)
                line_made = False  # stop delete line timer
                line_deleted = True  # start shift squares timer
                delete_delay = 0

        if line_deleted:
            if shift_delay < 13:  # delay before shifting all squares down
                shift_delay += 1
            else:
                shift_squares(grid, frozen_squares, line_at)
                shift_delay = 0     # stop and reset timers
                line_deleted = False

        # redraw everything
        screen.blit(gamescreen, (0,0))
        block.update(pygame.time.get_ticks())
        block_sprite.draw(screen)
        next_block_sprite.draw(screen)
        stats.render_text()
        frozen_squares.draw(screen)
        pygame.display.flip()

    # game over, restart
    pygame.quit()
    main()

def choose_piece(grid, block_type):
    # function accepts an initial random block type selection, chooses the
    # next block, creates the new block to drop and the next block to draw,
    # passes the back the next block type chosen, so it can be passed back in
    # to create the current block
    block_type = block_type  # block type is the next block type returned from last call
    next_block_type = random.randint(0,6)   # choose a new next block

    # block to drop
    # calculate start point based on the tetris grid coords and cell size
    curr_init_xpos = grid.left + (4 * grid.cellsize - 30)
    curr_init_ypos = grid.top - 30
    curr_block = Block(block_type, curr_init_xpos, curr_init_ypos, grid)  # Create block object

    # Add pieces to a sprite list, creating a single block to be drawn
    curr_block_sprite = pygame.sprite.RenderPlain(curr_block.squares[0], curr_block.squares[1],
                                                  curr_block.squares[2], curr_block.squares[3])

    # next block, to draw in "next" window
    next_init_xpos = 630
    next_init_ypos = 60
    next_block = Block(next_block_type, next_init_xpos, next_init_ypos, grid)
    next_block_sprite = pygame.sprite.RenderPlain(next_block.squares[0], next_block.squares[1],
                                                  next_block.squares[2], next_block.squares[3])


    # return the sprite list, and the block object
    return curr_block_sprite, curr_block, next_block_sprite, next_block_type

def detect_lines(grid):
     for row in range(0,20):  # step through each row of the grid
        if grid.squares_in_row[row] == 10: # if there is a complete line
            return row   # return the row number

def delete_lines(grid, frozen_squares, row):
    # delete the squares in the row indicated by the
    # detect_lines function
    for square in frozen_squares:
        if square.row == row: # find the squares in that make up the line
            square.kill()
    grid.track_squares(frozen_squares)  # update the grid

def shift_squares(grid, frozen_squares, row):
    # shift all squares above line(s) down one cell
    for square in frozen_squares:
        if square.row < row:
            square.shift_down()
        grid.track_squares(frozen_squares)

def update_game(block, stats, level_up):
    global block_drop_delay
    clock = pygame.time.Clock()

    stats.score += 100
    stats.lines -= 1
    if stats.score > stats.high_score:
        stats.high_score = stats.score
    if stats.lines == 0:
        stats.score += 500
        stats.level += 1
        stats.lines = 25
        block_drop_delay -= 100
        level_up.play()
        while pygame.mixer.get_busy(): # wait for line sound to stop
            clock.tick(60)             # before playing level up sound
        level_up.play()

def play_music(name):
    # play selected music, if already playing
    # stop current song, play new one
    song = os.path.join('Data', name)
    if pygame.mixer.music.get_busy == False:
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

if __name__ == '__main__':
    main()