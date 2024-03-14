import pygame
import random
import time
import math
from Cell import Cell

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/digital-7.ttf", size)

class Board:
  def __init__(self, x, y, density):
    self.x = x # length on x coord
    self.y = y # length on y coord
    self.density = density # mine density as a %
    self.cells = [[]] # the board itself, a collection of cells
    self.clicked=0 # initialize the # of cells clicked

    #coordinates for drawing the board
    self.startingX = int(((1280) / 2) - (self.x * 32 / 2))
    self.startingY = int(((720) / 2) - (self.y * 32 / 2))

    
    self.state = 0 # game's state (lose, playing, win)
    self.remainingMines = 0 
    self.totalMines=0

    # variables for measuring time
    self.timer_started = False
    self.elapsedTime = 0

    # initialize an empty board
    for curX in range(x):
      self.cells.append([])
      for curY in range(y):
        newCell=Cell((curX, curY))
        self.cells[curX].append(newCell)

  # show all cells value
  def revealBoard(self):
    for row in self.cells:
      for cell in row:
        cell.clicked=True

  # displays the # of mines remaining on the top left of the screen
  def show_remaining_mines(self, screen):
    REMAINING_MINES_TEXT = get_font(48).render(str(self.remainingMines), True, "Red")
    REMAINING_MINES_TEXT_RECT = REMAINING_MINES_TEXT.get_rect(center=((self.startingX + 50, self.startingY - 32)))
    rect_surface = pygame.Surface((80, 50))
    rect_surface.fill("black")
    screen.blit(rect_surface, ((self.startingX + 10, self.startingY - 58)))
    screen.blit(REMAINING_MINES_TEXT, REMAINING_MINES_TEXT_RECT)

  # displays the time since the game started in the top right of the screen
  def show_elapsed_time(self, screen):
    TIME_TEXT = get_font(48).render(str(self.elapsedTime), True, "Red")
    TIME_TEXT_RECT = TIME_TEXT.get_rect(center=((self.startingX + (32 * self.x) - 50, self.startingY - 32)))
    rect_surface = pygame.Surface((80, 50))
    rect_surface.fill("black")
    screen.blit(rect_surface, ((self.startingX + (32 * self.x) - 90, self.startingY - 58)))
    screen.blit(TIME_TEXT, TIME_TEXT_RECT)

  # check if the game is over
  def checkState(self):
    unflaggedMines = self.totalMines
    for row in self.cells:
      for cell in row:
        if cell.value == -1 and cell.clicked:
          self.state = -1
          self.revealBoard()
          return
        if cell.flagged and cell.value == -1:
          unflaggedMines-=1
    if unflaggedMines == 0:
      self.state = 1

  # get a cell with a x and y coordinate
  def getCell(self, x, y):
    return self.cells[x][y]
  
  # given a cell, return all cells surrounding this cell
  def getAdjacentCells(self, cell):
    cells = []
    for x in range (cell.location[0] - 1, cell.location[0] + 2, 1):
        for y in range (cell.location[1] - 1, cell.location[1] + 2, 1):
          if (x >= 0 and x < self.x) and (y >= 0 and y < self.y):
            cells.append(self.getCell(x, y))
    return cells
  
  # add one to the siblings of a bomb
  def addToSiblings(self, cell):
      cells = self.getAdjacentCells(cell)
      for cell in cells:
        cell.addOne()
      

  # display a grid of x * y cells, each taking 32 pixels
  def draw_grid(self, screen, sprites):
    size = 32  # Size of each sprite

    #display the timer and mines
    if self.timer_started and self.state == 0:
      self.elapsedTime = min(int(time.time() - self.start_time), 999)
    self.show_remaining_mines(screen)
    self.show_elapsed_time(screen)

    # draw a border for the board
    pygame.draw.rect(screen, (100, 100, 100),
                     ((self.startingX - 5, self.startingY - 5), (self.x * 32 + 10, self.y * 32 + 10))
    )
    # display each cell
    for (x, cellRows) in zip(range(self.startingX, (self.x * size) + self.startingX, size), self.cells):
      for (y, cell) in zip(range(self.startingY, (self.y * size) + self.startingY, size), cellRows):
        # display clicked cells
        if cell.clicked:
          screen.blit(sprites[cell.status], (x, y))  # Draw the sprite onto the screen
        # display flagged cells
        elif cell.flagged:
          screen.blit(sprites["flag"], (x, y))
        # display unclicked grid cells
        else:
          screen.blit(sprites["grid"], (x, y))  # Draw the sprite onto the screen


  # load assets and draw the board
  def draw_board(self, screen):
    sprites = {}
    # Import sprites
    sprites['empty'] = pygame.image.load("assets/Sprites/empty.png")
    sprites['flag'] = pygame.image.load("assets/Sprites/flag.png")
    sprites['grid'] = pygame.image.load("assets/Sprites/Grid.png")
    sprites['1'] = pygame.image.load("assets/Sprites/grid1.png")
    sprites['2'] = pygame.image.load("assets/Sprites/grid2.png")
    sprites['3'] = pygame.image.load("assets/Sprites/grid3.png")
    sprites['4'] = pygame.image.load("assets/Sprites/grid4.png")
    sprites['5'] = pygame.image.load("assets/Sprites/grid5.png")
    sprites['6'] = pygame.image.load("assets/Sprites/grid6.png")
    sprites['7'] = pygame.image.load("assets/Sprites/grid7.png")
    sprites['8'] = pygame.image.load("assets/Sprites/grid8.png")
    sprites['mine'] = pygame.image.load("assets/Sprites/mine.png")
    sprites['mineClicked'] = pygame.image.load("assets/Sprites/mineClicked.png")
    sprites['mineFalse'] = pygame.image.load("assets/Sprites/mineFalse.png")

    # draw the sprites to the screen
    self.draw_grid(screen, sprites)


  # place the mines on the board, anywhere but where first clicked
  def place_mines(self, initialCell):
    # start the game loop
    self.timer_started = True
    self.start_time=time.time()

    # determine how many mines should appear based on the density %
    numberOfMines = round(self.x * self.y * (self.density / 100))
    # place the cells randomly on the board, if a cell already exists, draw it again
    i=0
    while i<numberOfMines: 
      x = random.randint(0, self.x-1)
      y = random.randint(0, self.y-1)
      # Do not place mines on the first cell clicked, or where a mine exists
      if initialCell.isAdjacent(x, y) or self.getCell(x,y).value == -1:
        continue
      self.getCell(x, y).setMine() # set the mine if on a valid cell
      self.addToSiblings(self.getCell(x, y))
      i+=1 # increment loop
    self.remainingMines=numberOfMines
    self.totalMines=numberOfMines

  # fill empty cells (status=0) adjacent to a clickeFd empty cell, 
  # along with the border or cells with adjacent mines
  def fillAdjacentEmptyCells(self, initialCell):
    adjacentCells=self.getAdjacentCells(initialCell)
    for cell in adjacentCells:
      if cell.value == 0:
        cell.handleLeftClick(self)
      if cell.value > 0:
        cell.handleLeftClick(self)

