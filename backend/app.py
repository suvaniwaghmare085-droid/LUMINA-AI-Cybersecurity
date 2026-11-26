"""LUMINA 2.0 Flask API with role-based authentication."""
import os,re
from functools import wraps
from flask import Flask,jsonify,request,session
from flask_cors import CORS
from werkzeug.security import check_password_hash
from database import init_db,save_scan,get_history,clear_history,create_user,find_user,get_stats,connect
from text_analyzer import analyze_text
from url_analyzer import analyze_url
from risk_engine import assess_risk
app=Flask(__name__); app.secret_key=os.environ.get('LUMINA_SECRET','change-this-local-demo-secret')
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax')
CORS(app,supports_credentials=True,resources={r'/api/*':{'origins':['http://127.0.0.1:8080','http://localhost:8080','null']}}); init_db()
def current_user():
    uid=session.get('user_id')
    if not uid:return None
    with connect() as c:r=c.execute('SELECT id,name,email,role FROM users WHERE id=?',(uid,)).fetchone()
    return dict(r) if r else None
def required(admin=False):
    def deco(fn):
        @wraps(fn)
        def wrapped(*a,**kw):
            u=current_user()
            if not u:return jsonify({'error':'Please log in to continue.'}),401
            if admin and u['role']!='admin':return jsonify({'error':'Administrator access required.'}),403
            return fn(*a,**kw)
        return wrapped
    return deco
@app.get('/api/health')
def health():return jsonify({'status':'ok','application':'LUMINA','version':'2.0.0'})
@app.post('/api/register')
def register():
    d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip().lower(); pw=str(d.get('password',''))
    if len(name)<2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email):return jsonify({'error':'Enter a valid name and email address.'}),400
    if len(pw)<8:return jsonify({'error':'Password must contain at least 8 characters.'}),400
    try:uid=create_user(name,email,pw)
    except Exception:return jsonify({'error':'An account with this email already exists.'}),409
    session.clear();session['user_id']=uid
    return jsonify({'message':'Account created.','user':{'id':uid,'name':name,'email':email,'role':'user'}}),201
@app.post('/api/login')
def login():
    d=request.get_json(silent=True) or {}; email=str(d.get('email','')).strip().lower(); pw=str(d.get('password','')); role=str(d.get('role','user')).lower(); u=find_user(email)
    if not u or not check_password_hash(u['password_hash'],pw):return jsonify({'error':'Incorrect email or password.'}),401
    if role not in ('user','admin') or u['role']!=role:return jsonify({'error':'This account does not have the selected login role.'}),403
    session.clear();session['user_id']=u['id'];return jsonify({'message':'Welcome to LUMINA.','user':{'id':u['id'],'name':u['name'],'email':u['email'],'role':u['role']}})
@app.get('/api/me')
@required()
def me():return jsonify({'user':current_user()})
@app.post('/api/logout')
def logout():session.clear();return jsonify({'message':'Logged out.'})
@app.post('/api/analyze')
@required()
def analyze():
    d=request.get_json(silent=True) or {}; content=str(d.get('input','')).strip(); typ=str(d.get('type','auto')).lower()
    if not content:return jsonify({'error':'Please enter text or a URL to analyze.'}),400
    if len(content)>10000:return jsonify({'error':'Input is too long (maximum 10,000 characters).'}),400
    try:
        isurl=typ=='url' or (typ=='auto' and content.lower().startswith(('http://','https://','www.')))
        if typ not in {'auto','text','url'}:return jsonify({'error':'Type must be auto, text or url.'}),400
        tr=ur=None
        if isurl:ur=analyze_url(content);kind='url'
        else:
            tr=analyze_text(content);kind='text';m=re.search(r'https?://[^\s<>()]+|www\.[^\s<>()]+',content,re.I)
            if m:
                try:ur=analyze_url(m.group(0).rstrip('.,!?'))
                except ValueError:pass
        result=assess_risk(tr,ur);result.update({'input_type':kind,'text_analysis':tr,'url_analysis':ur});u=current_user();result['scan_id']=save_scan(kind,content,result,u['id']);return jsonify(result)
    except ValueError as e:return jsonify({'error':str(e)}),400
    except Exception:
        app.logger.exception('Analysis failed');return jsonify({'error':'Analysis failed. Check the backend terminal.'}),500
@app.get('/api/history')
@required()
def history():
    u=current_user();return jsonify({'history':get_history(user_id=u['id'],is_admin=u['role']=='admin')})
@app.get('/api/stats')
@required()
def stats():
    u=current_user();return jsonify(get_stats(user_id=u['id'],is_admin=u['role']=='admin'))
@app.delete('/api/history')
@required()
def delete_history():
    u=current_user();clear_history(user_id=u['id'],is_admin=u['role']=='admin');return jsonify({'message':'Scan history cleared.'})
@app.errorhandler(404)
def missing(_):return jsonify({'error':'Endpoint not found.'}),404
if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=False)
