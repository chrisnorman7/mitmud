if __name__ == '__main__': # Only run if this file has been called directly.
 import logging # Implement logging routines.
 import application # App-specific definitions.
 import os # OS-specific stuff.
 import connection # Starts the local process listening.
 import triggers # Give the start file access to the trigger mechanism.
 import commands # Give the start file access to the commands mechanism.
 from twisted.internet import reactor # The main event loop.
 from threading import Thread # Just in case scripts need to use threads.
 import json # Useful to have around for scripts.
 
 if application.args.file:
  if os.path.isfile(application.args.file):
   try:
    import sys, os # Need sys for sys.path, and os for os.path.
    sys.path.insert(0, os.path.dirname(application.args.file))
    execfile(application.args.file)
   except Exception as e:
    logging.exception(e)
    quit()
  else:
   quit('Cannot load from start file: %s.' % application.args.file)
 if not application.args.server or not application.args.port:
  quit('No server information supplied. Either include it in your script files by setting application.args.server and application.args.port, or on the command line with the -s and -p switches.')
    
 try:
  reactor.listenTCP(application.args.local_port, connection.LocalFactory()) # Start listening.
  max = application.args.max_connections
  logging.info('Now listening on port %s. Max connections: %s.', application.args.local_port, max if max else 'unlimited')
 except Exception as e:
  logging.exception(e)
  quit()
 
 logging.info('Destination: %s:%s.', application.args.server, application.args.port)
 
 reactor.run()
 logging.info('Server finished.')
