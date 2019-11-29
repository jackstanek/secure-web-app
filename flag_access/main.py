import cgi
import os
from pathlib import Path
import sqlite3

import cherrypy

GO_BACK = '<a href="/">go back.</a>'

LOGIN_FORM = '''\
<form action="login" method="post">
<p>Log in to your account:</p>
<div>
    <label for="username">Username:</label>
    <input name="username" id="username">
</div>
<div>
    <label for="password">Password:</label>
    <input type="password" name="password" id="password">
</div>
<button>Login</button>
</form>'''

CREATE_FORM = '''\
<form action="create" method="post">
<p>Create a new account:</p>
<div>
    <label for="username">Username:</label>
    <input name="username" id="username">
</div>
<div>
    <label for="password">Password:</label>
    <input type="password" name="password" id="password">
</div>
<button>Create Account</button>
</form>
'''

staticpath = os.path.join(Path(os.path.abspath(__name__)).parent, 'static')
print(staticpath)


def canonicalize_username(username):
    return cgi.escape(username.strip())


def replace_template(template, **kwargs):
    if kwargs:
        k, v = kwargs.popitem()
        replaced = template.replace('{' + k + '}', str(v))
        return replace_template(replaced, **kwargs)
    else:
        return template


class App:
    def __init__(self):
        self.users = {'admin': 'admin'} # wtf is "SQL"?

    def auth_user(self, username, password):
        su = canonicalize_username(username)
        if username is None or password is None \
           or su not in self.users \
           or self.users.get(su) != password:
            return None
        return su

    @cherrypy.expose
    def index(self):
        with open(os.path.join(staticpath, 'index.html')) as index_page:
            content = index_page.read()

            cookie = cherrypy.request.cookie
            if cookie.get('username'):
                username, password = (cookie.get('username').value,
                                      cookie.get('password').value)
            else:
                username = password = ''
            user = self.auth_user(username, password)

            if user is None:
                message = '''\
                You're not logged in! You need to be logged in through the
                secure login system to view the flag.
                '''
            elif user != 'admin':
                message = f'''\
                Logged in as {user}.
                Looks like you aren't authorized to access the flag.
                '''
            else:
                message = '''\
                The flag is <tt>flag{i_love_web_dev}</tt>.
                '''

            return replace_template(content,
                                    flag_contents=message,
                                    login=LOGIN_FORM if user is None else '',
                                    create=CREATE_FORM if user is None else '',
                                    logout='<a href="/logout">log out</a>' if user is not None else '')

    @cherrypy.expose
    def login(self, username='', password=''):
        if username and password:
            su = canonicalize_username(username)
            auth_user = self.auth_user(su, password)
            if auth_user == password == 'admin':
                return ('easiest trick in the book, eh? not so fast. '
                        'you are not permitted to log into the admin '
                        f'interface through a web browser. {GO_BACK}')

            elif auth_user is not None:
                cookie = cherrypy.response.cookie
                cookie['username'] = auth_user
                cookie['username']['path'] = '/'
                cookie['password'] = password
                cookie['password']['path'] = '/'
                raise cherrypy.HTTPRedirect('/')

            else:
                return f'Invalid username/password. {GO_BACK}'
        else:
            return f'Empty username/password. {GO_BACK}'

    @cherrypy.expose
    def create(self, username='', password=''):
        if username and password:
            if username not in self.users:
                su = canonicalize_username(username)
                self.users[su] = password
                return f'Created account {su}. {GO_BACK}'

            else:
                return f'User already exists. {GO_BACK}'
        else:
            return f'Can\'t create empty username/password. {GO_BACK}'

    @cherrypy.expose
    def logout(self):
        cherrypy.response.cookie['username'] = ''
        cherrypy.response.cookie['username']['expires'] = 0
        cherrypy.response.cookie['password'] = ''
        cherrypy.response.cookie['password']['expires'] = 0
        raise cherrypy.HTTPRedirect('/')

def main():
    conf = {
        '/': {
            'tools.staticdir.root': staticpath
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './'
        }
    }

    app = App()
    cherrypy.quickstart(app, '/', conf)

if __name__ == '__main__':
    main()
