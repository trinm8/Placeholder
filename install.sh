# Installing Bulma is not required, since it will load the css files from the internet
# wget https://github.com/jgthms/bulma/releases/download/0.8.0/bulma-0.8.0.zip
# unzip bulma-0.8.0.zip

sudo apt-get install python3-venv libpq-dev python-dev
python3 -m venv venv # Create a virtual environment

# Activate the virtual environment
source venv/bin/activate # Warning: this is different on windows: venv\Scripts\activate (but please Tim, just use Ubuntu)

# install flask in the virtual environment
#pip3 install flask
#pip3 install flask-wtf
#pip3 install python-dotenv
#pip3 install flask-sqlalchemy
#pip3 install flask-migrate
#pip3 install psycopg2
#pip3 install flask-login
#pip3 install python-dotenv
#pip3 install SQLAlchemy
#pip3 install flask-mail
#pip3 install pyjwt
#pip3 install geopy
#pip3 install httpie
#pip3 install flask-httpauth
#pip3 install flask-testing
#pip3 install email-validator
#pip3 install flask-babel
pip3 install -r requirements.txt # maak je adhv pip3 freeze > requirements.txt

# For creating a translation template file:
# pybabel extract -F babel.cfg -k _l -o messages.pot .
# For creating a dutch instance of the template:
# pybabel init -i messages.pot -d app/translations -l nl
# Compiling the edited .po files int .mo files
pybabel compile -d app/translations

# Two commands for updating translation files
# pybabel extract -F babel.cfg -k _l -o messages.pot .
# pybabel update -i messages.pot -d app/translations

echo "FLASK_APP=placeholder.py" > .flaskenv

flask db init
flask db migrate
flask db upgrade

