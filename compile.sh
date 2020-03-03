# Installing Bulma is not required, since it will load the css files from the internet
# wget https://github.com/jgthms/bulma/releases/download/0.8.0/bulma-0.8.0.zip
# unzip bulma-0.8.0.zip

sudo apt-get install python3-venv psycopg2 libpq-dev python-dev
python3 -m venv venv # Create a virtual environment

# Activate the virtual environment
source venv/bin/activate # Warning: this is different on windows: venv\Scripts\activate (but please Tim, just use Ubuntu)

# install flask in the virtual environment
pip install flask
pip install flask-wtf
pip install python-dotenv
pip install flask-sqlalchemy
pip install flask-migrate
pip install psycopg2
pip install flask-login

echo "FLASK_APP=placeholder.py" > .flaskenv

flask db init
flask db migrate -m "users table"
flask db upgrade

