#!/bin/bash
set -e

echo "Starting WeChat Bot..."

cd /app

echo "Bot started successfully"
python -m bot.src.main
