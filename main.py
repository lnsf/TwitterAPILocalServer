import http.server
import socketserver
import urllib
import sys
import webbrowser
import json

from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl, parse_qs, urlparse

consumer_key = ''
consumer_secret = ''

class EchoHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(http.HTTPStatus.OK)
        print(urllib.parse.urlparse(self.path))
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.end_headers()

        query = parse_qs(urlparse(self.path).query)
        print(query)

        if('oauth_token' in query):
            oauth_token = query['oauth_token'][0]
            oauth_verifier = query['oauth_verifier'][0]

            returntoken(self, oauth_token, oauth_verifier)

def runserver(server, handler,protocol="HTTP/1.0", port=80, bind=""):
    server_address = (bind, port)
    handler.protocol_version = protocol
    httpd = server(server_address, handler)
    sa = httpd.socket.getsockname()
    sever_message = "Serving HTTP on {host} port {port}"
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt recieved')
        sys.exit(0)

def returntoken(server, oauth_token, oauth_verifier):
    twitter = OAuth1Session(
                consumer_key,
                consumer_secret,
                oauth_token,
                oauth_verifier
            )
    
    response = twitter.post(
                'https://api.twitter.com/oauth/access_token',
                params={'oauth_verifier': oauth_verifier}
            )

    access_token = dict(parse_qsl(response.content.decode('utf-8')))

    print('consumer_key:', consumer_key)
    print('consumer_secret:', consumer_secret)
    print('access_tokens:', access_token)

    access_token.update({'consumer_key': consumer_key, 'consumer_secret': consumer_secret})
    body = json.dumps(access_token)
    print(body)
    server.wfile.write(body.encode('utf-8'))


def run():
    server = http.server.HTTPServer
    handler = EchoHandler
    runserver(server=server, handler=handler)

if __name__ == '__main__':
    oauth_callback = 'http://localhost'

    twitter = OAuth1Session(consumer_key, consumer_secret)

    response = twitter.post(
    'https://api.twitter.com/oauth/request_token',
    params={'oauth_callback': oauth_callback}
    )

    request_token = dict(parse_qsl(response.content.decode('utf-8')))

    authenticate_url = 'https://api.twitter.com/oauth/authenticate?oauth_token=%s' % (request_token['oauth_token'])

    webbrowser.open(authenticate_url)
    
    run()
    

