import pygame
from helingor.io import Map
from helingor.game import Game


def draw():
    if game.player_group.color == "black":
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
    game = Game(11, 8)
    m = Map(game)
    game.hookup_client(m)
    # m = Map(filename="foo")
    draw()
    mainLoop()
