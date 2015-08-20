import re # Regular expressions.
import logging # Logging routines.
import connection # For the factory objects.

logger = logging.getLogger('Triggers')

triggers = [] # All the loaded triggers.
litteral_triggers = {} # The exact-match triggers.

class Trigger(object):
 """A trigger object."""
 def __init__(self, trigger, code, regexp = True, stop = False, mode = 'exec', title = None):
  """
  Create a new trigger object.
  
  trigger: The line which should trigger this trigger.
  code: The code which should be executed when the trigger is matched.
  regexp: True if trigger is a regular expression, False otherwise.
  stop: Stop trying to match triggers after this trigger has been reached.
  mode: The compile mode.
  title: The title of this trigger.
  """
  if regexp:
   self.trigger = re.compile(trigger)
   triggers.append(self)
  else:
   self.trigger = trigger
   litteral_triggers[trigger] = self
  self.compile_mode = mode
  self.title = title if title else trigger
  self.set_code(code)
  self.regexp = regexp
  self.stop = stop
  logger.info('Added %s trigger: %s.', 'regexp' if regexp else 'litteral', self.title)
 
 def get_code(self):
  """Return the plain text version of the trigger's code."""
  return self._code
 
 def set_code(self, code):
  """Set the code for this trigger."""
  self._code = code
  self.code = compile(code, '<Trigger: %s>' % self.title, self.compile_mode)
 
 def eval(self, *args, **kwargs):
  """Execute this trigger's code."""
  kwargs['trigger'] = self
  kwargs['Trigger'] = Trigger
  kwargs['connection'] = connection
  try:
   eval(self.code, dict(args = args, **kwargs))
  except Exception as e:
   logger.exception(e)
   connection.send_local('Error in trigger %s: %s' % (self.title, str(e)))

def match_trigger(line):
 """Match a trigger given a line of text."""
 results = [] # The list of triggers that match.
 if line in litteral_triggers:
  t = literal_triggers[line]
  results.append((t, None))
  if t.stop:
   return results
 for trigger in triggers:
  m = trigger.trigger.match(line)
  if m:
   results.append((trigger, m))
   if trigger.stop:
    break
 return results
