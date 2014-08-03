import pygame
import pygame.locals
from .popup import Popup
from .game import Position


class LocalClient(pygame.sprite.Group):

    def __init__(self, game, loop):
        # pygame.sprite.Group.__init__(self)
        super().__init__()
        self._images = {}
        self._tiles = []
        self.cursor = HexTileSprite(Position(-1, -1), pygame.image.load('tiles/cursor.png'))
        self.popup = Popup()
        self.popup.add("Welcome")
        self._game = game
        self._loop = loop

    def inform_colors(self, my_color, player_colors, game_colors):
        self.popup.add("You are %s" % my_color)
        self.color = my_color
        self._images = dict((color, pygame.image.load('tiles/%s.png' % color)) for color in game_colors)

    def inform_valid_position_infos(self, q, r):
        self._q = q
        self._r = r

    def inform_text(self, text):
        self.popup.add(text)

    def inform_new_map(self, new_map):
        self.empty()
        self._tiles = []
        self._q = len(new_map)
        self._r = len(new_map[0])
        for i, col_info in enumerate(new_map):
            col = []
            for j, color in enumerate(col_info):
                t = HexTileSprite(Position(i, j), self._images[color], color)
                col.append(t)
                self.add(t)
            self._tiles.append(col)

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

    def on_click(self, position):
        q, r = position.offset
        color_to_overpower = self._tiles[q][r].color
        self._game.overpower(color_to_overpower)

    def on_mouse_move(self, position):
        self.cursor.update_position(position)

    def on_keypress(self, event):
        self._game.ready(self)


class HexTileSprite(pygame.sprite.Sprite):
    def __init__(self, position, image, color=None):
        super().__init__()
        self.image = image
        self.color = color
        self.rect = self.image.get_rect()
        self.update_position(position)

    def update_position(self, position):
        self.rect.topleft = position.topleft
