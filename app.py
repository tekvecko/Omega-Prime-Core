from flask import Flask, render_template_string, jsonify, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os, sys, time, random, subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RECOVERY-KEY-V6'
login_manager = LoginManager(app); login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name): self.id = id; self.name = name
users = {1: User(1, 'Architekt')}

@login_manager.user_loader
def load_user(user_id): return users.get(int(user_id))

@app.route('/')
@login_required
def dashboard(): return "SYSTEM RECOVERED via OMEGA"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('p') == 'password':
            login_user(users[1]); return redirect(url_for('dashboard'))
    return "<form method='POST'><input type='password' name='p'><button>LOGIN</button></form>"

if __name__ == "__main__": app.run(host='0.0.0.0', port=8080)
