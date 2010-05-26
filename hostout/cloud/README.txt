
hostout.cloud let's you build whole new application clusters in a matter of minutes.

Building on the power of collective.hostout_, buildout_ and fabric_ just few lines of configuration
and a single command is all thats needed to deploy apache, squid, mysql, zope, plone, django...


Installing hostout.cloud
************************

Add the collective.hostout part to your development buildout. Using the extends
option we add hostout.cloud to handle creating a host and hostout.ubuntu
to bootstrap that host ready for deployment.

>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1 helloworld
...
... [helloworld]
... recipe = zc.recipe.egg:scripts
... eggs = zc.recipe.egg
... initialization = import sys
...   main=lambda: sys.stdout.write('all your hosts are below to us!!!')
... entry-points = helloworld=__main__:main
...
... [host1]
... recipe = collective.hostout
... extends = hostout.cloud hostout.ubuntu
... hostsize - 256
... hostos = Ubuntu 9.10
... hosttype = rackspacecloud
... key = myaccount
... secret = myapikey
... """
... )


>>> print system('bin/buildout -N')
Installing host1.
Generated script '/sample-buildout/bin/hostout'.


Now with a single command everything is done for us

>>> print system('bin/hostout host1 deploy')

Our local environment
>>> print system('bin/helloworld')
all your hosts are below to us!!!

is now deployed to the cloud
>>> print system('bin/hostout host1 run bin/helloworld')
all your hosts are below to us!!!

Change your local code and just run deploy again
>>> print system('bin/hostout host1 deploy')

Reboot your server
>>> print system('bin/hostout host1 reboot')

and destroy it when you're done
>>> print system('bin/hostout host1 destroy')




Supported Cloud providers
*************************

hostout.cloud uses libcloud_. See the libcloud_ site for the supported serviers and options
for each.

Currently rackspace cloud and Ec2 are all thats tested.

Common options
**************

hostname
  Unique name to create the VM

hostsize
  The desired RAM size in MB. You will get the closet VM with at least this size

Rackspace
*********

key
  your username
  
secret
  your api password

hostos
  the title of the OS as shown on the distributions selection list
  
Amazon Ec2
**********

key
  

secret
  api secret key

key_filename
  path to your pem file

hostos
  is set to the image title



