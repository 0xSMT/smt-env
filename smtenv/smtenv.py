# Samuel Taylor (2020)w

import os
import gym
from gym import spaces
import numpy as np

import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from smtenv.basegame import BaseGame

class _GameWrapper:
    def __init__(self,
                 game, lock_fps=False, fps=30, display=True, state_preprocessor=None):
        self.game = game
        self.fps = fps
        self.NOOP = None
        self.display = display
        self.lock_fps = lock_fps

        self.last_action = []
        self.action = []
        self.previous_score = 0
        self.frame_count = 0

        self.noop = -1

        if not isinstance(self.game, BaseGame):
            class_name = self.game.__class__.__name__
            raise Exception("{0} is BaseGame: {1}".format(class_name, isinstance(self.game, BaseGame)))
        
        self.game.setup(display=self.display)
        self.game.init()

        self.state_preprocessor = state_preprocessor

    def displayable(self):
        return self.display

    def set_display(self, display_flag):
        self.display = display_flag
        self.game._setup_display(display_flag)

    def _tick(self):
        if not self.display or self.lock_fps:
            return 1000.0 / self.fps
        else:
            return self.game.tick(self.fps)

    def get_actions(self):
        actions = self.game.get_actions()
        actions = list(actions)

        actions.append(self.noop)

        return actions

    def get_frame_number(self):
        return self.frame_count

    def game_over(self):
        return self.game.is_game_over()

    def score(self):
        return self.game.get_score()

    def reset_game(self):
        self.last_action = []
        self.action = []
        self.previous_score = 0.0
        self.game.reset()

    def get_screen_dims(self):
        return self.game.get_screen_dims()

    def get_game_state(self):
        state = self.game.get_game_state()

        if self.state_preprocessor is not None:
            return self.state_preprocessor(state)
        else:
            return state

    def act(self, action):
        if self.game_over():
            return 0.0
        
        if action not in self.get_actions():
            action = self.noop
        
        previous_score = self.score()

        self.game._do_action(action)
        dt = self._tick()
        self.game.step(dt)
        self.game._draw()

        self.frame_count += 1
        rwd = self.score() - previous_score

        return rwd

class SMTEnv(gym.Env):
    @staticmethod
    def register(game, display_screen=True, state_preprocessor=lambda x: x, fps=30, **args):
        game_name = game.__class__.__name__

        gym.envs.registration.register(
            id=game_name.lower() + "-v0",
            entry_point='smtenv:SMTEnv',
            kwargs={'game_class': game, 'display_screen': display_screen, 'state_preprocessor': state_preprocessor, 'fps': fps, 'kwargs': args}
        )

        return gym.make(game_name.lower() + "-v0")

    @staticmethod
    def run(env, agent, episode_count=5, episode_length=100, debug=False):
        reward = 0
        done = False

        for i in range(episode_count):
            if debug:
                print("Starting Episode {0}".format(i))
            
            ob = env.reset()

            for _ in range(episode_length):
                action = agent.act(ob, reward, done)
                ob, reward, done, _ = env.step(action)

                if debug:
                    print(ob)

                if done:
                    break

            if debug:
                print("Died? {0}".format(done))
        env.close()

    def __init__(self, game_class, display_screen=True, state_preprocessor=lambda x: x, fps=30, kwargs={}):
        # import importlib
        
        # game_module_name = game_name.lower()

        # game_module = importlib.import_module(game_module_name)
        # game = getattr(game_module, game_name)(**kwargs)
        game = game_class(**kwargs)
        self.game_state = _GameWrapper(game, fps=fps, display=display_screen, state_preprocessor=state_preprocessor)

        self._action_set = self.game_state.get_actions()
        self.action_space = spaces.Discrete(len(self._action_set))
        self.screen_height, self.screen_width = self.game_state.get_screen_dims()

        self.viewer = None

    def set_display(self, display_flag):
        self.game_state.set_display(display_flag)

    def step(self, a):
        reward = self.game_state.act(self._action_set[a])
        state = self.game_state.get_game_state()
        terminal = self.game_state.game_over()
        return state, reward, terminal, {}

    @property
    def _n_actions(self):
        return len(self._action_set)

    def reset(self):
        self.game_state.reset_game()
        state = self.game_state.get_game_state()
        return state

    def render(self):
        if self.game_state.displayable():
            self.game_state.game._draw()
    