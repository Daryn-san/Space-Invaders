import math
import pygame
import random
import sys
from itertools import cycle
from datetime import datetime
from pygame import gfxdraw
from pygame.locals import *

def print_text(surface, font, text, surf_rect, x = 0, y = 0, center = False,\
               color = (255, 255, 255)):
    if not center:
        textimage = font.render(text, True, color)
        surface.blit(textimage, (x, y))
    else:
        textimage = font.render(text, True, color)
        text_rect = textimage.get_rect()
        x = (surf_rect.width // 2) - (text_rect.width // 2 )
        surface.blit(textimage, (x, y))

def game_is_over(surface, font, ticks):
    timer = ticks
    surf_rect = surface.get_rect()
    surf_height = surf_rect.height
    surf_width = surf_rect.width
    print_text(screen, font, "G A M E  O V E R", surf_rect, y = 260,\
               center = True)
    pygame.display.update()
    while True:
        ticks = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if ticks > timer + 3000:
            break

def next_level(level):
    level += 1
    if level > 6:
        level = 6
    return level

def load_level(level):
    invaders, colors = [], []

    start_intx, end_intx, increment_intx = 85, 725, 40 
    start_inty, end_inty, increment_inty = 60, 60, 30 
    end_inty = end_inty + level * 30 
    color_val = 256 / end_inty 
    for x in range(start_intx, end_intx, increment_intx):
        for y in range(start_inty, end_inty, increment_inty):
            invaders.append(pygame.Rect(x, y, 30, 15))
            colors.append(((x * 0.35) % 256, (y * color_val) % 256))

    return invaders, colors, len(invaders)


def draw_invader(backbuffer, rect, a, b, animate_invaders, ticks,\
                 animation_time):
    invader_width = 30
    pygame.draw.rect(backbuffer, (150, a, b), rect)
    pygame.gfxdraw.filled_circle(backbuffer, rect.x + 6, rect.y + 4, 3, \
                                 BLACK)
    pygame.gfxdraw.filled_circle(backbuffer, rect.x + invader_width - 7,\
                                 rect.y + 4, 3, BLACK)
    pygame.gfxdraw.line(backbuffer, rect.x + 14, rect.y, rect.x + 8,\
                       rect.y - 6, (150, a, b))
    pygame.gfxdraw.line(backbuffer, rect.x + invader_width - 15, rect.y,\
                        rect.x + invader_width - 8, rect.y - 6, (150, a, b))

    if animate_invaders:
        pygame.gfxdraw.filled_trigon(backbuffer, rect.x+6, rect.y + 12,\
                                     rect.x + 14, rect.y + 4, rect.x +\
                                     invader_width - 7, rect.y + 12, BLACK)
    else:
        pygame.gfxdraw.line(backbuffer, rect.x + 6, rect.y + 12,\
                            rect.x + 15, rect.y + 8, BLACK)
        pygame.gfxdraw.line(backbuffer, rect.x + invader_width - 7,\
                            rect.y + 12, rect.x + invader_width - 15,\
                            rect.y + 8, BLACK)
    if ticks > animation_time + 200:
        animate_invaders = False

    return animate_invaders


pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders")
fpsclock = pygame.time.Clock()

the_screen = screen.get_rect()
screen_width = the_screen.width
screen_height = the_screen.height

backbuffer = pygame.Surface((the_screen.width, the_screen.height))

font1 = pygame.font.SysFont(None, 30)
font2 = pygame.font.SysFont("Impact", 54)
font3 = pygame.font.SysFont("Impact", 36)

RELOAD_SPEED = 400
MOVE_SIDEWAYS = 1000
MOVE_DOWN = 1000
BONUS_FREQ = 10000
INV_SHOOT_FREQ = 500

move_invaders_sideways = pygame.USEREVENT + 1
move_invaders_down = pygame.USEREVENT + 2
reload = pygame.USEREVENT + 3
invader_shoot = pygame.USEREVENT + 4
bonus = pygame.USEREVENT + 5

pygame.time.set_timer(move_invaders_down, 0) 
pygame.time.set_timer(move_invaders_sideways, MOVE_SIDEWAYS) 
pygame.time.set_timer(reload, RELOAD_SPEED)
pygame.time.set_timer(invader_shoot, INV_SHOOT_FREQ) 
pygame.time.set_timer(bonus, BONUS_FREQ)

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
DIMGRAY = (105,105,105)

shots, invader_shots, inv_shot_colors, bonus_invaders = [], [], [], []
        
player = Rect(380,578,42,20)
player_gun = Rect(player.x + 18,player.y - 4, 6, 4)

the_screen = screen.get_rect()

animation_time = 0
animate_invaders = False
invader_width = 30
invader_height = 15

the_text = cycle(["Press Enter To Play, Earthling...", ""])
insert = next(the_text)
flash_timer = 0

y1,y2,y3,y4,y5,y6 = (255,255,0), (225,225,0), (195,195,0), (165,165,0),\
                    (135,135,0), (105,105,0)
bonus_colors = cycle([y1,y2,y3,y4,y5,y6])
bonus_color = next(bonus_colors)
bonus_x = cycle([4,11,18,25,32,39])
bonus_timer = 0

move_right, move_down, reloaded = True, True, True
vert_steps = 0
side_steps = 0
moved_down = False
invaders_paused = False

invaders = 0 
initial_invaders = 0 
shoot_level = 1

game_over = True
score = 0
lives = 2
level = 0
playing = False

while True:
    ticks = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYUP:
            if event.key == pygame.K_1 and not game_over:
                print("Next level")

        if event.type == invader_shoot and not game_over:
            i = random.randint(0, len(invaders)-1)
            shot_from = invaders[i]
            a, b = colors[i]
            invader_fired = True
            invader_shots.append(Rect(shot_from.x, shot_from.y, 5, 7))
            inv_shot_colors.append((150, a, b))

        if event.type == reload and not game_over:
            reloaded = True
            pygame.time.set_timer(reload, 0)

        if event.type == move_invaders_sideways and not game_over:
            if move_right:
                for invader in invaders: invader.move_ip(10,0)
                side_steps += 1
            else:
                for invader in invaders: invader.move_ip(-10,0)
                side_steps -= 1
            if side_steps == 6 or side_steps == -6:
                if vert_steps <= 31: 
                    pygame.time.set_timer(move_invaders_sideways, 0)
                    pygame.time.set_timer(move_invaders_down, MOVE_DOWN) 
                else: move_right = not move_right

        if event.type == move_invaders_down and not game_over:
            move_right = not move_right
            animate_invaders = True
            animation_time = ticks
            pygame.time.set_timer(move_invaders_sideways, MOVE_SIDEWAYS)
            pygame.time.set_timer(move_invaders_down, 0)
            for invader in invaders: invader.move_ip(0,10)
            vert_steps += 1


    pressed = pygame.key.get_pressed()
    if pressed[K_ESCAPE]: pygame.quit(), sys.exit()
    elif pressed[K_RETURN]:
        if game_over: game_over = False
    elif pressed[K_d] or pressed[K_RIGHT]:player.move_ip((8, 0))
    elif pressed[K_a] or pressed[K_LEFT]: player.move_ip((-8, 0))
    if pressed[K_SPACE]:
        if reloaded:
            reloaded = False
            pygame.time.set_timer(reload, RELOAD_SPEED)
            missile = player.copy().inflate(-38, -10)
            missile.y -= 9
            shots.append(missile)

    backbuffer.fill(BLACK)

    if not game_over:
        playing = True
        if level == 0:
            level = next_level(level)
            invaders, colors, initial_invaders = load_level(level)
            move_right, move_down, reloaded = True, True, True
            vert_steps = 0
            side_steps = 0
            moved_down = False
            invaders_paused = False
            pygame.time.set_timer(invader_shoot, 500)
            shoot_level = 1

        for shot in invader_shots:
            shot.move_ip((0,random.randint(5,11)))
            if not backbuffer.get_rect().contains(shot):
                i = invader_shots.index(shot)
                del invader_shots[i]
                del inv_shot_colors[i]
            if shot.colliderect(player):
                lives -= 1
                if lives < 0:
                    lives = 0
                    game_over = True
                i = invader_shots.index(shot)
                del invader_shots[i]
                del inv_shot_colors[i]

        for shot in shots:
            shot.move_ip((0, -8))
            for inv_shot in invader_shots:
                if inv_shot.colliderect(shot):
                    shots.remove(shot)
                    i = invader_shots.index(inv_shot)
                    del invader_shots[i]
                    del inv_shot_colors[i]
            if not backbuffer.get_rect().contains(shot):
                shots.remove(shot)
            else:
                hit = False
                for invader in invaders:
                    if invader.colliderect(shot):
                        score += 1
                        hit = True
                        i = invaders.index(invader)
                        del invaders[i]
                        del colors[i]
                if hit: shots.remove(shot)


        if len(invaders) == 0:
            level = next_level(level)
            invaders, colors, initial_invaders = load_level(level)
            move_right, move_down, reloaded = True, True, True
            vert_steps = 0
            side_steps = 0
            moved_down = False
            invaders_paused = False
            pygame.time.set_timer(invader_shoot, 500)
            shoot_level = 1

        if len(invaders) < initial_invaders*.75 and shoot_level == 1:
            pygame.time.set_timer(invader_shoot, 750)
            shoot_level = 2
        elif len(invaders) < initial_invaders*.5 and shoot_level == 2:
            pygame.time.set_timer(invader_shoot, 1000)
            shoot_level = 3
        elif len(invaders) < initial_invaders*.25 and shoot_level == 3:
            pygame.time.set_timer(invader_shoot, 1500)
            shoot_level = 4
       
        for rect, (a, b) in zip(invaders, colors):
            animate_invaders = draw_invader(backbuffer, rect, a, b,\
                                            animate_invaders, ticks, \
                                            animation_time)

        for shot in shots:
            pygame.draw.rect(backbuffer, (255,0,0), shot)
        for shot, color in zip(invader_shots, inv_shot_colors):
            pygame.draw.rect(backbuffer, color, shot)

        player_gun.x = player.x+18
        pygame.draw.rect(backbuffer, DIMGRAY, player)
        pygame.draw.rect(backbuffer, DIMGRAY, player_gun)

        player.clamp_ip(backbuffer.get_rect())

        print_text(backbuffer, font1, "Invaders Destroyed: {}".format(score),\
                   the_screen, x=565, y=0)
        print_text(backbuffer, font1, "Lives: {}".format(lives), the_screen,\
                   x=0, y=0)
        print_text(backbuffer, font1, "Level: {}".format(level), the_screen,\
                   x=0, y=580)

    if game_over:
        if playing:
            game_is_over(backbuffer, font2, ticks)
            playing = False
            level = 0
            lives = 2
            score = 0
            shots, invader_shots, inv_shot_colors, bonus_invaders = [], [], [], []

        print_text(backbuffer, font2, "SPACE INVADERS", the_screen, y=5,\
                   center=True)

        if ticks > flash_timer + 800:
            insert = next(the_text)
            flash_timer = ticks
        print_text(backbuffer, font3, insert, the_screen, y =\
                   the_screen.height-40, center=True)

    screen.blit(backbuffer, (0,0))
    pygame.display.update()
    fpsclock.tick(30)