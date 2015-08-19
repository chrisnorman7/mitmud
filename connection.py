import application # App-specific definitions.
from twisted.internet.protocol import ClientFactory, ServerFactory # Factories which connect sockets to protocols.
from twisted.protocols.basic import LineReceiver # Protocol which which only does it's thing when \r\n is reached.

class RemoteProtocol(LineReceiver):
 """
 This protocol will talk to the MUD servers, sending all the received data back to the client.
 """
 def lineReceived(self, line):
  """A line has been received. Parse it and send it on it's way."""
  local_factory.transport.write(line + '\r\n')
  if application.args.log_messages:
   logging.info('<Line: %s>', line)
 
 def connectionMade(self):
  """Connection successful."""
  remote_factory.transport = self.transport

class RemoteFactory(ClientFactory):
 """
 This is the server factory.
 
 Any connections made to servers will be routed through this factory.
 """
 def __init__(self):
  self.transport = None # The transport who's write method will send stuff directly to the MUD.
 
 def buildProtocol(self, addr):
  """Twisted wants a protocol."""
  return RemoteProtocol()
 
 def clientConnectionMade(self, addr):
  """Connected."""
  logging.info('Connected to %s:%s.', addr.host, addr.port)

 def clientConnectionLost(self, connector, reason):
  """The connection was lost."""
  logging.info('Lost server connection: %s', reason.getErrorMessage())
  self.transport = None # Clear the transport so it can't be written too.
  local_factory.transport.loseConnection()
 
 def clientConnectionFailed(self, connector, reason):
  """Could not establish a connection."""
  logging.critical('Could not establish connection: %s', reason.getErrorMessage())
  self.transport = None # Clear the transport so it can't be written too.
  local_factory.transport.loseConnection()

class LocalProtocol(LineReceiver):
 """
 This is the client protocol.
 
 It takes anything it's given and sends it to the MUD server.
 """
 def lineReceived(self, line):
  """Data received."""
  remote_factory.transport.write(line + '\r\n')
  if application.args.log_commands:
   logging.info('<Command: %s>', line)
 
 def connectionMade(self):
  """Connection has been made."""
  logging.info('Incoming connection from %s.', self.transport.hostname)
  local_factory.transport = self.transport
  try:
   reactor.connectTCP(application.args.host, application.args.port, remote_factory)
   logging.info('Connected to MUD server.')
  except Exception as e:
   logging.exception(e)
 
 def connectionLost(self, reason):
  """Connection was lost."""
  logging.info('Host %s disconnected.', self.transport.hostname)
  local_factory.transport = None

class LocalFactory(ServerFactory):
 """
 This is the client factory.
 
 Clients who connect will be routed through this factory.
 """
 def __init__(self):
  self.transport = None # The transport who's write method will send stuff back to the connected clients.
 
 def buildProtocol(self, addr):
  """Twisted expects a protocol if we want the host to connect (TODO: blacklist)."""
  print [x for x in dir(addr) if not x.startswith('_')]
  return LocalProtocol()
