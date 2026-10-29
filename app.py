from flask import Flask,render_template,request,redirect,url_for,session,flash,send_from_directory
import sqlite3, os
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
app=Flask(__name__); app.secret_key='jobconnect-pro-college-project'; ROOT=os.path.dirname(__file__); DB=os.path.join(ROOT,'jobconnect.db'); UP=os.path.join(ROOT,'uploads'); os.makedirs(UP,exist_ok=True)
def db(): c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def login_required(f):
 @wraps(f)
 def w(*a,**k):
  if not session.get('uid'): return redirect(url_for('login'))
  return f(*a,**k)
 return w
def init_db():
 c=db(); x=c.cursor(); x.executescript('''
 CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT UNIQUE,password TEXT,role TEXT,phone TEXT,location TEXT,headline TEXT,bio TEXT,skills TEXT,experience TEXT,education TEXT,resume TEXT,company TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,company TEXT,location TEXT,min_salary INTEGER,max_salary INTEGER,job_type TEXT,work_mode TEXT,experience TEXT,skills TEXT,description TEXT,requirements TEXT,vacancies INTEGER DEFAULT 1,posted_by INTEGER,status TEXT DEFAULT 'Active',created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
 CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,job_id INTEGER,status TEXT DEFAULT 'Applied',note TEXT,applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,job_id));
 CREATE TABLE IF NOT EXISTS saved_jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,job_id INTEGER,UNIQUE(user_id,job_id));
 CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,message TEXT,is_read INTEGER DEFAULT 0,created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
 ''')
 demos=[('Aarav Mehta','aarav@demo.test','jobseeker','Mumbai','Python Developer','Python, Flask, SQL, JavaScript','1 year internship','BSc IT'),('Priya Sharma','priya@demo.test','jobseeker','Pune','UI/UX Designer','Figma, UI, UX, Prototyping','Fresher','B.Des'),('Neha Recruiter','recruiter@jobconnect.test','recruiter','Mumbai','Talent Acquisition','Recruitment, HR','5 years','MBA HR'),('Admin','admin@jobconnect.test','admin','Mumbai','Administrator','','','')]
 for n,e,r,l,h,s,ex,ed in demos:
  if not x.execute('select 1 from users where email=?',(e,)).fetchone(): x.execute('insert into users(name,email,password,role,location,headline,skills,experience,education,company) values(?,?,?,?,?,?,?,?,?,?)',(n,e,generate_password_hash('demo123'),r,l,h,s,ex,ed,'JobConnect HR' if r=='recruiter' else ''))
 rid=x.execute("select id from users where email='recruiter@jobconnect.test'").fetchone()[0]
 if x.execute('select count(*) from jobs').fetchone()[0]==0:
  jobs=[('Python Developer','TechNova Solutions','Mumbai',400000,700000,'Full-time','On-site','1-3 years','Python, Flask, SQL, REST API','Build production web applications and APIs. Work with product and engineering teams.','Python fundamentals, SQL, Git and communication skills.',4),('Frontend Developer','PixelCraft Labs','Pune',350000,650000,'Full-time','Hybrid','0-2 years','HTML, CSS, JavaScript, React','Create responsive interfaces for modern web products.','JavaScript, responsive design and Git.',3),('Data Analyst','InsightWorks','Bengaluru',500000,850000,'Full-time','Hybrid','1-3 years','SQL, Excel, Python, Power BI','Analyze business data and create dashboards for decision making.','Strong SQL and spreadsheet skills.',2),('UI/UX Designer','DesignDeck','Remote',300000,600000,'Full-time','Remote','0-2 years','Figma, UI, UX, Prototyping','Design user journeys, wireframes and polished product interfaces.','Portfolio and Figma knowledge.',2),('Java Developer','CloudAxis','Hyderabad',450000,800000,'Full-time','On-site','1-4 years','Java, Spring Boot, MySQL','Develop scalable backend services and REST APIs.','Java, OOP, Spring basics.',5),('Digital Marketing Executive','GrowthMint','Mumbai',300000,500000,'Full-time','On-site','0-2 years','SEO, Social Media, Analytics','Plan campaigns and measure acquisition performance.','SEO basics and communication.',3),('Customer Support Associate','HelpHive','Remote',250000,400000,'Full-time','Remote','Fresher','Communication, CRM, English','Support customers through chat and email.','Good written communication.',10),('React Developer','AppForge','Navi Mumbai',500000,900000,'Full-time','Hybrid','2-4 years','React, JavaScript, REST API','Build fast, accessible product experiences.','React hooks and API integration.',3),('Business Development Intern','StartSphere','Mumbai',180000,240000,'Internship','On-site','Fresher','Sales, Communication, Excel','Support lead generation and client outreach.','Confident communication.',8),('HR Recruiter','PeopleBridge','Thane',300000,480000,'Full-time','On-site','0-2 years','Recruitment, HR, Communication','Source and coordinate candidates across roles.','Communication and organization.',4)]
  x.executemany('insert into jobs(title,company,location,min_salary,max_salary,job_type,work_mode,experience,skills,description,requirements,vacancies,posted_by) values(?,?,?,?,?,?,?,?,?,?,?,?,?)',[j+(rid,) for j in jobs])
 c.commit(); c.close()
