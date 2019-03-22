#!/usr/bin/python 

import tftpy 

if __name__ == '__main__': 
	try: 
		print "Tftp server is running" 
		server = tftpy.TftpServer('/var/lib/tftpboot') 
		server.listen('0.0.0.0', 4069) 
	except KeyboardInterrupt: 
		print " Shutting down the Tftp server"