"""helangor.

Usage:
    game.py
    game.py [-p PORT | -c SERVER]

Options:
    -h, --help          show this screen
    --version           show version
    -c SERVER, --connect SERVER
                        this will not run a local server, but rather connection
                        to the provided one.
"""


import pygame
import asyncio
import time
from docopt import docopt
from helangor.clients import SpectatorClient, LocalClient, NetworkClient
from helangor.game import Game, Server


class UI:

    def __init__(self, host):
        pygame.init()
        self.local_client = NetworkClient(host=host)
        self.screen = pygame.display.set_mode((900, 700))

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.main_loop(loop))
        finally:
            loop.close()

    def draw(self):
        self.local_client.draw(self.screen)
        pygame.display.flip()

    @asyncio.coroutine
    def main_loop(self, loop):
        now = last = time.time()

        while True:
            # 30 frames per second, considering computation/drawing time
            last, now = now, time.time()
            time_per_frame = 1 / 30
            yield from asyncio.sleep(last + time_per_frame - now)

            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    return
                self.local_client.handle_event(event)

            # DRAWING
            self.draw()


if __name__ == "__main__":
    arguments = docopt(__doc__, version='helangor 0.8')

    if not arguments.get('--connect'):
        game = Game(11, 8)
        gameserver = Server(game)
        asyncio.async(gameserver.run_server())

    ui = UI(host=arguments.get('--connect', 'localhost'))
    ui.run()
    # asyncio.async(local_client.connect())
