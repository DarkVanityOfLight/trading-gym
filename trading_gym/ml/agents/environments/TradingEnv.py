from typing import Any

import numpy as np
from tf_agents.environments import py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.typing import types

from trading_gym.apis.AlphaAPI.AlphaAPI import RequestType
from trading_gym.wrapper.wallet.TimedWallet import TimedWallet


# 0 Is Buy
# 1 is Sell

# Pass the last N steps of history as observation
# What is N, aghhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh
# Let's put N to 5 for now

# To keep it simple we will just pass the history and decide if to buy or sell
# Observation should be of shape
# [History, History, History, History, History, Money, Share Amount]
# Action should be of shape for now
# [Action]

class TradingEnvV2(py_environment.PyEnvironment, TimedWallet):

    def get_info(self) -> Any:
        return "Foo"

    def __init__(self, start_capital: int, train_on: str):
        TimedWallet.__init__(self, start_capital)

        # Init the wallet by getting a new course
        c = self.new_course(train_on, RequestType.DAILY, outputsize="full")
        self.course_to_train_on = c
        self._end_date = c.end_date

        # Define the specs
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=1, name="action")
        self._observation_spec = array_spec.ArraySpec(shape=(7, ), dtype=np.float64, name="observation")

        self._episode_ended = False
        self.start_capital = start_capital

        self.course_to_train_on.step = 5

        self._state = None
        self.create_state()

    def get_state(self) -> Any:
        return self._state

    def set_state(self, state):
        self._state = state

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self) -> ts.TimeStep:
        self.shares = {}
        self.money = self.start_capital
        self._episode_ended = False
        self.course_to_train_on.step = 5
        self.create_state()
        return ts.restart(self._state)

    def _step(self, action) -> ts.TimeStep:
        if self._episode_ended:
            return self.reset()

        if self.course_to_train_on.has_ended:
            self._episode_ended = True

        if self.money <= 0 and len(self.shares[self.course_to_train_on.symbols]):
            self._episode_ended = True

        if self._episode_ended:
            reward = self.start_capital - self.money
            return ts.termination(self._state, reward)

        # Go one forward in history
        self.course_to_train_on.next_step()
        # Get our new state
        self.create_state()

        # Not enough money and tries to buy, bad AI
        if self.money <= self.course_to_train_on.get_current_price() and action == 0:
            return ts.transition(self._state, -100)
        # First action is sell, we don't
        valid = True
        try:
            if len([shares for shares in self.shares[self.course_to_train_on.symbol]]) < 0:
                valid = False
        except KeyError:
            valid = False

        finally:
            if not valid:
                step = ts.transition(self._state, -100)
                return step

        # Buy
        if action == 0:
            # Get the close cost
            cost = self._state[4][3]
            # How many can we buy
            can_buy = self.money // cost
            # Buy them
            self.buy(self.course_to_train_on, can_buy)

            return ts.transition(self._state, 0.0)

        # Sell
        elif action == 1:
            total_gain = 0
            for share in self.shares[self.course_to_train_on.symbol]:
                bought_for = share.total_cost()
                sold_for = self.sell(share, share.quantity)
                total_gain += sold_for - bought_for

            return ts.transition(self._state, total_gain)

    def create_state(self):
        last_5 = self.course_to_train_on.get_last_n_steps(5)
        last_5 = [point[1] for point in last_5]
        state = np.array(last_5 + [self.money, 0])
        self._state = state


# BAD ENV
class TradingEnv(py_environment.PyEnvironment, TimedWallet):
    def get_info(self) -> Any:
        return "Foo"

    def get_state(self) -> Any:
        return self._state

    def set_state(self, state: Any):
        self._state = state

    start_capital: int

    def __init__(self, start_capital, train_on: str):
        self._state = 0
        TimedWallet.__init__(self, start_capital)
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1,), dtype=np.int32, minimum=[0], maximum=[1], name="action")

        self._observation_spec = array_spec.ArraySpec(shape=(5, 5), dtype=np.float64, name="observation")
        self._episode_ended = False

        # Init the wallet
        self.start_capital = start_capital
        self.new_course(train_on, RequestType.DAILY, outputsize="full")

        self._end_date = self.courses[0].end_date
        # self._current_date = self.courses[0].start_date
        self.courses[0].step = 5

    def observation_spec(self) -> types.NestedArraySpec:
        return self._observation_spec

    def action_spec(self) -> types.NestedArraySpec:
        return self._observation_spec

    def _step(self, action: types.NestedArray) -> ts.TimeStep:
        if self._episode_ended:
            return self.reset()

        history = self.courses[0].get_last_n_steps(5)
        # Cut the dates
        history = [point[1:] for point in history]
        observation = np.array([history])

        if self.courses[0].has_ended:
            self.has_ended = True

        first = next(iter(self.shares))
        shares = self.shares[first]

        buy_sell = action[0]

        reward = 0
        if buy_sell == 0:
            total_gain = 0
            for share in shares:
                origin_price = share.total_cost()
                gained = self.sell(share, share.quantity)
                difference = gained - origin_price
                total_gain += difference

            reward = total_gain
        if buy_sell == 1:
            current_price = self.course[0].get_current_price()
            to_buy = self.money // current_price
            self.buy(self.courses[0], to_buy)

            if to_buy < 1:
                reward = -10

        if self.money >= 0:
            return ts.termination(observation, -100)

        return ts.transition(observation, [reward])

    def _reset(self) -> ts.TimeStep:
        self.shares = {}
        self.money = self.start_capital
        self._episode_ended = False
        return ts.restart(np.array([self._state], dtype=np.int32))


if __name__ == '__main__':
    env = TradingEnvV2(10000, "IBM")
    utils.validate_py_environment(env, episodes=5)
