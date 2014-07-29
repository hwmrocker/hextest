import pygame
import pygame.locals
import random
screen = pygame.display.set_mode((1000,1000))
cursor = pygame.image.load('tiles/cursor.png')

TILE_WIDTH = TILE_HEIGHT = 80
ODD_COL_DISTANCE = TILE_HEIGHT / 2
COL_WIDTH = (TILE_WIDTH / 4) * 3
ROW_HEIGHT = TILE_HEIGHT

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
        self._q = x
        self._r = y
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

    def _is_position_valid(self, position):
        q, r = position
        return 0 <= q < self._q and 0 <= r < self._r

    def draw(self, screen):
        pygame.sprite.Group.draw(self, screen)
        # self.cursor.draw(screen)
        screen.blit(self.cursor.image, self.cursor.position)

    def get_hex(self, x, y):
        column = ((x) / (COL_WIDTH))
        delta = ODD_COL_DISTANCE if column % 2 == 1 else 0
        row = ((y - delta) / (ROW_HEIGHT))
        return column, row
    
    def on_raw_click(self, x, y):
        position = self.get_hex(x, y)
        if not self._is_position_valid(position):
            return
        return self.on_click(position)

    def on_raw_mouse_move(self, x, y):
        position = self.get_hex(x, y)
        if not self._is_position_valid(position):
            return
        return self.on_mouse_move(position)

    def on_click(self, position):
        q, r = position
        self._tiles[q][r].image = self._images["black"]

    def on_mouse_move(self, position):
        q, r = position
        self.cursor.update_position(q, r)

class HexTile(pygame.sprite.Sprite):
    def __init__(self, q, r, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.update_position(q, r)

    def update_position(self, q, r):
        self.q = q
        self.r = r
        self.position = (q * COL_WIDTH, (r * ROW_HEIGHT) + (ODD_COL_DISTANCE if (q % 2 == 1) else 0))
        self.rect.topleft = self.position

class Position():
    def __init__(self, q=None, r=None, x=None, y=None, z=None):
        super(Position, self).__init__()
        self.q = q
        self.r = r
        if all(i is not None for i in (x,y,z)):
            self.cube = x,y,z
        elif all(i is not None for i in (x,z)):
            self.axial
    @property
    def offset(self):
        return self.q, self.r
    @offset.setter
    def offset(self, value):
        self.q, self.r = value

    @property
    def cube(self):
        x = self.q
        z = self.r - (self.q - (self.q&1)) / 2
        y = -x-z
        return x,y,z
    @cube.setter
    def cube(self, value):
        x,y,z = value
        self.q = x
        self.r = z + (x - (x&1)) / 2

    @property
    def axial(self):
        x,y,z = self.cube
        return x, z
    @axial.setter
    def axial(self, value):
        x,z = value
        self.cube = x,-x-z,z


m = Map(16, 12)

def draw(X,Y):
    # for i in range(16):
    #     for j in range(12):
    #         tile = lightgreen
    #         if X == i and Y == j:
    #             tile = darkgreen
    #         foo = ODD_COL_DISTANCE if (i % 2 == 1) else 0
    #         screen.blit(tile, (i * COL_WIDTH, (j * ROW_HEIGHT) + foo))
    m.draw(screen)
    # screen.blit(cursor, (X * COL_WIDTH, (Y * ROW_HEIGHT) + (ODD_COL_DISTANCE if (X % 2 == 1) else 0)))
    pygame.display.flip()


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
                m.on_raw_mouse_move(event.pos[0], event.pos[1])
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                m.on_raw_click(event.pos[0], event.pos[1])

        # DRAWING             
        draw(X,Y)

draw(0,0)
mainLoop()