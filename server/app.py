"""
FastAPI application for the SQL Review Environment.

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 7860
"""

import sys
import os

# Ensure the project root is on the path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from openenv.core.env_server import create_app
from models import SQLReviewAction, SQLReviewObservation
from server.environment import SQLReviewEnvironment

# create_app expects (env_factory, action_cls, observation_cls, ...)
app = create_app(
    SQLReviewEnvironment,
    SQLReviewAction,
    SQLReviewObservation,
    env_name="sql-review-env",
)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL Review Environment</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #8b5cf6;
                --secondary: #3b82f6;
                --bg-grad: linear-gradient(135deg, #050505 0%, #111116 100%);
            }
            body { 
                font-family: 'Inter', sans-serif; 
                height: 100vh; 
                margin: 0; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                background: var(--bg-grad); 
                color: #e2e8f0; 
                overflow: hidden;
            }
            /* Ambient glowing orbs */
            .orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; z-index: 0; animation: float 10s ease-in-out infinite; }
            .orb-1 { width: 400px; height: 400px; background: var(--primary); top: -100px; left: -100px; animation-delay: 0s; }
            .orb-2 { width: 500px; height: 500px; background: var(--secondary); bottom: -150px; right: -150px; animation-delay: -5s; }
            
            @keyframes float {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(30px, 30px); }
            }

            .card { 
                position: relative;
                z-index: 10;
                background: rgba(255, 255, 255, 0.03); 
                padding: 3.5rem 4rem; 
                border-radius: 24px; 
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
                text-align: center; 
                max-width: 550px; 
                transform: translateY(20px);
                animation: slide-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }

            @keyframes slide-up {
                to { transform: translateY(0); opacity: 1; }
            }

            h1 { 
                font-size: 2.2rem; 
                margin-bottom: 1rem; 
                font-weight: 800;
                background: linear-gradient(to right, #a855f7, #60a5fa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.02em;
            }
            
            p { color: #94a3b8; line-height: 1.7; font-size: 1.05rem; }
            
            .btn { 
                display: inline-block; 
                background: linear-gradient(to right, #7c3aed, #2563eb); 
                color: white; 
                padding: 0.85rem 2rem; 
                border-radius: 12px; 
                text-decoration: none; 
                font-weight: 600; 
                margin-top: 2rem; 
                transition: all 0.3s ease;
                box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
                background: linear-gradient(to right, #6d28d9, #1d4ed8);
            }
            
            .features {
                display: flex;
                justify-content: center;
                gap: 1.5rem;
                margin-top: 1.5rem;
                color: #cbd5e1;
                font-size: 0.9rem;
            }
            .feature { display: flex; align-items: center; gap: 0.5rem; }
            .feature::before { content: '✓'; color: #34d399; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="card" style="opacity: 0;">
            <h1>SQL Review Environment</h1>
            <p>Welcome to your deterministic RL environment. A cutting-edge OpenEnv API natively deployed on Hugging Face infrastructure.</p>
            <div class="features">
                <div class="feature">25+ Scenarios</div>
                <div class="feature">AST Grader</div>
                <div class="feature">LLM Feedback</div>
            </div>
            <a href="/docs" class="btn">Explore API Docs</a>
        </div>
    </body>
    </html>
    """


def main():
    """Entry point for the SQL Review Environment server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
