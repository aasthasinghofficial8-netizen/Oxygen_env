# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the My Env Environment.

The my_env environment is a simple test environment that echoes back messages.
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from pydantic import BaseModel


class MyAction(BaseModel):
    dispatches: list[int]


class MyObservation(BaseModel):
    hospital_levels: list[float]
    message: str
    done: bool
    reward: float
    metadata: dict
