# Samuel Taylor (2020)

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame, math, sys, random, json

import numpy as np

import pygame.constants
from smtenv.basegame import BaseGame

# from gym.spaces import Box, Dict

def chase(self, px, py):
    disty = self.y - py
    distx = self.x - px

    if abs(distx) > abs(disty):
        if distx < 0:
            return Entity.RIGHT
        else:
            return Entity.LEFT
    else:
        if disty < 0:
            return Entity.DOWN
        else:
            return Entity.UP

def ymirror(self, px, py):
    if self.y < py:
        return Entity.DOWN
    elif self.y > py:
        return Entity.UP
    else:
        return Entity.NONE

def xmirror(self, px, py):
    if self.x < px:
        return Entity.RIGHT
    elif self.x > px:
        return Entity.LEFT
    else:
        return Entity.NONE

behaviors = {
    "chase": chase,
    "ymirror": ymirror,
    "xmirror": xmirror
}

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

def draw_cell(x, y, screen, color, cellsize):
    screen_x = x * (cellsize + 1) + 1
    screen_y = y * (cellsize + 1) + 1

    pygame.draw.rect(
        screen,
        color, 
        pygame.Rect(screen_x, screen_y, cellsize, cellsize),
        0
    )

class Entity(pygame.sprite.Sprite):
    NONE, UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3, 4

    def __init__(self, x, y, cellsize, width, height):
        pygame.sprite.Sprite.__init__(self)

        image = pygame.surface.Surface((cellsize, cellsize))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.cellsize = cellsize

        self.image = image

        self.dir = Entity.NONE

    def update(self, dt):
        if self.dir == Entity.NONE:
            pass
        elif self.dir == Entity.UP and self.y > 0:
            self.y -= 1
        elif self.dir == Entity.DOWN and self.y < self.height - 1:
            self.y += 1
        elif self.dir == Entity.LEFT and self.x > 0:
            self.x -= 1
        elif self.dir == Entity.RIGHT and self.x < self.width - 1:
            self.x += 1
        
        self.dir = Entity.NONE
    
    def to_screen_xy(self):
        return (self.x * (self.cellsize + 1) + 1, self.y * (self.cellsize + 1) + 1)
    
    def dist(self, poix, poiy):
        return abs(self.x - poix) + abs(self.y - poiy)
    
    def diamond(self, radius, color, screen):
        for i in range(radius + 1):
            for j in range(radius + 1 - i):
                if i != 0 or j != 0: 
                    draw_cell(self.x + i, self.y + j, screen, color, self.cellsize)
                    draw_cell(self.x + i, self.y - j, screen, color, self.cellsize)

                    draw_cell(self.x - i, self.y + j, screen, color, self.cellsize)
                    draw_cell(self.x - i, self.y - j, screen, color, self.cellsize)
    
    def draw(self, screen):
        # draw_cell(self.x, self.y, )
        screen.blit(self.image, self.to_screen_xy())

class Player(Entity):
    def __init__(self, x, y, cellsize, width, height, vision=None):
        super(Player, self).__init__(x, y, cellsize, width, height)

        pygame.draw.rect(
            self.image, 
            (0, 255, 0), 
            pygame.Rect(0, 0, cellsize, cellsize),
            0
        )

        self.vision = vision
    
    def update(self, dt):
        super(Player, self).update(dt)

class Enemy(Entity):
    def __init__(self, x, y, cellsize, width, height, id=None, behavior=lambda self, *x: self.dir, action_rate=1):
        super(Enemy, self).__init__(x, y, cellsize, width, height)

        self.behavior = behavior
        self.action_rate = action_rate
        self.action_tick = 0

        self.id = id

        pygame.draw.rect(
            self.image, 
            (255, 0, 0), 
            pygame.Rect(0, 0, cellsize, cellsize),
            0
        )
        
    def update(self, dt, px, py):
        self.action_tick += 1

        if self.action_tick == self.action_rate:
            self.dir = self.behavior(self, px, py)
            self.action_tick = 0
        
        super(Enemy, self).update(dt)

