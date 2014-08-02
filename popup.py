"""
authors: bison, hwmrocker (cosmetic changes)

"""

import pygame
import time


class Popup(object):
    def __init__(self, **kwargs):
        self.fnt = pygame.font.Font(kwargs.get("font","fonts/ArmWrestler.ttf"), kwargs.get("fontsize",30))
        self.color = kwargs.get("fontcolor",(245, 101, 44))  # orange ;)
        self.background_color = kwargs.get("background_color", (123,123,0))
        self.line_height_ratio = kwargs.get("line_height_ratio", 1.6)
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

        for i in range(len(self.popups)):
            if time.time() > self.popups[i]['start'] + self.popups[i]['duration']:
                self.popups.pop(i)
                break

        fullText = "\n".join(popup['txt'] for popup in self.popups).strip()

        if fullText != "":
            xPos = (screen.get_width() / 2)
            screen_width = screen.get_width()
            lines = fullText.splitlines()

            max_width = 0
            height = 0
            for line in lines:
                width, height = self.fnt.size(line)
                max_width = max(width, max_width)
                height += self.line_height_ratio * height

            pygame.draw.rect(screen, self.background_color,
                             (screen_width * 0.2, 0, screen_width * 0.6, height + 10))
            x = 0
            for line in lines:
                font_size = self.fnt.size(line)
                screen.blit(
                    self.fnt.render(line, 1, self.color),
                    ((screen_width / 2) - (font_size[0] / 2), x)
                )
                x += self.line_height_ratio * font_size[1]

        return True