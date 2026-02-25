#!/usr/bin/env python3
"""Deploy PhuHuong Digital to VPS via SSH using paramiko"""
import paramiko
import sys
import time

HOST = "36.50.26.99"
PORT = 22
USER = "root"
PASS = "Anhthu123#az1"

DEPLOY_SCRIPT = r"""
set -e
echo "=== [1/6] Cap nhat he thong ==="
apt-get update -qq 2>/dev/null || true

echo "=== [2/6] Kiem tra / cai Nginx ==="
if ! command -v nginx &> /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
    echo "Nginx da cai xong"
else
    echo "Nginx da co san"
fi

echo "=== [3/6] Kiem tra / cai Git ==="
if ! command -v git &> /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y git
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
cat > /etc/nginx/sites-available/puhuong << 'NGINXEOF'
server {
    listen 80;
    server_name puhuong.lvtcenter.it.com;
    root /var/www/puhuong;
    index index.html;
    charset utf-8;
    location / { try_files $uri $uri/ =404; }
}
server {
    listen 8096;
    server_name puhuong.lvtcenter.it.com;
    root /var/www/puhuong;
    index index.html;
    charset utf-8;
    location / { try_files $uri $uri/ =404; }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/puhuong /etc/nginx/sites-enabled/puhuong
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "Nginx config OK"

echo "=== [6/6] Mo firewall ==="
ufw allow 8096/tcp 2>/dev/null || true
ufw allow 80/tcp 2>/dev/null || true
iptables -I INPUT -p tcp --dport 8096 -j ACCEPT 2>/dev/null || true

echo ""
echo "======================================"
echo "DEPLOY HOAN THANH!"
echo "  http://puhuong.lvtcenter.it.com"
echo "  http://puhuong.lvtcenter.it.com:8096"
echo "======================================"
"""

def run_deploy():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, PORT, USER, PASS, timeout=30)
        print("Connected! Running deploy script...\n")
        
        stdin, stdout, stderr = client.exec_command(DEPLOY_SCRIPT, get_pty=True, timeout=180)
        
        # Stream output
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line, end='', flush=True)
        
        exit_code = stdout.channel.recv_exit_status()
        
        # Print any errors
        err = stderr.read().decode('utf-8', errors='replace')
        if err.strip():
            print("\nSTDERR:", err)
        
        print(f"\nExit code: {exit_code}")
        
        if exit_code == 0:
            print("\n✅ Deploy thanh cong!")
        else:
            print("\n❌ Co loi xay ra. Kiem tra output phia tren.")
            sys.exit(1)
            
    finally:
        client.close()

if __name__ == "__main__":
    run_deploy()
