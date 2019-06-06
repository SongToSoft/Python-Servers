#!/usr/bin/python
"""Simple HTTP Server.
This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.
"""

__version__ = "0.6"

__all__ = ["SimpleHTTPRequestHandler"]

HOST = "10.10.11.22"

PORT = 7800

import ssl
import os
import posixpath
import BaseHTTPServer, SimpleHTTPServer
import urllib
import cgi
import sys
import shutil
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from socket import *

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = "SimpleHTTP/" + __version__

    def do_GET(self):
        print "Request is: " + self.path
        """Serve a GET request."""
        if (self.path.endswith('/uploads/Song-with-meta.aac/meta')):
            self.path = "/uploads/Song-with-meta.json"
        if (self.path.endswith('/uploads/Large-song.aac/meta')):
            self.path = "/uploads/Large-song-meta.json"
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    #Handler for the POST requests
    def do_POST(self):
        #self.send_response(201, 'Created')
        self.send_response(200, 'Created')
        self.end_headers()
        file = os.path.basename(self.path)

        if self.check_Exist(file) == True:
            return
        
        length = int(self.headers['Content-Length'])
        with open(file, 'wb') as output_file:
            output_file.write(self.rfile.read(length))

        request_body = 'Saved "%s"\n' % file
        self.wfile.write(request_body.encode('utf-8'))

    #Handler for the PUT requests
    def do_PUT(self):
        #self.send_response(201, 'Created')
        self.send_response(200, 'Created')
        self.end_headers()
        file = os.path.basename(self.path)

        if self.check_Exist(file) == True:
            return
        
        length = int(self.headers['Content-Length'])
        with open(file, 'wb') as output_file:
            output_file.write(self.rfile.read(length))

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

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

def ssl_wrap_socket(sock, ssl_version=None, keyfile=None, certfile=None, ciphers=None):
    # init a context with given version(if any)
    if ssl_version is not None and ssl_version in version_dict:
        # create a new SSL context with specified TLS version
        sslContext = ssl.SSLContext(version_dict[ssl_version])
        if option_test_switch == 1:
            print "ssl_version loaded!! =", ssl_version
    else:
        # if not specified, default
        sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    if ciphers is not None:
        #if specified, set certain ciphersuite
        sslContext.set_ciphers(ciphers)
        if option_test_switch == 1:
            print "ciphers loaded!! =", ciphers

    # server-side must load certfile and keyfile, so no if-else
    sslContext.load_cert_chain(certfile, keyfile)
    print "ssl loaded!! certfile=", certfile, "keyfile=", keyfile
    
    try:
        return sslContext.wrap_socket(sock, server_side = True)
    except ssl.SSLError as e:
        print "wrap socket failed!"
        print traceback.format_exc()

def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    try:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        print("Server running on https://localhost:", PORT)
        httpd = ServerClass(('localhost', PORT), HandlerClass)
        httpd.socket = socket(AF_INET, SOCK_STREAM)
        httpd.socket.bind((HOST, PORT))
        httpd.socket.listen(10)
        httpd.socket = ssl_wrap_socket(httpd.socket, ssl_version = None, keyfile='./ssl/key.pem', certfile='./ssl/certificate.pem', ciphers = None)
        httpd.serve_forever()
        httpd.socket.close()
    except KeyboardInterrupt:
        print " Shutting down the http server"
        httpd.socket.close()

if __name__ == '__main__':
    test()
