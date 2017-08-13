# sovol
そぼる

![ロゴ](https://cloud.githubusercontent.com/assets/343556/17990628/530c3824-6aec-11e6-8ad1-545acfb9c35b.png)

## INSTALL (port 80/443)

注意: このリポジトリは[Dockerファイル](https://github.com/internship2016/django-uwsgi-nginx)と対になっています。

    $ git clone https://github.com/internship2016/django-uwsgi-nginx.git
    $ ( cd django-uwsgi-nginx && docker build -t webapp . )
    $ git clone https://github.com/internship2016/sovolo.git
    $ ( cd sovolo/app && npm install && gulp default )
    $ docker run -v $PWD/sovolo:/home/docker/code --name sovolo -p 80:80 -p 8000:8000 -p 443:443 -d webapp
    $ docker exec -it sovolo /bin/bash
    # install-project
    # migrate

## SEEDING
    # cd /home/docker/code/app
    # python3 manage.py flush
    # python3 manage.py seed_data

## TESTING (port 8000)
    # runserver