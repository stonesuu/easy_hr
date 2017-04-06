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



if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)