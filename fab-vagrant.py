# fabfile.py

from fabric import api
from fabtools.vagrant import vagrant

@api.task
def host_type():
    api.run('uname -s')