class ATESim(BaseGame):
    @staticmethod
    def path_preprocessor(config_path):
        with open(config_path) as json_file:
            return json.load(json_file)
    
    @staticmethod
    def state_flatten(state):
        ls = [state["player_x"], state["player_y"]]
        # ls = []
        
        for enemy in state["enemies"]:
            ls.extend([enemy[1], enemy[2]])
        
        # return np.asarray(ls, dtype=float)
        return tuple(ls)
    
    # REQUIRED method
    def __init__(self, config={}, config_preproccesor = lambda p: p):

        # Actions the player agent in the simulation can take
        actions = {
            "left": pygame.constants.K_LEFT,
            "right": pygame.constants.K_RIGHT,
            "up": pygame.constants.K_UP,
            "down": pygame.constants.K_DOWN
        }

        config = config_preproccesor(config)

        self.timestep = 0

        width, height = config["width"] * (config["cellsize"] + 1), config["height"] * (config["cellsize"] + 1)

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
                    self.player.dir = Entity.LEFT
                elif key == self.actions["right"]:
                    self.player.dir = Entity.RIGHT
                elif key == self.actions["up"]:
                    self.player.dir = Entity.UP
                elif key == self.actions["down"]:
                    self.player.dir = Entity.DOWN

    # REQUIRED method
    def init(self):
        self.score = 0
        self.rwd = 0

        self.timestep = 0

        # Simulation specific initialization (include here stuff for intializing a new game
        # in this class, since a class instance can run its game multiple times)
        self.player = Player(
            self.config['player']['x'], 
            self.config['player']['y'], 
            self.config['cellsize'], 
            self.config['width'], self.config['height'],
            self.config["player"].get("vision") or None
        )

        self.enemies = []

        for enemy in self.config['enemies']:
            e = Enemy(
                enemy['x'],
                enemy['y'],
                self.config['cellsize'],
                self.config['width'], self.config['height'],
                id=enemy['id'],
                behavior=behaviors[enemy['behavior']],
                action_rate=enemy['action_rate']
            )

            self.enemies.append(e)
                
        self.lives = 1
    
    # REQUIRED method
    def get_score(self):
        return self.score
    
    # REQUIRED method
    def is_game_over(self):
        # Simulation specific game over condition
        return self.lives == 0
    
    def _dist(self, e):
        return abs(self.player.x - e.x) + abs(self.player.y - e.y)

    # REQUIRED method -- body of game itself
    def step(self, dt):
        # Adjust score
        # Update game state for checking game_over

        # (NOTE: Game can be locked to a certain FPS (keeping dt constant) by 
        # setting self.allowed_fps to desried value)
        dt /= 1000

        self._handle_player_events()
        self.player.update(dt)

        sum_dist = 0.0

        for e in self.enemies:
            e.update(dt, self.player.x, self.player.y)

            dist = self._dist(e)
            sum_dist += dist

            if dist == 0:
                self.lives = 0
                self.rwd = -1000
            else:
                self.rwd = sum_dist ** 2
                self.timestep += 1
        # self.rwd = -sum_dist
        self.score += self.rwd
    
    def draw(self):
        self.screen.fill((0, 0, 0))

        for vert in range(self.width):
            x = vert * (self.config["cellsize"] + 1)

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (x, 0),
                (x, self.height)
            )
        
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (self.width - 1, 0),
            (self.width - 1, self.height)
        )
        
        for horz in range(self.height):
            y = horz * (self.config["cellsize"] + 1)

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (0, y),
                (self.width, y)
            )
        
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (0, self.height - 1),
            (self.width, self.height - 1)
        )

        self.player.draw(self.screen)

        if self.player.vision:
            self.player.diamond(self.player.vision, (0, 100, 0), self.screen)

        for e in self.enemies:
            e.draw(self.screen)

    # REQUIRED method (if you want the state space to be not the screen itself, highly 
    # advised for simulation purposes)
    def get_game_state(self):
        # query for particular state information here

        state = {
            "player_x":     self.player.x,
            "player_y":     self.player.y,
            # "enemy_x":      self.enemy.x,
            # "enemy_y":      self.enemy.y,
            "enemies":      [(e.id, e.x - self.player.x, self.player.y - e.y) for e in self.enemies if self.player.vision == None or self._dist(e) <= self.player.vision]
        }

        return state

if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = ATESim("./test.json", ATESim.path_preprocessor)
    game.setup(display=True)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(30)
        if game.is_game_over():
            game.reset()

        game.step(dt)
        game.draw()
        pygame.display.update()
