#!/bin/bash

mkdir -p /app/data

echo "🌐 Starting Flask panel..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app