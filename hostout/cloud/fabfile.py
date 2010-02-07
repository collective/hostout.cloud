import os
import os.path
import libcloud
from libcloud.types import Provider 
from libcloud import providers
import inspect
from fabric import api
  
#drivers = [ EC2('access key id', 'secret key'), 
#            Slicehost('api key'), 
#            Rackspace('username', 'api key') ] 

def _driver():
    hostout = api.env.get('hostout')
    hosttype = hostout.options.get('hosttype')
    #EC2_US_EAST	Amazon AWS US N. Virgina
    #EC2_US_WEST	Amazon AWS US N. California
    #EC2_EU_WEST	Amazon AWS EU Ireland
    #RACKSPACE	Rackspace Cloud Servers
    #SLICEHOST	Slicehost.com
    #GOGRID	GoGrid
    #VPSNET	VPS.net
    #LINODE	Linode.com
    #VCLOUD	vmware vCloud
    #RIMUHOSTING	RimuHosting.com    
    
    
    driver = providers.get_driver( getattr(Provider, hosttype.upper()) )
    
    spec = inspect.getargspec(driver.__init__)
    vargs = dict([(a,hostout.options.get(a)) for a in spec.args[1:] if hostout.options.get(a) ])
    args = [hostout.options.get(a) for a in spec.args[1:] if hostout.options.get(a) ]
    driver = driver(**vargs)
    return driver
  
def _node():
    hostout = api.env.get('hostout')
    driver = _driver()
    nodes = driver.list_nodes()
    hostname = hostout.options.get('hostname')
    node = filter(lambda x: x.name == hostname, nodes)
    if node:
        node = node[0]
    else:
        print "Host not found. %s" % ' '.join([ n.name for n in nodes])
        return
    api.env['fab_host'] = node.public_ip[0]
    
    return node

def printnode():
    node = _node()
    print node.extra.get('password')
    print node

def create():
    node = _node()
    hostout = api.env.get('hostout')
    filename, dsa_key = hostout.getIdentityKey()
    if node is None:
            
        hostname = hostout.options.get('hostname')
        hostos = hostout.options.get('hostos', 'Ubuntu 9.10 (karmic)')
        hostsize = int(hostout.options.get('hostsize', 256))
        driver = _driver()
        sizes = driver.list_sizes()
        size =  filter(lambda x: x.ram ==  hostsize, sizes)[0]
        images = driver.list_images()
        image=  filter(lambda x: x.name ==  hostos, images)[0]
        hostout = api.env.get('hostout')
        node = driver.create_node(size=size, name=hostname, image=image, files={'/root/.ssh/authorized_keys':dsa_key})
        print node.extra.get('password')
        while _node().state != 'ACTIVE':
            print _node().state

    api.env.hosts = node.public_ip[0:1]
    api.env.user = 'root'
    api.env.key_filename=filename
    print api.env
    

def reboot():
    print _node().reboot()

def destroy():
    print _node().destroy()
    
def predeploy():
        create()
