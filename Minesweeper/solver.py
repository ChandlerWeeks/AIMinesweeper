import time
import threading
import sys
from collections import deque

def update_display(board, screen, pygame):
  while board.state == 0:
    board.draw_board(screen)
    pygame.display.update()
    time.sleep(0.1)

class Solver:
  def __init__(self, board, screen, pygame):
    self.board = board
    self.FinishedCells = set()
    self.edgeCells = deque()
    self.screen = screen
    self.pygame = pygame

  def checkFinished(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    for adj_cell in adj_cells:
      if not adj_cell.clicked or not adj_cell.flagged:
        return False
      
    return True

  # rule one, we know all unopened cells around an existing cell are safe IF the cell has all neccessary flags around it
  def makeSafeMove(self, cell):
    count = 0
    adj_cells = self.board.getAdjacentCells(cell)
    for adj_cell in adj_cells:
      if adj_cell.flagged:
        count+=1
        #print(count, cell.value)
    if count==cell.value:
      for adj_cell in adj_cells:
        if not adj_cell.flagged:
          adj_cell.handleLeftClick(self.board)
    if self.checkFinished(cell):
      self.FinishedCells.add(cell)
    time.sleep(0.01)


  # rule two, we know if all unopened cells around an existing cell are mines IF the cell has the ammount of unopened cells as the # it has
  def makeSafeFlag(self, cell):
    count = 0
    adj_cells = self.board.getAdjacentCells(cell)
    for adj_cell in adj_cells:
      if adj_cell.clicked:
        count+=1
    if count==len(adj_cells)-cell.value:
      for adj_cell in adj_cells:
        if not adj_cell.flagged and not adj_cell.clicked:
          adj_cell.handleRightClick(self.board)
    if self.checkFinished(cell):
      self.FinishedCells.add(cell)
    time.sleep(0.01)

  """# after making the first guess, start getting cells
  def checkGuarenteedAdjacent(self):
    while self.board.state == 0:
      self.getEdgeCells()
      for edge in self.edgeCells:
        cell = self.board.getCell(edge[0], edge[1])
        if cell in self.FinishedCells:
          continue
        self.makeSafeFlag(cell)
        self.makeSafeMove(cell)

        if self.board.state != 0:
          break
          """

  def checkNextCell(self):
    for i in range(20):
      if self.edgeCells:
        tuple = self.edgeCells.popleft()
        cell = self.board.getCell(tuple[0], tuple[1])
        self.makeSafeFlag(cell)
        self.makeSafeMove(cell)
        self.checkFinished(cell)
      else:
        self.getEdgeCells()

  def initialize(self):
    if self.pygame:
      display_thread = threading.Thread(target=update_display, args=(self.board, self.screen, self.pygame), daemon=True)
      display_thread.start()
    time.sleep(1)  # pause for 0.1 seconds
    self.makeFirstMove()

  # i chose to start in the middle, many recommend starting in a corner however, to minimize 50/50's
  def makeFirstMove(self):
    x = self.board.x // 2
    y = self.board.y // 2
    self.board.getCell(x, y).handleLeftClick(self.board)
    
  # print the board to the conosle
  def printBoard(self):
    for row in self.board.cells:
      for cell in row:
        if cell.clicked:
          print(cell.value, end="")
        elif cell.flagged:
          print("f", end="")
        else:
          print("-", end="")
      print("\n")
    print("done")

  # get cells on the edge of the board, and mark cells that no longer need checking
  #TODO: SPEED THIS SHIT UP
  def getEdgeCells(self):
    for row in self.board.cells:
      for cell in row:
        if cell.clicked and cell not in self.FinishedCells:
          if cell.value == 0:
            self.FinishedCells.add(cell)
          adj_cells = self.board.getAdjacentCells(cell)
          for adj_cell in adj_cells:
            if adj_cell.clicked:
              self.edgeCells.append((cell.location[0], cell.location[1]))
              break



  