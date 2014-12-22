#!/usr/local/Python-2.7.3/python

# See LICENSE file
"""
A tornado web service for handling TaskQueue request from application servers.
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web
import time


# Default port this service runs on.
SERVER_PORT = 64839

# Global for Distributed TaskQueue.
task_queue = None

class MultiprocessHandler(tornado.web.RequestHandler):
  """ A multiprocess handler can be called with threaded = true
      or false
  """
  def initialize(self, threaded):
    self._threaded = threaded
    self._q = multiprocessing.Queue
  def start_process(self, worker, callback):
    """starts process and watcher thread"""
    self._callback = callback

    if self._threaded:
      multiprocessing.Process(target=worker , args=(self._q)).start()
      threading.Thread(target=self._watcher).start()
    else:
      worker(self._q)
      self.watcher()

  def _watcher(self):
    """watches the queue for process result"""
    while self._q.empty():
      time.sleep(0)

    response = self._q.get(False)
    tornado.ioloop.IOLoop.add_callback(lambda: self._callback(response))

class StopWorkerHandler(tornado.web.RequestHandler):
  """ Stops task queue workers for an app if they are running. """
  @tornado.web.asynchronous
  def post(self):
    """ Function which handles POST requests. Data of the request is
        the request from the AppController in an a JSON string.
    """
    
    request = self.request
    http_request_data = request.body
    json_response = task_queue.stop_worker(http_request_data)
    self.write(json_response)
    self.finish()

  @tornado.web.asynchronous
  def get(self):
    """ Handles get request for the web server. Returns the worker
        status in json.
    """
    time.sleep(5)
    self.write('{"status":"up"}')
    self.finish()

class StartWorkerHandler(tornado.web.RequestHandler):
  """ Starts task queue workers for an app if they are not running. """
  @tornado.web.asynchronous
  def post(self):
    """ Function which handles POST requests. Data of the request is
        the request from the AppController in an a JSON string.
    """
    request = self.request
    http_request_data = request.body
    json_response = task_queue.start_worker(http_request_data)
    self.write(json_response)
    self.finish()

  @tornado.web.asynchronous
  def get(self):
    """ Handles get request for the web server. Returns the worker
        status in json.
    """
    time.sleep(5)
    self.write('{"status":"up"}')
    self.finish()

class MainHandler(tornado.web.RequestHandler):
  """
  Defines what to do when the webserver receieves different
  types of HTTP requests.
  """
  def unknown_request(self, app_id, http_request_data, pb_type):
    """ Function which handles unknown protocol buffers.

    Args:
      app_id: Name of the application.
      http_request_data: The encoded protocol buffer from the AppServer.
    Raise:
      NotImplementedError: This unknown type is not implemented.
    """
    raise NotImplementedError("Unknown request of operation %s" % pb_type)

  @tornado.web.asynchronous
  def post(self):
    """ Function which handles POST requests. Data of the request is
        the request from the AppServer in an encoded protocol buffer
        format.
    """
    request = self.request
    http_request_data = request.body
    pb_type = request.headers['protocolbuffertype']
    app_data = request.headers['appdata']
    app_data  = app_data.split(':')
    app_id = app_data[0]

    if pb_type == "Request":
      self.remote_request(app_id, http_request_data)
    else:
      self.unknown_request(app_id, http_request_data, pb_type)

    self.finish()

  @tornado.web.asynchronous
  def get(self):
    """ Handles get request for the web server. Returns that it is currently
        up in json.
    """
    time.sleep(5)
    self.write('{"status":"up"}')
    self.finish()

 

def main():
  """ Main function which initializes and starts the tornado server. """
  tq_application = tornado.web.Application([
    # Takes json from AppController
    (r"/startworker", StartWorkerHandler),
    (r"/stopworker", StopWorkerHandler),
    # Takes protocol buffers from the AppServers
    (r"/*", MainHandler)
  ])

  server = tornado.httpserver.HTTPServer(tq_application)
  server.bind(SERVER_PORT)
  while 1:
    try:
     server.start(0)
     tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
      print "Server interrupted by user, terminating..."
      exit(1)
if __name__ == '__main__':
  main()




