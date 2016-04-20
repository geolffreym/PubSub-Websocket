# PubSub Websocket Server
A simple Python PubSub Websocket

Run the requirements.txt 
`pip install -r requirements.txt`

Run the server
`python server.py`

###A simple websocket javascript client
```js
        var jwt = 'token1234589$%KRT_MK';
        var channels = ['my_channel','my_channel2']
       
        //Token is needed to authenticate user
        //Channels to suscribe
        
        var _socket = new WebSocket(
            'ws://127.0.0.1:9000?token=' + jwt + '&channels=' + JSON.stringify(channels)
        );

        _socket.addEventListener('open', function () {
            console.log('open')
            
            _socket.send(
                JSON.stringify({
                    "channel": "my_channel",
                    "message":{"content": "Hi", "my_name": "Clone Mena"}
                })
            );
        });

        _socket.addEventListener('message', function (e) {
            console.log(e)
        });
```