@app.context_processor
def ctx(): return dict(me=session)
@app.route('/')
def home():
 c=db(); jobs=c.execute("select * from jobs where status='Active' order by id desc limit 6").fetchall(); stats=(c.execute('select count(*) from jobs').fetchone()[0],c.execute("select count(*) from users where role='jobseeker'").fetchone()[0],c.execute("select count(*) from users where role='recruiter'").fetchone()[0]); c.close(); return render_template('home.html',jobs=jobs,stats=stats)
@app.route('/jobs')
def jobs():
 q=request.args.get('q',''); loc=request.args.get('location',''); typ=request.args.get('type',''); mode=request.args.get('mode',''); sql="select * from jobs where status='Active'"; p=[]
 if q: sql+=' and (title like ? or company like ? or skills like ?)'; p += ['%'+q+'%']*3
 if loc: sql+=' and location like ?'; p.append('%'+loc+'%')
 if typ: sql+=' and job_type=?'; p.append(typ)
 if mode: sql+=' and work_mode=?'; p.append(mode)
 c=db(); rows=c.execute(sql+' order by id desc',p).fetchall(); c.close(); return render_template('jobs.html',jobs=rows)
@app.route('/job/<int:id>')
def job(id):
 c=db(); j=c.execute('select * from jobs where id=?',(id,)).fetchone(); saved=False; applied=False
 if session.get('uid'): saved=bool(c.execute('select 1 from saved_jobs where user_id=? and job_id=?',(session['uid'],id)).fetchone()); applied=bool(c.execute('select 1 from applications where user_id=? and job_id=?',(session['uid'],id)).fetchone())
 c.close(); return render_template('job.html',job=j,saved=saved,applied=applied)
@app.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  try:
   c=db(); c.execute('insert into users(name,email,password,role,phone,location,skills,company) values(?,?,?,?,?,?,?,?)',(request.form['name'],request.form['email'].lower(),generate_password_hash(request.form['password']),request.form['role'],request.form.get('phone',''),request.form.get('location',''),request.form.get('skills',''),request.form.get('company',''))); c.commit(); c.close(); flash('Account created. Please sign in.'); return redirect(url_for('login'))
  except sqlite3.IntegrityError: flash('Email already registered.')
 return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  c=db(); u=c.execute('select * from users where email=?',(request.form['email'].lower(),)).fetchone(); c.close()
  if u and check_password_hash(u['password'],request.form['password']): session.update(uid=u['id'],name=u['name'],role=u['role']); return redirect(url_for('dashboard'))
  flash('Invalid email or password.')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/dashboard')
@login_required
def dashboard():
 c=db(); u=c.execute('select * from users where id=?',(session['uid'],)).fetchone()
 if session['role']=='jobseeker': apps=c.execute('select a.*,j.title,j.company,j.location from applications a join jobs j on j.id=a.job_id where a.user_id=? order by a.id desc',(session['uid'],)).fetchall(); saved=c.execute('select j.* from saved_jobs s join jobs j on j.id=s.job_id where s.user_id=?',(session['uid'],)).fetchall(); c.close(); return render_template('seeker_dashboard.html',user=u,apps=apps,saved=saved)
 if session['role']=='recruiter': jobs=c.execute('select j.*,(select count(*) from applications a where a.job_id=j.id) applicants from jobs j where posted_by=? order by j.id desc',(session['uid'],)).fetchall(); c.close(); return render_template('recruiter_dashboard.html',user=u,jobs=jobs)
 stats=[c.execute('select count(*) from users').fetchone()[0],c.execute('select count(*) from jobs').fetchone()[0],c.execute('select count(*) from applications').fetchone()[0]]; users=c.execute('select * from users order by id desc limit 20').fetchall(); jobs=c.execute('select * from jobs order by id desc limit 20').fetchall(); c.close(); return render_template('admin.html',stats=stats,users=users,jobs=jobs)
