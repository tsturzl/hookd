# -*- coding: utf-8 -*-
import yaml
import subprocess
from twisted.internet.defer import Deferred
from twisted.internet.fdesc import readFromFD, setNonBlocking
from twisted.internet.protocol import ProcessProtocol
from twisted.internet import reactor

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
    self.configPath = "/etc/hookd.conf"
    self.hookName = hookName
    self.json = json
    self.d = Deferred()

  def getConf(self):
    try:
      conf = with open(self.configPath) as f:
        fd = f.filename()
        setNonBlocking(fd)
        readFromFD(fd, self.runConf)
    except IOError, e:
      self.d.errback(e)

  def runConf(self, conf):
    try:
      config = yaml.load(conf)
      cmd = config[self.hookName]['cmd']
      env = config[self.hookName]['env'] if 'env' in config[self.hookName] else None
      self.run(cmd, args, env)
    except KeyError, e:
      self.d.errback(e)
    except yaml.YAMLError, e:
      self.d.errback(e)

  def run(self, cmd, env):
    p = SubprocessProtocol()
    reactor.spawnProcess(p, cmd, env=env)
    p.d.addCallback(self.d.callback)