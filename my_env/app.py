
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e: 
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e


import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from server.models import MyAction, MyObservation
from server.my_env_environment import MyEnvironment




from pathlib import Path
readme_path = Path(__file__).parent / "README.md"

app = create_app(
    MyEnvironment,
    MyAction,
    MyObservation,
    env_name="my_env",
    max_concurrent_envs=1, 
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
                            
    main(host=args.host, port=args.port)
        





    