@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
 c=db(); u=c.execute('select * from users where id=?',(session['uid'],)).fetchone()
 if request.method=='POST':
  resume=u['resume']; f=request.files.get('resume')
  if f and f.filename: resume=secure_filename(str(session['uid'])+'_'+f.filename); f.save(os.path.join(UP,resume))
  c.execute('update users set name=?,phone=?,location=?,headline=?,bio=?,skills=?,experience=?,education=?,company=?,resume=? where id=?',(request.form['name'],request.form.get('phone',''),request.form.get('location',''),request.form.get('headline',''),request.form.get('bio',''),request.form.get('skills',''),request.form.get('experience',''),request.form.get('education',''),request.form.get('company',''),resume,session['uid'])); c.commit(); session['name']=request.form['name']; flash('Profile updated.'); return redirect(url_for('profile'))
 c.close(); return render_template('profile.html',user=u)
@app.route('/uploads/<path:name>')
def uploads(name): return send_from_directory(UP,name)
@app.post('/apply/<int:id>')
@login_required
def apply(id):
 if session['role']!='jobseeker': flash('Only job seekers can apply.'); return redirect(url_for('job',id=id))
 c=db()
 try: c.execute('insert into applications(user_id,job_id) values(?,?)',(session['uid'],id)); c.commit(); flash('Application submitted successfully.')
 except sqlite3.IntegrityError: flash('You already applied to this job.')
 c.close(); return redirect(url_for('job',id=id))
@app.post('/save/<int:id>')
@login_required
def save(id):
 c=db(); old=c.execute('select id from saved_jobs where user_id=? and job_id=?',(session['uid'],id)).fetchone()
 if old: c.execute('delete from saved_jobs where id=?',(old['id'],)); flash('Removed from saved jobs.')
 else: c.execute('insert into saved_jobs(user_id,job_id) values(?,?)',(session['uid'],id)); flash('Job saved.')
 c.commit(); c.close(); return redirect(request.referrer or url_for('jobs'))
@app.route('/post-job',methods=['GET','POST'])
@login_required
def post_job():
 if session['role']!='recruiter': return redirect(url_for('dashboard'))
 if request.method=='POST':
  f=request.form; c=db(); c.execute('insert into jobs(title,company,location,min_salary,max_salary,job_type,work_mode,experience,skills,description,requirements,vacancies,posted_by) values(?,?,?,?,?,?,?,?,?,?,?,?,?)',(f['title'],f['company'],f['location'],f['min_salary'],f['max_salary'],f['job_type'],f['work_mode'],f['experience'],f['skills'],f['description'],f['requirements'],f['vacancies'],session['uid'])); c.commit(); c.close(); flash('Job published.'); return redirect(url_for('dashboard'))
 return render_template('post_job.html')
@app.route('/applicants/<int:job_id>')
@login_required
def applicants(job_id):
 c=db(); j=c.execute('select * from jobs where id=?',(job_id,)).fetchone(); rows=c.execute('select a.*,u.name,u.email,u.phone,u.location,u.skills,u.experience,u.education,u.resume from applications a join users u on u.id=a.user_id where a.job_id=?',(job_id,)).fetchall(); c.close(); return render_template('applicants.html',job=j,apps=rows)
@app.post('/application/<int:id>/status')
@login_required
def status(id):
 st=request.form['status']; c=db(); a=c.execute('select * from applications where id=?',(id,)).fetchone(); c.execute('update applications set status=? where id=?',(st,id)); c.execute('insert into notifications(user_id,message) values(?,?)',(a['user_id'],'Your application status was updated to '+st)); c.commit(); c.close(); return redirect(request.referrer)
@app.post('/job/<int:id>/toggle')
@login_required
def toggle_job(id):
 c=db(); j=c.execute('select status from jobs where id=?',(id,)).fetchone(); c.execute('update jobs set status=? where id=?',('Closed' if j['status']=='Active' else 'Active',id)); c.commit(); c.close(); return redirect(url_for('dashboard'))
if __name__=='__main__': init_db(); app.run(debug=True)
