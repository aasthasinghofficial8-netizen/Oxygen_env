# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
My Env Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""
from typing import Any
import random
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
        sys.path.append(parent_dir)
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from .models import MyAction, MyObservation
except ImportError:
    from .models import MyAction, MyObservation
    import models
    MyAction = models.MyAction
    MyObservation = models.MyObservation


class MyEnvironment(Environment):
    """
    A simple echo environment that echoes back messages.

    This environment is designed for testing the HTTP server infrastructure.
    It maintains minimal state and simply echoes back whatever message it receives.

    Example:
        >>> env = MyEnvironment()
        >>> obs = env.reset()
        >>> print(obs.echoed_message)  # "My Env environment ready!"
        >>> obs = env.step(MyAction(message="Hello"))
        >>> print(obs.echoed_message)  # "Hello"
        >>> print(obs.message_length)  # 5
    """

    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the my_env environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.levels=[50.0, 50.0, 50.0]

    def reset(self, task_id: str= "easy_stabilization") -> Any:
        """
        Reset the environment.

        Returns:
            MyObservation with a ready message
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        task = str(task_id).strip().lower()
        if "hard" in task or task == "hard_scarcity":
            self.levels = [30.0, 30.0, 30.0]
            self.usage_min, self.usage_max=12, 25

        elif "medium" in task or task == "medium_surge":
            self.levels = [50.0,50.0,50.0]
            self.usage_min,self.usage_max=8, 15

        else:
            self.levels = [80.0, 80.0, 80.0]
            self.usage_min,self.usage_max= 2, 5
        
        self.current_task = task
        

        return MyObservation(
            hospital_levels=self.levels,
            message=f"Environment reset to {task}",
            done=False,
            reward=0.0,
            metadata={"active_task": task}
        )

    def step(self, action: MyAction) -> MyObservation:  # type: ignore[override]
        """
        Execute a step in the environment by echoing the message.

        Args:
            action: MyAction containing the message to echo

        Returns:
            MyObservation with the echoed message and its length
        """
        self._state.step_count += 1
        total_reward =0.0

        for i in range(3):
            usage=random.uniform(self.usage_min, self.usage_max)
            self.levels[i]-=usage
            self.levels[i]+=action.dispatches[i]
            self.levels[i]= max(0, min(100,self.levels[i]))
            if self.levels[i]<= 0:
                total_reward+= 0.0
            elif self.levels[i]<20:
                total_reward+= 0.1
            else:
                total_reward+= 0.33
            
        is_done=self._state.step_count >=24

        return MyObservation(
            hospital_levels=self.levels, 
            message=f"Status at Hour{self._state.step_count}",
            done=is_done,
            reward=total_reward,
            metadata={}
        )

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            Current State with episode_id and step_count
        """
        return self._state
