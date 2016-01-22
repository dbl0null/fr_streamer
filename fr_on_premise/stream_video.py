from fr_on_premise.websocket_client import *

import functools
import json
import time
import cv2

class StreamVideo(WebSocketClient):

    def __init__(self):
        self.connect_timeout = DEFAULT_CONNECT_TIMEOUT
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.time_out_stream = None
        self.original_frame = None
        self.stream_id = -1
        

    def _on_message(self, msg):
        ores = json.loads(msg)
        self.client.on_message(self.original_frame, ores, self.stream_id)
        self.call_stream()


    def call_stream(self):
        if self.time_out_stream is not None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)

        self.stream()
        deadline = time.time() + 10
        self.time_out_stream = ioloop.IOLoop().instance().add_timeout(deadline, self.close)

    
    def config(self, stream_path, ws_url, stream_id, client):
        self.video = cv2.VideoCapture(stream_path)
        self.client = client
        self.stream_id = stream_id
        if self.video.isOpened() == False:
            print('problem opening', stream_path)
            return

        self.connect(ws_url)


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(data, binary=True)


    def _on_connection_success(self):
        self.stream()


    def _on_connection_close(self):
        if self.time_out_stream is not None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)


    @gen.coroutine
    def stream(self):
        print('streaming!!!')
        ret, self.original_frame = self.video.read()

        if self.original_frame is None:
            print('Closing')
            self.close()
            return

        frame = cv2.cvtColor(self.original_frame, cv2.COLOR_BGR2GRAY)
        _, framecomp = cv2.imencode('.jpg', frame)

        self.send(framecomp.tobytes())
