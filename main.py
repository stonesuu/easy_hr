#!/bin/env python2.7
#coding=utf-8
from flask import Flask,session,request,render_template,redirect,json
import dbutil,time
try:
	conn = dbutil.DB('hr_test','10.99.160.36','root','root')
	conn.connect()
except Exception as e:
	print e
	try:
		conn = dbutil.DB('hr_test','192.168.199.12','root','root')
		conn.connect()
	except Exception as e:
		print e
	else:
		print 'connect success'
else:
	print 'connect success'
SN_dict = {}
date_list = []
app = Flask(__name__)
app.secret_key = 'sadfagraegrgaregareghhqare'

def getjson(sql):
	try:
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
	except Exception as e:
		return 'error'
	else:
		return res

def cal(date,base_c,key,val):
	string = ''
	id_i = int(key)
	#val={'salary','another','drawback','benefit01','benefit02','benefit03','benefit04','exam'}
	base_i = int(val['salary'])*(1-int(val[u'exam'])/100)
	endow_i = base_i*0.05
	endow_c = endow_i*2
	unemploy_i = base_i*0.02
	unemploy_c = unemploy_i*2
	medical_i = base_i*0.01
	medical_c = medical_i*2
	injury_i = base_i*0.01
	injury_c = injury_i*2
	house_i = base_i*0.05
	house_c = house_i*2
	individual = base_i*0.05
	another = int(val[u'another'])
	drawback = int(val[u'drawback'])
	bene01 = int(val[u'benefit01'])
	bene02 = int(val[u'benefit02'])
	bene03 = int(val[u'benefit03'])
	bene04 = int(val[u'benefit04'])
	actual = base_i-endow_i-unemploy_i-medical_i-injury_i-house_i-individual-another+drawback+bene01+bene02+bene03+bene04
	profit = base_c-base_i-endow_c-unemploy_c-medical_c-injury_c-house_c
	string = "INSERT INTO salary_temp(ID_I,TIME,BASE_C,BASE_I,ENDOWMENT_C,ENDOWMENT_I,UNEMPLOYMENT_C,UNEMPLOYMENT_I,\
		MEDICAL_C,MEDICAL_I,INJURY_C,INJURY_I,HOUSING_C,HOUSING_I,\
		INDIVIDUAL,ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,\
		ACTUAL,PROFIT) VALUES(%s,'%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" \
		%(id_i,date,base_c,base_i,endow_c,endow_i,unemploy_c,unemploy_i,medical_c,medical_i,injury_c,injury_i,\
		house_c,house_i,individual,another,drawback,bene01,bene02,bene03,bene04,actual,profit)
	return string
	

@app.route('/')
def login_r():
	return redirect('/signin')

@app.route('/signin',methods=['GET','POST'])
def signin():
	if request.method == 'GET':
		return render_template('signin.html')
	elif request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		sql = "SELECT COMPANY FROM user WHERE (NAME='%s' AND PASSWORD='%s')" % (username,password)
		res = conn.execute(sql)
		if len(res) == 0:
			return render_template('signin.html',message="error")
		else:
			session['user'] = username
			session['group'] = res[0][0]
			if session['group'] == 0:
				return redirect('/super/user')
			else:
				return redirect('/common/stuff')

@app.route('/logout')
def logout():
	session.pop('user')
	session.pop('group')
	return redirect('/signin')

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/common/getC')
def com_getC():
	sql = 'SELECT NAME FROM COMPANY'
	res = getjson(sql)
	return res

@app.route('/common/signup',methods=['post'])
def com_signup():
	username = request.form.get('username')
	password = request.form.get('password')
	company = request.form.get('company')
	sql = "INSERT INTO user(NAME,PASSWORD,COMPANY) SELECT '%s','%s',ID_C FROM company WHERE NAME='%s'" %(username,password,company)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'


@app.route('/common/stuff')
def com_stuff():
	if 'user' in session:
		return render_template('stuff.html')
	else:
		return redirect('/signin')

@app.route('/common/stuff/getmessage')
def com_stuff_getm():
	print session['user']
	return json.dumps((session['user'],session['group']))

@app.route('/common/stuff/add',methods=['POST'])
def com_stuff_add():
	name = request.form.get('name')
	age = int(request.form.get('age'))
	sex = request.form.get('sex')
	tele = int(request.form.get('tele'))
	address = request.form.get('address')
	company = int(request.form.get('company'))
	salary = int(request.form.get('salary'))
	sql = "INSERT INTO stuff(NAME,SEX,AGE,COMPANY,TEL,ADDRESS,SALARY) VALUES ('%s','%s',%s,%s,'%s','%s',%s)" %(name,sex,age,company,tele,address,salary)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'

