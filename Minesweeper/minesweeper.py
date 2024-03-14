import pygame
import pygame_gui
import sys
from Board import Board
import Menu
import time
from solver import Solver

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAME_RATE = 60

clock = pygame.time.Clock()

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/BG.png")

manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/mine-sweeper.ttf", size)

# GUI for the main menu
def main_menu():
  SCREEN.fill("White")
  response = Menu.menu_loop(SCREEN_WIDTH, SCREEN_HEIGHT, manager, SCREEN)
  play(response[0], response[1], response[2])
  return

def play(length, width, density):
  board = Board(length, width, density)
  ai = Solver(board, SCREEN, pygame)
  ai_mode = True
  SCREEN.fill("White")
  pygame.display.set_caption("Minesweeper")
  SCREEN.blit(BG, (0, 0))
  board.draw_board(SCREEN)
  while True:
    clock.tick(FRAME_RATE)
    if ai_mode:
      ai.initialize()
      while True:
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
          if board.state == 0:
            ai.checkNextCell()
          else:
            board.draw_board(SCREEN)
            pygame.display.update()
    else:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if board.state == 0:
          if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
              try:
                xClicked, yClicked = event.pos
                col = (xClicked - board.startingX) // 32
                row = (yClicked - board.startingY) // 32
                board.getCell(col, row).handleLeftClick(board)
                SCREEN.blit(BG, (0, 0))
              except IndexError:
                continue
            elif event.button == 3:
              try:
                xClicked, yClicked = event.pos
                col = (xClicked - board.startingX) // 32
                row = (yClicked - board.startingY) // 32
                board.getCell(col, row).handleRightClick(board)
                SCREEN.blit(BG, (0, 0))
              except IndexError:
                continue


    board.draw_board(SCREEN)
    pygame.display.update()

  def gameOver(msg):
    return

main_menu()

pygame.quit()
sys.exit()
