import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--newName', help='new service name', default='simpleservice')
parser.add_argument('--tempName', help='new service name', default='+-template-+')
args = parser.parse_args()
print('get args:', args)
dirpath = os.getcwd()
print('current dir:', dirpath)
assert dirpath.find(args.newName) > 0, 'Current dir does not equal service name in lower case'


def doChange(p):
    sp = ['run.sh',
          'config_log.yaml',
          'swagger_template.yaml',
          'config_service.yaml',
          'systemd/api-template.socket',
          'systemd/api-template.service',
          'nginx/api-config']
    if p.find(args.newName) < 0:
         return False
    for v in sp:
        if p.find(v) > 0:
            return True
    return False


cntRep = 0
for dname, dirs, files in os.walk(dirpath):
    for fname in files:
        fpath = os.path.join(dname, fname)
        if doChange(fpath):
            with open(fpath) as f:
                s = f.read()
            if s.count(args.tempName)>0:
                s = s.replace(args.tempName, args.newName)
            print('>>> process file:', fpath, 'replaced %s template' % str(s.count(args.newName)))
            cntRep += s.count(args.newName)
            with open(fpath, "w") as f:
                f.write(s)
assert cntRep > 3, 'Error replace template service name - try copy new template configuration' \
                   ' an restart setup.sh process'
print('Context change complete')

# Nginx
addconf = '''location /%s {
      proxy_redirect   off;
      proxy_buffering off;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_pass http://unix:/home/flask/api/socket/%s.sock;
    } 
    location /''' % (args.newName, args.newName)
if  os.path.exists('/etc/nginx/sites-available/api-config') \
    and os.path.isfile('/etc/nginx/sites-available/api-config'):
        shutil.copyfile('/etc/nginx/sites-available/api-config', dirpath + 'template/nginx/api-config')
        fpath = dirpath + '/nginx/api-config'
        with open(fpath) as f:
            s = f.read()
        if s.find(args.newName) < 0:
            s = s.replace('location /', addconf, 1)
            with open(fpath, "w") as f:
                f.write(s)

