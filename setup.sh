#!/usr/bin/env bash

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DJANGO_DIR="$REPO_DIR/mysite"
VENV_DIR="$REPO_DIR/venv"
SERVICE_NAME="resourcehub"
APP_MODULE="mysite.wsgi:application"
PORT=8000
BRANCH="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"

echo "====================================="
echo "Starting Django server setup/update"
echo "Repo directory:   $REPO_DIR"
echo "Django directory: $DJANGO_DIR"
echo "Branch:           $BRANCH"
echo "====================================="

if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Error: setup.sh must be run from inside the git repository."
    exit 1
fi

if [ ! -f "$DJANGO_DIR/manage.py" ]; then
    echo "Error: Could not find manage.py at $DJANGO_DIR/manage.py"
    exit 1
fi

echo "Updating package list..."
sudo apt update

echo "Installing required system packages..."
sudo apt install -y python3 python3-venv python3-pip git nginx

echo "Updating repository from GitHub..."
git -C "$REPO_DIR" fetch origin
git -C "$REPO_DIR" reset --hard "origin/$BRANCH"

echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

if [ -f "$REPO_DIR/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r "$REPO_DIR/requirements.txt"
else
    echo "No requirements.txt found, skipping dependency install."
fi

echo "Applying Django migrations..."
cd "$DJANGO_DIR"
python manage.py migrate

SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Writing systemd service file..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=$SERVICE_NAME Gunicorn Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$DJANGO_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:$PORT $APP_MODULE
Restart=always
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF

echo "Writing nginx site config..."
NGINX_SITE="/etc/nginx/sites-available/$SERVICE_NAME"
sudo tee "$NGINX_SITE" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf "$NGINX_SITE" "/etc/nginx/sites-enabled/$SERVICE_NAME"
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing nginx config..."
sudo nginx -t

echo "Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo "Stopping stray gunicorn processes..."
pkill -f "$VENV_DIR/bin/gunicorn" || true
pkill -f "gunicorn.*127.0.0.1:$PORT" || true

echo "Restarting services..."
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl restart nginx

echo "====================================="
echo "resourcehub service status:"
sudo systemctl --no-pager status "$SERVICE_NAME" || true
echo "====================================="
echo "nginx status:"
sudo systemctl --no-pager status nginx || true
echo "====================================="
echo "Active gunicorn processes:"
ps aux | grep gunicorn | grep -v grep || true
echo "====================================="
echo "Done."