@app.route('/common/stuff/get')
def com_stuff_get():
	company = session['group']
	sql = 'SELECT ID_I,NAME,SEX,AGE,TEL,ADDRESS,SALARY FROM stuff WHERE COMPANY=%s' % (company,)
	res = getjson(sql)
	return res

@app.route('/common/stuff/del',methods=['POST'])
def com_stuff_del():
	ID_I = request.form.get('id')
	sql = "DELETE FROM stuff WHERE ID_I=%s" % (ID_I)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'

@app.route('/common/stuff/update',methods=['POST'])
def com_stuff_upd():
	ID_I = request.form.get('id')
	name = request.form.get('name')
	sex = request.form.get('sex')
	age = request.form.get('age')
	tele = request.form.get('tele')
	address = request.form.get('address')
	salary = request.form.get('salary')
	sql = "UPDATE stuff SET NAME='%s',SEX='%s',AGE=%s,TEL='%s',ADDRESS='%s',SALARY=%s WHERE ID_I=%s" %(name,sex,age,tele,address,salary,ID_I)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'
	
@app.route('/common/salary',methods=['GET','POST'])
def com_salary():
	if request.method == 'POST':
		sql = 'UPDATE company_lock SET LOK=0 WHERE ID_C=%s' % (session['group'])
		res = conn.execute(sql)
		if not res:
			return 'ok'
		else:
			return 'error'
	else:
		if 'user' in session:
			sql = 'SELECT LOK FROM company_lock WHERE ID_C=%s' %(session['group'])
			res = conn.execute(sql)
			if res[0][0] == 0:
				return render_template('salary.html')
			else:
				return render_template('salary_cal.html')
		else:
			return redirect('/signin')

@app.route('/common/salary/getbase')
def com_salary_gb():
	session['salary_dict'] = {}
	# sql = "SELECT ID_I,NAME,SALARY,ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,EXAM FROM stuff f JOIN set_i s ON f.ID_I = s.ID"
	#创建了一个视图，但是这里要注意视图需要带上company
	sql = "SELECT ID_I,NAME,SALARY,ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,EXAM FROM stuff_set_i WHERE COMPANY=%s" % (session['group'])
	tmp = conn.execute(sql)
	for item in tmp:
 		session['salary_dict'][item[0]] = {'salary':item[2],'another':item[3],'drawback':item[4],'benefit01':item[5],'benefit02':item[6],'benefit03':item[7],'benefit04':item[8],'exam':item[9]}
 	#print session['salary_dict']
	res = json.dumps(tmp)
	return res

@app.route('/common/salary/set',methods=['POST'])
def com_salary_set():
	ID_I = request.form.get('id')
	col = request.form.get('col')
	val = request.form.get('val')
	#print session['salary_dict'],session会将内容全部转换成unicode
	session['salary_dict'][ID_I][col]=val
	#print session['salary_dict']
	sql = "UPDATE set_i SET %s=%s WHERE ID=%s" % (col,val,ID_I)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'

@app.route('/common/salary/cal',methods=['POST'])
def com_salary_cal():
	date = request.form.get('date')
	check = 0
	lock = "UPDATE company_lock SET LOK=1 WHERE ID_C=%s" %(session['group'])
	res_lock = conn.execute(lock)
	if(res_lock):
		return 'error'
	before = 'start transaction'
	res_begin = conn.execute(before)
	if not(res_begin):
		delete = 'DELETE FROM salary_temp WHERE TIME="%s" AND ID_I IN (SELECT ID_I FROM stuff WHERE COMPANY=%s)' % (date,session['group'])
		conn.execute(delete)
		for key,val in session['salary_dict'].items():
			print cal(date,839600,key,val)
			res = conn.execute(cal(date,839600,key,val))
			if(res):
				check=1
				break
	  	if check == 1:
	  		conn.execute('rollback')
	  		return 'error'
	  	else:
	  		conn.execute('commit')
	  		return 'ok'
	else:
		return 'cannot start transaction'

@app.route('/connom/salary/get_cal')
def com_salary_gc():
	sql = 'SELECT ID_I,NAME,BASE_I,ENDOWMENT_I,UNEMPLOYMENT_I,MEDICAL_I,INJURY_I,HOUSING_I,INDIVIDUAL,ANOTHER,\
	DRAWBACK,NENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,ACTUAL FROM stuff_salary_temp'
	res = getjson(sql)
	return res
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)