I developed this website for a project that was never completed. Figure it demonstrates I can do webprogramming in a pinch.

##############################################################################################
Setup a virtual box server
##############################################################################################

This tutorial assumes the host machine is Ubuntu 18.04 LTS but it should work on other operating systems.

Download Ubuntu Server 18.04 LTS image from

https://ubuntu.com/download/server

Then install and open virtualbox.

$ sudo apt-get install virtualbox

$ virtualbox

Create a virtual machine “demo_site” with properties
Ubuntu (64-bit)
Ram -> 4096 MB*
10 GB Virtual Hard Disk* (VDI Dynamically Allocated)

(* really should not matter)

Next open demo_site’s settings in virtualbox and under the Network tab enable Adapter 1 and set it to 
Attached to: NAT

Under the advanced settings Cable Connected is checked but I’m not sure this matters. 

Open “Port Forwarding” and set two rules.
	Name	Protocol	Host IP		Host Port	Guest IP	Guest Port
	Rule 1	TCP		127.0.0.1	2200		10.0.2.15	22
	Rule 2	TCP		127.0.0.1	8000		10.0.2.15	80

(This allows one to connect locally to demo_site only)

Under the Storage tab in the Settings for demo_site load the Ubuntu Server 18.04 LTS disk image on the CD drive and start demo_site.

Click through the first 7 steps of the server installation using all the default settings. 

Under the Profile setup enter page enter

Your name: a_user
Sever name: demo_site
Username: a_user
Password: passwd
Confirm password: passwd

On the next page check the option to install the OpenSSH server then click Done. 

On the following page click Done without installing any additional packages. 

Then Reboot the server and remove the disk image from demo_site.

Connect to demo_site via

$ ssh -p 2200 a_user@127.0.0.1

with password “passwd”.
 
###################################################################################
Install the Nginx server on the demo_site and test Flask
(based on https://vladikk.com/2013/09/12/serving-flask-with-nginx-on-ubuntu/)
###################################################################################

Login to demo_site

$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get dist-upgrade

$ sudo apt-get install nginx-common
$ sudo apt-get install nginx
$ sudo apt-get -y install python3 ipython3 python3-flask curl

$ mkdir ~/flask

$ cd flask
$ vim hello.py and paste in (minus "*")

****************************************************************************
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
****************************************************************************

$ sudo apt-get install python3-dev
$ sudo apt-get install python3-pip
$ pip3 install uwsgi

$ sudo rm /etc/nginx/sites-enabled/default

In /home/a_user/flask/ save flask_nginx.conf as (minus "*")

****************************************************************************
server {
	listen      80;
    	server_name localhost;
    	charset     utf-8;
    	client_max_body_size 75M;

    	location / { try_files $uri @yourapplication; }
    	location @yourapplication {
        	include uwsgi_params;
        	uwsgi_pass unix:/home/a_user/flask/test_uwsgi.sock;
    	}   
}
****************************************************************************

$ sudo ln -s /home/a_user/flask/flask_nginx.conf /etc/nginx/conf.d/
$ sudo /etc/init.d/nginx restart

Create file /home/a_user/flask/test_uwsgi.ini with contents

****************************************************************************
[uwsgi]
#python module to import
app = hello
module = %(app)

#socket file's location
socket = /home/a_user/flask/%n.sock

#permissions for the socket file
chmod-socket    = 666

#the variable that holds a flask application inside the module imported at line #6
callable = app

#location of log files
logto = /var/log/uwsgi/%n.log
****************************************************************************

Make log folder for uwsgi 

$ sudo mkdir -p /var/log/uwsgi
$ sudo chown -R a_user:a_user /var/log/uwsgi

pip3 installed uwsgi in ~/.local/bin

Create symlink to bin.

$ sudo ln -s ~/.local/bin/uwsgi /usr/bin/uwsgi

Run

$ uwsgi --ini /home/a_user/flask/test_uwsgi.ini

Goto server IP address 127.0.0.1:8000 in a browser on your host machine.

Output “Hello World!”

This means the nginx server and Flask are working and correctly configured.

(I skip setting up uWSGI Emperor which allows uWSGI to run as a background service for the moment.)

###################################################################################
Pull down the web app and reconfigure uWSGI
###################################################################################

Download app from github.

$ sudo apt-get install git
$ git clone https://github.com/sophist0/demo_web_app
$ mv demo_web_app/ app/
$ mkdir demo
$ mv app/ demo/
$ cp -r flask/ demo_conf/

$ cd demo_conf/

In test_uwsgi.ini set 

****************************************************************************
app = demo
****************************************************************************

and

****************************************************************************
socket = /home/a_user/demo_conf/%n.sock
****************************************************************************

$ pip3 install flask-wtf
$ pip3 install flask-sqlalchemy
$ pip3 install flask-migrate
$ pip3 install flask-login
$ pip3 install Pillow	

$ cd ~/demo/app/
$ export FLASK_APP=demo.py
$ flask db init
$ flask db migrate -m "users table"
$ flask db upgrade

$ sudo chmod 775 app/
$ sudo chmod 775 static/		(not sure either of these permission changes are needed)

In /home/a_user/demo_conf/ 

$ cp flask_nginx.conf demo_nginx.conf

Update the contents of demo_nginx.conf to be

****************************************************************************
server {
	listen      80;
    	server_name localhost;
    	charset     utf-8;
    	client_max_body_size 75M;

    	location / { try_files $uri @yourapplication; }
    	location @yourapplication {
        	include uwsgi_params;
        	uwsgi_pass unix:/home/a_user/demo_conf/demo_uwsgi.sock;
    	}   
	location /static {
    		root /home/a_user/demo/app/;
	} 
}
****************************************************************************

$ sudo ln -s /home/a_user/demo_conf/demo_nginx.conf /etc/nginx/conf.d/
$ sudo rm /etc/nginx/conf.d/flask_nginx.conf
$ sudo /etc/init.d/nginx restart

$ cd ~/demo/app
$ uwsgi --ini /home/a_user/demo_conf/test_uwsgi.ini --wsgi-file=demo.py --callable app

In a browser go to 127.0.0.1:8000

###################################################################################
Common Errors
###################################################################################

After a server has been setup and the files have been pulled off github there are two major errors you may run into.

(1) The server crashes as soon as you try to open the login page or login.

	This may indicate that the pulled site has a different database model then you have. Delete the database and /migrations folder and re-init the database.

(2) Server doesn't crash but non-html/database files don't load. This may indicate that the file system in the /static folder has changed. Delete the database and /migrations folder as in (1). Delete everything in /static except the CSS files.

If something goes wrong check the error logs location:

/var/log/uwsgi/rat_uwsgi.log
/var/log/nginx/error.log

###################################################################################
Note: I have not setup this demo site or the database backing it to be secure.
###################################################################################
