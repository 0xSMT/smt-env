# Samuel Taylor (2020)

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame, math, sys, random

import pygame.constants
from smtenv.basegame import BaseGame 

# from gym.spaces import Box, Dict

def unitvec(x, y): 
    mag = math.sqrt(x * x + y * y)

    if mag == 0:
        return 0, 0
    else:
        return (x / mag), (y / mag)

def rescale(x, y, scale):
    return scale * x, scale * y

def clamp(x, mini, maxi):
    return max(min(x, maxi), mini)

class Entity(pygame.sprite.Sprite):
    def __init__(self, max_speed, radius, fric, SCREEN_BOUNDS, x, y):
        self.max_speed = max_speed
        self.radius = radius
        self.fric = fric

        self.vx = 0
        self.vy = 0

        self.ax = 0
        self.ay = 0

        self.SCREEN_BOUNDS = SCREEN_BOUNDS

        pygame.sprite.Sprite.__init__(self)

        image = pygame.surface.Surface((2 * radius, 2 * radius))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        self.x = x
        self.y = y

        self.image = image

    def speed(self):
        return math.sqrt(self.vx ** 2 + self.vy ** 2)

    def update(self, dt):
        uvx, uvy = unitvec(self.vx, self.vy)

        if uvx != 0 or uvy != 0:
            self.dirx = uvx
            self.diry = uvy

        uvx, uvy = rescale(uvx, uvy, -self.fric * (self.speed() / self.max_speed))

        self.vx = self.vx + (self.ax + uvx) * dt
        self.vy = self.vy + (self.ay + uvy) * dt

        spd = self.speed()
        if spd > self.max_speed:
            self.vx = (self.vx / spd) * self.max_speed
            self.vy = (self.vy / spd) * self.max_speed
        elif spd < 0.5:
            self.vx = 0
            self.vy = 0

        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt

        self.x = clamp(self.x, 0 + self.radius, self.SCREEN_BOUNDS[0] - self.radius)
        self.y = clamp(self.y, 0 + self.radius, self.SCREEN_BOUNDS[1] - self.radius)
    
    def draw(self, screen):
        screen.blit(self.image, (self.x - self.radius, self.y - self.radius))

class Player(Entity):
    def __init__(self, max_speed, radius, fric, SCREEN_BOUNDS):
        super(Player, self).__init__(max_speed, radius, fric, SCREEN_BOUNDS, SCREEN_BOUNDS[0] // 2, SCREEN_BOUNDS[1] // 2)

        pygame.draw.circle(
            self.image, 
            (0, 255, 0), 
            (radius, radius),
            radius,
            0
        )

class Enemy(Entity):
    def __init__(self, max_speed, radius, fric, SCREEN_BOUNDS, x, y, acc):
        super(Enemy, self).__init__(max_speed, radius, fric, SCREEN_BOUNDS, x, y)

        self.acc = acc

        pygame.draw.circle(
            self.image, 
            (255, 0, 0), 
            (radius, radius),
            radius,
            0
        )  
    
    def update(self, dt, px, py):
        ux, uy = unitvec(-self.x + px, -self.y + py)
        ux, uy = rescale(ux, uy, self.acc)

        self.ax = ux
        self.ay = uy

        super(Enemy, self).update(dt)

class AvoidGame(BaseGame):
    # REQUIRED method
    def __init__(self, width=200, height=200):

        # Actions the player agent in the simulation can take
        actions = {
            "left": pygame.constants.K_LEFT,
            "right": pygame.constants.K_RIGHT,
            "up": pygame.constants.K_UP,
            "down": pygame.constants.K_DOWN
        }

        # Simulation specific initialization (include here stuff for intializing class itself)
        config = {
            'enemy': {
                'radius': 10,
                'max_speed': 30,
                'acc': 800    
            },
            'player': {
                'radius': 20,
                'max_speed': 50,
                'acc': 900
            },
            'fric': 400,
            'width': width,
            'height': height
        }

        # Run the initialization on the base class
        BaseGame.__init__(self, width, height, actions=actions, config=config)
    
    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                key = event.key
                
                if key == self.actions["left"]:
                    self.player.ax = -self.config['player']['acc']
                elif key == self.actions["right"]:
                    self.player.ax = self.config['player']['acc']
                elif key == self.actions["up"]:
                    self.player.ay = -self.config['player']['acc']
                elif key == self.actions["down"]:
                    self.player.ay = self.config['player']['acc']
            elif event.type == pygame.KEYUP:
                key = event.key

                if key == self.actions["left"] and self.player.vx < 0:
                    self.player.ax = 0
                elif key == self.actions["right"] and self.player.vx > 0:
                    self.player.ax = 0
                elif key == self.actions["up"] and self.player.vy < 0:
                    self.player.ay = 0
                elif key == self.actions["down"] and self.player.vy > 0:
                    self.player.ay = 0

    # REQUIRED method
    def init(self):
        self.score = 0

        # Simulation specific initialization (include here stuff for intializing a new game
        # in this class, since a class instance can run its game multiple times)
        self.player = Player(
            self.config['player']['max_speed'], 
            self.config['player']['radius'], 
            self.config['fric'], 
            (self.config['width'], self.config['height'])
        )

        x = round((self.config['width'] / 4) * random.random())
        y = round((self.config['height'] / 4) * random.random())

        self.enemy = Enemy(
            self.config['enemy']['max_speed'], 
            self.config['enemy']['radius'], 
            self.config['fric'], 
            (self.config['width'], self.config['height']),
            x, # TODO: Make it generate some distance from player 
            y, #       (random dist, random theta => convert to x, y)
            self.config['enemy']['acc']
        )
                
        self.lives = 1
    
    # REQUIRED method
    def get_score(self):
        return self.score
    
    # REQUIRED method
    def is_game_over(self):
        # Simulation specific game over condition
        return self.lives == 0

    # REQUIRED method -- body of game itself
    def step(self, dt):
        # Adjust score
        # Update game state for checking game_over

        # (NOTE: Game can be locked to a certain FPS (keeping dt constant) by 
        # setting self.allowed_fps to desried value)
        dt /= 1000

        self.screen.fill((0, 0, 0))

        self._handle_player_events()
        self.player.update(dt)
        # self.player.draw(self.screen)

        self.enemy.update(dt, self.player.x, self.player.y)

        dist = math.hypot(self.player.x - self.enemy.x, self.player.y - self.enemy.y) - (self.player.radius + self.enemy.radius) 
        if dist < 0:
            self.lives = 0
        # elif self.player.x 
        # self.enemy.draw(self.screen)

        self.score += dt * dist
    
    def draw(self):
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

    # REQUIRED method (if you want the state space to be not the screen itself, highly 
    # advised for simulation purposes)
    def get_game_state(self):
        # query for particular state information here

        state = {
            "player_x":     self.player.x,
            "player_y":     self.player.y,
            "player_vx":    self.player.vx,
            "player_vy":    self.player.vy,
            "enemy_x":      self.enemy.x,
            "enemy_y":      self.enemy.y,
            "enemy_vx":     self.enemy.vx,
            "enemy_vy":     self.enemy.vy
        }

        return state

if __name__ == "__main__":
    import numpy as np

    game = AvoidGame(width=256, height=256)
    game.setup(display=True)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(30)
        if game.is_game_over():
            game.reset()

        game.step(dt)
        game.draw()
        pygame.display.update()