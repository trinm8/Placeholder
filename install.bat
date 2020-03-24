::# Installing Bulma is not required, since it will load the css files from the internet
::# wget https://github.com/jgthms/bulma/releases/download/0.8.0/bulma-0.8.0.zip
::# unzip bulma-0.8.0.zip

::#sudo apt-get install python3-venv libpq-dev python-dev
::# Create a virtual environment
python -m venv venv

::# Activate the virtual environment
call venv\Scripts\activate.bat

::# install flask in the virtual environment
pip3 install flask
pip3 install flask-wtf
pip3 install python-dotenv
pip3 install flask-sqlalchemy
pip3 install flask-migrate
pip3 install psycopg2
pip3 install flask-login
pip3 install python-dotenv
pip3 install SQLAlchemy
pip3 install flask-mail
pip3 install pyjwt
pip3 install geopy

echo "FLASK_APP=placeholder.py" > .flaskenv

flask db init
flask db migrate
flask db upgrade

pause