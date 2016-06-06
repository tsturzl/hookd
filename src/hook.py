# -*- coding: utf-8 -*-
import yaml
import subprocess
import os
import sys
import logging
from twisted.internet.defer import Deferred
from twisted.internet.fdesc import readFromFD, setNonBlocking
from twisted.internet.protocol import ProcessProtocol
from twisted.internet.error import ProcessDone
from twisted.internet import reactor


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

class SubprocessProtocol(ProcessProtocol):
    outBuffer = ""
    errBuffer = ""

    def connectionMade(self):
        self.d = Deferred()

    def outReceived(self, data):
        self.outBuffer += data

    def errReceived(self, data):
        self.errBuffer += data

    def processEnded(self, reason):
        if reason.check(ProcessDone):
            self.d.callback(self.outBuffer)
        else:
            self.d.errback(reason)

class Hook(object):

  def __init__(self, hookName, json):
    logger.debug("Hook constructor")
    self.configPath = "/etc/hookd.conf"
    self.hookName = hookName
    self.json = json
    self.d = Deferred()
    self.getConf()

  def getConf(self):
    try:
      logger.debug("Getting config file")
      with open(self.configPath) as f:
        fd = f.fileno()
        setNonBlocking(fd)
        readFromFD(fd, self.runConf)
    except IOError, e:
      self.d.errback(e)

  def runConf(self, conf):
    try:
      logger.debug("Running config file")
      config = yaml.load(conf)
      cmd = config[self.hookName]['cmd']
      env = config[self.hookName]['env'] if 'env' in config[self.hookName] else None
      self.run(cmd, env)
    except KeyError, e:
      self.d.errback(e)
    except yaml.YAMLError, e:
      self.d.errback(e)

  def run(self, cmd, env):
    print cmd
    logger.debug("Running subprocess")
    p = SubprocessProtocol()
    reactor.spawnProcess(p, cmd, [cmd, self.json], env=env)
    p.d.addCallback(self.d.callback)