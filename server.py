from flask import Flask
from flask import request


app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    args = request.args.get('name', '').lower()
    print(args)
    if args == 'dad':
        return "dady is NOT an asshole!"
    else:
        return "youyou IS an ASSHOLE!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的验证
        if username == 'shayou' and password == '123456':
            return f'Login successful! Welcome {username}'
        else:
            return 'Invalid credentials!'
    
    # GET 请求时显示登录表单
    html_form = '''
    <h1>Login Form</h1>
    <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br><br>
        
        <label>Password:</label><br>
        <input type="password" name="password" required><br><br>
        
        <input type="submit" value="Login">
    </form>
    '''
    return html_form

@app.route("/hi/")
def hi():
    return '''
        <html>
            <p>Daddy is not an asshole!</p>
        </html>
    '''

@app.route("/test")
def test():
    print(request.method)
    print(request.path)
    print(request.headers)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
