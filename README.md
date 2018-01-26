# sovol
そぼる

![ロゴ](https://cloud.githubusercontent.com/assets/343556/17990628/530c3824-6aec-11e6-8ad1-545acfb9c35b.png)

## INSTALL (port 80/443)

注意: このリポジトリは[Dockerファイル](https://github.com/internship2016/django-uwsgi-nginx)と対になっています。

    $ git clone https://github.com/internship2016/django-uwsgi-nginx.git
    $ ( cd django-uwsgi-nginx && docker build -t webapp . )
    $ git clone https://github.com/internship2016/sovolo.git
    $ ( cd sovolo/app && npm install && npm run gulp default )
    $ docker run -v $PWD/sovolo:/home/docker/code --name sovolo -p 80:80 -p 8000:8000 -p 443:443 -d webapp
    $ docker exec -it sovolo /bin/bash
    # install-project
    # migrate

## SEEDING
    # cd /home/docker/code/app
    # # python3 manage.py flush # if need
    # python3 manage.py seed_data

## I18N
    # cd /home/docker/code/app
    # python3 manage.py compilemessages

## TESTING (port 8000)
    # runserver

## Production Guide

### Python3

    (root) yum install https://centos7.iuscommunity.org/ius-release.rpm
    (root) yum install python36u python36u-libs python36u-devel python36u-pip

### Front Web Server

    (root) yum install nginx
    (root) systemctl enable nginx
    (root) systemctl start nginx

### Supervisor

    (root) yum install python-pip
    (root) pip install --upgrade pip
    (root) pip install supervisor
    (root) mkdir -p /etc/supervisord/conf.d
    (root) echo_supervisord_conf > /etc/supervisord/supervisord.conf
    (root) vi /etc/supervisord/supervisord.conf

        ...
        [inet_http_server]         ; inet (TCP) server disabled by default
        port=127.0.0.1:9001        ; ip_address:port specifier, *:port for all iface
        ...
        [include]
        files = conf.d/*.conf
        ;eof

    (root) vi /usr/lib/systemd/system/supervisord.service

        [Unit]
        Description=supervisord - Supervisor process control system for UNIX
        Documentation=http://supervisord.org
        After=network.target

        [Service]
        Type=forking
        ExecStart=/usr//bin/supervisord -c /etc/supervisord/supervisord.conf
        ExecReload=/usr/bin/supervisorctl reload
        ExecStop=/usr/bin/supervisorctl shutdown
        User=root

        [Install]
        WantedBy=multi-user.target

    (root) systemctl enable supervisord
    (root) systemctl start supervisord.service

### PostgreSQL

    (root) yum install https://download.postgresql.org/pub/repos/yum/10/redhat/rhel-7.3-x86_64/pgdg-redhat10-10-2.noarch.rpm
    (root) yum install postgresql10 postgresql10-server postgresql10-contrib postgresql10-libs
    (root) /usr/pgsql-10/bin/postgresql-10-setup initdb
    (root) systemctl enable postgresql-10
    (root) systemctl start postgresql-10

### uWSGI

    (root) yum install libtiff-devel libjpeg-turbo-devel zlib-devel freetype-devel lcms2-devel libwebp-devel
    (root) yum group install "Development Tools"
    (root) pip3.6 install uwsgi

### LetsEncrypt

    (root) yum install certbot
    (root) systemctl stop nginx.service
    (root) certbot certonly --standalone -d sovol.moe -m who@example.com
    (root) vi /etc/nginx/conf.d/sovol.conf

        # mysite_nginx.conf

        # the upstream component nginx needs to connect to
        upstream django {
            #server unix:/usr/local/src/sovolo/app.sock; # for a file socket
            server unix:/var/run/sovol.sock; # for a file socket
            # server 127.0.0.1:8001; # for a web port socket (we'll use this first)
        }

        server {
            listen 80;
            server_name sovol.moe;
            return 301 https://$host$request_uri;
        }

        # configuration of the server
        server {
            # the port your site will be served on, default_server indicates that this server block
            # is the block to use if no blocks match the server_name
            listen 443 ssl;

            # the domain name it will serve for
            server_name sovol.moe; # substitute your machine's IP address or FQDN
            ssl_certificate      /etc/letsencrypt/live/sovol.moe/fullchain.pem;
            ssl_certificate_key  /etc/letsencrypt/live/sovol.moe/privkey.pem;
            charset     utf-8;

            # max upload size
            client_max_body_size 75M;   # adjust to taste

            #auth_basic "closed";
            #auth_basic_user_file "/etc/nginx/htpasswd";

            # Django media
            location /media  {
                # your Django project's media files - amend as required
                alias /usr/local/src/sovolo/app/media;
            }

            location /static {
                # your Django project's static files - amend as required
                alias /usr/local/src/sovolo/app/static;
            }

            # Finally, send all non-media requests to the Django server.
            location / {
                uwsgi_pass  django;

                # the uwsgi_params file you installed
                include     /usr/local/src/sovolo/uwsgi_params;
            }
        }

    (root) systemctl start nginx.service

### Clone django-uwsgi-nginx

    (user) cd $HOME
    (user) git clone https://github.com/internship2016/django-uwsgi-nginx.git

### Clone sovol application to shared directory

    (root) mkdir /usr/local/src/sovolo.git
    (root) cd /usr/local/src/sovolo.git
    (root) git init --bare --shared=group
    (root) chown -R root:wheel /usr/local/src/sovolo.git

    (user) cd $HOME
    (user) git clone https://github.com/internship2016/sovolo.git
    (user) cd sovolo
    (user) git remote add local /usr/local/src/sovolo.git
    (user) git push local master

    (root) cd /usr/local/src
    (root) git clone sovolo.git
    (root) cd sovolo
    (root) cp /home/user/django-uwsgi-nginx/uwsgi_params ./
    (root) cp /home/user/django-uwsgi-nginx/uwsgi.ini ./
    (root) cd app
    (root) vi .env

        SOCIAL_AUTH_TWITTER_KEY=*************************
        SOCIAL_AUTH_TWITTER_SECRET=**************************************************
        DATABASE_PASSWORD=*********
        EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
        SOCIAL_AUTH_FACEBOOK_KEY=***************
        SOCIAL_AUTH_FACEBOOK_SECRET=********************************
        GOOGLE_MAP_KEY=***************************************
        GOOGLE_RECAPTCHA_SECRET=****************************************

    (root) cd ..
    (root) vi uwsgi.ini

        [uwsgi]
        # this config will be loaded if nothing specific is specified
        # load base config from below
        ini = :base
        logger = file:/tmp/errlog

        # %d is the dir this configuration file is in
        #socket = %dapp.sock
        socket = /var/run/sovol.sock
        master = true
        processes = 4

        [dev]
        ini = :base
        # socket (uwsgi) is not the same as http, nor http-socket
        socket = :8001


        [local]
        ini = :base
        http = :8000
        # set the virtual env to use
        home=/Users/you/envs/env


        [base]
        # chdir to the folder of this config file, plus app/website
        chdir = %dapp/
        # load the module from wsgi.py, it is a python path from
        # the directory above.
        module=sovolo.wsgi:application
        # allow anyone to connect to the socket. This is very permissive
        chmod-socket = 666

    (root) vi /etc/supervisord/conf.d/sovolo.conf

        [program:sovolo-uwsgi]
        command = /usr/bin/uwsgi --ini /usr/local/src/sovolo/uwsgi.ini
        stopsignal = INT

        stdout_logfile = /tmp/uwsgi_stdout
        stderr_logfile = /tmp/uwsgi_stderr

### Reload supervisor

    (root) supervisorctl reload
    (root) supervisorctl start sovol-uwsgi

### Install nodejs/npm (Do not use sudo)

    (root) curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
    (root) yum install nodejs

### Install python packages

    (root) cd /usr/local/src/sovolo/app
    (root) pip3.6 install -r requirements.txt

### Application preprocess (Do not use sudo)

    (root) cd /usr/local/src/sovolo/app
    (root) npm install
    (root) npm run gulp default

### Postfix Configuration

    (root) vi /etc/postfix/main.cf

        ...
        inet_interfaces = loopback-only
        ...

    (root) systemctl restart postfix.service

### I18N

    (root) yum install gettext
    (root) python3.6 manage.py makemessages -l ja
    (root) python3.6 manage.py compilemessages

### Setup postgres database

    (root) vi /var/lib/pgsql/10/data/pg_hba.conf

        ...
        # IPv4 local connections:
        #host    all             all             127.0.0.1/32            ident
        host    all             all             127.0.0.1/32            md5
        # IPv6 local connections:
        #host    all             all             ::1/128                 ident
        host    all             all             ::1/128                 md5
        ...

    (root) systemctl restart postgresql-10.service
    (root) sudo su - postgres
    (postgres) psql --command "CREATE USER sovolo_admin WITH SUPERUSER PASSWORD '*********';"
    (postgres) psql --command "CREATE DATABASE sovolo WITH OWNER sovolo_admin TEMPLATE template0 ENCODING 'UTF8';"
    (postgres) exit

### Migrate database

    (root) python3.6 manage.py migrate

### Allow hostname using settings.py

    (root) vi app/sovolo/settings.py

        ...
        ALLOWED_HOSTS = ['sovol.moe']
        ...

### Testing with runserver

    (root) yum install nc
    (root) cd app
    (root) python3.6 manage.py runserver 8080

    (user) ( echo 'GET / HTTP/1.1'; sleep 1; echo 'Host: sovol.moe'; sleep 1; echo; sleep 1; ) | nc localhost 8080

        HTTP/1.1 302 Found
        Date: Fri, 26 Jan 2018 06:53:29 GMT
        Server: WSGIServer/0.2 CPython/3.6.4
        Content-Type: text/html; charset=utf-8
        Location: /event/top
        X-Frame-Options: SAMEORIGIN
        Content-Length: 0
        Vary: Accept-Language, Cookie
        Content-Language: ja-jp
