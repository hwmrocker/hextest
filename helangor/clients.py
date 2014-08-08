import asyncio
import pygame
import pygame.locals
import msgpack
from math import sqrt
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

    HALF_HEIGHT = TILE_HEIGHT // 2

    EVEN_COL_DISTANCE = 0
    ODD_COL_DISTANCE = HALF_HEIGHT

    # we use flat topped hexagons
    COL_WIDTH = (TILE_WIDTH // 4) * 3
    COL_OVERLAP = TILE_WIDTH - COL_WIDTH
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
            _x, _y = x - x_offset, y - y_offset
            column, column_reminder = divmod(x,  COL_WIDTH)
            delta = ODD_COL_DISTANCE if column % 2 == 1 else EVEN_COL_DISTANCE
            row, row_remainder = divmod((y - delta), ROW_HEIGHT)
            self.offset = column, row

            if (column_reminder < COL_OVERLAP):
                # we need to check better
                normalized_y = (row_remainder - HALF_HEIGHT) / HALF_HEIGHT
                normalized_x = column_reminder / COL_OVERLAP
                qx, qy, qz = self.cube
                if normalized_x >= abs(normalized_y):
                    # we are safe
                    pass
                elif -normalized_y > normalized_x:
                        self.cube = qx - 1, qy + 1, qz
                elif normalized_y > normalized_x:
                        self.cube = qx - 1, qy, qz + 1

            
            # q = int(x / COL_WIDTH)
            # r = int((1/3*sqrt(3) * y - 1/3 * x) / sqrt(COL_WIDTH**2 + (TILE_HEIGHT/2)**2))
            # self.axial = q, r
            # sqrt(COL_WIDTH**2 + (TILE_HEIGHT/2)**2)


    return TranslatedPosition

class PygameClient(pygame.sprite.Group):

    VALID_INFORM_TYPES = (
        "colors",
        "valid_position_infos",
        "text",
        "new_map",
    )

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

    def __init__(self):
        # pygame.sprite.Group.__init__(self)
        super().__init__()
        self._images = {}
        self._tiles = []
        self._q = 0
        self._r = 0
        self._x_offset = 10
        self._y_offset = 10
        self.TranslatedPosition = translated_position_factory(self._x_offset, self._y_offset)
        self.cursor = HexTileSprite(self.TranslatedPosition(-1, -1), pygame.image.load('tiles/cursor.png'))
        self.popup = Popup()
        self.popup.add("Welcome")
        self.font = pygame.font.Font("fonts/ArmWrestler.ttf", 30)
        self.player_color = "black"

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
        self._images = dict((self.COLORS[color_idx], pygame.image.load('tiles/%s.png' % self.COLORS[color_idx])) \
            for color_idx in game_colors)

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
            for j, color_idx in enumerate(col_info):
                color = self.COLORS[color_idx]
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
        pygame.draw.rect(screen, (250, 0, 0), (5, 5, 690, 690), 1)
        pygame.sprite.Group.draw(self, screen)
        screen.blit(self.cursor.image, self.cursor.rect.topleft)
        # draw menu
        pygame.draw.rect(screen, (50, 50, 50), (700, 0, 200, 700))
        total_tiles = self._q * self._r
        if not total_tiles:
            return
        white_points = sum(1 for col in self._tiles for t in col if t.color == "white")
        black_points = sum(1 for col in self._tiles for t in col if t.color == "black")
        other_points = total_tiles - (white_points + black_points)

        white_pixels = white_points / total_tiles * 700
        black_pixels = black_points / total_tiles * 700

        pygame.draw.rect(screen, (0, 100, 100), (730, 0, 10, 700))
        pygame.draw.rect(screen, (255, 255, 255), (730, 0, 10, white_pixels))
        pygame.draw.rect(screen, (0, 0, 0), (730, 700 - black_pixels, 10, black_pixels))
        pygame.draw.rect(screen, (250, 0, 0), (720, 350, 30, 2), 1)
        screen.blit(self.font.render(str(white_points), 1, (255, 255, 255)), (750, 50))
        screen.blit(self.font.render(str(other_points), 1, (0, 100, 100)), (750, 335))
        screen.blit(self.font.render(str(black_points), 1, (0, 0, 0)), (750, 600))

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
        color_to_overpower = self.COLORS.index(self._tiles[q][r].color)

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
