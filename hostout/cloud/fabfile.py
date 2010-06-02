import os
import os.path
import libcloud
from libcloud.types import Provider, NodeState 
from libcloud import providers
import inspect
from fabric import api
import sys
  
#drivers = [ EC2('access key id', 'secret key'), 
#            Slicehost('api key'), 
#            Rackspace('username', 'api key') ] 

nodes = {}

def _driver():
    hostout = api.env.get('hostout')
    hosttype = api.env.get('hosttype')
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
    for a in spec.args[1:]:
        api.require(a)
                    #"Th(is|ese) variable(s) (are|is) used for logging into your %(hosttype)s account" %locals())
    vargs = dict([(a,hostout.options.get(a)) for a in spec.args[1:] if hostout.options.get(a) ])
    args = [hostout.options.get(a) for a in spec.args[1:] if hostout.options.get(a) ]
    driver = driver(**vargs)
    return driver

def _nodes(refresh=False):
    hostout = api.env.get('hostout')
    hostname = hostout.options.get('hostname')

    driver = _driver()
    list = driver.list_nodes()
    return list

  
def _node(refresh=False):
    hostout = api.env.get('hostout')
    hostname = hostout.options.get('hostname')
    if hostname in nodes.keys() and not refresh:
        return nodes[hostname]

    driver = _driver()
    list = driver.list_nodes()
    if driver.type == Provider.EC2:
       node = filter(lambda x: x.extra['keyname'] == hostname, list)
    else:
       node = filter(lambda x: x.name == hostname, list)
    node = filter(lambda x: x.state != NodeState.TERMINATED, node)
    if node:
        node = node[0]
    else:
        print "Host not found. %s" % ' '.join([ n for n in nodes])
        return
    nodes[hostname] = node
    return node

def initcommand(cmd):
    """Called before every connection to set host and login"""
    node = _node()
    if node and node.public_ip[0:1]:
        api.env.hosts = node.public_ip[0:1]
#        api.env.hostout.options['user'] = 'root'
#        api.env.user = 'root'
        key_filename = api.env['identity-file']
        if os.path.exists(key_filename):
            api.env.key_filename = key_filename
    

def printnode():
    node = _node()
    print node.extra.get('password')
    print node

def create():
    """Construct node on nominated provider"""
    hostout = api.env.get('hostout')
    if hostout.options.get('host'):
        return
    node = _node()
    if node is None:
            
        hostname = api.env.get('hostname')
        hostos = api.env.get('hostos', 'Ubuntu').lower()
        imageid = api.env.get('imageid','').lower()
        hostsize = int(api.env.get('hostsize', 256))
        driver = _driver()
        sizes = driver.list_sizes()
        sizes.sort(lambda x,y: cmp(x.ram,y.ram))
        contenders = filter(lambda x: x.ram <=  hostsize, sizes)
        if not contenders:
            print "No node available with <=%(hostsize)sMB on %(hosttype)s" % api.env
            return
        size = contenders[-1]
        images = driver.list_images()
        images.sort(lambda x,y: cmp(x.name,y.name))
        if imageid:
            contenders =  filter(lambda x: x.id.lower().startswith(imageid), images)
        else:
            contenders =  filter(lambda x: x.name.lower().startswith(hostos), images)
        if not contenders:
            print "No node available with <=%(hostsize)sMB on %(hosttype)s" % api.env
            return
        image = contenders[-1]
        print "Using the image %s (%s)." % (image.name,image.id)
        
        args = {}
        if driver.type == Provider.EC2:
            # Create a unique keypair for this host
            filename = api.env.get('identity-file')
            #if not filename or filename and os.path.exists(filename):
            #    raise Exception("Identity file must not exist to create EC2 Nodes as it will be overwritten")
            params = {'Action': 'DeleteKeyPair',
                      'KeyName': hostname,
            }
            try:  object = driver.connection.request('/',params=params).object
            except: pass
            params = {'Action': 'CreateKeyPair',
                      'KeyName': hostname,
            }
            object = driver.connection.request('/',params=params).object
            key = driver._findtext(object, "keyMaterial")
            key_file = open(filename,"w")
            key_file.write(key)
            key_file.close()
            args['ex_keyname'] = hostname
            api.env.key_filename = filename
            
            #also create security group
            try:
                driver.ex_create_security_group(hostname, 'hostout.cloud instance for %s'%hostname)
            except:
                pass
            driver.ex_authorize_security_group_permissive(hostname)
            args['ex_securitygroup'] = hostname
            
        elif driver.type == Provider.RACKSPACE:
            filename, key = hostout.getIdentityKey()
            args['ex_files']={'/root/.ssh/authorized_keys':key}

        node = driver.create_node(size=size, name=hostname,
                                  image=image,
                                  **args)
        print node.extra.get('password')

    print _nodes()
    _wait([NodeState.RUNNING, 'ACTIVE'])
    initcommand('predeploy')
    
def _wait(states):
    node = _node(refresh=True)
    if node and node.state not in states:
        print "State: %s" % node.state
    while node and (node.state not in states or not node.public_ip[0:1]):
        node = _node(refresh=True)
        print "State: %s, IP: %s" % (node.state, node.public_ip[0:1])
        print ".",



def reboot():
    print _node().reboot()

def destroy():
    print _node().destroy()
    driver = _driver()
    if driver.type == Provider.EC2:
        filename = api.env.get('identity-file')
        if os.path.exists(filename):
            os.remove(filename)
    _wait([None])
  
def predeploy():
        create()

def bootstrap():
    while True:
        print "trying to connect"
        try:
            api.run("echo 'Server now booted'")
            break
        except Exception,e:
            pass

    
    
