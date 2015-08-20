"""
MitMud commands.

The parser will look through the keys of the commands dictionary to find a command that matches, then call that command as command(line), where line is the remainder of the line from the user.

A convenience function parse_args is available which will set command.args to the parsed command line arguments and return True upon success, or False on failure. Thus, a typical command's __call__ method could look like this:

def __call__(self, line):
 if self.parse_args(line):
  # statements...
"""

import argparse, connection

commands = {}

class ArgumentError (Exception):
 pass

class CommandParser(argparse.ArgumentParser):
 def error(self, msg):
  """Overridden because the default error quit()s."""
  raise CommandError(msg)

class Command(object):
 """A command object."""
 def __init__(self, name):
  """Initialise the command."""
  self.name = name
  self.args = None
  self.parser = CommandParser(prog = name, version = 'Irrelevant')
  commands[name] = self
 
 def parse_args(self, line):
  """Parse the args provided in line and make them available to the programmer as self.args."""
  try:
   self.args = self.parser.parse_args(line.split())
   return True
  except ArgumentError as e:
   connection.local_send(e.message)
   self.args = None
   return False
 
 def __call__(self, line):
  """Make this command callable."""
  raise NotImplementedError("This command hasn't had it's __call__ method overridden yet.")
