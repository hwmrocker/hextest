import pygame
import pygame.locals
import random
screen = pygame.display.set_mode((1000,1000))
cursor = pygame.image.load('tiles/cursor.png')

TILE_WIDTH = TILE_HEIGHT = 80
ODD_COL_DISTANCE = TILE_HEIGHT / 2
COL_WIDTH = (TILE_WIDTH / 4) * 3
COL_HEIGHT = TILE_HEIGHT

class Map(pygame.sprite.Group):
    COLORS = [
        "black",
        "white",
        "brown",
        "darkblue",
        "darkgreen",
        "grey",
        "lightblue",
        "lightgreen",
        "red",
        "yellow"
    ]

    def __init__(self, x,y):
        pygame.sprite.Group.__init__(self)
        self._images = dict((color, pygame.image.load('tiles/%s.png' % color)) for color in self.COLORS)
        self._tiles=[]
        self.cursor = HexTile(-1,-1,cursor)
        for i in range(x):
            col = []
            for j in range(y):
                rand_col = random.choice(self.COLORS[2:])
                rand_img = self._images[rand_col]
                t = HexTile(i,j, rand_img)
                col.append(t)
                self.add(t)
            self._tiles.append(col)
        
        self.add(self.cursor)

    def draw(self, screen):
        pygame.sprite.Group.draw(self, screen)
        # self.cursor.draw(screen)
        screen.blit(self.cursor.image, self.cursor.position)

    def onClick(self, x, y):
        self._tiles[x][y].image = self._images["black"]

    def onMouseMove(self, x, y):
        self.cursor.update_position(x,y)

class HexTile(pygame.sprite.Sprite):
    def __init__(self, x,y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.update_position(x,y)

    def update_position(self, x,y):
        self.x = x
        self.y = y
        self.position = (x * COL_WIDTH, (y * COL_HEIGHT) + (ODD_COL_DISTANCE if (x % 2 == 1) else 0))
        self.rect.topleft = self.position

m = Map(16, 12)

def draw(X,Y):
    # for i in range(16):
    #     for j in range(12):
    #         tile = lightgreen
    #         if X == i and Y == j:
    #             tile = darkgreen
    #         foo = ODD_COL_DISTANCE if (i % 2 == 1) else 0
    #         screen.blit(tile, (i * COL_WIDTH, (j * COL_HEIGHT) + foo))
    m.draw(screen)
    # screen.blit(cursor, (X * COL_WIDTH, (Y * COL_HEIGHT) + (ODD_COL_DISTANCE if (X % 2 == 1) else 0)))
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
                m.onMouseMove(*get_hex(event.pos[0],event.pos[1]))
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                m.onClick(* get_hex(event.pos[0],event.pos[1]))

        # DRAWING             
        draw(X,Y)

draw(0,0)
mainLoop()