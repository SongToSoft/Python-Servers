#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import BaseHTTPServer
import CGIHTTPServer
import os

PORT_NUMBER = 7800 

class MyHandler(BaseHTTPRequestHandler): 

    #Handler for the GET requests 
    def do_GET(self): 
        #You can continue this list 
        if (self.path.endswith('.html')):
            customType = 'text/html'
        elif (self.path.endswith('.json')):
            customType = 'application/json'
        elif (self.path.endswith('.aac')):
            customType = 'audio/aac'
        elif (self.path.endswith('.webm')):
            customType = 'video/webm'
        elif (self.path.endswith('.xml')):
            customType = 'application/xml'
        elif (self.path.endswith('.pdf')):
            customType = 'application/pdf'
        else:
            self.send_response(404)
            self.end_headers()
            return
        file = open(curdir + sep + self.path, 'rb')
        self.send_response(200)
        self.send_header('Content-type', customType)
        self.end_headers()
        self.wfile.write(file.read())
        file.close()
        return

    #I'm not sure about that
    #Handler for the POST requests 
    def do_POST(self):
        file = open("post_file", 'wb')
        self.send_response(201, 'Created')
        self.end_headers()
        length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(length)
        self.wfile.write(request_body.encode('utf-8'))
        file.write(request_body.encode('utf-8'))

    #Handler for the PUT requests
    def do_PUT(self):
        file = os.path.basename(self.path)

        if self.check_Exist(file) == True:
            return
        
        length = int(self.headers['Content-Length'])
        with open(file, 'wb') as output_file:
            output_file.write(self.rfile.read(length))

        self.send_response(201, 'Created')
        self.end_headers()
        request_body = 'Saved "%s"\n' % file
        self.wfile.write(request_body.encode('utf-8'))

    def check_Exist(self, file):
        if os.path.exists(file):
            self.send_response(409, 'Conflict')
            self.end_headers()
            request_body = '"%s" already exists\n' % file
            self.wfile.write(request_body.encode('utf-8'))
            return True
        else:
            return False

if __name__=="__main__":
    try:
        print ("Server running on " + str(PORT_NUMBER) + " port")
        
        baseServer = BaseHTTPServer.HTTPServer
        myHandler = MyHandler
        server_address = ("", PORT_NUMBER)
        
        myServer = baseServer(server_address, myHandler)
        myServer.serve_forever()
    
    except KeyboardInterrupt:
        print " Shutting down the web server"
        myServer.socket.close()