# SMT-Env

A small library for binding arbitrary PyGames to OpenAI Gym. By designing a game that extends the BaseGame class, any given game can utilize OpenAI's interface and resources for easy AI algorithm design and experimental verification.

## Installation

First navigate to a proper location to store the cloned repository (deleting the cloned repository will delete the library from your system).

Then execute the following commands:

```bash
git clone https://github.com/0xSMT/smt-env.git
cd smt-env
pip3 install -e .
```

## Usage

A Q-Learning example is available in `examples/`

To create a new simulation, example the example environments in `smtenv/envs` and note the methods they extend from `smtenv.basegame.BaseGame` 