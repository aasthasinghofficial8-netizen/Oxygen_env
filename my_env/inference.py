import os
import time 
import json
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("OPENAI_API_KEY", "any")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN", "")  

client = OpenAI(base_url=f"{API_BASE_URL}/v1", api_key=API_KEY)

def run_task(task_id):
    print(f"\n[START] Task: {task_id}")
    reset_response = requests.post(f"{API_BASE_URL}/reset", json={"task_id": task_id})
    obs_data = reset_response.json()
    current_levels = obs_data.get("hospital_levels", [0.0, 0.0, 0.0])

    total_reward = 0
    final_score = 0.0 
    for step in range(24):
        prompt = f"""
        Context: You are managing 3 Hospital Oxygen Tanks.
        Current Levels: {current_levels} (Scale 0-100).
        Goal: Keep all levels above 20% to save lives.
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

            content = json.loads(response.choices[0].message.content)
            dispatch_values = content.get("dispatches", [0.0,0.0,0.0])
            step_response = requests.post(f"{API_BASE_URL}/step", json={"dispatches": dispatch_values})
            obs_data = step_response.json()
            levels = obs_data.get("hospital_levels")
            reward = obs_data.get("reward", 0.0)
            done = obs_data.get("done", False)
            total_reward += reward
            print(f"[STEP] Hour {step}: Reward={reward:.2f}, Levels={levels}")
            
            final_score = total_reward / 24
            if done:
                final_score = obs_data.get("metadata", {}).get("grader_score", total_reward/24)
                break

        except Exception as e:
            print(f"Error at hour {step}: {e}")
            break

    print(f"[END] Final Task Reward: {min(1.0, final_score):.2f}")
    
if __name__ == "__main__":
    tasks = ["easy_stabilization", "medium_surge", "hard_scarcity"]
    for tid in tasks:
        run_task(tid)
        time.sleep(1)
