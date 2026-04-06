import requests
import time


print("🚀 Resetting Environment...")

URL = "http://0.0.0.0:8000"

try:
    resp = requests.post(f"{URL}/reset", json={"task_id": "hard_scarcity"})
    obs = resp.json()
    print(f"Initial Levels: {obs['hospital_levels']}")

    for hour in range(1, 6):
        print(f"\n--- Hour {hour} ---")
        action = {"dispatches": [15.0, 10.0, 5.0]} 
        step_resp = requests.post(f"{URL}/step", json=action)
        data = step_resp.json()
                                                                                            
        print(f"Action Sent: {action['dispatches']}")
        print(f"New Levels: {data['hospital_levels']}")
        print(f"Reward Received: {data.get('reward', 0):.2f}")
                                                                                                                            
        if data.get('done', False):
            print("⚠️ Emergency: Hospital at 0% Oxygen! Game Over.")
            break
        time.sleep(1)
except Exception as e:
    print(f"❌ Error: Is your server running? {e}")
                                                                                                                                                