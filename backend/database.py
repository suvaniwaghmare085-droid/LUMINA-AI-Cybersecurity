"""SQLite persistence for users and scan history."""
from pathlib import Path
import sqlite3, json
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
DB_PATH = Path(__file__).resolve().parent / 'lumina.db'
def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user',created_at TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,input_type TEXT NOT NULL,input_text TEXT NOT NULL,risk_score INTEGER NOT NULL,risk_level TEXT NOT NULL,reasons_json TEXT NOT NULL,user_id INTEGER)''')
        if 'user_id' not in [r['name'] for r in c.execute('PRAGMA table_info(scans)').fetchall()]: c.execute('ALTER TABLE scans ADD COLUMN user_id INTEGER')
        email='admin@lumina.local'
        if not c.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
            c.execute('INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)',('LUMINA Administrator',email,generate_password_hash('Admin@123'),'admin',datetime.now(timezone.utc).isoformat()))
def create_user(name,email,password):
    with connect() as c:
        cur=c.execute('INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)',(name,email.lower(),generate_password_hash(password),'user',datetime.now(timezone.utc).isoformat())); return cur.lastrowid
def find_user(email):
    with connect() as c: r=c.execute('SELECT * FROM users WHERE email=?',(email.lower(),)).fetchone()
    return dict(r) if r else None
def save_scan(kind,content,result,user_id=None):
    with connect() as c:
        cur=c.execute('INSERT INTO scans(created_at,input_type,input_text,risk_score,risk_level,reasons_json,user_id) VALUES(?,?,?,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),kind,content[:2048],result['risk_score'],result['risk_level'],json.dumps(result['reasons']),user_id)); return cur.lastrowid
def get_history(limit=50,user_id=None,is_admin=False):
    with connect() as c:
        rows=c.execute('SELECT * FROM scans ORDER BY id DESC LIMIT ?',(limit,)).fetchall() if is_admin else c.execute('SELECT * FROM scans WHERE user_id=? ORDER BY id DESC LIMIT ?',(user_id,limit)).fetchall()
    return [{'id':r['id'],'created_at':r['created_at'],'input_type':r['input_type'],'input_text':r['input_text'],'risk_score':r['risk_score'],'risk_level':r['risk_level'],'reasons':json.loads(r['reasons_json'])} for r in rows]
def get_stats(user_id=None,is_admin=False):
    where,args=('',[]) if is_admin else (' WHERE user_id=?',[user_id])
    with connect() as c:
        r=c.execute("SELECT COUNT(*) total,SUM(CASE WHEN risk_level='HIGH RISK' THEN 1 ELSE 0 END) high,SUM(CASE WHEN risk_level='SUSPICIOUS' THEN 1 ELSE 0 END) suspicious,SUM(CASE WHEN input_type='url' THEN 1 ELSE 0 END) urls FROM scans"+where,args).fetchone()
        dist=c.execute('SELECT risk_level,COUNT(*) count FROM scans'+where+' GROUP BY risk_level',args).fetchall()
    return {'total':r['total'] or 0,'high_risk':r['high'] or 0,'suspicious':r['suspicious'] or 0,'urls':r['urls'] or 0,'distribution':{x['risk_level']:x['count'] for x in dist}}
def clear_history(user_id=None,is_admin=False):
    with connect() as c:
        c.execute('DELETE FROM scans' if is_admin else 'DELETE FROM scans WHERE user_id=?',() if is_admin else (user_id,))
