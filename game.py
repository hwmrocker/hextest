import pygame
import pygame.locals

screen = pygame.display.set_mode((1000,1000))
darkgreen = pygame.image.load('tiles/darkgreen.png')
lightgreen = pygame.image.load('tiles/lightgreen.png')

TILE_WIDTH = TILE_HEIGHT = 80
ODD_COL_DISTANCE = TILE_HEIGHT / 2
COL_WIDTH = (TILE_WIDTH / 4) * 3
COL_HEIGHT = TILE_HEIGHT



def draw(X,Y):
    for i in range(16):
        for j in range(12):
            tile = lightgreen
            if X == i and Y == j:
                tile = darkgreen
            foo = ODD_COL_DISTANCE if (i % 2 == 1) else 0
            screen.blit(tile, (i * COL_WIDTH, (j * COL_HEIGHT) + foo))

    pygame.display.flip()

def get_hex(x, y):
    column = ((x) / (COL_WIDTH))
    delta = ODD_COL_DISTANCE if column % 2 == 1 else 0
    row = ((y - delta) / (COL_HEIGHT))
    return column,row

def mainLoop():    
    X = Y = 0
    # pygame.init()    
    clock = pygame.time.Clock()
                    
    showGridRect = True

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return                
                elif event.key == pygame.locals.K_SPACE:
                    showGridRect = not showGridRect 
            
            elif event.type == pygame.locals.MOUSEMOTION:
                # setCursor(event.pos[0],event.pos[1])
                X,Y = get_hex(event.pos[0],event.pos[1])

        # DRAWING             
        draw(X,Y)

draw(0,0)
mainLoop()