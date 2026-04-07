---
title: My Env Environment Server
emoji: 🥁
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# Hospital Oxygen Supply Management Environment

An OpenEnv reinforcement learning environment simulating real-world hospital oxygen supply logistics. An AI agent decides how many oxygen cylinders to dispatch to 3 hospitals every hour to keep patients alive.

## Motivation

Oxygen shortages in hospitals are a real crisis — witnessed globally during COVID-19. This environment models the logistics decision-making required to prevent oxygen levels from dropping below critical thresholds across multiple hospitals, with realistic constraints like supply limits, fluctuating patient counts, and delivery delays.

## Action Space

**MyAction**
- `dispatches` (list[float]) — Oxygen cylinders to send to each of 3 hospitals
- Total across all hospitals capped at 30 cylinders per hour
- Each hospital capped at 20 cylinders per hour
- Example: `{"dispatches": [10.0, 12.0, 8.0]}`

## Observation Space

**MyObservation**
- `hospital_levels` (list[float]) — Current oxygen levels at each hospital (0-100)
- `patient_counts` (list[int]) — Current patient count at each hospital (affects consumption rate)
- `pending_delivery` (list[float]) — Cylinders arriving next hour (delivery delay mechanic)
- `message` (str) — Status message for current step
- `reward` (float) — Reward earned this step
- `done` (bool) — Whether episode is complete (24 hours)
- `metadata` (dict) — Extra info including final `grader_score` at episode end

## Reward Function

Per step, per hospital:
- `0.33` — oxygen level above 20 (safe zone)
- `0.10` — oxygen level below 20 but above 0 (critical zone)
- `0.00` — oxygen level at 0 (hospital failure)

Maximum possible reward per step = 0.99 (all 3 hospitals safe)

## Tasks

| Task ID | Difficulty | Starting Levels | Patient Count | Usage/Hour | Description |
|---|---|---|---|---|---|
| `easy_stabilization` | Easy | [80, 80, 80] | 10-20 | 2-5 units | Low demand, maintain steady levels |
| `medium_surge` | Medium | [50, 50, 50] | 25-40 | 8-15 units | Sudden spike in patient oxygen usage |
| `hard_scarcity` | Hard | [30, 30, 30] | 40-60 | 12-25 units | Prevent total failure during shortage crisis |

## Grader

At episode end (24 steps):
- `grader_score` = hospitals above 20% / 3
- All 3 safe → 1.0
- 2 safe → 0.66
- 1 safe → 0.33
- 0 safe → 0.0

## Key Environment Mechanics

**Supply Limit** — Agent cannot send unlimited cylinders. Total dispatch per hour is capped at 30, forcing real trade-off decisions between hospitals.

**Delivery Delay** — Cylinders dispatched this hour arrive next hour. Agent must plan ahead, not just react.

**Dynamic Patient Counts** — Patient counts change every hour, making oxygen consumption unpredictable. Agent must read current patient counts in observation to make smart decisions.

## Setup & Usage

### Local Development

```bash
git clone <your-repo-url>
cd my_env
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

Docker

docker build -t my-env .
docker run -p 8000:8000 my-env

Run Baseline Inference

export OPENAI_API_KEY=your_key
export API_BASE_URL=http://localhost:8000
export MODEL_NAME=gpt-4o
export HF_TOKEN=your_hf_token
python inference.py

Environment Variables

Variable-Description
API_BASE_URL-API endpoint for the LLM
MODEL_NAME-Model identifier for inference
OPENAI_API_KEY-Your OpenAI API key
HF_TOKEN-Your Hugging Face token

Baseline Scores

Task-Expected Score
easy_stabilization- ~0.90
medium_surge- ~0.66
hard_scarcity- ~0.33

Project Structure

my_env/
├── app.py                     # FastAPI application
├── inference.py               # Baseline inference script
├── openenv.yaml               # OpenEnv manifest
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container definition
├── README.md                  # This file
└── server/
    ├── __init__.py
    ├── models.py              # Action and Observation models
    └── my_env_environment.py  # Core environment logic

---