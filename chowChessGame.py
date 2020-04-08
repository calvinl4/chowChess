# Program Name: chowChess
#
# Program Description:
# A chess game created with Pygame for an ICS4U1 final assessment.
# This program runs a 2 player chess game, with no engine or AI implementation.
# There are methods included that may pave the way for future engine implementation.

import pygame
import chess
import webbrowser

import time
import random

from pygame.locals import *

pygame.init()

# colors
white = (255, 255, 255)
red = (110, 0, 0)
green = (34, 177, 76)
black = (0, 0, 0)
yellow = (200, 200, 0)
blue = (0, 0, 255)
light_green = (0, 255, 0)
light_yellow = (230, 230, 0)
light_red = (240, 0, 0)

# width
display_width = 600
display_height = 600

# img = pygame.image.load('intro_icon2.png')


# types of fonts
supersmallfont = pygame.font.SysFont("comicsansms", 18)
smallfont = pygame.font.SysFont("comicsansms", 25)
medfont = pygame.font.SysFont("comicsansms", 50)
largefont = pygame.font.SysFont("comicsansms", 85)

gameDisplay = pygame.display.set_mode((600, 600))

gameDisplay.fill(white)


# method that initializes the text object itself
def text_objects(text, color, size="small"):
    if size == "supersmall":
        textSurface = supersmallfont.render(text, True, color)
    if size == "small":
        textSurface = smallfont.render(text, True, color)
    if size == "medium":
        textSurface = medfont.render(text, True, color)
    if size == "large":
        textSurface = largeFont.render(text, True, color)

    return textSurface, textSurface.get_rect()


# method that converts text into button format.
def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size="small"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = ((buttonx + (buttonwidth / 2)), buttony + (buttonheight / 2))
    gameDisplay.blit(textSurf, textRect)


def message_to_screen(msg, color, y_displace=0, size="small"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = (int(display_width / 2), int(display_height / 2) + y_displace)
    gameDisplay.blit(textSurf, textRect)


def button(text, x, y, width, height, inactive_color, active_color, action):
    cur = pygame.mouse.get_pos()

    click = pygame.mouse.get_pressed()
    if x + width > cur[0] > x and y + height > cur[1] > y:
        pygame.draw.rect(gameDisplay, active_color, (x, y, width, height))
        if click[0] == 1 and action != None:
            if action == "Quit":
                pygame.quit()
                quit()
            if action == "Controls":
                game_controls()
            if action == "Play":
                chess.main()


    else:
        pygame.draw.rect(gameDisplay, inactive_color, (x, y, width, height))

    text_to_button(text, black, x, y, width, height)


def game_controls():
    webbrowser.open_new("wikipedia.org/wiki/Rules_of_chess")
    gameControl = True
    while gameControl:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameControl = False

        gameDisplay.fill(white)
        # gameDisplay.blit(img,(0,0))
        message_to_screen("Controls", black, -130, size="medium")
        message_to_screen("Movement:", black, -75, size="small")
        message_to_screen("Click and drag a piece to a square.", black, -40, size="supersmall")
        message_to_screen("The game of chess is very complex.", black, -10, size="supersmall")
        message_to_screen("A single page is insufficient to explain", black, 20, size="supersmall")
        message_to_screen("As such, the rules can be found here:", black, 50, size="supersmall")
        message_to_screen("wikipedia.org/wiki/Rules_of_chess", black, 80, size="supersmall")

        '''
        if 130 > cur[0] > 30 and 190 > cur[1] > 150:
            pygame.draw.rect(gameDisplay, light_green, (30, 150, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, green, (30, 150, 100, 40))

        if 130 > cur[0] > 30 and 240 > cur[1] > 200:
            pygame.draw.rect(gameDisplay, light_yellow, (30, 200, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, yellow, (30, 200, 100, 40))

        if 130 > cur[0] > 30 and 290 > cur[1] > 250:
            pygame.draw.rect(gameDisplay, light_red, (30, 250, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, red, (30, 250, 100, 40))

        text_to_button("Play", black, 30, 150, 100, 40)
        text_to_button("Intro", black, 30, 200, 100, 40)
        text_to_button("Quit", black, 30, 250, 100, 40)
        '''

        pygame.display.update()


def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)
        # gameDisplay.blit(img,(0,0))
        message_to_screen("chowChess", black, -100, size="medium")

        button("Play", 250, 150 + 100, 100, 40, green, light_green, "Play")
        button("Intro", 250, 200 + 100, 100, 40, yellow, light_yellow, "Controls")
        button("Quit", 250, 250 + 100, 100, 40, red, light_red, "Quit")

        '''
        if 130 > cur[0] > 30 and 190 > cur[1] > 150:
            pygame.draw.rect(gameDisplay, light_green, (30, 150, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, green, (30, 150, 100, 40))

        if 130 > cur[0] > 30 and 240 > cur[1] > 200:
            pygame.draw.rect(gameDisplay, light_yellow, (30, 200, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, yellow, (30, 200, 100, 40))

        if 130 > cur[0] > 30 and 290 > cur[1] > 250:
            pygame.draw.rect(gameDisplay, light_red, (30, 250, 100, 40))
        else:
            pygame.draw.rect(gameDisplay, red, (30, 250, 100, 40))

        text_to_button("Play", black, 30, 150, 100, 40)
        text_to_button("Intro", black, 30, 200, 100, 40)
        text_to_button("Quit", black, 30, 250, 100, 40)
        '''

        pygame.display.update()


game_intro()
