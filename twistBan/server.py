###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Geolffrey Mena
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################


import sys
import os
import json
import redis

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from mixin.jwt.JWT import JWTHandler as jwt
from autobahn.websocket.types import ConnectionDeny
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory, listenWS


# CHANNELS = {
#     'client_channel': 'CLIENT_CHANNEL',
#     'movies_channel': 'MOVIES_CHANNEL'
# }

class Listener(object):
    """Handle listeners"""

    def __init__(self, protocol):
        try:
            # self.redis = r
            self.pubsub = protocol.r.pubsub()
            self.protocol = protocol

            # Sanitized channels
            channels = self.sanitize_channels(protocol)

            self.pubsub.subscribe(**channels)
            self.thread = self.pubsub.run_in_thread(sleep_time=0.001)
        except Exception as e:
            print e

    def handle_msg(self, item):
        print "\n Sending message to " + self.protocol.user
        self.protocol.sendMessage(
            item['data']
        )

    def sanitize_channels(self, protocol):
        # Handle channels
        true_channels = {}

        print "\nSuscribed channels for " + protocol.user
        for ch in protocol.channels:
            print ch + "\n"
            true_channels.update(**{
                ch: self.handle_msg
            })

        return true_channels

    def clear(self, protocol):
        # Sanitized channels
        # self.thread.stop()
        print "\nCleaning channels"
        channels = self.sanitize_channels(protocol)
        self.pubsub.unsubscribe(channels)


# The Protocol Handler WebSocket
class ServerProtocol(WebSocketServerProtocol):
    user = None
    channels = None

    def onOpen(self):
        print "Connection open"

    def onConnect(self, request):
        token = request.params.get('token')
        # Token needed
        if not token:
            print 'Rejected connection: Token needed'
            raise ConnectionDeny

        # Validate token
        token = str(token[0])
        keys = jwt.jwt_prepare_keys()

        try:
            # Handle valid token
            if not jwt.jwt_verify(keys, token):
                print 'Rejected connection: Invalid token'
                raise ConnectionDeny

            # Get token content
            payload = json.loads(
                jwt.jwt_decode_handler(
                    keys, token
                )
            )

            # User data
            self.user = payload['email']
            self.channels = request.params.get('channels')

            # Invalid channels
            if not self.channels:
                raise ConnectionDeny

        except (Exception, UnicodeDecodeError) as e:
            raise ConnectionDeny

        # Get channels
        self.channels = list(json.loads(
            self.channels[0]
        ))

        print 'Trying connect from ' + request.host
        print 'Connecting user ' + self.user
        print "Client connecting: {}".format(request.peer)
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            self.factory.handleMessage(payload, self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


# The Factory
class ServerFactory(WebSocketServerFactory):
    def __init__(self, url, redis):
        WebSocketServerFactory.__init__(self, url)
        self.client = {}
        self.protocol.r = redis

    def register(self, protocol):
        print("Registered client {}".format(protocol.user))
        # Handle protocols
        self.client[protocol.user] = Listener(
            protocol
        )

    def unregister(self, protocol):
        # Protocol needed to close
        if protocol.user:
            print("Unregistered client {}".format(protocol.user))
            self.client[protocol.user].clear(protocol)
        else:
            print 'Undefined Error'

    def handleMessage(self, msg, protocol):
        try:
            msg = json.loads(msg)
            channel = msg['channel']

            # Handle message
            message = msg['message']
            message = json.dumps(message)

            print 'Trying send message to ' + channel
            protocol.r.publish(channel, message)
        except Exception as e:
            print e
            pass


if __name__ == '__main__':
    from twisted.internet import reactor

    # Redis server
    r_server = redis.StrictRedis(
        host='localhost', port='6379', db=0
    )

    # Make server factory
    factory = ServerFactory(
        url="ws://127.0.0.1:9500",
        redis=r_server
    )

    # Conf protocol factory
    factory.protocol = ServerProtocol
    factory.isServer = True
    # factory.setProtocolOptions(
    #     allowedOrigins=[
    #         'http://127.0.0.1:8000',
    #         "http://localhost:9500"
    #     ]
    # )

    # Listen port
    listening_port = listenWS(factory)
    print "Listening on " + str(listening_port.port)
    reactor.run()


    # webdir = File("/tmp")
    # web = Site(webdir)
    # reactor.listenTCP(port, factory)
