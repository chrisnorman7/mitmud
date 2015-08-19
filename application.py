name = 'MitMud'
version = '0.1'
description = 'The client-agnostic MUD proxy'

import argparse # Parse command line arguments.
import sys # System-related stuff.

parser = argparse.ArgumentParser(prog = name, version = version) # Add all command line arguments to this.

parser.add_argument('host', type = str, help = 'The MUD hostname')
parser.add_argument('port', type = int, help = 'The port the MUD server is running on')
parser.add_argument('-p', '--localport', dest = 'local_port', nargs = '?', metavar = 'port', default = 1234, type = int, help = 'The local port %(prog)s should run on')
parser.add_argument('-c', '--command-char', nargs = '?', default = '/', help = 'The character which indicates this is a %(prog)s command')
parser.add_argument('-l', '--logfile', dest = 'log_file', metavar = 'filename', type = argparse.FileType('w'), default = sys.stderr, help = 'Log %(prog)s output')
parser.add_argument('-L', '--loglevel', dest = 'log_level', nargs = '?', default = 'info', choices = ['debug', 'info', 'warning', 'error', 'critical'], help = 'The log level')
parser.add_argument('-F', '--logformat', dest = 'log_format', metavar = 'format', nargs = '?', default = '[%(asctime)s] %(name)s -> %(levelname)s: %(message)s', help = 'The format for log messages')
parser.add_argument('-M', '--log-messages', action = 'store_true', help = 'Log messages coming from the server')
parser.add_argument('-C', '--log-commands', action = 'store_true', help = 'Log commands coming from clients')

args = parser.parse_args() # Options get added to this object.
