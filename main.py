#!/bin/env python2.7
#coding=utf-8
from flask import Flask,session,request,render_template,redirect,json
import dbutil,time
conn = dbutil.DB('hr_test','192.168.199.12','root','root')
conn.connect()
SN_dict = {}
date_list = []
app = Flask(__name__)

def getjson(sql):
	try:
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
	except Exception as e:
		return 'error'
	else:
		return res

@app.route('/')
def login():
	return render_template('signin.html')

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


@app.route('/stuff')
def stuff():
	return render_template('stuff.html')




if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)