from __future__ import annotations
import os, subprocess, sys, tempfile
from pathlib import Path

TIMEOUT = int(os.getenv("CODE_EXEC_TIMEOUT_SECONDS", "15")); MAX_CODE_BYTES = int(os.getenv("MAX_CODE_BYTES", "20000"))
def _limits():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT, TIMEOUT)); resource.setrlimit(resource.RLIMIT_FSIZE, (5*1024*1024, 5*1024*1024)); resource.setrlimit(resource.RLIMIT_NPROC, (32,32))
    except (ImportError, ValueError, PermissionError): pass

def _result(stdout, stderr, code, timed_out, tmp):
    files=[str(p.relative_to(tmp)) for p in Path(tmp).rglob('*') if p.is_file() and p.name!='main.py']; return {'stdout':stdout,'stderr':stderr,'exit_code':code,'timed_out':timed_out,'generated_files':files}

def execute_python(code: str) -> dict:
    if len(code.encode('utf-8')) > MAX_CODE_BYTES: return {'stdout':'','stderr':'Code exceeds MAX_CODE_BYTES','exit_code':-1,'timed_out':False,'generated_files':[]}
    if os.getenv('CODE_EXECUTION_MODE','disabled') == 'disabled': return {'stdout':'','stderr':'Code execution is disabled on this deployment (CODE_EXECUTION_MODE=disabled)','exit_code':-1,'timed_out':False,'generated_files':[]}
    if os.getenv('CODE_EXECUTION_MODE','disabled') == 'runner':
        import httpx
        try:
            r=httpx.post(os.getenv('SANDBOX_RUNNER_URL','http://sandbox:9000')+'/execute', headers={'X-Runner-Secret':os.getenv('SANDBOX_RUNNER_SECRET','')}, json={'code':code}, timeout=TIMEOUT+5); r.raise_for_status(); return r.json()
        except Exception as exc: return {'stdout':'','stderr':f'Sandbox runner unavailable: {exc}','exit_code':-1,'timed_out':False,'generated_files':[]}
    with tempfile.TemporaryDirectory(prefix='compai-run-') as tmp:
        script=Path(tmp)/'main.py'; script.write_text(code, encoding='utf-8')
        try:
            proc=subprocess.run([sys.executable,'-I',str(script)],cwd=tmp,capture_output=True,text=True,timeout=TIMEOUT,env={'PATH':'/usr/bin:/bin','PYTHONIOENCODING':'utf-8','HOME':tmp},preexec_fn=_limits if os.name=='posix' else None)
            return _result(proc.stdout,proc.stderr,proc.returncode,False,Path(tmp))
        except subprocess.TimeoutExpired as exc: return _result(exc.stdout or '',exc.stderr or '',-1,True,Path(tmp))
