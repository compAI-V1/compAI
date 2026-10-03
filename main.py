from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agent.memory import init_db, init_learning_db
from api.routes import router
from config import validate_config, readiness
from middleware import SafetyMiddleware
BASE=Path(__file__).resolve().parent
validate_config()
app=FastAPI(title='compAI',version='0.5.0',description="Plateforme éducative IA")
app.add_middleware(SafetyMiddleware,max_body_bytes=int(os.getenv('MAX_REQUEST_BYTES','12582912')),requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE','60')))
origins=[x.strip() for x in os.getenv('CORS_ORIGINS','').split(',') if x.strip()]
if origins: app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
app.include_router(router); init_db(); init_learning_db()
@app.get('/health')
def health(): return {'status':'ok','service':'compAI','claude_configured':bool(os.getenv('ANTHROPIC_API_KEY'))}
@app.get('/ready')
def ready(): return readiness()
@app.get('/')
def home(): return FileResponse(BASE/'frontend'/'index.html')
