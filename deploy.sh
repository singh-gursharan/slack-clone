#! /bin/bash
sudo apt install redis
sudo apt install nginx
sudo service nginx restart
python3 -m venv venv
source venv/bin/activate
sudo apt install pip3
pip3 install flask
pip3 install -r requirement.txt
flask db migrate
pip3 install SQLAlchemy==1.3.5
flask db init
sudo apt-get install libpq-dev
flask db migrate
pip3 install psycopg2
flask db migrate
flask db upgrade
sudo apt install ufw
sudo ufw app list
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'OpenSSH'
sudo ufw status
sudo ufw enable
pip3 install gunicorn
sudo bash -c 'cat > /etc/nginx/conf.d/virtual.conf <<EOF
server {
    listen       80;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF'
sudo service nginx restart
sudo bash -c 'cat > /etc/systemd/system/slack_guni_test.service <<EOF
[Unit]
Description=slack_clone application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/slack-clone-project-gursharan
Environment="PATH=/home/ubuntu/slack-clone-project-gursharan/venv/bin"
ExecStart=/home/ubuntu/slack-clone-project-gursharan/venv/bin/gunicorn -b localhost:8000 -w 4 slack_clone:slack_app_instance
Restart=always

[Install]
WantedBy=multi-user.target
EOF'
sudo bash -c 'cat > /etc/systemd/system/slack_celery_test.service <<EOF
[Unit]
Description=slack_clone application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/slack-clone-project-gursharan
Environment="PATH=/home/ubuntu/slack-clone-project-gursharan/venv/bin"
ExecStart=/home/ubuntu/slack-clone-project-gursharan/venv/bin/celery -A app.celery worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF'
sudo systemctl daemon-reload
sudo systemctl start slack_guni_test
sudo systemctl start slack_celery_test