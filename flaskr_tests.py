# -*- coding: utf-8 -*- 

import os
import flaskr
import unittest
import tempfile


'''flaskr项目的测试类'''

class FlaskrTestCase(unittest.TestCase):

	# 默认方法,启动测试
	def setUp(self):
		self.db_fd,flaskr.app.config['DATABASE'] = tempfile.mkstemp()
		flaskr.app.config['TESTING'] = True
		self.app = flaskr.app.test_client() # 测试客户端
		flaskr.init_db()

	# 最后关掉测试库,删除临时文件
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(flaskr.app.config['DATABASE'])

	# 自定义测试方法

	# 测试数据库为空
	def test_empty_db(self):
		rv = self.app.get('/')
		assert '不可思议,居然没有发表任何动态~~' in rv.data

	# 测试登陆和登出
	def login(self,username,password):
		return self.app.post('/login',data=dict(
				username = username,
				password = password
			),follow_redirects=True)

	def logout(self):
		return self.app.get('/logout',follow_redirects=True)

	def test_login_logout(self):
		rv = self.login('admin','wrongpassword')
		assert '密码错误' in rv.data

		rv = self.login('wrongname','password')
		assert '用户名错误' in rv.data

		rv = self.login('admin','admin')
		assert '登陆成功' in rv.data
		
		rv = self.logout()
		assert '登出成功'


if __name__ == '__main__':
	unittest.main()
