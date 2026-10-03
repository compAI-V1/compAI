import os
os.environ.pop('APP_API_KEY', None); os.environ['APP_TOKEN_SECRET']='test-secret'; os.environ['APP_ENV']='development'
from fastapi.testclient import TestClient
from main import app
from tools.code_execution import execute_python
from tools.file_access import safe_path
client=TestClient(app)
def auth():
    email='edu-test@example.com'; password='strong-password'; client.post('/api/auth/register',json={'email':email,'password':password}); r=client.post('/api/auth/login',json={'email':email,'password':password}); return {'Authorization':'Bearer '+r.json()['token']}
def test_health(): assert client.get('/health').json()['status']=='ok'
def test_auth_and_chat_fallback():
    r=client.post('/api/chat',headers=auth(),json={'message':'Bonjour','session_id':'tests'}); assert r.status_code==200 and 'ANTHROPIC_API_KEY' in r.json()['response']
def test_educational_flow():
    headers=auth(); assert client.get('/api/learning/overview',headers=headers).status_code==200
    e=client.post('/api/exercises/generate',headers=headers,json={'topic':'probabilités','difficulty':'débutant'}); assert e.status_code==200
    exercise_id=e.json()['id']; s=client.post(f'/api/exercises/{exercise_id}/submit',headers=headers,json={'answer':'3/5'}); assert s.status_code==200
    assert client.get('/api/progress',headers=headers).json()['attempts_completed'] >= 1
def test_unauthorized(): assert client.get('/api/progress').status_code==401
def test_root_serves_ui(): assert 'Plateforme éducative' in client.get('/').text
def test_file_escape_blocked():
    try: safe_path('../secret.txt'); assert False
    except ValueError: assert True
def test_python_tool():
    result=execute_python('print(2 + 2)'); assert result['stdout'].strip()=='4' and result['exit_code']==0
