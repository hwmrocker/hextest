import asyncio
import pygame
import pygame.locals
import msgpack
from .popup import Popup
from .game import Position


class MinimalClienInterface:

    def inform_colors(self, my_color, player_colors, game_colors):
        raise NotImplemented()

    def inform_valid_position_infos(self, q, r):
        raise NotImplemented()

    def inform_text(self, text):
        raise NotImplemented()

    def inform_new_map(self, new_map):
        raise NotImplemented()

def translated_position_factory(x_offset=0, y_offset=0):

    TILE_WIDTH = TILE_HEIGHT = 80

    EVEN_COL_DISTANCE = 0
    ODD_COL_DISTANCE = TILE_HEIGHT // 2

    # we use flat topped hexagons
    COL_WIDTH = (TILE_WIDTH // 4) * 3
    ROW_HEIGHT = TILE_HEIGHT

    class TranslatedPosition(Position):

        def __init__(self, q=None, r=None, x=None, y=None, z=None):
            super().__init__(q=q, r=r, x=x, y=y, z=z)

        @property
        def topleft(self):
            q, r = self.offset
            return q * COL_WIDTH + x_offset, (r * ROW_HEIGHT) + y_offset + \
                (ODD_COL_DISTANCE if (q % 2 == 1) else EVEN_COL_DISTANCE)

        @topleft.setter
        def topleft(self, value):
            # we will make an rounding error here!
            x, y = value
            x, y = x - x_offset, y - y_offset
            column = (x // COL_WIDTH)
            delta = ODD_COL_DISTANCE if column % 2 == 1 else EVEN_COL_DISTANCE
            row = ((y - delta) // ROW_HEIGHT)
            self.offset = column, row

    return TranslatedPosition

class PygameClient(pygame.sprite.Group):

    VALID_INFORM_TYPES = (
        "colors",
        "valid_position_infos",
        "text",
        "new_map",
    )

    def __init__(self):
        # pygame.sprite.Group.__init__(self)
        super().__init__()
        self._images = {}
        self._tiles = []
        self._q = 0
        self._r = 0
        self._x_offset = 15
        self._y_offset = 15
        self.TranslatedPosition = translated_position_factory(self._x_offset, self._y_offset)
        self.cursor = HexTileSprite(self.TranslatedPosition(-1, -1), pygame.image.load('tiles/cursor.png'))
        self.popup = Popup()
        self.popup.add("Welcome")

    @property
    def _offset(self):
        return self._x_offset, self._y_offset

    @_offset.setter
    def _offset(self, value):
        self._x_offset, self._y_offset = value

    def inform(self, msg_type, args):
        if msg_type not in self.VALID_INFORM_TYPES:
            print("{} is not a valid type".format(msg_type))
            return False

        getattr(self, "inform_{}".format(msg_type))(*args)
    
    def inform_colors(self, my_color, player_colors, game_colors):
        self.popup.add("You are %s" % my_color)
        self.color = my_color
        self._images = dict((color, pygame.image.load('tiles/%s.png' % color)) for color in game_colors)

    def inform_valid_position_infos(self, q, r):
        self._q = q
        self._r = r

    def inform_text(self, text):
        self.popup.add(text)

    def inform_new_map(self, new_map, player_color):
        self.player_color = player_color
        self.empty()
        self._tiles = []
        self._q = len(new_map)
        self._r = len(new_map[0])
        for i, col_info in enumerate(new_map):
            col = []
            for j, color in enumerate(col_info):
                t = HexTileSprite(self.TranslatedPosition(i, j), self._images[color], color)
                col.append(t)
                self.add(t)
            self._tiles.append(col)

    def _is_position_valid(self, position):
        q, r = position.offset
        return 0 <= q < self._q and 0 <= r < self._r

    def draw(self, screen):
        if self.player_color == "black":
            screen.fill((0, 0, 0))
        else:
            screen.fill((250, 250, 250))
        pygame.sprite.Group.draw(self, screen)
        screen.blit(self.cursor.image, self.cursor.rect.topleft)
        self.popup.draw(screen)

    def on_raw_click(self, x, y):
        position = self.TranslatedPosition(x=(x - self._x_offset), y=(y - self._y_offset))
        if not self._is_position_valid(position):
            return
        return self.on_click(position)

    def on_raw_mouse_move(self, x, y):
        position = self.TranslatedPosition(x=(x - self._x_offset), y=(y - self._y_offset))
        if not self._is_position_valid(position):
            return
        return self.on_mouse_move(position)

    def on_click(self, position):
        pass

    def on_mouse_move(self, position):
        pass

    def on_keypress(self, event):
        pass


class LocalClient(PygameClient):

    def __init__(self, game):
        super().__init__()
        self._game = game

    def on_click(self, position):
        q, r = position.offset
        color_to_overpower = self._tiles[q][r].color
        self._game.overpower(color_to_overpower)

    def on_mouse_move(self, position):
        self.cursor.update_position(position)

    def on_keypress(self, event):
        self._game.ready(self)


class NetworkClient(PygameClient):

    reader = None
    writer = None
    sockname = None

    def __init__(self, host='127.0.0.1', port=8001):
        super().__init__()
        self.host = host
        self.port = port

    def on_click(self, position):
        q, r = position.offset
        color_to_overpower = self._tiles[q][r].color
        self.send_msg(("overpower", (color_to_overpower,)))

    def on_mouse_move(self, position):
        self.cursor.update_position(position)

    def on_keypress(self, event):
        self.send_msg(("ready", (self.sockname,)))

    def send_msg(self, msg):
        pack = msgpack.packb(msg)
        self.writer.write(pack)

    def close(self):
        if self.writer:
            self.writer.write_eof()

    @asyncio.coroutine
    def connect(self):
        print('Connecting...')
        try:
            reader, writer = yield from asyncio.open_connection(self.host, self.port)
            # asyncio.async(self.create_input())
            self.reader = reader
            self.writer = writer
            self.sockname = writer.get_extra_info('sockname')
            unpacker = msgpack.Unpacker(encoding='utf-8')
            while not reader.at_eof():
                pack = yield from reader.read(1024)
                unpacker.feed(pack)
                for msg in unpacker:
                    self.inform(*msg)
            print('The server closed the connection')
            self.writer = None
        except ConnectionRefusedError as e:
            print('Connection refused: {}'.format(e))
            self.close()


class SpectatorClient(PygameClient):

    def on_mouse_move(self, position):
        self.cursor.update_position(position)


class HexTileSprite(pygame.sprite.Sprite):

    def __init__(self, position, image, color=None):
        super().__init__()
        self.image = image
        self.color = color
        self.rect = self.image.get_rect()
        self.update_position(position)

    def update_position(self, position):
        self.rect.topleft = position.topleft
