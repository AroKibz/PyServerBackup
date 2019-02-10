#!/usr/bin/python
# -*- coding: utf-8 -*-
import ftplib
import os
import shutil
import zipfile
import time
import sys
import datetime
import re

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText


def startMail():
	try:
		x = datetime.datetime.now()
		msg = MIMEText(content, text_subtype)
		msg['Subject']= subject
		msg['From']   = sender # some SMTP servers will do this automatically, not all

		conn = SMTP(SMTPserver)
		conn.set_debuglevel(False)
		conn.login(USERNAME, PASSWORD)
		try:
			conn.sendmail(sender, destination, msg.as_string())
		finally:
			conn.close()
	
	except Exception, exc:
		sys.exit( "mail failed; %s" % str(exc) ) # give a error message


def stopMail(dc):
	try:
		vDir=""
		x = datetime.datetime.now()
		for k in dc['directories']:
			vDir=vDir + "\t" + k[0] + "  -  " + k[1] + "\n"



		fecha_backup = "Backup finalizado el %s/%s/%s a las %s:%s:%s" % (x.day, x.month, x.year, x.hour, x.minute, x.second) + " en el servidor: \n" + path_ftp

		content=fecha_backup + ", tamaño total: " + str(size) + "\n" + vDir
		#print content
		subject=fecha_backup
		msg = MIMEText(content, text_subtype)
		msg['Subject']=       subject
		msg['From']   = sender # some SMTP servers will do this automatically, not all

		conn = SMTP(SMTPserver)
		conn.set_debuglevel(False)
		conn.login(USERNAME, PASSWORD)
		try:
			conn.sendmail(sender, destination, msg.as_string())
		finally:
			conn.close()

	except Exception, exc:
		sys.exit( "mail failed; %s" % str(exc) ) # give a error message


def uploadThis(path,exclude_files=[]):
	files = os.listdir(path)
	os.chdir(path)
	excluir_con_extension=False
	if 'parametros' in files:excluir_con_extension=True

	for f in files:
		fichero = path + r'/{}'.format(f)
		#print fichero
		if os.path.isfile(fichero):
			if excluir_con_extension and '.' in fichero:continue
			if f not in exclude_files:
				fh = open(fichero, 'rb')
				print 'Subiendo '+fichero
				size=get_FileSize(fichero)        
				dc['directories'].append([fichero,size])
				ftp.storbinary('STOR %s' % f, fh)
				fh.close()
		elif os.path.isdir(fichero):
			try:ftp.mkd(f)
			except:pass
			ftp.cwd(f)

			uploadThis(fichero,exclude_files)
		else:
			print fichero

	ftp.cwd('..')
	os.chdir('..')


def zipThis(path,exclude_files=[]):
	files = os.listdir(path)
	zipear=False
	if 'parametros' in files:zipear=True
	if zipear:
		zf = zipfile.ZipFile(path+'.zip', "w",zipfile.ZIP_DEFLATED)
		for dirname, subdirs, files in os.walk(path):
			for filename in files:
				if '.' in filename:continue
				file=os.path.join(dirname, filename)
				zf.write(file,arcname=filename)
		zf.close()
		shutil.rmtree(path)
	else:
		for f in files:
			fichero = path + r'/{}'.format(f)
			if os.path.isdir(fichero):
				zipThis(fichero,exclude_files)


def get_FileSize(filename):
    st = os.stat(filename)
    st = st.st_size

    B = "B"
    KB = "KB" 
    MB = "MB"
    GB = "GB"
    TB = "TB"
    UNITS = [B, KB, MB, GB, TB]
    HUMANFMT = "%s %s"
    HUMANRADIX = 1024.
    for u in UNITS[:-1]:
    	if st < HUMANRADIX :
    		st = "%.2f" % st
    		return HUMANFMT % (st, u)
    	st = st/HUMANRADIX
    st = "%.2f" % st
    return HUMANFMT % (st,  UNITS[-1])


def get_size(the_path):

	bytes_size = 0
	for path, directories, files in os.walk(the_path):
		for filename in files:
			bytes_size += os.lstat(os.path.join(path, filename)).st_size
		for directory in directories:
			bytes_size += os.lstat(os.path.join(path, directory)).st_size
		bytes_size += os.path.getsize(the_path)

		#bytes_size = int(bytes_size*100)/100

	B = "B"
	KB = "KB" 
	MB = "MB"
	GB = "GB"
	TB = "TB"
	UNITS = [B, KB, MB, GB, TB]
	HUMANFMT = "%s %s"
	HUMANRADIX = 1024.

	for u in UNITS[:-1]:
		if bytes_size < HUMANRADIX :
			bytes_size = "%.2f" % bytes_size
			return HUMANFMT % (bytes_size, u)
		bytes_size = bytes_size/HUMANRADIX

	bytes_size = "%.2f" % bytes_size
	return HUMANFMT % (bytes_size,  UNITS[-1])


x = datetime.datetime.now()

# Cargar variables fichero
#print 'sys.argv[0] =', sys.argv[0
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)
fecha = "%s_%s_%s" % (x.year, x.month, x.day )
config = fullpath + '/ftp.conf' 

txt=open(config,'r').read()
dc=eval(txt)

file=dc['filename']
username=dc['username']
password=dc['password']
url=dc['url']
directories=dc['directories']
path_ftp=dc['path_ftp']

#Recordatorio: Si se usa una cuenta GMAIL como remitente, activar el acceso de aplicaciones 
#menos seguras en https://myaccount.google.com/security


SMTPserver = dc['SMTPserver']
sender = dc['sender']
destination = dc['destination']
USERNAME = dc['USERNAME']
PASSWORD = dc['PASSWORD']

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'

fecha_backup = "Backup comenzado el %s/%s/%s a las %s:%s:%s" % (x.day, x.month, x.year, x.hour, x.minute, x.second) + " en el servidor: " + path_ftp

content=fecha_backup

subject=fecha_backup


ftp = ftplib.FTP()
ftp.connect(url,21212)
ftp.login(username, password)

startMail()


try:ftp.mkd(path_ftp)
except:pass
ftp.cwd(path_ftp)

try:shutil.rmtree(fullpath + '/tmp')
except:pass
dc={}
dc['directories']=[]

#os.mkdir(fullpath + '/tmp')
for dc_directory in directories:
	directory=dc_directory['path']

	if directory[-1]<>'/':directory+='/'

	exclude_files=dc_directory['exclude_files']

	directory_name=directory.split('/')[-2]

	shutil.copytree(directory,fullpath + '/tmp/' + fecha + '/' + directory_name)

	directory=fullpath + '/tmp/' +fecha + '/' + directory_name

	zipThis(directory,exclude_files)

	place = os.path.dirname(os.path.realpath(directory))

	size=get_size(place)        
	#dc['directories'].append([directory,size])

	print "Tamaño total: " + size 

	uploadThis(place,exclude_files) # now call the recursive function 


try:shutil.rmtree(fullpath + '/tmp')
except:pass
ftp.close()
stopMail(dc)