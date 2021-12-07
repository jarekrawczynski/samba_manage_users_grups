#!/usr/bin/python

import ldb
import os, shutil
import sys
import stat, pwd
from connect_ldap import Ldap

ldap = Ldap()
ldap.connect()

LEAD_PATH = '/home/'
BASEDIR = '/etc/adduser/'
LOCK_FILE = '/etc/adduser/addldapgroups.lock'
ID_FILE = 'id'
lockFileExist = "Previous copy of script is running. Exiting!"
homeDirExist = "HomeDir user exist!!"
gid = 0
uid = 0
GROUPOU = "OU=Groups"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def wrong_arguments():
     print(bcolors.HEADER+'\nusage: ./labgroup login name surname'+bcolors.ENDC)

def file_exists(a,b,c):
    if a(b):
	print (c)
	sys.exit()
    else:
	file = open(LOCK_FILE, "w")
	file.write("")
	file.close()



def search_user(l):
    query = ("(cn="+l+")")
    result = ldap.samdb.search('OU=XXX,DC=XX,DC=XX,DC=XX', expression=query, scope=ldb.SCOPE_SUBTREE) 
    dn = len(result)
    #print(dn)
    if dn == 1:
	os.remove(LOCK_FILE)
        print ("User "+l+" exists!!")
        sys.exit()
    else:
         os.mkdir("/home/"+l)

def gid_id(a):
    f = open(a, "r")
    b = int(f.read().replace('\n', ''))
    f.close()
    global gid
    gid = b+1

def uid_id():
    global uid
    uid = gid+1

def password(length=8, charset="abcdefghijklmnopqrstuvwxyz1234567890"):
    random_bytes = os.urandom(length)
    len_charset = len(charset)
    indices = [int(len_charset * (ord(byte) / 256.0)) for byte in random_bytes]
    return "".join([charset[index] for index in indices])

def save_id(i):
    i = str(i)
    file = open(ID_FILE, "w")
    file.write(i)
    file.close()


def create_group(l,groupou,gid):
    ldap.samdb.newgroup(l,groupou=groupou,gidnumber=gid)

def create_user(l,password,name,lastname,uid,gid):
	ldap.samdb.newuser(l,password,userou="OU=XXX",surname=lastname,givenname=name,
	profilepath="\\\\XXX\users\\"+l+"\profile",scriptpath="logon.bat",homedirectory="\\\\XXX\users\\"+l,
	homedrive="U:",mailaddress=l+"@XXX",unixhome="/home/"+l,
	uidnumber=uid,gidnumber=gid,nisdomain="ad",uid=l,loginshell="/bin/bash",
	gecos=name+lastname)

	print (bcolors.OKBLUE+l+": "+bcolors.ENDC+bcolors.OKGREEN+password+bcolors.ENDC)
	filepassword = BASEDIR+l+".pass"
	file = open(filepassword, "w") 
	file.write(password) 
	file.close()

	#save id 
	save_id(uid)

def copy_skel(l, symlinks=False, ignore=None):
    src = "/etc/skel/"
    dst = LEAD_PATH+l
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

RWXU = stat.S_IRWXU
def change_permisson(l,path,b):
    os.chmod(path,b)
    os.chown(path, pwd.getpwnam(l).pw_uid, pwd.getpwnam(l).pw_gid)
    for root, dirs, files in os.walk(path):  
     for momo in dirs:  
        os.chown(momo, 502, 20)
     for file in files:
        fname = os.path.join(root, file)
        os.chown(fname, pwd.getpwnam(l).pw_uid, pwd.getpwnam(l).pw_gid)   


if len(sys.argv) <= 3:
    wrong_arguments()
else:
    login = sys.argv[1]
    name = sys.argv[2]
    lastname = sys.argv[3]
    file_exists(os.path.isfile,LOCK_FILE,lockFileExist)
    search_user(login)
    gid_id(ID_FILE)
    uid_id()
    create_group(login,GROUPOU,gid)
    create_user(login,password(),name,lastname,uid,gid)
    copy_skel(login)
    change_permisson(login,LEAD_PATH+login,RWXU)
    os.remove(LOCK_FILE)