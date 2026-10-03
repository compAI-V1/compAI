from __future__ import annotations
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from tools.code_execution import execute_python

app = FastAPI(title='compAI Sandbox Runner')
SECRET = os.getenv('SANDBOX_RUNNER_SECRET', '')
class ExecuteRequest(BaseModel): code: str = Field(min_length=1, max_length=20000)
@app.get('/health')
def health(): return {'status':'ok','service':'sandbox-runner'}
@app.post('/execute')
def execute(body: ExecuteRequest, x_runner_secret: str | None = Header(default=None)):
    if not SECRET or not x_runner_secret or x_runner_secret != SECRET: raise HTTPException(401, 'Invalid runner secret')
    return execute_python(body.code)
