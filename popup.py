"""
authors: bison, hwmrocker (cosmetic changes)

"""

import pygame
import time


class Popup(object):
    def __init__(self):
        self.fnt = pygame.font.Font("fonts/ArmWrestler.ttf", 30)
        self.color = (245, 101, 44)  # orange ;)
        self.popups = []
        self.defaultDuration = 3

    def single_popup(self, txt, duration=0):
        if duration == 0:
            duration = self.defaultDuration
        self.popups = []
        self.popups.append({"txt": txt, "start": time.time(), "duration": duration})

    def add(self, txt, duration=0):
        if duration == 0:
            duration = self.defaultDuration
        self.popups.append({"txt": txt, "start": time.time(), "duration": duration})

    def draw(self, screen):
        if len(self.popups) == 0:
            return False

        fullText = ""
        for i in range(len(self.popups)):
            if time.time() > self.popups[i]['start'] + self.popups[i]['duration']:
                self.popups.pop(i)
                break

        for popup in self.popups:
            fullText += popup['txt'] + " "

        # TODO: multilines!
        # http://stackoverflow.com/questions/2770886/pygames-message-multiple-lines
        if fullText != "":
            xPos = (screen.get_width() / 2)
            screen_width = screen.get_width()
            font_size = self.fnt.size(fullText)
            pygame.draw.rect(screen, (123,123,0), (screen_width*0.2, 0, screen_width*0.6, font_size[1]+10))
            screen.blit(self.fnt.render(fullText, 1, self.color), (xPos - (font_size[0] / 2), 5))

        return True