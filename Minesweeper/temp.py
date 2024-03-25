import time
import threading
import sys
import itertools
from collections import deque
import random

# function to update the screen every 1/10th a second
def update_display(board, screen, pygame):
  while board.state == 0:
    board.draw_board(screen)
    pygame.display.update()
    time.sleep(0.01)

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
    flags = self.countAdjacentFlags(cell)
    unopened = self.countAdjacentUnopened(cell)
    if (cell.value == flags and unopened == 0) or self.board.remainingMines == 0:
      self.edgeCells.remove(cell)
      return True
    return False
  
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
      if cell is not None:  # Check if cell is not None
        cell.handleLeftClick(self.board)
        self.addNewKnowledge(cell)
        if self.sleepMode:
          time.sleep(0.01)
        else:
          pass
    else:
      if len(self.hundredQueue) == 0:
        self.make_decision_based_on_probabilities()


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
    if self.board.state == 0:
      for cell in self.edgeCells:
        self.calculateAdjacentProbabilities(cell)
        if self.checkFinished(cell):
          self.FinishedCells.add(cell)
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
  
  def is_configuration_valid(self, configuration):
    for cell in self.edgeCells:
        if not cell.clicked:  # Skip if the cell is not revealed
            continue
        adjacent_mines = sum(1 for adj in self.board.getAdjacentCells(cell) if adj in configuration)
        if adjacent_mines != cell.value:
            return False
    return True
  
  def calculateEdgeProbabilities(self):
    configurations = self.calculate_all_configurations()
    if configurations is None:
      configurations = []
    num_configurations = len(configurations)
    unopened_cells = self.getEdgeUnopened()

    for cell in unopened_cells:
      flagged_configurations = 0
      for configuration in configurations:
        if cell in configuration:
          flagged_configurations += 1
      if num_configurations > 0:
        self.probabilities[cell.location[0]][cell.location[1]] = flagged_configurations / num_configurations * 100
      else:
        self.probabilities[cell.location[0]][cell.location[1]] = 100

  def make_decision_based_on_probabilities(self):
    self.calculateEdgeProbabilities()
    unopened_edge_cells = self.getEdgeUnopened()
    min_probability = float('inf')
    min_cell = None
    for cell in unopened_edge_cells:
      if not cell.clicked and not cell.flagged and self.probabilities[cell.location[0]][cell.location[1]] < min_probability:
        min_probability = self.probabilities[cell.location[0]][cell.location[1]]
        min_cell = cell
    if min_cell is not None:
      # Introduce a randomness factor to implement exploration
      if random.random() < 0.05:  # 5% chance to explore
        if unopened_edge_cells:
          min_cell = random.choice(unopened_edge_cells)
      self.zeroQueue.append(min_cell)
    else:
      # All cells have been clicked or flagged, make a random guess
      unopened_edge_cells = self.getEdgeUnopened()
      if unopened_edge_cells:
        random_cell = random.choice(unopened_edge_cells)
        self.zeroQueue.append(min_cell)
      else:
        if self.board.elapsedTime < 15:
          self.board.state = -1 # Critical failure, this shouldnt happen but take the L when it does

  def are_cells_connected(self, cells):
    for cell in cells:
      adj_cells = self.board.getAdjacentCells(cell)
      if not any(adj_cell in cells for adj_cell in adj_cells):
        return False
    return True

  def dfs(self, cell, visited, strip):
    visited.add(cell)
    strip.append(cell)
    for adj_cell in self.board.getAdjacentCells(cell):
      if adj_cell in self.getEdgeUnopened() and adj_cell not in visited:
        self.dfs(adj_cell, visited, strip)

  def calculate_all_configurations(self):
    unopened_edge_cells = self.getEdgeUnopened()
    self.all_configurations = []
    visited = set()
    memo = {}  # Initialize memo dictionary
    for cell in unopened_edge_cells:
      if cell not in visited:
        strip = []
        self.dfs(cell, visited, strip)
        if len(strip) > 0:
          self.explore_mine_configurations(strip, self.board.remainingMines, set(), memo)  # Pass memo to function

  def is_partial_configuration_valid(self, configuration):
    for row in self.board.cells:
      for cell in row:
        if cell.clicked:  # The cell is clicked
          mines = len([adj_cell for adj_cell in self.board.getAdjacentCells(cell) if adj_cell in configuration])
          if mines > cell.value:  # The number of mines is greater than the cell's value
            return False
    return True

  def explore_mine_configurations(self, border_tiles, depth, current_configuration, memo):
    # Convert set to frozenset before using it as a key
    current_configuration_key = frozenset(current_configuration)

    # Base case: Check if current configuration is valid
    if current_configuration_key in memo:
      return memo[current_configuration_key]
    if self.is_configuration_valid(current_configuration):
      self.all_configurations.append(current_configuration.copy())
      self.last_valid_configuration = current_configuration.copy()
      memo[current_configuration_key] = True
      return True

    # Pruning: If the current configuration is not valid, stop the recursion
    if not self.is_partial_configuration_valid(current_configuration):
      memo[current_configuration_key] = False
      return False

    # Pruning: If the number of mines left to place is less than the number of cells left to process, stop the recursion
    if self.board.remainingMines < len(border_tiles) - depth:
      memo[current_configuration_key] = False
      return False

    # Recursive case: Explore further if not all border tiles have been processed
    if depth < len(border_tiles):
      cell = border_tiles[depth]
      # Assume the current cell is a mine and explore
      current_configuration.add(cell)
      if self.explore_mine_configurations(border_tiles, depth + 1, current_configuration, memo):
        memo[current_configuration_key] = True
        return True
      # Only remove the cell if it's in the set
      if cell in current_configuration:
        current_configuration.remove(cell)
      # Assume the current cell is not a mine and explore
      if self.explore_mine_configurations(border_tiles, depth + 1, current_configuration, memo):
        memo[current_configuration_key] = True
        return True

    memo[current_configuration_key] = False
    return False


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