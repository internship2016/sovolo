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
    (root) echo "[include]" >> /etc/supervisord/supervisord.conf
    (root) echo "files = conf.d/*.conf" >> /etc/supervisord/supervisord.conf
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

    (root) yum install https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
    (root) yum install postgresql96 postgresql96-server
    (root) /usr/pgsql-9.6/bin/postgresql96-setup initdb
    (root) systemctl enable postgresql-9.6
    (root) systemctl start postgresql-9.6
    (root) yum install postgresql96-contrib

### uWSGI

    (root) yum install libtiff-devel libjpeg-turbo-devel zlib-devel freetype-devel lcms2-devel libwebp-devel
    (root) pip3.5 install uwsgi
    (root) yum group install "Development Tools"

### LetsEncrypt

    (root) yum install certbot
    (root) systemctl stop nginx.service
    (root) certbot certonly --standalone -d sovol.moe -m who@example.com
    (root) systemctl start nginx.service

### Clone django-uwsgi-nginx

    (user) cd $HOME
    (user) git clone https://github.com/internship2016/django-uwsgi-nginx.git

### Clone sovol application to shared directory

    (root) mkdir /usr/local/src/sovolo.git
    (root) chown root:wheel /usr/local/src/sovolo.git
    (root) cd /usr/local/src/sovolo.git
    (root) git init --bare --shared=group

    (user) cd $HOME
    (user) git clone https://github.com/internship2016/sovolo.git
    (user) cd sovolo
    (user) git remote add local /usr/local/src/sovolo.git
    (user) git push local master

    (root) chown -R root:wheel /usr/local/src/sovolo.git
    (root) cd /usr/local/src
    (root) git clone sovolo.git
    (root) cd sovolo
    (root) cp /home/user/django-uwsgi-nginx/uwsgi_params ./
    (root) cp /home/user/django-uwsgi-nginx/uwsgi.ini ./
    (root) cd app
    (root) vi .env
    (root) cd ..
    (root) vi uwsgi.ini
    (root) vi /etc/supervisord.d/sovolo.conf

        [program:sovolo-uwsgi]
        command = /bin/uwsgi --ini /usr/local/src/sovolo/uwsgi.ini
        stopsignal = INT

        stdout_logfile = /tmp/uwsgi_stdout
        stderr_logfile = /tmp/uwsgi_stderr

### Reload supervisor

    (root) supervisorctl reload
    (root) supervisorctl start sovolo
    (root) supervisorctl start sovol-uwsgi

### Install nodejs/npm

    (root) yum install gcc-c++ make
    (root) curl --silent --location https://rpm.nodesource.com/setup_6.x | bash -
    (root) yum install nodejs

### Install python packages

    (root) pip3.5 -r requirements.txt

### Application preprocess

    (root) cd /usr/local/src/sovolo/app
    (root) npm install
    (root) npm run gulp default

### Install Postfix

    (root) yum install postfix
    (root) vi /etc/postfix/main.cf
    (root) systemctl restart postfix.service

### I18N

    (root) yum install gettext
    (root) python3.5 manage.py meakemessages -l ja
    (root) python3.5 manage.py compilemessages

### Migrate database

    (root) python3.5 manage.py migrate
