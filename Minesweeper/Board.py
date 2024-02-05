import pygame
import random
import time
import math

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/digital-7.ttf", size)

class Board:
  def __init__(self, x, y, density):
    self.x = x
    self.y = y
    self.density = density
    self.cells = [[]]
    self.startingX = int(((1280) / 2) - (self.x * 32 / 2))
    self.startingY = int(((720) / 2) - (self.y * 32 / 2))
    self.clicked=0
    self.state = 0
    self.remainingMines = 0

    self.timer_started = False
    self.elapsedTime = 0

    # initialize an empty board
    for curX in range(x):
      self.cells.append([])
      for curY in range(y):
        newCell=Cell((curX, curY))
        self.cells[curX].append(newCell)

  def revealBoard(self):
    for row in self.cells:
      for cell in row:
        cell.clicked=True

  
  def show_remaining_mines(self, screen):
    REMAINING_MINES_TEXT = get_font(48).render(str(self.remainingMines), True, "Red")
    REMAINING_MINES_TEXT_RECT = REMAINING_MINES_TEXT.get_rect(center=((self.startingX + 50, self.startingY - 32)))
    rect_surface = pygame.Surface((80, 50))
    rect_surface.fill("black")
    screen.blit(rect_surface, ((self.startingX + 10, self.startingY - 58)))
    screen.blit(REMAINING_MINES_TEXT, REMAINING_MINES_TEXT_RECT)

  def show_elapsed_time(self, screen):
    TIME_TEXT = get_font(48).render(str(self.elapsedTime), True, "Red")
    TIME_TEXT_RECT = TIME_TEXT.get_rect(center=((self.startingX + (32 * self.x) - 50, self.startingY - 32)))
    rect_surface = pygame.Surface((80, 50))
    rect_surface.fill("black")
    screen.blit(rect_surface, ((self.startingX + (32 * self.x) - 90, self.startingY - 58)))
    screen.blit(TIME_TEXT, TIME_TEXT_RECT)


  def checkState(self):
    empty=0
    for row in self.cells:
      for cell in row:
        if cell.value == -1 and cell.clicked:
          self.state = -1
          self.revealBoard()
          print('made it here')
          return
        elif cell.clicked:
          continue
        else:
          empty+=1
    if empty > 0:
      state = 1


  def getCell(self, x, y):
    return self.cells[x][y]
  

  def getAdjacentCells(self, cell):
    cells = []
    for x in range (cell.location[0] - 1, cell.location[0] + 2, 1):
        for y in range (cell.location[1] - 1, cell.location[1] + 2, 1):
          if (x >= 0 and x < self.x) and (y >= 0 and y < self.y):
            cells.append(self.getCell(x, y))
    return cells
  

  def addToSiblings(self, cell):
      cells = self.getAdjacentCells(cell)
      for cell in cells:
        cell.addOne()
      

  # display a grid of x * y cells, each taking 32 pixels
  def draw_grid(self, screen, sprites):
    size = 32  # Size of each sprite
    if self.timer_started and self.state == 0:
      self.elapsedTime = min(int(time.time() - self.start_time), 999)
    self.show_remaining_mines(screen)
    self.show_elapsed_time(screen)
    pygame.draw.rect(screen, (100, 100, 100),
                     ((self.startingX - 5, self.startingY - 5), (self.x * 32 + 10, self.y * 32 + 10))
    )
    for (x, cellRows) in zip(range(self.startingX, (self.x * size) + self.startingX, size), self.cells):
      for (y, cell) in zip(range(self.startingY, (self.y * size) + self.startingY, size), cellRows):
        if cell.clicked:
          screen.blit(sprites[cell.status], (x, y))  # Draw the sprite onto the screen
        elif cell.flagged:
          screen.blit(sprites["flag"], (x, y))
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

    self.draw_grid(screen, sprites)


  # place the mines on the board, anywhere but where first clicked
  def place_mines(self, initialCell):
    self.timer_started = True
    self.start_time=time.time()
    numberOfMines = round(self.x * self.y * (self.density / 100))
    i=0
    while i<numberOfMines:
      x = random.randint(0, self.x-1)
      y = random.randint(0, self.y-1)
      if initialCell.isAdjacent(x, y) or self.getCell(x,y).value == -1:
        continue
      self.getCell(x, y).setMine()
      self.addToSiblings(self.getCell(x, y))
      i+=1
    self.remainingMines=numberOfMines

  
  def fillAdjacentEmptyCells(self, initialCell):
    adjacentCells=self.getAdjacentCells(initialCell)
    for cell in adjacentCells:
      if cell.value == 0:
        cell.handleLeftClick(self)
      if cell.value > 0:
        cell.handleLeftClick(self)


class Cell:
  def __init__(self, location):
    self.location = location # tuple storing (x,y) pairing
    self.status = "empty" # status is for locating the sprite used on the board
    self.clicked = False
    self.flagged = False
    self.value = 0 # value states that value under a cell (-1 for mine)

  def handleLeftClick(self, board):
    if self.clicked:
      return
    
    self.clicked = True
    board.clicked += 1
    if self.value == -1:
      self.status="mineClicked"
      board.checkState()
    if board.clicked==1:
      board.place_mines(self)
    if self.value == 0:
      board.fillAdjacentEmptyCells(self)
    else:
      return 1
    
  def handleRightClick(self, board):
    if self.flagged:
      self.flagged = False
      board.remainingMines+=1
    else:
      self.flagged = True
      board.remainingMines-=1
      if board.remainingMines==0:
        board.checkState()
    
  def addOne(self):
    if self.value == -1:
      return
    self.value += 1
    self.status = str(self.value)
    
  def setMine(self):
    self.status = "mine"
    self.value = -1

  def isAdjacent(self, x, y):
    if (self.location == (x, y)):
      return True
    # Calculate the absolute difference in coordinates
    dx = abs(self.location[0] - x)
    dy = abs(self.location[1] - y)
    
    # Two cells are adjacent if their absolute differences in coordinates
    # are at most 1 in both directions (orthogonal or diagonal)
    return dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)