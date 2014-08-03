import pygame
import pygame.locals
import random
from itertools import cycle
from collections import Counter
from popup import Popup
import yaml


TILE_WIDTH = TILE_HEIGHT = 80

EVEN_COL_DISTANCE = 0
ODD_COL_DISTANCE = TILE_HEIGHT // 2

# we use flat topped hexagons
COL_WIDTH = (TILE_WIDTH // 4) * 3
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

    def __init__(self, x=None, y=None, filename=None):
        assert x and y or filename
        pygame.sprite.Group.__init__(self)
        self._images = dict((color, pygame.image.load('tiles/%s.png' % color)) for color in self.COLORS)
        self.player_colors = ["black", "white"]
        self.auto_players = ["white"]
        self._tiles = []
        self.cursor = HexTile(-1, -1, "a", {"a": pygame.image.load('tiles/cursor.png')})
        self._q = x
        self._r = y
        self.winner = None
        self.popup = Popup()
        self.popup.add("Welcome")
        self.popup.add("to the jungle", start=1)
        if filename:
            self.load_map(filename)
            if x and y:
                assert x == self._q and y == self._r
        else:
            self.generate_random_map()
            self.save_map()
            # self.add(self.cursor)

    def generate_random_map(self):
        self.empty()
        self._tiles = []
        for i in range(self._q):
            col = []
            for j in range(self._r):
                rand_col = random.choice(self.COLORS[2:])
                t = HexTile(i, j, rand_col, self._images)
                col.append(t)
                self.add(t)
            self._tiles.append(col)

        self.generate_neighbour_links()

    def generate_neighbour_links(self):
        self.black_group = Group(tiles=[self._tiles[0][-1]], color="black")
        self.white_group = Group(tiles=[self._tiles[-1][0]], color="white")
        self.player_groups = [self.black_group, self.white_group]
        self.iter_player_groups = cycle([self.black_group, self.white_group])
        self.player_group = next(self.iter_player_groups)
        # create neighbour links
        for col in self._tiles:
            for t in col:
                for p in t.position.neighbours:
                    if not self._is_position_valid(p):
                        continue
                    q, r = p.offset
                    t.add_neighbour(self._tiles[q][r])
                    # self._tiles[q][r].add_neighbour(t)

    def save_map(self, filename="latest"):
        new_map = []
        for col in self._tiles:
            new_map.append([t.color for t in col])
        with open("maps/%s.map" % filename, "w") as fh:
            yaml.dump(new_map, fh)

    def load_map(self, filename):
        self.empty()
        self._tiles = []
        with open("maps/%s.map" % filename, "r") as fh:
            new_map = yaml.load(fh)
        self._q = len(new_map)
        self._r = len(new_map[0])
        for i, col_info in enumerate(new_map):
            col = []
            for j, color in enumerate(col_info):
                t = HexTile(i, j, color, self._images)
                col.append(t)
                self.add(t)
            self._tiles.append(col)

        self.generate_neighbour_links()

    def _is_position_valid(self, position):
        q, r = position.offset
        return 0 <= q < self._q and 0 <= r < self._r

    def draw(self, screen):
        pygame.sprite.Group.draw(self, screen)
        screen.blit(self.cursor.image, self.cursor.rect.topleft)
        self.popup.draw(screen)

    def on_raw_click(self, x, y):
        position = Position(x=x, y=y)
        if not self._is_position_valid(position):
            return
        return self.on_click(position)

    def on_raw_mouse_move(self, x, y):
        position = Position(x=x, y=y)
        if not self._is_position_valid(position):
            return
        return self.on_mouse_move(position)

    def eliminate_enclosed_areas(self):
        possible_black = self._get_reachable_groups(self.black_group)
        possible_white = self._get_reachable_groups(self.white_group)

        only_black = possible_black - possible_white
        only_white = possible_white - possible_black

        for group in only_black:
            self.black_group.merge(group, update_color=True)
        for group in only_white:
            self.white_group.merge(group, update_color=True)

    def _get_reachable_groups(self, group):
        reachable = set([])
        visited = set([])
        todo = [n for n in group.neighbours if n.color not in self.player_colors]

        while todo:
            group = todo.pop()
            visited.add(group)
            if group.color in self.player_colors:
                continue

            reachable.add(group)
            for neighbour in group.neighbours:
                if neighbour not in visited:
                    todo.append(neighbour)

        return reachable

    def on_click(self, position):
        q, r = position.offset
        color_to_overpower = self._tiles[q][r].color
        self.overpower(color_to_overpower)

    def overpower(self, color_to_overpower):
        # new_friends are the tiles that will change the color this round
        new_friends = set([])

        # it is not possible to overpower a human player
        if color_to_overpower in self.player_colors:
            return False

        for group in list(self.player_group.neighbours):
            if group.color == color_to_overpower:
                new_friends |= group.tiles
                self.player_group.merge(group)

        if len(new_friends) == 0:
            return False

        for n in new_friends:
            n.set_color(self.player_group.color)

        self.eliminate_enclosed_areas()
        return True

    def end_of_round(self):
        self.player_group = next(self.iter_player_groups)

        print("Black: %s\nWhite: %s\n\n" % (
            len(self.black_group.tiles),
            len(self.white_group.tiles))
        )

        # check if the game is finished

        # we detect the reachable groups allready during the elimination
        # TODO maybe some caching if we get performance issues with big maps
        possible_black = self._get_reachable_groups(self.black_group)
        possible_white = self._get_reachable_groups(self.white_group)
        if any(len(pg) == 0 for pg in (possible_black, possible_white)):
            print("game finished")
            if len(self.black_group.tiles) == len(self.white_group.tiles):
                self.winner = True
                print("oh no, there are only looser :(")
                self.popup.add("oh no, there are only looser :(")
            else:
                self.winner = max(self.player_groups, key=lambda g: len(g.tiles))
                print("%s won the game" % self.winner.color)
                self.popup.add("%s won the game" % self.winner.color)

            print("Hit space to generate a new map")
        else:
            print("turn for %s" % self.player_group.color)
            if self.player_group.color in self.auto_players:
            # it is auto players turn
                self.auto_player()

    def auto_player(self):
        """
        overpowers a color
        """
        cnt = Counter()
        for ng in self.player_group.neighbours:
            if ng.color in self.player_colors:
                continue
            cnt.update({ng.color: len(ng.tiles)})
        color = cnt.most_common(1)[0][0]
        print("white choses %s" % color)
        self.overpower(color)

    def on_mouse_move(self, position):
        q, r = position.offset
        self.cursor.update_position(q, r)

    def on_keypress(self, event):
        if self.winner:
            self.generate_random_map()
            self.winner = None


class Group(object):
    def __init__(self, tiles=None, color=None):
        self.tiles = set([])
        self.neighbours = set([])
        self.color = color
        tiles = [] if tiles is None else tiles
        for tile in tiles:
            self.tiles.add(tile)
            try:
                self.merge(tile.group)
            except AttributeError:
                pass
            if color is None:
                self.color = tile.color
            else:
                tile.set_color(color)

    def merge(self, other, update_color=False):

        for tile in other.tiles:
            self.tiles.add(tile)
            tile.group = self
            if update_color:
                tile.set_color(self.color)

        self.neighbours |= other.neighbours
        for on in list(other.neighbours):
            on.neighbours.discard(other)
            on.neighbours.add(self)
    # other.tiles = None

    def __str__(self):
        return "Group(color=%r, tiles=%r)" % (self.color, self.tiles)

    def __repr__(self):
        return self.__str__()


class HexTile(pygame.sprite.Sprite):
    def __init__(self, q, r, color, images):
        pygame.sprite.Sprite.__init__(self)
        self._images = images
        self.color = None
        self.image = None
        self.set_color(color)
        self.rect = self.image.get_rect()
        self.position = Position(q, r)
        self.update_position(q, r)
        self.neighbours = set([])
        self.group = Group([self])

    def update_position(self, q, r):
        self.position.offset = (q, r)
        self.rect.topleft = self.position.topleft

    def add_neighbour(self, other):
        self.group.neighbours.add(other.group)
        other.group.neighbours.add(self.group)
        self.neighbours.add(other)
        other.neighbours.add(self)
        if self.color == other.color:
            self.group.merge(other.group)

    def set_color(self, color):
        assert color in self._images
        self.image = self._images[color]
        self.color = color

    def __str__(self):
        return "HexTile(%s,%s)" % self.position.offset

    def __repr__(self):
        return self.__str__()


class Position(object):
    def __init__(self, q=None, r=None, x=None, y=None, z=None):
        super(Position, self).__init__()
        self.q = q
        self.r = r
        self._neighbours = None
        if all(i is not None for i in (x, y, z)):
            self.cube = x, y, z
        elif all(i is not None for i in (x, z)):
            self.axial = x, z
        elif all(i is not None for i in (x, y)):
            self.topleft = x, y

    @property
    def offset(self):
        return self.q, self.r

    @offset.setter
    def offset(self, value):
        self.q, self.r = value

    @property
    def cube(self):
        x = self.q
        z = self.r - (self.q - (self.q & 1)) // 2
        y = -x - z
        return x, y, z

    @cube.setter
    def cube(self, value):
        x, y, z = value
        self.q = x
        self.r = z + (x - (x & 1)) // 2

    @property
    def axial(self):
        x, y, z = self.cube
        return x, z

    @axial.setter
    def axial(self, value):
        x, z = value
        self.cube = x, -x - z, z

    @property
    def topleft(self):
        q, r = self.offset
        return q * COL_WIDTH, (r * ROW_HEIGHT) + \
            (ODD_COL_DISTANCE if (q % 2 == 1) else EVEN_COL_DISTANCE)

    @topleft.setter
    def topleft(self, value):
        # we will make an rounding error here!
        x, y = value
        column = (x // COL_WIDTH)
        delta = ODD_COL_DISTANCE if column % 2 == 1 else EVEN_COL_DISTANCE
        row = ((y - delta) // ROW_HEIGHT)
        self.offset = column, row

    @property
    def neighbours(self):
        if self._neighbours is not None:
            return self._neighbours
        x, z = self.axial
        self._neighbours = []
        for dx, dz in [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]:
            self.neighbours.append(Position(x=x + dx, z=z + dz))
        return self._neighbours

    def __str__(self):
        return "Position(q=%s, r=%s)" % self.offset

    def __repr__(self):
        return self.__str__()


def draw():
    if m.player_group.color == "black":
        screen.fill((0, 0, 0))
    else:
        screen.fill((250, 250, 250))

    m.draw(screen)
    pygame.display.flip()


def mainLoop():
    clock = pygame.time.Clock()

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return
                m.on_keypress(event)

            elif event.type == pygame.locals.MOUSEMOTION:
                # setCursor(event.pos[0],event.pos[1])
                m.on_raw_mouse_move(event.pos[0], event.pos[1])
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                m.on_raw_click(event.pos[0], event.pos[1])

        # DRAWING
        draw()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    m = Map(11, 8)
    # m = Map(filename="foo")
    draw()
    mainLoop()
