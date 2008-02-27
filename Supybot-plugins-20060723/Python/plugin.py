###
# Copyright (c) 2003-2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import gc
import os
import re
import imp
import sys
import math
import inspect
import random
import string

# Stupid printing on import...
from cStringIO import StringIO
try:
    # We used to use sys.__stdout__ here, but that caused problems with
    # daemonization, since sys.stdout is replaced with a StringIO.
    original = sys.stdout
    sys.stdout = StringIO()
    import this
finally:
    sys.stdout = original

import supybot.utils as utils
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

L = [os.__file__]
if hasattr(math, '__file__'):
    L.append(math.__file__)
pythonPath = map(os.path.dirname, L)

class Python(callbacks.PluginRegexp):
    callBefore = ['Web']
    regexps = ['aspnRecipes']
    modulechars = string.ascii_letters + string.digits + '_.'
    def pydoc(self, irc, msg, args, name):
        """<python function>

        Returns the __doc__ string for a given Python function.
        """
        def normalize(s):
            return utils.str.normalizeWhitespace(s.replace('\n\n', '.  '))
        def getModule(name, path=pythonPath):
            if name in sys.modules:
                return sys.modules[name]
            else:
                parts = name.split('.')
                for name in parts:
                    try:
                        info = imp.find_module(name, path)
                        newmodule = imp.load_module(name, *info)
                        path = [os.path.dirname(newmodule.__file__)]
                        if info[0] is not None:
                            info[0].close()
                    except ImportError:
                        if parts == ['os', 'path']:
                            return os.path
                        else:
                            return None
                return newmodule
        if name.translate(utils.str.chars, self.modulechars) != '':
            irc.error('That\'s not a valid module or function name.')
            return
        if '.' in name:
            (moduleName, funcName) = utils.str.rsplit(name, '.', 1)
            if moduleName in __builtins__:
                obj = __builtins__[moduleName]
                if hasattr(obj, funcName):
                    obj = getattr(obj, funcName)
                    if hasattr(obj, '__doc__'):
                        irc.reply(normalize(obj.__doc__))
                    else:
                        irc.reply(format('%s has no documentation.', name))
                else:
                    s = format('%s has no method %s.', moduleName, funcName)
                    irc.reply(s)
            elif moduleName:
                newmodule = getModule(moduleName)
                if newmodule is None:
                    irc.error(format('No module %s exists.', moduleName))
                else:
                    if hasattr(newmodule, funcName):
                        f = getattr(newmodule, funcName)
                        if hasattr(f, '__doc__') and f.__doc__:
                            s = normalize(f.__doc__)
                            irc.reply(s)
                        else:
                            irc.error(format('%s has no documentation.', name))
                    else:
                        s = format('%s has no function %s.',
                                   moduleName, funcName)
                        irc.error(s)
        else:
            if name in sys.modules:
                newmodule = sys.modules[name]
                if hasattr(newmodule, '__doc__') and newmodule.__doc__:
                    irc.reply(normalize(newmodule.__doc__))
                else:
                    irc.reply(format('Module %s has no documentation.', name))
            elif name in __builtins__:
                f = __builtins__[name]
                if hasattr(f, '__doc__') and f.__doc__:
                    irc.reply(normalize(f.__doc__))
                else:
                    irc.error('That function has no documentation.')
            else:
                irc.error(format('No function or module %s exists.', name))
    pydoc = wrap(pydoc, ['somethingWithoutSpaces'])

    _these = [str(s) for s in this.s.decode('rot13').splitlines() if s]
    _these.pop(0) # Initial line (The Zen of Python...)
    def zen(self, irc, msg, args):
        """takes no arguments

        Returns one of the zen of Python statements.
        """
        irc.reply(utils.iter.choice(self._these))
    zen = wrap(zen)

    _title = re.compile(r'<b>(Title):</b>&nbsp;(.*)', re.I)
    _submit = re.compile(r'<b>(Submitter):</b>&nbsp;(.*)', re.I)
    _update = re.compile(r'<b>Last (Updated):</b>&nbsp;(.*)', re.I)
    _version = re.compile(r'<b>(Version) no:</b>&nbsp;(.*)', re.I)
    _category = re.compile(r'<b>(Category):</b>.*?<a href[^>]+>(.*?)</a>',
        re.I | re.S)
    _description = re.compile(r'<p><b>(Description):</b></p>.+?<p>(.+?)</p>',
        re.I | re.S)
    _searches = (_title, _submit, _update, _version, _category, _description)
    _bold = lambda self, g: (ircutils.bold(g[0]),) + g[1:]
    def aspnRecipes(self, irc, msg, match):
        r"http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/\d+"
        if not self.registryValue('aspnSnarfer', msg.args[0]):
            return
        url = match.group(0)
        s = utils.web.getUrl(url)
        resp = []
        for r in self._searches:
            m = r.search(s)
            if m:
                resp.append(format('%s: %s', *self._bold(m.groups())))
        if resp:
            resp = map(utils.web.htmlToText, resp)
            irc.reply('; '.join(resp), prefixNick=False)
    aspnRecipes = urlSnarfer(aspnRecipes)

    def objects(self, irc, msg, args):
        """takes no arguments

        Returns the number and types of Python objects in memory.
        """
        classes = 0
        functions = 0
        modules = 0
        strings = 0
        dicts = 0
        lists = 0
        tuples = 0
        refcounts = 0
        objs = gc.get_objects()
        for obj in objs:
            if isinstance(obj, str):
                strings += 1
            if isinstance(obj, tuple):
                tuples += 1
            elif inspect.isroutine(obj):
                functions += 1
            elif isinstance(obj, dict):
                dicts += 1
            elif isinstance(obj, list):
                lists += 1
            elif inspect.isclass(obj):
                classes += 1
            elif inspect.ismodule(obj):
                modules += 1
            refcounts += sys.getrefcount(obj)
        response = format('I have %i objects: %s modules, %s classes, %s '
                          'functions, %s dictionaries, %s lists, %s tuples, '
                          '%s strings, and a few other odds and ends.  I have '
                          'a total of %s references.',
                          len(objs), modules, classes, functions, dicts,
                          lists, tuples, strings, refcounts)
        irc.reply(response)
    objects = wrap(objects)


Class = Python


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
