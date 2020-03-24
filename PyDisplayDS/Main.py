import pygame

INPUT_DISPLAY_ENABLED = True
if INPUT_DISPLAY_ENABLED:
    pygame.init()

    pygame.display.set_caption("PyDisplayDS")
    screen = pygame.display.set_mode((700, 700))

    ds = pygame.image.load("PyDisplayDS/DS_corrected.png")
    ds = pygame.transform.scale(ds, (700, 700))

    up = pygame.image.load("PyDisplayDS/up.png")
    up = pygame.transform.scale(up, (700, 700))

    down = pygame.image.load("PyDisplayDS/down.png")
    down = pygame.transform.scale(down, (700, 700))

    left = pygame.image.load("PyDisplayDS/left.png")
    left = pygame.transform.scale(left, (700, 700))

    right = pygame.image.load("PyDisplayDS/right.png")
    right = pygame.transform.scale(right, (700, 700))

    a = pygame.image.load("PyDisplayDS/a.png")
    a = pygame.transform.scale(a, (700, 700))

    b = pygame.image.load("PyDisplayDS/b.png")
    b = pygame.transform.scale(b, (700, 700))

    x = pygame.image.load("PyDisplayDS/x.png")
    x = pygame.transform.scale(x, (700, 700))

    y = pygame.image.load("PyDisplayDS/y.png")
    y = pygame.transform.scale(y, (700, 700))

    l = pygame.image.load("PyDisplayDS/l.png")
    l = pygame.transform.scale(l, (700, 700))

    r = pygame.image.load("PyDisplayDS/r.png")
    r = pygame.transform.scale(r, (700, 700))

    start = pygame.image.load("PyDisplayDS/start.png")
    start = pygame.transform.scale(start, (700, 700))

    select = pygame.image.load("PyDisplayDS/select.png")
    select = pygame.transform.scale(select, (700, 700))

    battery = pygame.image.load("PyDisplayDS/low_battery.png")
    battery = pygame.transform.scale(battery, (700, 700))

if INPUT_DISPLAY_ENABLED == False:
    pygame.quit()

def display_inputs(inputs):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255,00,255))
    #screen.blit(ds, (0,0))


    font = pygame.font.SysFont("AGENCYR.ttf", 54)
    for i,button in enumerate(inputs):
        screen.blit(font.render(button.capitalize(), False, (0, 255, 0)), (10, 10+i*35))

    """
    for input in inputs:
        if input == "up":
            screen.blit(font.render("Up", False, (0, 255, 0)), (10, 10))
            #screen.blit(up, (0,0))
        if input == "down":
            screen.blit(font.render("Down", False, (0, 255, 0)), (10, 45))
            #screen.blit(down, (0,0))
        if input == "left":
            screen.blit(font.render("Left", False, (0, 255, 0)), (10, 80))
            #screen.blit(left, (0,0))
        if input == "right":
            screen.blit(font.render("Right", False, (0, 255, 0)), (10, 115))
            #screen.blit(right, (0,0))
        if input == "x":
            screen.blit(font.render("X", False, (0, 255, 0)), (10, 150))
            #screen.blit(x, (0,0))
        if input == "y":
            screen.blit(font.render("Y", False, (0, 255, 0)), (10, 185))
            #screen.blit(y, (0,0))
        if input == "a":
            screen.blit(font.render("A", False, (0, 255, 0)), (10, 220))
            #screen.blit(a, (0,0))
        if input == "b":
            screen.blit(font.render("B", False, (0, 255, 0)), (10, 255))
            #screen.blit(b, (0,0))
        if input == "l":
            screen.blit(font.render("L", False, (0, 255, 0)), (10, 290))
            #screen.blit(l, (0,0))
        if input == "r":
            screen.blit(font.render("R", False, (0, 255, 0)), (10, 325))
            #screen.blit(r, (0,0))
        if input == "z":
            screen.blit(font.render("Z", False, (0, 255, 0)), (10, 360))
            #screen.blit(r, (0,0))
        if input == "start":
            screen.blit(font.render("Start", False, (0, 255, 0)), (10, 395))
            #screen.blit(start, (0,0))
        if input == "select":
            screen.blit(font.render("Select", False, (0, 255, 0)), (10, 430))
            #screen.blit(select, (0,0))
        #if input == "#": screen.blit(battery, (0,0))
    """
    pygame.display.update()











#
