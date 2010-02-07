

Installing hostout.cloud
***************************

Add the collective.hostout part to your development buildout.

>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1
...
... [host1]
... recipe = collective.hostout
... extends = hostout.cloud
... hostname = blah
... hosttype = rackspacecloud
... path = /usr/local/plone/host1
... """
... )


>>> print system('bin/buildout -N')
Installing host1.
Generated script '/sample-buildout/bin/hostout'.

The generated script is run with a command and host(s) as arguments

>>> print system('bin/hostout host1 reboot')
cmdline is: bin/hostout host1 [host2...] [all] cmd1 [cmd2...] [arg1 arg2...]
Valid hosts are: host1
