import logging # Implement logging routines.
import application # App-specific definitions.

from twisted.internet import reactor # The main event loop.

logging.basicConfig(stream = application.args.log_file, level = application.args.log_level.upper(), format = application.args.log_format)
logging.info('Destination: %s:%s.', application.args.host, application.args.port)

from connection import LocalFactory, RemoteFactory

local_factory = LocalFactory()
remote_factory = RemoteFactory()

reactor.listenTCP(application.args.local_port, local_factory)
logging.info('Now listening on port %s.', application.args.local_port)

reactor.run()
logging.info('Server finished.')
