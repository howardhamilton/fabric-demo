# fabfile.py

from fabric import api

def host_type():
    api.run('uname -s')