#!/bin/bash

# جایگزینی UUID و WSPATH در کانفیگ Xray
sed -i "s/REPLACE_UUID/$XRAY_UUID/g" /app/xray_config.json
sed -i "s/REPLACE_WSPATH/$WS_PATH/g" /app/xray_config.json

echo "🚀 Starting Xray core..."
/usr/local/bin/xray -config /app/xray_config.json &

echo "🌐 Starting Flask panel..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app