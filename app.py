from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

# ===== تنظیمات ادمین (موقت - بعداً میبریم تو دیتابیس) =====
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')

# ===== کانفیگ تست Xray =====
TEST_UUID = os.environ.get('XRAY_UUID', str(uuid.uuid4()))
SERVER_DOMAIN = os.environ.get('SERVER_DOMAIN', 'localhost')
WS_PATH = os.environ.get('WS_PATH', 'xray')


# ===== دکوراتور برای صفحات نیازمند لاگین =====
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ===== صفحه اصلی =====
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ===== صفحه لاگین =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است', 'error')

    return render_template('login.html')


# ===== داشبورد =====
@app.route('/dashboard')
@login_required
def dashboard():
    # ساخت لینک VLESS تستی
    vless_link = (
        f"vless://{TEST_UUID}@{SERVER_DOMAIN}:443"
        f"?encryption=none&security=tls&type=ws"
        f"&host={SERVER_DOMAIN}&path=%2F{WS_PATH}"
        f"&sni={SERVER_DOMAIN}#TestConfig"
    )

    return render_template(
        'dashboard.html',
        vless_link=vless_link,
        uuid=TEST_UUID,
        domain=SERVER_DOMAIN,
        ws_path=WS_PATH
    )


# ===== خروج =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ===== سلامت سرور (برای Railway) =====
@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)