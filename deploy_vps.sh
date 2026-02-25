#!/bin/bash
# Script deploy PhuHuong Digital lên VPS
set -e

echo "=== [1/6] Cap nhat he thong ==="
apt-get update -qq

echo "=== [2/6] Kiem tra / cai Nginx ==="
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    echo "Nginx da cai xong"
else
    echo "Nginx da co san: $(nginx -v 2>&1)"
fi

echo "=== [3/6] Kiem tra / cai Git ==="
if ! command -v git &> /dev/null; then
    apt-get install -y git
fi

echo "=== [4/6] Clone / cap nhat repo ==="
WEBDIR="/var/www/puhuong"
if [ -d "$WEBDIR/.git" ]; then
    echo "Repo da ton tai, cap nhat..."
    cd "$WEBDIR"
    git pull origin master
else
    echo "Clone repo moi..."
    rm -rf "$WEBDIR"
    git clone https://github.com/impactslowforest/PuHuong-Digital.git "$WEBDIR"
fi

echo "=== [5/6] Cau hinh Nginx ==="
cat > /etc/nginx/sites-available/puhuong << 'EOF'
# Port 80
server {
    listen 80;
    server_name puhuong.lvtcenter.it.com;
    root /var/www/puhuong;
    index index.html;
    charset utf-8;
    location / {
        try_files $uri $uri/ =404;
    }
}

# Port 8096
server {
    listen 8096;
    server_name puhuong.lvtcenter.it.com;
    root /var/www/puhuong;
    index index.html;
    charset utf-8;
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/puhuong /etc/nginx/sites-enabled/puhuong

# Xoa default site neu con
rm -f /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Reload nginx
systemctl reload nginx || systemctl restart nginx

echo "=== [6/6] Mo firewall port 8096 ==="
if command -v ufw &> /dev/null; then
    ufw allow 8096/tcp 2>/dev/null || true
    ufw allow 80/tcp 2>/dev/null || true
    echo "UFW: da mo port 8096 va 80"
fi

if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=8096/tcp 2>/dev/null || true
    firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
    echo "firewalld: da mo port 8096 va 80"
fi

echo ""
echo "======================================"
echo "DEPLOY HOAN THANH!"
echo "  http://puhuong.lvtcenter.it.com"
echo "  http://puhuong.lvtcenter.it.com:8096"
echo "======================================"
