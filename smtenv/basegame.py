# Samuel Taylor (2020)

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame, math, sys, random
import numpy as np
from pygame.constants import KEYUP, KEYDOWN, K_F15

class BaseGame:
    def __init__(self, width, height, actions, rng_seed=None, config=None):

        # Actions the player agent in the simulation can take
        self.actions = actions

        self.config = config if config is not None else {}
        self.width = width
        self.height = height
        
        self.score = 0.0
        self.screen = None
        self.clock = None
        self.rng = np.random.RandomState(seed=None)
        # self.display = display
        self.rwd = 0.0

        self.last_action = None
    
    def setup(self, display=True, rng=None):
        pygame.init()
        self._setup_display(display)
        self.clock = pygame.time.Clock()
        self.rng = rng
    
    def _setup_display(self, display_flag):
        self.display = display_flag

        if self.display:
            self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)
        else:
            self.screen = None
    
    def _handle_player_events(self):
        pass

    def _do_action(self, action):
        if action not in self.actions.values():
            action = K_F15
        
        if self.last_action not in self.actions.values():
            self.last_action = K_F15

        kd = pygame.event.Event(KEYDOWN, {"key": action})
        ku = pygame.event.Event(KEYUP, {"key": self.last_action})

        pygame.event.post(kd)
        pygame.event.post(ku)
    
    def _draw(self):
        if self.display:
            self.draw()

            pygame.display.update()
    
    def tick(self, fps):
        return self.clock.tick_busy_loop(fps)

    def get_screen_dims(self):
        return (self.width, self.height)

    def get_actions(self):
        return self.actions.values()
    
    def get_score(self):
        return self.score
    
    def reset(self):
        self.init()
    
    def get_reward(self):
        return self.rwd

    def init(self):
        raise NotImplementedError("Please override this method")

    def draw(self):
        raise NotImplementedError("Please override this method")

    def get_game_state(self):
        raise NotImplementedError("Please override this method")

    def is_game_over(self):
        raise NotImplementedError("Please override this method")

    def step(self, dt):
        raise NotImplementedError("Please override this method")