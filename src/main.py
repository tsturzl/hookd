# -*- coding: utf-8 -*-
import sys
import os
import logging
from klein import Klein
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.internet.error import ProcessTerminated
from hook import Hook

ENV = os.environ['PY_ENV']

logger = logging.getLogger()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler(sys.stdout)
if(ENV is "test"):
  logger.setLevel(logging.DEBUG)
  ch.setLevel(logging.DEBUG)
else:
  logger.setLevel(logging.ERROR)
  ch.setLevel(logging.ERROR)

ch.setFormatter(formatter)
logger.addHandler(ch)

try:
  import json
except ImportError:
  import simplejson as json

class NotFound(Exception):
  pass

class App(object):
  app = Klein()

  def __init__(self):
    self.app.run("localhost", 3000)

  @app.handle_errors(NotFound)
  def notfound(self, request, failure):
    request.setResponseCode(404)
    return 'Missing'

  @app.route('/hook/<string:hookName>', methods=['POST'])
  @inlineCallbacks
  def hook(self, request, hookName):
    try:
      logger.info("Hook called: " + hookName)

      #make sure json is valid and unprettified
      body = json.dumps(json.loads(request.content.read()))

      H = Hook(hookName, body)
      result = yield H.d

      returnValue(result)
    except ValueError, e:
      logger.error(hookName + " Called with invalid JSON")
      logger.debug(e)
      raise NotFound()
    except ProcessTerminated, e:
      logger.error(hookName + " Command exited with a non-zero code(unsuccessful)")
      logger.debug(e)
      raise NotFound()

if __name__ == "__main__":
  App()