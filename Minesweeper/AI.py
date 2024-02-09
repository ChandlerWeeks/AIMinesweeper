from Board import Board
from Cell import Cell

def firstMove(board):
  if board.clicked > 0:
    return
  else:
    # Theory: Corners are safer to start at the prevent needing to guess later
    # We will start the board at the top left
    board.getCell(0, 0).handleLeftClick()
