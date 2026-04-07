
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
    import models
    MyAction = models.MyAction
    MyObservation = models.MyObservation


class MyEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the my_env environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.levels=[50.0, 50.0, 50.0]
        self.usage_min = 2.0
        self.usage_max = 5.0
        self.current_task = "easy_stabilization"
        self.pending_delivery = [0.0, 0.0, 0.0]
        self.patient_counts = [10, 10, 10]

    def _generate_patient_counts(self):
        """Generate patient counts based on difficulty."""
        if "hard" in self.current_task:
            return [random.randint(40, 60) for _ in range(3)]
        elif "medium" in self.current_task:
            return [random.randint(25, 40) for _ in range(3)]
        else:
            return [random.randint(10, 20) for _ in range(3)]

    def reset(self, task_id: str= "easy_stabilization") -> Any:
        
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
        self.pending_delivery = [0.0, 0.0, 0.0]
        self.patient_counts = self._generate_patient_counts()
        

        return MyObservation(
            hospital_levels=self.levels,
            patient_counts=self.patient_counts,
            pending_delivery=self.pending_delivery,
            message=f"Environment reset to {task}",
            done=False,
            reward=0.0,
            metadata={"active_task": task}
        )

    def step(self, action: MyAction):  
        self._state.step_count += 1
        total_reward =0.0

        for i in range(3):
            self.levels[i] += self.pending_delivery[i]
            self.levels[i] = max(0, min(100, self.levels[i]))
            
        self.pending_delivery = list(action.dispatches)

        for i in range(3):
            usage=random.uniform(self.usage_min, self.usage_max)
            patient_multiplier = self.patient_counts[i] / 20.0
            usage = usage * patient_multiplier
            self.levels[i]-=usage
            self.levels[i]= max(0, min(100,self.levels[i]))
            if self.levels[i]<= 0:
                total_reward+= 0.0
            elif self.levels[i]<20:
                total_reward+= 0.1
            else:
                total_reward+= 0.33
            
        self.patient_counts = self._generate_patient_counts()
        is_done=self._state.step_count >=24
        metadata = {}
        if is_done:
             # Success criteria: Were all hospitals above 20% at the end?
             survived_hospitals = sum(1 for level in self.levels if level > 20)
             # Final Score: 0.0, 0.33, 0.66, or 1.0
             metadata["grader_score"] = survived_hospitals / 3.0 


        return MyObservation(
            hospital_levels=self.levels, 
            patient_counts=self.patient_counts,
            pending_delivery=self.pending_delivery,
            message=f"Status at Hour{self._state.step_count}",
            done=is_done,
            reward=total_reward,
            metadata=metadata
        )

    @property
    def state(self) -> State:
        return self._state
