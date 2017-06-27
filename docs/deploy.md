## Web part:
* `apt-get update && apt-get install python-pip mysql-server nginx git python-dev vim python-imaging python-mysqldb`
* `git clone https://github.com/8cbx/OnlineJudge_Web.git`
* setting nginx
* change mysql character set to utf-8
* `pip install -r requirements.txt`
* import environment variables
* init db(we need to install flask-celery first, the install flask-celery-helper. otherwise manage.py will not in good use), `python manage.py db init`, `python manage.py db migrate -m "first init"`, `python manage.py db upgrade`
* insert default role
* good to start! `python manage.py runserver` or use gunicorn, and run celery for email sending

## Judge part:

* install rabbitmq(in any way)
* import environment variables
* set API_URL in config.py
* `wget https://github.com/quark-zju/lrun/releases/download/v1.1.4/lrun_1.1.4_amd64.deb`
* `sudo apt-get install -y libseccomp2 build-essential clisp fpc gawk gccgo gcj-jdk ghc git golang lua5.2 mono-mcs ocaml openjdk-8-jdk perl php-cli python2.7 python3 racket rake ruby valac rlwrap`
* `sudo dpkg -i lrun_1.1.4_amd64.deb`
* `sudo gpasswd -a $USER lrun`
* `wget https://deb.nodesource.com/node/pool/main/n/nodejs/nodejs_0.10.46-1nodesource1~xenial1_amd64.deb`
* `sudo dpkg -i nodejs_0.10.46-1nodesource1~xenial1_amd64.deb`
* `git clone https://github.com/8cbx/ljudge.git`
* `cd ljudge`
* `make `
* `sudo make install`
* `sudo cp -r ./etc/ljudge /etc/ljudge`