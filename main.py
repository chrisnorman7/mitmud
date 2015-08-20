if __name__ == '__main__': # Only run if this file has been called directly.
 import logging # Implement logging routines.
 import application # App-specific definitions.
 import connection # Starts the local process listening.
 
 from twisted.internet import reactor # The main event loop.
 logging.info('Destination: %s:%s.', application.args.host, application.args.port)
 
 reactor.run()
 logging.info('Server finished.')
