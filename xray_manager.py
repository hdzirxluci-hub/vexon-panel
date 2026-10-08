import json
import os
import subprocess
import signal

CONFIG_PATH = '/app/xray_config.json'
XRAY_BIN = '/usr/local/bin/xray'
xray_process = None


def build_config(uuid, ws_path):
    """ساخت فایل کانفیگ Xray"""
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "listen": "0.0.0.0",
            "port": int(os.environ.get('PORT', 8080)),
            "protocol": "vless",
            "settings": {
                "clients": [{"id": uuid}],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "wsSettings": {"path": f"/{ws_path}"}
            }
        }],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def start_xray(uuid, ws_path):
    """اجرای Xray (پس‌زمینه)"""
    global xray_process
    build_config(uuid, ws_path)

    # اگه Xray از قبل در حال اجرا بود، ببند
    stop_xray()

    if os.path.exists(XRAY_BIN):
        xray_process = subprocess.Popen(
            [XRAY_BIN, '-config', CONFIG_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    return False


def stop_xray():
    global xray_process
    if xray_process:
        try:
            xray_process.terminate()
            xray_process.wait(timeout=5)
        except Exception:
            try:
                xray_process.kill()
            except Exception:
                pass
        xray_process = None


def restart_xray(uuid, ws_path):
    stop_xray()
    return start_xray(uuid, ws_path)