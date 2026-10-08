from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os
import secrets
import database as db

app = Flask(__name__)

# ساخت secret key خودکار و ذخیره در دیتابیس
db.init_db()
if not db.get_setting('secret_key'):
    db.set_setting('secret_key', secrets.token_hex(32))
app.secret_key = db.get_setting('secret_key')

# ساخت UUID و WS_PATH خودکار (اگر نبود)
db.init_default_settings()


# ===== دکوراتورها =====
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def setup_required(f):
    """اگه نصب نشده، به صفحه setup بفرست"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not db.is_setup_complete():
            return redirect(url_for('setup'))
        return f(*args, **kwargs)
    return decorated


# ===== روت‌ها =====
@app.route('/')
def index():
    if not db.is_setup_complete():
        return redirect(url_for('setup'))
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # اگه قبلاً نصب شده، نذار دوباره بره
    if db.is_setup_complete():
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if len(username) < 3:
            flash('نام کاربری حداقل ۳ کاراکتر باشد', 'error')
        elif len(password) < 6:
            flash('رمز عبور حداقل ۶ کاراکتر باشد', 'error')
        elif password != password2:
            flash('رمزهای عبور یکسان نیستند', 'error')
        else:
            db.create_admin(username, password)
            flash('نصب با موفقیت انجام شد! وارد شوید.', 'success')
            return redirect(url_for('login'))

    return render_template('setup.html')


@app.route('/login', methods=['GET', 'POST'])
@setup_required
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if db.verify_admin(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است', 'error')

    return render_template('login.html')


@app.route('/dashboard')
@setup_required
@login_required
def dashboard():
    uuid_val = db.get_setting('xray_uuid')
    ws_path = db.get_setting('ws_path')
    domain = request.host  # دامنه از خود درخواست گرفته میشه

    vless_link = (
        f"vless://{uuid_val}@{domain}:443"
        f"?encryption=none&security=tls&type=ws"
        f"&host={domain}&path=%2F{ws_path}"
        f"&sni={domain}#MyPanel"
    )

    return render_template(
        'dashboard.html',
        vless_link=vless_link,
        uuid=uuid_val,
        domain=domain,
        ws_path=ws_path
    )


@app.route('/regenerate', methods=['POST'])
@login_required
def regenerate():
    """ساخت UUID و مسیر جدید"""
    import uuid as uuid_lib
    db.set_setting('xray_uuid', str(uuid_lib.uuid4()))
    db.set_setting('ws_path', 'xray' + str(uuid_lib.uuid4())[:8])
    flash('کانفیگ جدید ساخته شد', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)