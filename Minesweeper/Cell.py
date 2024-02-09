class Cell:
  def __init__(self, location):
    self.location = location # tuple storing (x,y) pairing
    self.status = "empty" # status is for locating the sprite used on the board
    self.clicked = False
    self.flagged = False
    self.value = 0 # value states that value under a cell (-1 for mine)

  # handle a cell being clicked
  def handleLeftClick(self, board):
    if self.clicked: # if the cell has been clicked, ignore this one
      return
    
    self.clicked = True # the mine has been clicked
    board.clicked += 1 # increment the board's clicked cells

    # if the cell has a mine, end the game
    if self.value == -1: 
      self.status="mineClicked"
      board.checkState()
    # if the cell is the first cell clicked, place mines
    if board.clicked==1:
      board.place_mines(self)
    # if the cell is empty, make adjacent empty cells filled
    if self.value == 0:
      board.fillAdjacentEmptyCells(self)
    else:
      return
  
  # handle a cell being clicked
  def handleRightClick(self, board):
    board.clicked += 1 # note that a cell has been clicked

    # unflag a cell
    if self.flagged:
      self.flagged = False
      board.remainingMines+=1

    # flag a cell
    else:
      self.flagged = True
      board.remainingMines-=1
      if board.remainingMines==0:
        board.checkState()

  # add one to the value of a non mine cell  
  def addOne(self):
    if self.value == -1: # ignore mines
      return
    self.value += 1
    self.status = str(self.value)
    
  # recognize a cell as a mine
  def setMine(self):
    self.status = "mine"
    self.value = -1

  # returns if a cell is adjacent to a pair of x, y coordinates (or is on that cell)
  def isAdjacent(self, x, y):
    if (self.location == (x, y)):
      return True
    # Calculate the absolute difference in coordinates
    dx = abs(self.location[0] - x)
    dy = abs(self.location[1] - y)
    
    # Two cells are adjacent if their absolute differences in coordinates
    # are at most 1 in both directions (orthogonal or diagonal)
    return dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)