#!/usr/bin/python

from samba.auth import system_session
from samba.credentials import Credentials
from samba.param import LoadParm
from samba.samdb import SamDB
import ldb

class Ldap():
		

    		def __init__(self):
				samdb = None


    		def connect(self):
				lp = LoadParm()
				creds = Credentials()
				creds.guess(lp)
				creds.set_username("Administrator")
				creds.set_password('PASSWORD')
				self.samdb = SamDB(url='ldap://127.0.0.1:389', session_info=system_session(),credentials=creds, lp=lp)

