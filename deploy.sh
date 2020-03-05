# src: https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a

sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
sudo pip3 install virtualenv

python3 -m venv venv
virtualenv venv
source venv/bin/activate

pip install gunicorn flask

nano wsgi.py

# from app import app
# if __name__ == "__main__":
#   app.run()

gunicorn --bind 0.0.0.0:5000 wsgi:app

deactivate

sudo nano /ets/systemd/system/app.service

#[Unit]
##  specifies metadata and dependencies
#Description=Gunicorn instance to serve myproject
#After=network.target
## tells the init system to only start this after the networking target has been reached
## We will give our regular user account ownership of the process since it owns all of the relevant files
#[Service]
## Service specify the user and group under which our process will run.
#User=yourusername
## give group ownership to the www-data group so that Nginx can communicate easily with the Gunicorn processes.
#Group=www-data
## We'll then map out the working directory and set the PATH environmental variable so that the init system knows where our the executables for the process are located (within our virtual environment).
#WorkingDirectory=/home/tasnuva/work/deployment/src
#Environment="PATH=/home/tasnuva/work/deployment/src/myprojectvenv/bin"
## We'll then specify the commanded to start the service
#ExecStart=/home/tasnuva/work/deployment/src/myprojectvenv/bin/gunicorn --workers 3 --bind unix:app.sock -m 007 wsgi:app
## This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running:
#[Install]
#WantedBy=multi-user.target

sudo systemctl start app
sudo systemctl enable app

sudo nano /etc/nginx/sites-available/app

server {
    listen 80;
    server_name server_domain_or_IP;
}
location / {
  include proxy_params;
  proxy_pass http://unix:/app/PlaceHolder/app.sock;
    }
}

sudo ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled

sudo systemctl restart nginx

sudo ufw allow 'Nginx Full'