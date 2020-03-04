sudo apt-get -y update
sudo apt-get -y install python3 python3-venv python3-dev
sudo apt-get -y install postgresql postgresql-contrib postfix supervisor nginx git
#update-rc.d postgresql enable
#service postgresql start
# Manually create a postgres db named "dbtutor" with login and password postgres