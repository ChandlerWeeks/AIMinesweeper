from Board import Board
from solver import Solver
import time

easyWins = 0
mediumWins = 0
hardWins = 0

iterations = 100

print('starting easy benchmarks')

# Benchmarks for easy
for i in range(iterations):
  board = Board(9, 9, 10)
  ai = Solver(board, None, None)
  ai.sleepMode = False

  ai.initialize()

  while ai.board.state == 0:
    ai.checkNextCell()
    if ai.board.state != 0:
      break
  if board.state == 1:
    easyWins += 1
  print(i)

print("easy benchmark done")


# Benchmarks for beginner
for i in range(iterations):
  board = Board(16, 16, 15)
  ai = Solver(board, None, None)
  ai.sleepMode = False

  ai.initialize()

  while ai.board.state == 0:
    ai.checkNextCell()
    if ai.board.state != 0:
      break
  if board.state == 1:
    mediumWins += 1

print("medium benchmark done")

# Benchmarks for expert
for i in range(iterations):
  board = Board(30, 24, 20)
  ai = Solver(board, None, None)
  ai.sleepMode = False

  ai.initialize()

  while ai.board.state == 0:
    ai.checkNextCell()
    if ai.board.state != 0:
      break
  if board.state == 1:
    hardWins += 1


print("hard benchmark done")

print(f"Easy win rate: {round(easyWins / iterations * 100, 2)}%")
print(f"Medium win rate: {round(mediumWins / iterations * 100, 2)}%")
print(f"Hard win rate: {round(hardWins / iterations * 100, 2)}%")

