from Board import Board
from solver import Solver
import time

board = Board(30, 30, 10.0)
ai = Solver(board, None, None)

ai.initialize()

while ai.board.state == 0:
  ai.checkNextCell()
  if ai.board.state != 0:
    break

if ai.board.state == 1:
  print (f"won in {min(int(time.time() - board.start_time), 999)} seconds")
else:
  print(f"lost in {min(int(time.time() - board.start_time), 999)} seconds")