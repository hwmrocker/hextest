"""
authors: bison, hwmrocker (cosmetic changes)

"""

import pygame
import time


class Popup(object):
    def __init__(self, **kwargs):
        """
        Popup is responsible for displaying popups in the game

        :param font: string path to a font file (default: "fonts/ArmWrestler.ttf")
        :param fontsize: int (default: 30)
        :param color: RGB tuple, fontcolor (default: (245, 101, 44))
        :param background_color: RGB tuple (default: (123, 123, 0))
        :param line_height_ratio: float (default: 1.2)
        """
        self.fnt = pygame.font.Font(
            kwargs.get("font","fonts/ArmWrestler.ttf"),
            kwargs.get("fontsize",30)
        )
        self.color = kwargs.get("fontcolor",(245, 101, 44))  # orange ;)
        self.background_color = kwargs.get("background_color", (123,123,0))
        self.line_height_ratio = kwargs.get("line_height_ratio", 1.2)
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
        """
        :param screen: pygame surface
        :return: None
        """
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

            # calculate dimensions for background
            max_width = 0
            height = 0
            for line in lines:
                width, height = self.fnt.size(line)
                max_width = max(width, max_width)
                height += self.line_height_ratio * height

            # add a little bit vertical space before and after the text
            height += (self.line_height_ratio - 1) * height

            # draw the background
            pygame.draw.rect(
                screen,
                self.background_color,
                (screen_width * 0.2, 0, screen_width * 0.6, height)
            )

            # divide the extra vertical space in half
            x = (self.line_height_ratio - 1) * height * 0.5
            for line in lines:
                # draw line by line
                font_size = self.fnt.size(line)
                screen.blit(
                    self.fnt.render(line, 1, self.color),
                    ((screen_width / 2) - (font_size[0] / 2), x)
                )
                x += self.line_height_ratio * font_size[1]

        return True