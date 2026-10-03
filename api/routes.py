from __future__ import annotations
import base64, hashlib, hmac, os, tempfile, time
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from agent.orchestrator import Agent
from agent.memory import create_user, authenticate_user, learning_overview, list_exercises, create_exercise, submit_attempt, list_exams
from tools.voice import synthesize_speech

router=APIRouter(prefix='/api'); agent=Agent(); TOKEN_SECRET=os.getenv('APP_TOKEN_SECRET','dev-only-change-me')
def issue_token(user):
    payload=f"{user['id']}:{user['email']}:{int(time.time())+86400}"; sig=hmac.new(TOKEN_SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest(); return base64.urlsafe_b64encode(f'{payload}:{sig}'.encode()).decode()
def current_user(authorization: str|None=Header(default=None)):
    if os.getenv('APP_API_KEY'):
        if authorization != f"Bearer {os.getenv('APP_API_KEY')}": raise HTTPException(401,'Authentication required')
        return {'id':'api-key','email':'api-key'}
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Authentication required')
    try:
        raw=base64.urlsafe_b64decode(authorization[7:].encode()).decode(); user_id,email,expiry,sig=raw.rsplit(':',3); payload=f'{user_id}:{email}:{expiry}'
        if int(expiry)<int(time.time()) or not hmac.compare_digest(sig,hmac.new(TOKEN_SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()): raise ValueError
        return {'id':user_id,'email':email}
    except Exception as exc: raise HTTPException(401,'Invalid or expired token') from exc
class Credentials(BaseModel): email:str=Field(min_length=5,max_length=254); password:str=Field(min_length=8,max_length=128)
class ChatRequest(BaseModel): message:str=Field(min_length=1,max_length=12000); session_id:str=Field(default='default',max_length=100)
class ExerciseRequest(BaseModel): subject:str='Mathématiques appliquées'; difficulty:str='débutant'; topic:str='pourcentages'
class AttemptRequest(BaseModel): answer:str=Field(min_length=1,max_length=12000)

@router.post('/auth/register')
def register(body:Credentials):
    try: user_id=create_user(body.email,body.password)
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc
    user={'id':user_id,'email':body.email.lower().strip()}; return {'user':user,'token':issue_token(user)}
@router.post('/auth/login')
def login(body:Credentials):
    user=authenticate_user(body.email,body.password)
    if not user: raise HTTPException(401,'Invalid email or password')
    return {'user':user,'token':issue_token(user)}
@router.get('/auth/me')
def me(user=Depends(current_user)): return {'user':user}
@router.post('/chat')
def chat(body:ChatRequest,user=Depends(current_user)): return agent.chat(f"user:{user['id']}:{body.session_id}",body.message)

@router.get('/learning/overview')
def overview(user=Depends(current_user)): return learning_overview(str(user['id']))
@router.get('/exercises')
def exercises(subject:str|None=None,user=Depends(current_user)): return {'items':list_exercises(subject)}
@router.post('/exercises/generate')
def generate_exercise(body:ExerciseRequest,user=Depends(current_user)):
    templates={
      'pourcentages':('Évolution en pourcentage','Un produit coûte 800 DH. Son prix augmente de 12 %. Quel est son nouveau prix ?','896 DH','2 points : calcul de l’augmentation (1), résultat final (1).'),
      'probabilités':('Probabilité simple','Une urne contient 3 boules rouges et 2 boules bleues. Quelle est la probabilité de tirer une boule rouge ?','3/5','2 points : cas favorables (1), cas possibles et fraction (1).'),
      'moyenne':('Moyenne pondérée','Une note 12 compte pour 40 % et une note 15 compte pour 60 %. Calculer la moyenne pondérée.','13,8','2 points : pondération (1), somme correcte (1).')}
    title,statement,solution,rubric=templates.get(body.topic.lower(),templates['pourcentages'])
    exercise_id=create_exercise(title,body.subject,body.difficulty,statement,solution,rubric)
    return {'id':exercise_id,'title':title,'subject':body.subject,'difficulty':body.difficulty,'statement':statement,'status':'generated'}
@router.post('/exercises/{exercise_id}/submit')
def submit(exercise_id:int,body:AttemptRequest,user=Depends(current_user)):
    try: return submit_attempt(str(user['id']),exercise_id,body.answer)
    except ValueError as exc: raise HTTPException(404,str(exc)) from exc
@router.get('/exams')
def exams(user=Depends(current_user)): return {'items':list_exams()}
@router.get('/progress')
def progress(user=Depends(current_user)): return learning_overview(str(user['id']))

@router.post('/voice/message')
async def voice_message(file:UploadFile=File(...),session_id:str='default',user=Depends(current_user)):
    if not os.getenv('OPENAI_API_KEY'): raise HTTPException(503,'OPENAI_API_KEY is not configured')
    from openai import OpenAI
    suffix=Path(file.filename or 'audio.webm').suffix or '.webm'
    with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as tmp: tmp.write(await file.read()); audio_path=tmp.name
    try:
        with open(audio_path,'rb') as audio: transcription=OpenAI(api_key=os.environ['OPENAI_API_KEY']).audio.transcriptions.create(model='whisper-1',file=audio,language='fr')
        result=agent.chat(f"user:{user['id']}:{session_id}",transcription.text); audio_url=None
        if os.getenv('ELEVENLABS_API_KEY'): audio_url='/api/audio/'+Path(synthesize_speech(result['response'],f"response-{user['id']}.mp3")).name
        return {'transcription':transcription.text,'audio_url':audio_url,**result}
    finally:
        try: os.unlink(audio_path)
        except OSError: pass
@router.get('/audio/{filename}')
def audio(filename:str,user=Depends(current_user)):
    path=Path(__file__).resolve().parents[1]/'data'/'files'/Path(filename).name
    if path.suffix!='.mp3' or not path.is_file(): raise HTTPException(404,'Audio not found')
    return FileResponse(path,media_type='audio/mpeg',filename=path.name)
