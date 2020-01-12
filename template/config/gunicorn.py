# http://docs.gunicorn.org/en/latest/settings.html#config-file

import yaml
# ************* Load Parms
with open(r'./config/config_get.yaml') as file:
    parms= yaml.load(file, Loader=yaml.FullLoader)

bind = "unix:/home/flask/api/socket/%s.sock"%(parms['URL'])
workers = 4
chdir   = '/home/flask/api/%s/' %(parms['URL'])
capture_output=True
errorlog = './logs/%s_main.log'%(parms['URL'])
accesslog = './logs/%s_access.log'%(parms['URL'])
preload = True
loglevel = 'info'
max_requests=1000
max_requests_jitter=100
timeout=30
keepalive=2
