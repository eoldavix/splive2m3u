#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import pwd, grp, os
import ConfigParser
import urllib2
from shutil import copyfile 
from time import strftime
from BeautifulSoup import BeautifulSoup

CONF_FILE="splive2m3u.conf"

# Inicializamos log
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('splive2m3u')



def Parsea(url, f):
	descarga = urllib2.urlopen(url)
	xml = descarga.read()
	
	tree = BeautifulSoup(xml)
	
	for channel in tree.findAll('channel'):
		channel_attrs = dict(channel.attrs)
		c_id = channel.find('id_channel').string
		c_name = channel.find('name').string
		c_category = channel.find('category').string
		c_available = channel.find('available').string
		c_rtmp = channel.find('rtmp').string
		c_link_logo = channel.find('link_logo').string
		c_url_html = channel.find('url_html').string
		#c_isIliveTo = channel.find('isIliveTo').string
		#c_isFreeLive = channel.find('isFreeLive').string
		#c_isFlashStreaming = channel.find('isFlashStreaming').string
		f.write('#EXTINF:0 tvg-name="%s" tvg-logo="%s" group-title="%s",%s\n%s\n' % (c_name, c_link_logo, c_category, c_name, c_rtmp))

def Backup(file, uid, gid):
	logging.info('Backing up file  %s' % file)

	timeStamp = strftime('%Y%m%d%H%M')
	backup = "%s.%s" % (file, timeStamp)
	
	if os.path.isfile(file): 
		copyfile (file, backup)
		if os.path.isfile(backup):
			logging.info('Backup %s generated' % backup)
			os.chown(backup, uid, gid)
		else:
			logging.error('Error generating %s backup file' % backup)
	else:
		logging.warn('File %s not exists' % file)
	
def main():
	# Carga del fichero de configuración
	config = ConfigParser.ConfigParser()
	config.read(CONF_FILE)
	urlRoot = config.get('GLOBALS', 'urlRoot')
	fileList = config.items('URLLIST')
	playlist = "%s/%s" % (config.get('GLOBALS', 'dirPlex'), config.get('GLOBALS', 'playlist'))
	uid = pwd.getpwnam(config.get('GLOBALS', 'playlistUser')).pw_uid
	gid = grp.getgrnam(config.get('GLOBALS', 'playlistGroup')).gr_gid

	# Inicializamos log
	
	logging.info('Starting...')
	
	# Copia de seguridad del fichero

	Backup(playlist, uid, gid)
	
	# Creamos el fichero
	
	logging.info('Generating file %s' % playlist)
	try: 
		with open(playlist, 'w') as fich:
			# Cabecera
			fich.write('#EXTM3U\n')
	
			# Parseamos los ficheros descargables	
			for key, i in fileList:
				logging.info('Downloading and generating channel list "%s"' % (key))
				Parsea( "%s/%s" % (urlRoot, i), fich )
	except IOError:
		logging.critical('Error opening %s for writing' % playlist)	

	# Cerramos fichero
	finally: 
		fich.close()
		logging.debug('File %s successfully generated' % playlist)

		# Cambiamos permisos fichero
		try:
			os.chown(playlist, uid, gid)
		except IOError:
			logging.error('Error changing user and group of file %s' % playlist)
		finally:
			logging.debug('Changed user and group of file %s' % playlist)
			
	
	logging.info('Finished execution')
	
if __name__ == "__main__":
	main()
