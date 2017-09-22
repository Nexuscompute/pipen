#!/usr/bin/env python
"""
Generate API docs for pyppl
"""
import sys, os, inspect
sys.path.insert (0, os.path.dirname(__file__))
import pyppl


modules = [
	'PyPPL', 'Proc', 'Channel', 'Job', 'Aggr', 'Flowchart', 'Parameter', 'Parameters', 
	'logger', 'utils', 
	'templates.TemplatePyPPL', 'templates.TemplateJinja2',
	'runners.Runner', 'runners.RunnerQueue', 'runners.RunnerLocal', 'runners.RunnerSsh', 'runners.RunnerSge', 'runners.RunnerSlurm', 'runners.RunnerDry', 
]

excludes = [
	"Box", "Process", "Pipe", "Popen", "ProcessEx", "S_IEXEC", "__builtins__", "__doc__", "__file__", "__name__", "__package__", "__module__", "__str__", "__dict__", "__weakref__", "__repr__"
]

doc = """
# API
<!-- toc -->
"""

def getDoc(module, name):
	sys.stderr.write('- Generating doc for %s ... \n' % name)
	ret = ''
	ret += "\n## Module `" + modname + "`  \n"
	ret += "> "
	ret += (module.__doc__ if module.__doc__ is not None else ".").lstrip()
	ret += "\n\n"
	for m in sorted(module.__dict__.keys()):
		if m in excludes: continue
		sys.stderr.write('  * %s\n' % m)
		if m.startswith('__') and m!='__init__': continue
		mobj = getattr(module, m)
		if not callable (mobj): continue
		if inspect.isclass (mobj):
			ret += "#### `class: " + m + "`\n"
			ret += "```\n" + (mobj.__doc__.strip() if mobj.__doc__ is not None else "") + "\n```\n"
			continue
		try:
			args = tuple(inspect.getargspec(mobj))
		except Exception as ex:
			pass

		strargs  = args[0]
		if args[1] is not None: strargs.append ("*" + str(args[1]))
		if args[2] is not None: strargs.append ("**" + str(args[2]))
		isstatic = "[@staticmethod]" if type(mobj) == type(lambda x:x) and modname!="utils" else ""
		ret += "#### `" + m + " (%s) %s`\n" % (", ".join(strargs), isstatic)			
		modoc = mobj.__doc__ if mobj.__doc__ is not None else ""
		modoc = modoc.split("\n")
		for line in modoc:
			line = line.strip()
			if line.startswith ("@"):
				ret += "\n- **" + line[1:] + "**  \n"
			else:
				ret += line + "  \n"
	return ret


for modname in modules:
	
	if '.' not in modname:
		if not hasattr(pyppl, modname):
			continue

		module = getattr (pyppl, modname)
		doc += getDoc(module, modname)
	
	else:
		ns, mod = modname.split('.')
		module  = getattr(getattr(pyppl, ns), mod)
		doc += getDoc(module, modname)
	
open (os.path.join( os.path.dirname(__file__), 'docs', 'api.md' ), 'w').write (doc)
#print template
sys.stderr.write('- Done!\n')
			
	
