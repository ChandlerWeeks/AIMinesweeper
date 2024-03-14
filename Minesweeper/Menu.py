import pygame
import pygame_gui
import sys

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/mine-sweeper.ttf", size)

def menu_loop(SCREEN_WIDTH, SCREEN_HEIGHT, manager, SCREEN, FRAME_RATE=60):
  # initialize variables
  current_width = 8
  current_height = 8
  current_mine_density = 10.0
  BG = pygame.image.load("assets/BG.png")

  # create pygame_GUI objects
  PLAY_BUTTON = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT/2 + 150), (100, 50)),
    text="START",
    manager=manager
  )
  HORIZONTAL_SLIDER = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((SCREEN_WIDTH/2 - 175, SCREEN_HEIGHT/2 - 50), (400, 30)),
    start_value=10,
    value_range=(8, 30)
  )
  VERTICAL_SLIDER = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((SCREEN_WIDTH/2 - 175, SCREEN_HEIGHT/2), (400, 30)),
    start_value=10,
    value_range=(8, 18)
  )
  MINES_DENSITY_SLIDER = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((SCREEN_WIDTH/2 - 175, SCREEN_HEIGHT/2 + 50), (400, 30)),
    start_value=10,
    value_range=(5.0, 30.0),
  )
  while True:
    SCREEN.blit(BG, (0, 0))

    # Create text that appears on the screen using pygame's blit function
    # There is certainly an easier way to solve this, this works though 
    MENU_TEXT = get_font(48).render("MINESWEEPER", True, "Black")
    MENU_TEXT_RECT = MENU_TEXT.get_rect(center=((SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 225)))
    SCREEN.blit(MENU_TEXT, MENU_TEXT_RECT)

    HORIZONTAL_SLIDER_LABEL = get_font(16).render("Board Width", True, "Black")
    HORIZONTAL_SLIDER_LABEL_RECT = HORIZONTAL_SLIDER_LABEL.get_rect(center=((SCREEN_WIDTH/2 - 275, SCREEN_HEIGHT/2 - 36)))
    SCREEN.blit(HORIZONTAL_SLIDER_LABEL, HORIZONTAL_SLIDER_LABEL_RECT)

    VERTICAL_SLIDER_LABEL = get_font(16).render("Board Height", True, "Black")
    VERTICAL_SLIDER_LABEL_RECT = VERTICAL_SLIDER_LABEL.get_rect(center=((SCREEN_WIDTH/2 - 275, SCREEN_HEIGHT/2 + 14)))
    SCREEN.blit(VERTICAL_SLIDER_LABEL, VERTICAL_SLIDER_LABEL_RECT)

    MINE_DENSITY_LABEL = get_font(16).render("Mine Density", True, "Black")
    MINE_DENSITY_LABEL_RECT = MINE_DENSITY_LABEL.get_rect(center=((SCREEN_WIDTH/2 - 275, SCREEN_HEIGHT/2 + 64)))
    SCREEN.blit(MINE_DENSITY_LABEL, MINE_DENSITY_LABEL_RECT)

    WIDTH_LABEL = get_font(16).render(str(current_width), True, "Black")
    WIDTH_LABEL_RECT = WIDTH_LABEL.get_rect(center=((SCREEN_WIDTH/2 + 250, SCREEN_HEIGHT/2 - 36)))
    SCREEN.blit(WIDTH_LABEL, WIDTH_LABEL_RECT)

    HEIGHT_LABEL = get_font(16).render(str(current_height), True, "Black")
    HEIGHT_LABEL_RECT = HEIGHT_LABEL.get_rect(center=((SCREEN_WIDTH/2 + 250, SCREEN_HEIGHT/2 + 14)))
    SCREEN.blit(HEIGHT_LABEL, HEIGHT_LABEL_RECT)

    MINE_DENSITY_LABEL = get_font(16).render(str(current_mine_density) + "%", True, "Black")
    MINE_DENSITY_LABEL_RECT = MINE_DENSITY_LABEL.get_rect(center=((SCREEN_WIDTH/2 + 272, SCREEN_HEIGHT/2 + 64)))
    SCREEN.blit(MINE_DENSITY_LABEL, MINE_DENSITY_LABEL_RECT)

    # set the framerate
    time_delta = pygame.time.Clock().tick(FRAME_RATE) / 1000.0        

    # register any events that happen on the menu
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == PLAY_BUTTON:         
          return (current_width, current_height, current_mine_density)
      if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
        if event.ui_element == HORIZONTAL_SLIDER:
          current_width = round(event.value)
        if event.ui_element == VERTICAL_SLIDER:
          current_height = round(event.value)
        if event.ui_element == MINES_DENSITY_SLIDER: 
          current_mine_density = round(event.value, 1)

      manager.process_events(event) # process pygame_GUI events

    # update the menu
    manager.update(time_delta)
    manager.draw_ui(SCREEN)
    pygame.display.update()