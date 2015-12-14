# Cosplay Chase
# A top-down stealth game

import itertools
import argparse
import cProfile
import os

import pygame
from pygame.locals import *

import entity
import platform
import world
import lift

ONEONSQRT2 = 0.70710678118

def main():
    # Initialise screen
    pygame.init()

    screen = pygame.display.set_mode()

    # Load level from tiled level file
    level = world.Level(os.path.join("data","4level.tmx"))

    #spawnLoc = level.data.get_object_by_name("Player")

    ###########################
    #spawnLoc = find the tile with Spawn=True
    #goalLoc = find the tile with Goal=True
    ###########################

    screen = pygame.display.set_mode(level.surface.get_size())
    pygame.display.set_caption('Elevation')
    screenRect = screen.get_rect()

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255,255,255))

    # splash_screen = pygame.image.load(os.path.join("data", "title.png"))
    # splash_rect = splash_screen.get_rect()
    # splash_rect.center = screenRect.center
    
    # gameover_screen = pygame.image.load(os.path.join("data", "gameover.png"))
    # gameover_rect = gameover_screen.get_rect()
    # gameover_rect.center = screenRect.center
    # font = pygame.font.SysFont(pygame.font.match_font("sans", "arial"), 50)
    
    # splash = True
    # while splash:
    #     screen.blit(background, (0,0))
    #     screen.blit(splash_screen, splash_rect)
    #     pygame.display.flip()
    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             return
    #         elif event.type == KEYDOWN:
    #             if event.key == K_ESCAPE:
    #                 return
    #             else:
    #                 splash = False

    win_time = 1.0

    robot_img = pygame.image.load("data/RobotModel.png")
    lift_img = pygame.image.load("data/platform.png")
    while True:
        # level.dx = 0
        # level.dy = 0
        robots = pygame.sprite.Group()
        lifts = pygame.sprite.Group()
        for s in level.shafts:
            lifts.add(lift.Lift(lift_img, s, 160))
        # player = character.Player(spawnLoc.x, spawnLoc.y, 800, level)
        # sprites.add(player)
        # guards = character.GuardManager(player, level, screenRect)
        #e = entity.Entity(img,300,300,150,0)
        for spawn in level.spawn:
            robot = entity.Entity(robot_img, (58, 98), spawn, (80,0))
            robots.add(robot)

        # Initialise clock
        clock = pygame.time.Clock()

        time = 0.0
        frames = 0
        start_time = pygame.time.get_ticks()
        min_fps = 200
        max_fps = 0

        while True:
            dt = clock.tick(200) / 1000.0
            time += dt
            frames += 1
            if time >= 1.0:
                fps = frames / time
                #min_fps = min(min_fps, fps)
                #max_fps = min(max_fps, fps)
                #avg_fps += frames
                if fps < 30:
                    print("WARNING: Low framerate: "+str(fps)+" FPS")
                time = 0.0
                frames = 0

            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    elif event.key == K_UP:
                        for p in lifts:
                            p.up()
                    elif event.key == K_DOWN:
                        for p in lifts:
                            p.down()

            # level.update(dt, dx, dy)
            robots.update(dt, itertools.chain(level.walls, (p.body for p in lifts)))
            lifts.update(dt)
            remove = []
            for robot in robots:
                for goal in level.goals:
                    if goal.contains(robot.rect):
                        remove.append(robot)
                        break
            for robot in remove:
                robots.remove(robot)
            if len(robots) == 0:
                win_time -= dt
                if win_time <= 0:
                    print("You win!")
                    exit(0)
            # guards.update(dt, dx, dy)

            # Blit everything to the screen
            screen.blit(background, (0,0))
            level.draw(screenRect, screen)
            robots.draw(screen)
            lifts.draw(screen)
            # for body in robot.contact:
            #     img = pygame.Surface(body[0].size)
            #     img.fill((0, 0, 100))
            #     screen.blit(img, body[0].pos)
            pygame.display.flip()

        # splash = True
        # while splash:
        #     screen.blit(background, (0,0))
        #     screen.blit(gameover_screen, gameover_rect)
        #     screen.blit(lifetime_img, lifetime_rect)
        #     pygame.display.flip()
        #     for event in pygame.event.get():
        #         if event.type == QUIT:
        #             return
        #         elif event.type == KEYDOWN:
        #             if event.key == K_ESCAPE:
        #                 return
        #             else:
        #                 splash = False

def resolution(raw):
    a = raw.split("x")
    if len(a) != 2:
        raise ValueError()
    return (int(a[0]), int(a[1]))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A top-down stealth game.')
    parser.add_argument('--profile-file', action='store',
                        help="File to store profiling output in")
    parser.add_argument('-p', '--profile', action='store_true',
                        help="Enable profiling using cProfile")
    # parser.add_argument('-r', '--resolution', action='store', type=resolution, default=(0,0),
    #                     help="Target screen resolution (e.g. 1920x1080)")
    args = parser.parse_args()
    if args.profile:
        # cProfile.run("main(args.resolution)", filename=args.profile_file)
        cProfile.run("main()", filename=args.profile_file)
    else:
        # main(args.resolution)
        main()
