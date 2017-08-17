# FlaskWebPage
Flask Website tutorial from https://pythonprogramming.net/

## requirements:
* unbuntu 16.04    
* apache2
* flask
* python2.7.12
* mysql 
* [WTForms](https://flask-wtf.readthedocs.io/en/stable/)(a build in forms module in Flask)
* passlib (used for password encryption)
* [Pygal](http://www.pygal.org/en/stable/) (SVG Graphs with Flask)
* [letsencrypt](https://letsencrypt.org/) 

## path
> app path: /var/www/FlaskApp    
> apache2 config path: /etc/apache2/sites-available/FlaskApp.conf

## install
> apt-get install apache2 mysql-client mysql-erver    
> apt-get install libapache2-mod-wsgi    
> sudo a2enmod wsgi    
> sudo apt-get install python-MySQLdb    
> pip install flask-wtf    
> pip install passlib    
> pip install Flask-Mail    
> pip install pygal

# solution:
Q: kill nginx to release port 80 for apache2
> sudo netstat -tulpn | grep :80

> service nginx stop

> service apache2 start

Q: set root password of MySQL
> mysql>set password for 'root'@'localhost' = password('mysqlpassword');

Q: ubuntu close the firewall
> ufw disable



