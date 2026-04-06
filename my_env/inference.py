import os
import time 
import json
from openai import OpenAI
from server.my_env_environment import MyEnvironment 
from server.models import MyAction, MyObservation 

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

client = OpenAI(base_url=API_BASE_URL,api_key=API_KEY)

def run_task(task_id):
    env = MyEnvironment()
    obs = env.reset(task_id=task_id)

    print(f"[START] Task:{task_id}")

    total_reward = 0
    for step in range(24):
        prompt = f"""
        Context: You are managing 3 Hospital Oxygen Tanks.
        Current Levels: {obs.hospital_levels}(Scale 0-100).
        Goal: Keep all levels above 20% to save lives.and
        Task Difficulty: {task_id}
        Action: Decide how many units to dispatch to each [Hospital 1, Hospital 2, Hospital 3].
        Constraint: Respond ONLY with a JSON object like: {{"dispatches": [10.0, 5.0, 20.0]}}
        """

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content":"You are a healthcare logistics expert."},
                          {"role":"user","content": prompt}],
                response_format={"type": "json_object"}  
            )

            content = json.loads(response.choices.message.content)
            dispatch_values = content.get("dispatches", [0.0,0.0,0.0])

            action = MyAction(dispatches=dispatch_values)

            obs=env.step(action)
            total_score+=obs.reward

            print(f"[STEP] Hour {step}: Reward={obs.reward:.2f}, Levels={obs.hospital_levels}")

            if obs.done:
                break

        except Exception as e:
            print(f"Error at hour {step}: {e}")
            break

    final_avg_reward = total_reward/24
    print(f"[END] Final Task Reward: {min(1.0,final_avg_reward):.2f}")

if __name__=="__main__":
    tasks = ["easy_stabilization","medium_surge","hard_scarcity"]

    for tid in tasks:
        run_task(tid)
        time.sleep(1)
