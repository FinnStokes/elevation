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

    # Load levels from tiled level files
    levels = []
    f = open(os.path.join("data","levels.txt"))
    for name in f:
        levels.append(world.Level(os.path.join("data",name.rstrip())))
    level_times = [0.0]*len(levels)

    #spawnLoc = level.data.get_object_by_name("Player")

    ###########################
    #spawnLoc = find the tile with Spawn=True
    #goalLoc = find the tile with Goal=True
    ###########################

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
    font = pygame.font.SysFont("sans,arial", 30)
    
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

    reset = [False]
    i = [0]
    
    def win_level():
        print("Well Done!")
        reset[0] = True
        i[0] += 1

    def lose_level():
        print("Oops! You lost a robot!")
        reset[0] = True

    robot_img = pygame.image.load("data/RobotModel.png")
    lift_img = pygame.image.load("data/platform.png")
    while i[0] < len(levels):
        level = levels[i[0]]
        level.refresh(level.surface.get_rect())

        screen = pygame.display.set_mode(level.surface.get_size())
        pygame.display.set_caption('Elevation - Level {}'.format(i[0] + 1))
        screenRect = screen.get_rect()

        win_time = 0.5
        lose_time = 0.5
        reset_time = 1.0
        if level.time_limit:
            time_limit = level.time_limit
        else:
            time_limit = float("+inf")

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

        reset = [False]

        paused = False

        while not reset[0]:
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

            pressed = pygame.key.get_pressed()
            if pressed[K_UP] and pressed[K_DOWN]:
                reset_time -= dt
                if reset_time <= 0:
                    reset[0] = True
            else:
                reset_time = 1.0

            # level.update(dt, dx, dy)
            if not paused:
                robots.update(dt, list(itertools.chain(level.walls, (p.body for p in lifts))))
                lifts.update(dt)
                for button in level.buttons:
                    button.update(dt)
                    if not button.pressed:
                        for robot in robots:
                            if button.rect.contains(robot.rect):
                                button.press()
                                break
                    else:
                        pressed = False
                        for robot in robots:
                            if button.rect.contains(robot.rect):
                                pressed = True
                                break
                        if not pressed:
                            button.release()
            remove = []
            for robot in robots:
                for goal in level.goals:
                    if goal.contains(robot.rect):
                        remove.append(robot)
                        break
                for teleporter in level.teleporters:
                    if teleporter.contains(robot.rect):
                        dist = float("+inf")
                        dest = robot.rect.midbottom
                        for endpoint in level.endpoints:
                            d = (robot.rect.centerx - endpoint[0])**2 + (robot.rect.bottom - endpoint[1])**2
                            if d < dist:
                                dist = d
                                dest = endpoint
                        robot.moveto(dest)
                        robot.contact = []
                        
            for robot in remove:
                robots.remove(robot)
            paused = False
            if len(robots) == 0:
                paused = True
                win_time -= dt
                if win_time <= 0:
                    win_level()
            for robot in robots:
                if not robot.rect.colliderect(screenRect):
                    paused = True
                    lose_time -= dt
                    if lose_time <= 0:
                        lose_level()
                    break
                else:
                    for spikes in level.spikes:
                        if robot.rect.colliderect(spikes):
                            paused = True
                            lose_time -= dt
                            if lose_time <= 0:
                                lose_level()
                                break
                    if paused:
                        break
            if not paused:
                level_times[i[0]] += dt

                time_limit -= dt
                if time_limit <= 0:
                    print("Oops! You ran out of time")
                    reset[0] = True
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
            time_remaining = font.render("{:.1f}".format(time_limit), True, (100,0,0))
            fontrect = time_remaining.get_rect()
            fontrect.midtop = screenRect.midtop
            screen.blit(time_remaining, fontrect.topleft)
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

    if i[0] == len(levels):
        print("You win!")
        print("Level times:")
        for j, time in enumerate(level_times):
            print("Level {}: {:6.1f}s".format(j+1, time))
        return

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
