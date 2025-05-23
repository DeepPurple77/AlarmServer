#!/usr/bin/python
## Alarm Server
## Supporting Envisalink 2DS/3
## Contributors: https://github.com/juggie/AlarmServer/graphs/contributors
## Compatibility: https://github.com/juggie/AlarmServer/wiki/Compatibility
##
## This code is under the terms of the GPL v3 license.

#python standard modules
import sys, getopt, os, glob, importlib.util

#alarm server modules
from core.config import config
from core.state import state
from core.events import events
from core import logger
from core import httpslistener
from core import envisalink
from core import envisalinkproxy

#TODO: move elsewhere
import tornado.ioloop

def main(argv):
    #welcome message
    logger.info('Alarm Server Starting')

    #set default config
    conffile='alarmserver.cfg'

    try:
        opts, args = getopt.getopt(argv, "c:", ["config="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            conffile = arg

    #load config
    config.load(conffile)

    #start logger
    if config.LOGTOFILE == True:
        logger.start(config.LOGFILE)
    else:
        logger.start()

    #enable the state
    state.init()

    #set version
    state.setVersion(0.3)

    #start envisalink client
    alarmclient = envisalink.Client()

    #start envisalink proxy
    alarmproxy = envisalinkproxy.Proxy()

    #start https server
    if config.HTTPS == True:
        httpsserver = httpslistener.start()

    #start http server
    if config.HTTP == True:
        httpserver = httpslistener.start(https = False)

    #load plugins - TODO: make this way better
    currpath = os.path.dirname(os.path.abspath(__file__))
    #plugins = glob.glob(currpath+"/plugins/*.py")
    plugins_files = glob.glob(os.path.join(currpath, "plugins", "*.py"))
    for p in plugins_files:
        #if str.find(p, '__init__.py') != -1: continue
        if '__init__.py' in p:
            continue

        base=os.path.basename(p)
        name=os.path.splitext(base)[0]
        
        spec = importlib.util.spec_from_file_location(name, p)
        module = importlib.util.module_from_spec(spec)

        sys.modules[name] = module
        spec.loader.exec_module(module)

        if hasattr(module, 'init'):
            module.init()
            print(f"Loaded plugin: {name}")
        else:
            print(f"Plugin {name} has no 'init' function.")

    #start tornado ioloop
    tornado.ioloop.IOLoop.instance().start()

if __name__=="__main__":
    main(sys.argv[1:])
