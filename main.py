import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from src.api_body.pydantic_structure import BOMRequest,BOMResponse
from api_router import *
from src.configuration.env_key import EnvironKey
from backend_logs import get_logger
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request

# CALL the function
config = EnvironKey.setting()
logger = get_logger("main.py")


app = FastAPI(title="Circor Backend Server.")
app.include_router(production_api, tags=["Production-API"])
app.include_router(developer_api, tags=["developer-api-inspect"])
app.include_router(logs_api,tags=["logs"])

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("main file reloaded done!")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time

    # Add header
    response.headers["X-Process-Time"] = str(process_time)

    return response

# ── Browser viewer at "/" ─────────────────────────────────────────────────────
@app.get("/")
async def log_viewer():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Live Logs</title></head>
    <body style="background:#111;color:#0f0;font-family:monospace;padding:20px">
        <h3 style="color:#fff">Live Log Stream</h3>
        <div id="logs" style="white-space:pre-wrap;font-size:13px"></div>
        <script>
            const es = new EventSource("/logs/live_log");
            const div = document.getElementById("logs");
            es.onmessage = (e) => {
                div.textContent += e.data + "\\n";
                window.scrollTo(0, document.body.scrollHeight);
            };
            es.onerror = () => {
                div.textContent += "\\n[connection lost — reconnecting...]\\n";
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"\nBackend successfully running on: http://{config["deployment"]["host"]}:{config["deployment"]["port"]}/docs\n")
    uvicorn.run("main:app", host=config["deployment"]["host"], port=config["deployment"]["port"],reload=True)
    