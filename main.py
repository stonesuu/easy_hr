#!/bin/env python2.7
#coding=utf-8
import datetime
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

@app.route('/common/getC',methods=['GET','POST'])
def com_getC():
	if request.method == 'GET':
		sql = 'SELECT NAME FROM COMPANY'
		res = getjson(sql)
		return res
	else:
		sql = 'SELECT NAME FROM COMPANY WHERE ID_C=%s' %(session['group'])
		res = conn.execute(sql)
		return res[0][0]

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
	sql = 'SELECT ID_I,NAME,SEX,AGE,TEL,ADDRESS,SALARY FROM stuff WHERE COMPANY=%s ORDER BY ID_I' % (company,)
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

@app.route('/common/salary/getime')
def com_salary_gt():
	sql = 'SELECT TIMELOK FROM company_lock WHERE ID_C=%s' %(session['group'],)
	res = conn.execute(sql)
	#print type(res[0][0])
	date = res[0][0].strftime('%Y-%m-%d')
	return date
	
@app.route('/common/salary',methods=['GET','POST'])
def com_salary():
	if request.method == 'POST':
		sql = "UPDATE company_lock SET LOK=0 WHERE ID_C=%s" % (session['group']) #只要点击过一次产生工资表，那么时间就被冻结了。重新修改的时间还是上次产生工资表的时间。timelok的值只有第一次被修改后就不变了
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
	session['salary_dict'] = {}#创建一个以ID_I为key，其余为value的session['salary_dict']
	# sql = "SELECT ID_I,NAME,SALARY,ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,EXAM FROM stuff f JOIN set_i s ON f.ID_I = s.ID"
	#创建了一个视图，但是这里要注意视图需要带上company
	sql = "SELECT ID_I,NAME,SALARY,ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,EXAM FROM stuff_set_i WHERE COMPANY=%s ORDER BY ID_I" % (session['group'])
	tmp = conn.execute(sql)
	for item in tmp:
 		session['salary_dict'][item[0]] = {'salary':item[2],'another':item[3],'drawback':item[4],'benefit01':item[5],'benefit02':item[6],'benefit03':item[7],'benefit04':item[8],'exam':item[9]}
 	#print session['salary_dict']
	res = json.dumps(tmp)
	return res

@app.route('/common/salary/set',methods=['POST'])
def com_salary_set():#每一次修改，都会同步修改数据库和session['salary_dict']的值
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

@app.route('/common/salary/cal',methods=['POST'])#LOK用于点击生成工资表之后锁定这个状态，TIMELOK用于锁定点击时的日期
def com_salary_cal():
	date = request.form.get('date')
	check = 0
	lock = "UPDATE company_lock SET LOK=1,TIMELOK='%s' WHERE ID_C=%s" %(date,session['group'])
	res_lock = conn.execute(lock)
	if(res_lock):
		return 'error'
	before = 'start transaction'
	res_begin = conn.execute(before)
	if not(res_begin): #修改的按钮会删除掉该公司中存储的所有数据，而不再去匹配时间。
		delete = 'DELETE FROM salary_temp WHERE ID_I IN (SELECT ID_I FROM stuff WHERE COMPANY=%s)' % (date,session['group'])
		conn.execute(delete)
		for key,val in session['salary_dict'].items():#这个session['salary_dict']就是用来计算工资的。
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

@app.route('/common/salary/get_cal')
def com_salary_gc():
	sql = 'SELECT ID_I,NAME,BASE_I,ENDOWMENT_I,UNEMPLOYMENT_I,MEDICAL_I,INJURY_I,HOUSING_I,INDIVIDUAL,ANOTHER,\
	DRAWBACK,NENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,ACTUAL FROM stuff_salary_temp WHERE COMPANY=%s ORDER BY ID_I' %(session['group'])
	res = getjson(sql)
	return res

@app.route('/common/salary/submit',methods=['POST'])
def com_salary_sub():
	check = 0
	sql_start = "start transaction"
	sql_sub = "INSERT INTO salary SELECT * FROM salary_temp WHERE ID_I IN (SELECT ID_I FROM stuff WHERE COMPANY=%s)" % (session['group'])
	sql_clean_temp = "DELETE FROM salary_temp WHERE ID_I IN (SELECT ID_I FROM stuff WHERE COMPANY=%s)" %(session['group'])
	sql_clean_set = "UPDATE set_i SET ANOTHER=0,DRAWBACK=0,BENEFIT01=0,BENEFIT02=0,BENEFIT03=0,BENEFIT04=0,EXAM=0 WHERE ID IN (SELECT ID_I FROM stuff WHERE COMPANY=%s)" % (session['group'])
	sql_clean_lok = "UPDATE company_lock SET LOK=0,TIMELOK='1971-01-01' WHERE ID_C=%s" % (session['group'])
	for sql in (sql_start,sql_sub,sql_clean_temp,sql_clean_set,sql_clean_lok):
		res = conn.execute(sql)
		if res:
			check =1
			break
	if check == 1:
		conn.execute('rollback')
		return 'error'
	else:
		conn.execute('commit')
		return 'ok'

@app.route('/common/summary')
def com_sum():
	return render_template('salary_sum.html')

@app.route('/common/summary/getable',methods=['GET','POST'])
def com_sum_getable():
	if request.method == 'GET':
		sql = "SELECT ID_I,NAME,date_format(TIME,'%Y-%m-%d'),BASE_I,ENDOWMENT_C,ENDOWMENT_I,"
		sql += "UNEMPLOYMENT_C,UNEMPLOYMENT_I,MEDICAL_C,MEDICAL_I,INJURY_C,INJURY_I,HOUSING_C,HOUSING_I,INDIVIDUAL,"
		sql += "ANOTHER,DRAWBACK,BENEFIT01,BENEFIT02,BENEFIT03,BENEFIT04,ACTUAL FROM stuff_salary WHERE COMPANY=%s" %(session['group'])
		res = getjson(sql)
		return res

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)