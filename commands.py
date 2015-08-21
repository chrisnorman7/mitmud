"""
MitMud commands.

The parser will look through the keys of the commands dictionary to find a command that matches, then call that command as command(line), where line is the remainder of the line from the user.

A convenience function parse_args is available which will set command.args to the parsed command line arguments and return True upon success, or False on failure. Thus, a typical command's __call__ method could look like this:

def __call__(self, transport, line):
 if self.parse_args(line):
  # statements...
  # Transport is the transport that issued the command.
"""

import argparse, connection, application, datetime

commands = {}

class ArgumentError (Exception):
 pass

class CommandParser(argparse.ArgumentParser):
 def error(self, msg):
  """Overridden because the default error quit()s."""
  raise ArgumentError(msg)
 
 def __init__(self, command, *args, **kwargs):
  self.command = command
  super(CommandParser, self).__init__(*args, **kwargs)
  self.exited = False # The program would have exited if I hadn't lobotomised it.
 
 def _print_message(self, message, file = None):
  """Send the message to the transport, rather than stdout."""
  return super(CommandParser, self)._print_message(message, self.command.transport)
 
 def exit(self, code = 0, message = None):
  """Don't let it exit really."""
  print 'Called.'
  self.exited = True # Tell parse_args to give up.
  if message:
   self.command.transport.write(message + '\r\n')

class Command(object):
 """A command object."""
 def __init__(self, name):
  """Initialise the command."""
  self.name = name
  self.args = None
  self.parser = CommandParser(self, prog = name, version = 'No version information available.')
  commands[self.name] = self
  self.transport = None
 
 def parse_args(self, line):
  """Parse the args provided in line and make them available to the programmer as self.args."""
  self.parser.exited = False # Reset it.
  try:
   self.args = self.parser.parse_args(line.split())
   return not self.parser.exited # If it was supposed to exit, then we should too.
  except ArgumentError as e:
   if self.transport:
    self.transport.write(e.message + '\r\n')
   self.args = None
   return False
 
 def __call__(self, transport, line):
  """Make this command callable."""
  self.transport = transport

class Quit(Command):
 """Closes your session without disconnecting the MUD."""
 def __init__(self):
  super(Quit, self).__init__('quit')
 
 def __call__(self, transport, line):
  """This command takes no arguments."""
  super(Quit, self).__call__(transport, line)
  if line:
   connection.send_local('This command takes no arguments.')
  else:
   transport.write('Goodbye.\r\n')
   transport.loseConnection()

Quit()

class Stats(Command):
 """Shows statistics about the state of MitMud."""
 def __init__(self):
  super(Stats, self).__init__('stats')
  p = self.parser # Saves typing.
  p.add_argument('-u', '--uptime', action = 'store_true', help = 'Displays uptime')
  p.add_argument('-l', '--lines', action = 'store_true', help = 'Shows lines received from server')
  p.add_argument('-c', '--commands', action = 'store_true', help = 'Shows commands sent from client.')
  p.add_argument('-t', '--transports', action = 'store_true', help = 'Shows the number of connected clients')
 
 def __call__(self, transport, line):
  super(Stats, self).__call__(transport, line)
  if self.parse_args(line):
   a = self.args # Save typing again.
   transport.write('Statistics:\r\n')
   if not a.uptime and not a.lines and not a.commands and not a.transports:
    for thing in ['uptime', 'lines', 'commands', 'transports']:
     setattr(a, thing, True)
   if a.uptime:
    transport.write('Uptime: %s\r\n' % str(datetime.datetime.now() - application.start))
   if a.lines:
    transport.write('Lines received from server: %s\r\n' % connection.remote_lines)
   if a.commands:
    transport.write('Commands received from clients: %s\r\n' % connection.local_lines)
   if a.transports:
    transport.write('Number of connected clients: %s\r\n' % len(connection.local_transports))

Stats()
