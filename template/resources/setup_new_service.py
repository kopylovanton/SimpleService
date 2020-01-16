import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--newName', help='new service name')
parser.add_argument('--tempName', help='new service name', default='+-template-+')
args = parser.parse_args()
print('get args:', args)
dirpath = os.getcwd()
print('current dir:', dirpath)
assert dirpath.find(args.newName) > 0, 'Current dir does not equal service name in lower case'


def doChange(p):
    sp = ['.py', '.sh', '.temp', '.log', 'cache', '.git', '.idea', '.md']
    if p.find('/home/flask') < 0:
        return False
    for v in sp:
        if p.find(v) > 0:
            return False
    return True


cntRep = 0
for dname, dirs, files in os.walk(dirpath):
    for fname in files:
        fpath = os.path.join(dname, fname)
        if doChange(fpath):
            with open(fpath) as f:
                s = f.read()
            s = s.replace(args.tempName, args.newName)
            cntRep += s.count(args.newName)
            print('>>> prcess file:', fpath, 'replaced %s template' % str(s.count(args.newName)))
            with open(fpath, "w") as f:
                f.write(s)
assert cntRep > 3, 'Error replace template service name - try copy new template configuration' \
                   ' an restart setup.sh process'
print('Context change complete')

# Nginx
addconf = '''location /%s {
      proxy_redirect   off;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_pass http://unix:/home/flask/api/socket/%s.sock;
    } 
    location /''' % (args.newName, args.newName)
if os.path.exists('/etc/nginx/sites-available/api-config'):
    if os.path.isfile('/etc/nginx/sites-available/api-config'):
        shutil.copyfile('/etc/nginx/sites-available/api-config', dirpath + '/nginx/api-config')
        fpath = dirpath + '/nginx/api-config'
        with open(fpath) as f:
            s = f.read()
        if s.find(args.newName) < 0:
            s = s.replace('location /', addconf, 1)
            with open(fpath, "w") as f:
                f.write(s)
