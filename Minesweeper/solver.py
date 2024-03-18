import time
import threading
import sys
import itertools
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

    self.all_configurations = None

    # used in BFS and determining next cell to check for mines/clear around
    self.FinishedCells = set()
    self.edgeCells = []

    # objects to update screen
    self.screen = screen
    self.pygame = pygame
    self.source = (board.x // 2, board.y // 2) # first node clicked for original BFS
    self.visited = set() # set of visited cells

    # values for the probability of a cell being a mine
    self.hundredQueue = deque()
    self.zeroQueue = deque()
    self.probabilities = [[-1 for i in range(board.y)] for j in range(board.x)] # create a 2D array of probabilities initialized to -1
    self.sleepMode = True # create a 2D array of probabilities initialized to 0

  # check if an edge cell no longer needs checking for the states of adjacent cells
  def checkFinished(self, cell):
    unopened = self.countAdjacentUnopened(cell)
    flags = self.countAdjacentFlags(cell)
    if unopened != flags:
      return False
    
    return True
  
  def calculateAdjacentProbabilities(self, cell):
    flags = self.countAdjacentFlags(cell)
    unopened = self.countAdjacentUnopened(cell)
    adj_cells = self.board.getAdjacentCells(cell)
    clicked = self.countClicked(cell)
    if cell.value == flags:
      for adj_cell in adj_cells:
        if not adj_cell.clicked and adj_cell not in self.zeroQueue and not adj_cell.flagged:
          self.probabilities[adj_cell.location[0]][adj_cell.location[1]] = 0
          self.zeroQueue.append(adj_cell)
      if self.checkFinished(cell):
        self.FinishedCells.add(cell)
    elif clicked == len(adj_cells) - cell.value:
      for adj_cell in adj_cells:
        if not adj_cell.clicked and adj_cell not in self.hundredQueue and not adj_cell.flagged:
          self.probabilities[adj_cell.location[0]][adj_cell.location[1]] = 100
          self.hundredQueue.append(adj_cell)

  # count flags around a cell
  def countAdjacentFlags(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    count = 0
    for adj_cell in adj_cells:
      if adj_cell.flagged:
        count+=1
    return count
  
  # count unopened cells around a cell
  def countAdjacentUnopened(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    count = 0
    for adj_cell in adj_cells:
      if not adj_cell.clicked:
        count+=1
    return count
  
  def countClicked(self, cell):
    adj_cells = self.board.getAdjacentCells(cell)
    count = 0
    for adj_cell in adj_cells:
      if adj_cell.clicked:
        count+=1
    return count

  def makeSafeOpen(self):
      # Make safe open move
    if len(self.zeroQueue) != 0:
      cell = self.zeroQueue.popleft()
      cell.handleLeftClick(self.board)
      self.addNewKnowledge(cell)
      if self.sleepMode:
        time.sleep(0.01)
    else:
      if (len(self.hundredQueue) == 0):
        print("guessing")
        min_probability_cell = self.getCellWithLowestProbability()
        if min_probability_cell is None:
          print('error')
        min_probability_cell.handleLeftClick(self.board)
        print('done guessing')
      else:
        return
    # issue, WE HAVE TO GUESS
    # lets click the cell with the lowest odds of being a mine

  # update version of make safe flag that accounts for the probability queue
  def makeSafeFlag(self):
    if len(self.hundredQueue) != 0:
      cell = self.hundredQueue.popleft()
      if not cell.flagged:
        cell.handleRightClick(self.board)
      if self.sleepMode:
        time.sleep(0.01)
      #time.sleep(0.01)

  # calulates available probabilities if no zeroes, if there are still none make the most likely to succeed move
  def checkNextCell(self):
    updated_edge_cells = []
    for cell in self.edgeCells:
      self.calculateAdjacentProbabilities(cell)
      if self.checkFinished(cell):
        self.FinishedCells.add(cell)
        self.edgeCells.remove(cell)
    self.makeSafeOpen()
    self.makeSafeFlag()

  # initialize the playing of the game by the AI
  def initialize(self):
    if self.pygame:
      display_thread = threading.Thread(target=update_display, args=(self.board, self.screen, self.pygame), daemon=True)
      display_thread.start()
    if self.sleepMode:
      time.sleep(1)
    self.makeFirstMove()
    if self.sleepMode:
      time.sleep(1)
    self.getEdgeCells()

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

  # returns boolean, checks if a cell is on the edge of the board
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

  # breadth first search to find all cells that are on the edge of the board after the first click
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

  # add new knowledge of edges to the queue when a cell is clicked
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

  def getEdgeUnopened(self):
    unopened = []
    for cell in self.edgeCells:
      adj_cells = self.board.getAdjacentCells(cell)
      for adj_cell in adj_cells:
        if not adj_cell.clicked and not adj_cell.flagged:
          unopened.append(adj_cell)
    return unopened
    
  def calculateAllConfigurations(self):
    print("good luck")
    if self.all_configurations is None:
      unopened_edge_cells = [cell for cell in self.getEdgeUnopened()]
      num_unopened = len(unopened_edge_cells)
      remaining_mines = self.board.remainingMines - 1
      self.all_configurations = []
      print(min(num_unopened, remaining_mines))
      for num_mines in range(min(num_unopened, remaining_mines)):
        for configuration in itertools.combinations(unopened_edge_cells, num_mines):
          self.all_configurations.append(set(configuration))
    print("EscAPED")


  def countFlaggedConfigurations(self, target_cell):
    all_configurations = self.computeAllConfigurations()
    count = 0

    print(len(all_configurations))
    for configuration in all_configurations:
      if target_cell in configuration and self.isValidConfiguration(configuration):
        count += 1
        print(count)

    return count
  
  def isValidConfiguration(self, configuration):
    for edge_cell in self.edgeCells:
      adjacent_mines = [cell for cell in self.board.getAdjacentCells(edge_cell) if cell in configuration]
      if edge_cell.value != len(adjacent_mines):
        return False
    return True
  
  def calculateEdgeProbabilities(self):
    self.calculateAllConfigurations()
    num_configurations = len(self.all_configurations)
    unopened_cells = self.getEdgeUnopened()

    for cell in unopened_cells:
      flagged_configurations = 0
      for configuration in self.all_configurations:
        if cell in configuration:
          flagged_configurations += 1
      self.probabilities[cell.location[0]][cell.location[1]] = flagged_configurations / num_configurations * 100


  def getCellWithLowestProbability(self):
    self.calculateEdgeProbabilities()
    if self.board.state != 0:
      return
    min_probability = float('inf')
    min_probability_cell = None
    edge_cells = self.getEdgeUnopened()
    for cell in edge_cells:
      i, j = cell.location
      probability = self.probabilities[i][j]
      if not cell.clicked and not cell.flagged and probability < min_probability:
        min_probability = probability
        min_probability_cell = cell
    return min_probability_cell


  # deperecated funcitons
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
          
  #TO DO: adjust function to calculate odds of adjacent cells being mines, design another method to flag high probability mines and open low probability cells
  # rule one, we know all unopened cells around an existing cell are safe IF the cell has all neccessary flags around it
  """
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
  """

  """
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

  """
  # check the next cell in the queue
  def checkNextCell(self):
    cell = self.edgeCells.popleft()
    self.makeSafeFlag(cell)
    self.makeSafeMove(cell)
    self.checkFinished(cell)
  """