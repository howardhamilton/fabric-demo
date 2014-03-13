# fab-arguments.py

def hello():
    print 'Hello, Fabric!'

def greet(name):
    print 'Hello, {}!'.format(name)

def args_n_kwargs(*args, **kwargs):
    print 'args: {}'.format(args)
    print 'kwargs: {}'.format(kwargs)