import application # App-specific definitions.
import triggers # Triggers and their objects.
import logging # Logging routines.
from twisted.internet.protocol import ClientFactory, ServerFactory # Factories which connect sockets to protocols.
from twisted.protocols.basic import LineReceiver # Protocol which which only does it's thing when \r\n is reached.
from twisted.internet import reactor # For opening connections to the MUD servers.

logger = logging.getLogger('Connection')

local_transports = [] # The list of local transports.

class RemoteProtocol(LineReceiver):
 """
 This protocol will talk to the MUD servers, sending all the received data back to the client.
 """
 def lineReceived(self, line):
  """A line has been received. Parse it and send it on it's way."""
  remote_factory.line = line
  if application.args.log_messages:
   logger.info('<Line: %s>', line)
  for t, m in triggers.match_trigger(line):
   if m:
    args = m.groups()
    kwargs = m.groupdict()
   else:
    args = []
    kwargs = {}
   t.eval(*args, **kwargs)
   if t.stop:
    break
  if remote_factory.line: # Only send the line if there's something to send.
   line += '\r\n' # Add new line characters to the line.
   for t in local_transports:
    t.write(line)
 
 def connectionMade(self):
  """Connection successful."""
  remote_factory.transport = self.transport # So the local connections can access it.

class RemoteFactory(ClientFactory):
 """
 This is the server factory.
 
 Any connections made to servers will be routed through this factory.
 """
 def __init__(self):
  self.transport = None # The transport who's write method will send stuff directly to the MUD.
  self.line = None # The line that was sent by the server.
 
 def buildProtocol(self, addr):
  """Twisted wants a protocol."""
  return RemoteProtocol()
 
 def clientConnectionMade(self, addr):
  """Connected."""
  logger.info('Connected to %s:%s.', addr.host, addr.port)

 def clientConnectionLost(self, connector, reason):
  """The connection was lost."""
  logger.info('Lost server connection: %s', reason.getErrorMessage())
  self.on_loseConnection()
 
 def clientConnectionFailed(self, connector, reason):
  """Could not establish a connection."""
  logger.critical('Could not establish connection: %s', reason.getErrorMessage())
  self.on_loseConnection()
 
 def on_loseConnection(self):
  """Just prevents duplicated code."""
  msg = 'Session ended.\r\n'
  for t in local_transports:
   t.write(msg)
   t.loseConnection()
  self.transport = None # Clear the transport so it can't be written too.

class LocalProtocol(LineReceiver):
 """
 This is the client protocol.
 
 It takes anything it's given and sends it to the MUD server.
 """
 def lineReceived(self, line):
  """Data received."""
  if application.args.log_commands:
   logger.info('<Command: %s>', line)
  if self.transport.authenticated: # No need to bug them again.
   remote_factory.transport.write(line + '\r\n')
  else:
   if application.args.username: # The user must authenticate.
    if self.transport.username: # They've already entered it, let's see if they've entered a password too...
     if self.transport.username == application.args.username and line == application.args.password: #Congratulations: They've entered the right authentication details.
      self.transport.write('Authentication successful. Now connecting to %s:%s.\r\n\r\n' % (application.args.host, application.args.port))
      self.do_connect()
     else:
      self.transport.write('Sorry, but the username or password you entered are incorrect.\r\nUsername: ')
      self.transport.username = None
    else:
     self.transport.username = line
     self.transport.write('Password: ')
 
 def connectionMade(self):
  """Connection has been made."""
  self.transport.username = None
  self.transport.authenticated = False # Set to true when they enter the right details.
  local_transports.append(self.transport)
  max = application.args.max_connections
  if max and len(local_transports) > max:
   self.transport.write('Sorry, but this server is only configured to accept %s incoming %s.\r\n' % (max, 'connection' if max == 1 else 'connections'))
   self.transport.loseConnection()
   logger.warning('Connection refused from %s because connection limit exceded.', self.transport.hostname)
  else:
   logger.info('Incoming connection from %s.', self.transport.hostname)
   if application.args.username:
    self.transport.write('This server requires authentication.\r\n\r\nUsername: ')
   else:
    self.do_connect()
 
 def do_connect(self):
  """Connect to the remote server."""
  self.transport.authenticated = True # Don't ask them for credentials again.
  if len(local_transports) == 1: # Only the connection that was just established.
   try:
    reactor.callFromThread(reactor.connectTCP, application.args.host, application.args.port, remote_factory)
    logger.info('Connected to MUD server.')
    return True # Connection successful.
   except Exception as e:
    logger.exception(e)
    self.transport.write('Could not connect to the remote server: %s', str(e))
    self.transport.loseConnection()
  return False # Either Exception was raised or there's already a  remote connection.
 
 def connectionLost(self, reason):
  """Connection was lost."""
  logger.info('Host %s disconnected: %s', self.transport.hostname, reason.getErrorMessage())
  local_transports.remove(self.transport) # Remove this connection from the local connections pool.

class LocalFactory(ServerFactory):
 """
 This is the client factory.
 
 Clients who connect will be routed through this factory.
 """
 def buildProtocol(self, addr):
  """Twisted expects a protocol if we want the host to connect (TODO: blacklist)."""
  return LocalProtocol()

remote_factory = RemoteFactory()

try:
 listener = reactor.listenTCP(application.args.local_port, LocalFactory()) # Store that so we can permit only one connection at a time.
 max = application.args.max_connections
 logging.info('Now listening on port %s. Max connections: %s.', application.args.local_port, max if max else 'unlimited')
except Exception as e:
 logger.exception(e)
 quit()

def send_local(string):
 """Write a string to all local transports."""
 string += '\r\n' # Save us doing this multiple times.
 for t in local_transports:
  t.write(string)

def remote_send(string):
 """Send a string to the remote server."""
 remote_factory.transport.write(string + '\r\n')
