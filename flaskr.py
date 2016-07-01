# coding=utf-8

'''flaskr项目'''
import os
import sqlite3
from flask import Flask, request, session, g, redirect, \
     url_for, flash, abort,render_template

app = Flask(__name__)
app.config.from_object(__name__)

# 配置文件
app.config.update(dict(
    DATABASE = os.path.join(app.root_path,'flaskr.db'),
    SECRET_KEY = 'development_key',
    USERNAME = 'admin',
    PASSWORD = 'admin'
))
app.config.from_envvar('FLASKR_SETTINGS',silent=True)

# 数据库操作部分
# 1.建立数据库链接
def connect_db():
    '''数据库链接方法,返回sqlite3.Row,返回值可以被当作字典进行处理'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

# 2.获取数据库链接对象,存储在g对象里
def get_db():
    '''打开一个数据库链接,并且存放到应用程序上下文里
    如果没有就创建一个新的链接
    '''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# 3.关闭数据库链接
@app.teardown_appcontext  
def close_db(error):
    '''每次应用环境被销毁时调用此方法,正常结束请求error为None,否则为异常信息'''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# 4.初始化数据库
def init_db():
    '''初始化数据库,可以供shell使用'''
    # 应用环境在每次请求传入时创建
    # 如果在shell中执行,是没有应用环境,所以手动创建一个
    # 在语句的结束地方,释放关联并执行销毁函数
    with app.app_context():  
        db = get_db()
        # open_resource方法可以打开应用提供的资源
        # 这里就是来读取应用目录下的sql脚本并执行
        with app.open_resource('schemal.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def init_db_new():
    '''初始化数据看的最新方式'''
    db = get_db()
    with db.open_resource('schemal.sql',mode='r') as f:
        db.cursor().execute(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db_new()
    print '正在初始化数据库...'

# 每次请求前自动获取数据库对象
@app.before_request
def before_request():
    g.sqlite_db = get_db()


# 视图函数        
@app.route('/')
def index():
    cursor = g.sqlite_db.execute('select eid,title,text from entries order by eid desc')
    entries = cursor.fetchall()
    return render_template('show_entries.html',entries=entries)

    
@app.route('/add',methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.sqlite_db.execute('insert into entries(title,text) values(?,?)',[request.form['title'],request.form['text']])
    g.sqlite_db.commit()
    flash(u'添加新的内容成功')
    return redirect(url_for('index'))
 
 # 处理登陆方法   
@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'用户名错误'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'密码错误'
        else :
            session['logged_in'] = True
            flash(u'登陆成功')
            return redirect(url_for('index'))
    return render_template('login.html',error=error)

@app.route('/logout')
def logout():
        session.pop('logged_in',None)
        flash(u'登出成功')
        return redirect(url_for('index'))

   
if __name__ == '__main__':
    app.run(debug=True)