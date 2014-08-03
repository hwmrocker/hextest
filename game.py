import pygame
import asyncio
import time
from helingor.io import Map
from helingor.game import Game


def draw():
    if game.player_group.color == "black":
        screen.fill((0, 0, 0))
    else:
        screen.fill((250, 250, 250))

    m.draw(screen)
    pygame.display.flip()

@asyncio.coroutine
def main_loop(loop):
    now = last = time.time()

    while True:
        last, now = now, time.time()
        time_per_frame = 1 / 30
        # yield from clock.tick(30)
        yield from asyncio.sleep(last + time_per_frame - now)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return
                m.on_keypress(event)

            elif event.type == pygame.locals.MOUSEMOTION:
                m.on_raw_mouse_move(event.pos[0], event.pos[1])
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                m.on_raw_click(event.pos[0], event.pos[1])

        # DRAWING
        draw()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    game = Game(11, 8)
    m = Map(game)
    game.hookup_client(m)
    draw()

    try:
        loop.run_until_complete(main_loop(loop))
    finally:
        loop.close()
