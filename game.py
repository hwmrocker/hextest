import pygame
import asyncio
import time
from helingor.io import SpectatorClient, LocalClient, NetworkClient
from helingor.game import Game, Server


def draw():
    if game.player_group.color == "black":
        screen.fill((0, 0, 0))
    else:
        screen.fill((250, 250, 250))

    local_client.draw(screen)
    pygame.display.flip()


@asyncio.coroutine
def main_loop(loop):
    now = last = time.time()

    while True:
        # 30 frames per second, considering computation/drawing time
        last, now = now, time.time()
        time_per_frame = 1 / 30
        yield from asyncio.sleep(last + time_per_frame - now)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return
                local_client.on_keypress(event)

            elif event.type == pygame.locals.MOUSEMOTION:
                local_client.on_raw_mouse_move(event.pos[0], event.pos[1])
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                local_client.on_raw_click(event.pos[0], event.pos[1])

        # DRAWING
        draw()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    game = Game(11, 8, loop=loop)
    # local_client = LocalClient(game)
    # game.hookup_client(local_client)
    gameserver = Server(game)
    asyncio.async(gameserver.run_server())
    local_client = NetworkClient()
    asyncio.async(local_client.connect())
    
    try:
        loop.run_until_complete(main_loop(loop))
    finally:
        loop.close()
