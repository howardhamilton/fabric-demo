# fabfile.py

from fabric import api
from fabtools.vagrant import vagrant
import fabtools as FT

@api.task
def show_sudo():
    api.puts("I'm in ur ROOT!")
    api.sudo('whoami')


@api.task
def webserver():
    FT.require.nginx.server()
    template_contents = '''
    server {
        listen      80;
        server_name %(server_name)s www.pyatl.org;
        root        /vagrant;
        access_log  /var/log/nginx/%(server_name)s.log;
    }'''
    FT.require.nginx.site('vagrantstuff', template_contents=template_contents)
    FT.require.nginx.disabled('default')
    FT.require.nginx.enabled('vagrantstuff')

@api.task
def mongodb():
    FT.deb.add_apt_key(
        keyid='7F0CEB10', keyserver='keyserver.ubuntu.com')
    FT.require.deb.source(
        'mongodb',
        'http://downloads-distro.mongodb.org/repo/ubuntu-upstart',
        'dist', '10gen')
    FT.deb.update_index()
    FT.require.deb.package('mongodb-10gen')

@api.task
def app():
    APP_HOME='/var/lib/app'
    FT.require.directory(APP_HOME, owner=api.env.user, use_sudo=True)
    with api.cd(APP_HOME):
        FT.require.git.working_copy('https://github.com/synappio/chapman.git')
        FT.require.git.working_copy('https://github.com/rick446/MongoTools.git')
        FT.require.python.virtualenv('env')
        with FT.python.virtualenv('env'):
            FT.require.python.requirements('https://raw.github.com/synappio/chapman/master/requirements.txt')
            FT.require.python.packages(['ming'])
            with api.cd('chapman'):
                api.run('pip install -e .')
            with api.cd('MongoTools'):
                api.run('pip install -e .')

    FT.require.supervisor.process(
        'chapman-hq',
        command='/var/lib/app/env/bin/pserve chapman/development.ini',
        directory=APP_HOME,
        user=api.env.user)

@api.task
def proxy_nginx():
    template_contents = '''
    server {
        listen 81;
        server_name hq0;

        gzip_vary on;

        # path for static files
        root /var/lib/app;


        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://127.0.0.1:8080/;
        }

        access_log /var/log/nginx/hq0.log;
    }
    '''
    FT.require.nginx.site('hq0', template_contents=template_contents)
    FT.require.nginx.enabled('hq0')

@api.task
def make_user(username, public_key):
    FT.require.user(
        username,
        ssh_public_keys=[public_key],
        shell='/bin/bash')
    FT.require.sudoer(username)
