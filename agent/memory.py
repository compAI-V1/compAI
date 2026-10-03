from __future__ import annotations
import base64, hashlib, hmac, os, secrets
from contextlib import contextmanager
from pathlib import Path
import tempfile
DATABASE_URL=os.getenv('DATABASE_URL','').strip(); DB_PATH=None
if DATABASE_URL.startswith('sqlite:///'):
    _p=Path(DATABASE_URL[len('sqlite:///'):])
    if str(_p).startswith('/'):
        DB_PATH=_p
elif DATABASE_URL:
    DB_PATH=None  # PostgreSQL via DATABASE_URL
if DB_PATH is None:
    cand=Path('./data/compai.db')
    try:
        cand.parent.mkdir(parents=True,exist_ok=True); DB_PATH=cand
    except OSError:
        DB_PATH=Path(tempfile.gettempdir())/'compai.db'
if DB_PATH:
    try: DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    except OSError: DB_PATH=None
if DB_PATH is None:
    DB_PATH=Path(tempfile.gettempdir())/'compai.db'
    try: DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    except OSError: pass
def _connect():
    if DB_PATH:
        import sqlite3
        c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
    import psycopg
    return psycopg.connect(DATABASE_URL,row_factory=psycopg.rows.dict_row)
@contextmanager
def connection():
    c=_connect()
    try: yield c; c.commit()
    finally: c.close()
def _sql(sql:str)->str: return sql.replace('?', '%s') if not DB_PATH else sql
def init_db():
    with connection() as c:
        if DB_PATH: schemas=['CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)']
        else: schemas=['CREATE TABLE IF NOT EXISTS users (id BIGSERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS messages (id BIGSERIAL PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS notes (id BIGSERIAL PRIMARY KEY, session_id TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)']
        for s in schemas:c.execute(_sql(s))
def get_history(session_id:str,limit:int=30):
    with connection() as c: rows=c.execute(_sql('SELECT role,content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?'),(session_id,limit)).fetchall()
    return [{'role':r['role'],'content':r['content']} for r in reversed(rows)]
def save_message(session_id:str,role:str,content:str):
    with connection() as c:c.execute(_sql('INSERT INTO messages(session_id,role,content) VALUES (?,?,?)'),(session_id,role,content))
def hash_password(password:str)->str:
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,240000); return base64.urlsafe_b64encode(salt+digest).decode()
def verify_password(password:str,encoded:str)->bool:
    try:
        raw=base64.urlsafe_b64decode(encoded.encode()); return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',password.encode(),raw[:16],240000),raw[16:])
    except Exception:return False
def create_user(email:str,password:str):
    with connection() as c:
        try:return c.execute(_sql('INSERT INTO users(email,password_hash) VALUES (?,?) RETURNING id'),(email.lower().strip(),hash_password(password))).fetchone()['id']
        except Exception as exc:
            if 'unique' in str(exc).lower():raise ValueError('Email already registered')
            raise
def authenticate_user(email:str,password:str):
    with connection() as c: row=c.execute(_sql('SELECT id,email,password_hash FROM users WHERE email=?'),(email.lower().strip(),)).fetchone()
    if not row or not verify_password(password,row['password_hash']):return None
    return {'id':row['id'],'email':row['email']}
def init_learning_db():
    with connection() as c:
        if DB_PATH: schemas=['CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, difficulty TEXT NOT NULL, statement TEXT NOT NULL, solution TEXT NOT NULL, rubric TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, exercise_id INTEGER NOT NULL, answer TEXT NOT NULL, score REAL NOT NULL, feedback TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, duration_minutes INTEGER NOT NULL, exercise_ids TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)']
        else: schemas=[s.replace('INTEGER PRIMARY KEY','BIGSERIAL PRIMARY KEY') for s in ['CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, difficulty TEXT NOT NULL, statement TEXT NOT NULL, solution TEXT NOT NULL, rubric TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, exercise_id INTEGER NOT NULL, answer TEXT NOT NULL, score REAL NOT NULL, feedback TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)','CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, duration_minutes INTEGER NOT NULL, exercise_ids TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)']]
        for s in schemas:c.execute(_sql(s))
def learning_overview(user_id:str):
    with connection() as c:
        exercises=c.execute(_sql('SELECT COUNT(*) AS n FROM exercises')).fetchone()['n']; attempts=c.execute(_sql('SELECT COUNT(*) AS n FROM attempts WHERE user_id=?'),(str(user_id),)).fetchone()['n']; row=c.execute(_sql('SELECT COALESCE(AVG(score),0) AS avg_score FROM attempts WHERE user_id=?'),(str(user_id),)).fetchone()
    return {'exercises_available':exercises,'attempts_completed':attempts,'average_score':round(float(row['avg_score'] or 0),2),'has_real_progress':attempts>0}
def list_exercises(subject=None):
    with connection() as c:
        rows=c.execute(_sql('SELECT id,title,subject,difficulty,statement,rubric FROM exercises WHERE subject=? ORDER BY id DESC'),(subject,)).fetchall() if subject else c.execute(_sql('SELECT id,title,subject,difficulty,statement,rubric FROM exercises ORDER BY id DESC')).fetchall()
    return [dict(r) for r in rows]
def create_exercise(title,subject,difficulty,statement,solution,rubric):
    with connection() as c:return int(c.execute(_sql('INSERT INTO exercises(title,subject,difficulty,statement,solution,rubric) VALUES (?,?,?,?,?,?) RETURNING id'),(title,subject,difficulty,statement,solution,rubric)).fetchone()['id'])
def submit_attempt(user_id,exercise_id,answer):
    with connection() as c:
        if not c.execute(_sql('SELECT id FROM exercises WHERE id=?'),(exercise_id,)).fetchone():raise ValueError('Exercise not found')
        feedback='Réponse enregistrée. La correction détaillée doit être vérifiée par l’enseignant ou l’agent IA.'; score=0.0; attempt_id=c.execute(_sql('INSERT INTO attempts(user_id,exercise_id,answer,score,feedback) VALUES (?,?,?,?,?) RETURNING id'),(str(user_id),exercise_id,answer,score,feedback)).fetchone()['id']
    return {'attempt_id':int(attempt_id),'score':score,'feedback':feedback}
def list_exams():
    with connection() as c: rows=c.execute(_sql('SELECT id,title,subject,duration_minutes,exercise_ids FROM exams ORDER BY id DESC')).fetchall()
    return [dict(r) for r in rows]
