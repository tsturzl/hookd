# -*- coding: utf-8 -*-
import sys
import os
import logging
from __future__ import print_function
from klein import Klein
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.internet.error import ProcessTerminated
from hook import Hook

ENV = os.environ['PY_ENV']

if(ENV is "test"):
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.ERROR)

try:
  import json
except ImportError:
  import simplejson as json

class NotFound(Exception):
  pass

class App(object):
  app = Klein()

  @app.handle_errors(NotFound)
  def notfound(self, request, failure):
    request.setResponseCode(404)
    return 'Missing'

  @app.route('/hook/<string:hookName>', methods=['POST'])
  @inlineCallbacks
  def hook(self, request, hookName):
    try:
      #make sure json is valid and unprettified
      body = json.dumps(json.loads(request.content.read()))

      H = Hook(hookName, body)
      result = yield H.d

      returnValue(result)
    except ValueError, e:
      logging.error(hookName + " Called with invalid JSON")
      logging.debug(e)
      raise NotFound()
    except ProcessTerminated, e:
      logging.error(hookName + " Command exited with a non-zero code(unsuccessful)")
      logging.debug(e)
      logging
      raise NotFound()