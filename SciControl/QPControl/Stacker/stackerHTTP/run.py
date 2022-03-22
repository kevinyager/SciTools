#!/usr/bin/env python3 
#import os

# Web server
from http.server import HTTPServer, CGIHTTPRequestHandler
#os.chdir('.')
print('Creating HTTPServer...')
server_object = HTTPServer(server_address=('', 3030), RequestHandlerClass=CGIHTTPRequestHandler)
print('Starting HTTPServer...')
server_object.serve_forever()


