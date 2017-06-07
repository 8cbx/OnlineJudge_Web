## Web part:
* `apt-get update && apt-get install python-pip mysql-server nginx git python-dev vim python-imaging python-mysqldb`
* `git clone https://github.com/8cbx/OnlineJudge_Web.git`
* setting nginx
* `pip install -r requirements.txt`
* import environment variables
* init db(we need to install flask-celery first, the install flask-celery-helper. otherwise manage.py will not in good use), `python manage.py db init`, `python manage.py db migrate -m "first init"`, `python manage.py db upgrade`
* insert default role
* good to start!

## Judge part: