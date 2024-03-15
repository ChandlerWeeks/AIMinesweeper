import time
import threading
import sys
from collections import deque

# function to update the screen every 1/10th a second
def update_display(board, screen, pygame):
  while board.state == 0:
    board.draw_board(screen)
    pygame.display.update()
    time.sleep(0.1)

class Solver:
  def __init__(self, board, screen, pygame):
    self.board = board

    # used in BFS and determining next cell to check for mines/clear around
    self.FinishedCells = set()
    self.edgeCells = deque()

    # objects to update screen
    self.screen = screen
    self.pygame = pygame
    self.source = (board.x // 2, board.y // 2) # first node clicked for original BFS
    self.visited = set()

    # values for the probability of a cell being a mine
    self.hundredCount = 0
    self.zeroCount = 0
    self.probabilities = [[-1 for i in range(board.y)] for j in range(board.x)] # create a 2D array of probabilities initialized to 0

  def checkFinished(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    for adj_cell in adj_cells:
      if not adj_cell.clicked or not adj_cell.flagged:
        return False
      
    return True
  
  #TODO: finsih this function, implement into project
  def calulateAdjacentProbabilities(self, cell):
    flags = self.countAdjacentFlags(cell)
    unopened = self.countAdjacentUnopened(cell)
    adj_cells = self.board.getAdjacentCells(cell)
    if cell.value == flags:
      for adj_cell in adj_cells:
        if not adj_cell.clicked:
          self.probabilities[adj_cell.location[0]][adj_cell.location[1]] = 0
          self.zeroCount += 1
    elif unopened == len(adj_cells) - cell.value:
      for adj_cell in adj_cells:
        if not adj_cell.clicked:
          self.probabilities[adj_cell.location[0]][adj_cell.location[1]] = 100
          self.hundredCount += 1
    #else:
      #for adj_cell in adj_cells:
        #if not adj_cell.clicked:
          #self.probabilities[adj_cell.x][adj_cell.y] = (cell.value - flags) / unopened



  def countAdjacentFlags(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    count = 0
    for adj_cell in adj_cells:
      if adj_cell.flagged:
        count+=1
    return count
  
  def countAdjacentUnopened(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    count = 0
    for adj_cell in adj_cells:
      if not adj_cell.clicked:
        count+=1
    return count

  #TODO: adjust function to calculate odds of adjacent cells being mines, design another method to flag high probability mines and open low probability cells
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
          time.sleep(0.01)
    if self.checkFinished(cell):
      self.FinishedCells.add(cell)
    else:
      self.edgeCells.append(cell)
      for adj_cell in adj_cells:
        if not adj_cell.flagged:
          self.addNewKnowledge(adj_cell)

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
          time.sleep(0.01)
    if self.checkFinished(cell):
      self.FinishedCells.add(cell)

  """
  # after making the first guess, start getting cells
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
  def makeNextMove(self):
    self.getEdgeCells()
    for cell in getEdgeCells:
      self.calulateAdjacentProbabilities(cell)

  def checkNextCell(self):
    if self.edgeCells:
      cell = self.edgeCells.popleft()
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
    #self.getEdgeCells()

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

  def isEdgeCell(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    for adj_cell in adj_cells:
        if not adj_cell.clicked:
            return True
    return False

  # get cells on the edge of the board, and mark cells that no longer need checking
  def getEdgeCells(self):
    self.edgeCells.clear()  # Clear the list of edge cells
    cell = self.board.getCell(self.source[0], self.source[1])
    self.visited.clear()
    self.bfs(cell)
    print('call to getEdgeCells finished')

  def bfs(self, cell):
    queue = deque([cell])
    while queue:
      cell = queue.popleft()
      if cell in self.visited:
        continue
      self.visited.add(cell)
      if cell.clicked and cell.value == 0:
        self.FinishedCells.add(cell)
      if cell.clicked and cell not in self.FinishedCells:
        self.edgeCells.append(cell)
      for adj_cell in self.board.getAdjacentCells(cell):
        if adj_cell.clicked and adj_cell not in self.visited:
          queue.append(adj_cell)

  def addNewKnowledge(self, source):
    queue = deque([source])
    while queue:
      cell = queue.popleft()
      if cell in self.visited:
        continue
      self.visited.add(cell)
      if cell.clicked and cell.value == 0:
        self.FinishedCells.add(cell)
      if cell.clicked and cell not in self.FinishedCells:
        self.edgeCells.append(cell)
      for adj_cell in self.board.getAdjacentCells(cell):
        if adj_cell.clicked and adj_cell not in self.visited:
          queue.append(adj_cell)