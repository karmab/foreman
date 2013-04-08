#!/usr/bin/python
"""
interacts with foreman
based on http://curl.haxx.se/libcurl/c/curl_easy_setopt.html
and  http://www.angryobjects.com/2011/10/15/http-with-python-pycurl-by-example/
"""

__author__ = "Karim Boumedhel"
__credits__ = ["Karim Boumedhel"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Karim Boumedhel"
__email__ = "karimboumedhel@gmail.com"
__status__ = "Production"

import ast
import os
import sys
import re
import pexpect
import socket
import simplejson
import pycurl
import StringIO
import optparse
import urllib
import ConfigParser


ERR_NOFOREMANFILE="You need to create a correct foreman.ini file in your home directory.Check documentation"

def foremando(url,actiontype=None,postdata=None):
 if postdata:postdata="%s" % str(postdata).replace("'",'"')
 c = pycurl.Curl()
 b = StringIO.StringIO()
 c.setopt(pycurl.URL, url)
 #c.setopt(pycurl.HTTPHEADER, [ "Content-type: application/json","Accept: application/json"])
 #c.setopt(pycurl.HTTPHEADER, [ "Content-type: application/json","Accept: application/json","Accept: version=2"])
 c.setopt(pycurl.HTTPHEADER, [ "Content-type: application/json","Accept: application/json,version=2" ])
 c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
 #c.setopt(pycurl.USERPWD, password)
 c.setopt(pycurl.SSL_VERIFYPEER, False)
 c.setopt(pycurl.SSL_VERIFYHOST, False)
 if actiontype=="POST":
  c.setopt( pycurl.POST, 1 )
  if postdata:c.setopt(pycurl.POSTFIELDS,postdata)
 elif actiontype=="DELETE":
  c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
 elif actiontype=="PUT":
  c.setopt( pycurl.CUSTOMREQUEST, "PUT" )
  if postdata:c.setopt(pycurl.POSTFIELDS, postdata)
 else:
  c.setopt(pycurl.WRITEFUNCTION, b.write)
 c.perform()
 if not actiontype in ["POST","PUT","DELETE"]:
  result = b.getvalue()
  result = simplejson.loads(result)
  result=eval(str(result))
  return result


#create a vm with 
#python foreman.py -f 192.168.17.5  -n prout.ib -1 192.168.17.206 
def foremancreate(host=None,name=None,dns=None,ip=None,osid=None,envid=None,archid=None,puppetid=None,ptableid=None,hostgroup=None,powerup=None,mac=None,memory=None,core=None,computeid=None):
 url="http://%s/api/hosts" % (host)
 if dns:name="%s.%s" % (name,dns)
 if osid:osid=foremangetid(foremanhost,"operatingsystems",osid)
 if not envid:envid="production"
 if envid:envid=foremangetid(foremanhost,"environments",envid)
 if archid:archid=foremangetid(foremanhost,"architectures",archid)
 if puppetid:puppetid=foremangetid(foremanhost,"puppet",puppetid)
 postdata={}
 postdata["host"]={"name":name}
 if osid:postdata["host"]["operatingsystem_id"]=ip
 if envid:postdata["host"]["environment_id"]=envid
 if archid:postdata["host"]["architecture_id"]=envid
 if puppetid:postdata["host"]["puppet_proxy_id"]=puppetid
 if ptableid:postdata["host"]["ptable_id"]=ptableid
 if ip:postdata["host"]["ip"]=ip
 if mac:postdata["host"]["mac"]=mac
 if powerup:postdata["host"]["powerup"]=powerup
 if memory:postdata["host"]["memory"]=memory
 if core:postdata["host"]["core"]=core
 if computeid:postdata["host"]["compute_resource_id"]=computeid
 if hostgroup:
  hostgroupid=foremangetid(host,"hostgroups",hostgroup)
  postdata["host"]["hostgroup_id"]=hostgroupid
 postdata="%s" % str(postdata).replace("'",'"')
 foremando(url,actiontype="POST",postdata=postdata)
 
def foremangetid(host,searchtype,searchname):
 url="http://%s/api/%s/%s" % (host,searchtype,searchname)
 result=foremando(url)
 if searchtype.endswith("es"):
  shortname=searchtype[:-2]
 else:
  shortname=searchtype[:-1]
 return str(result[shortname]["id"])


def foremanaddpuppetclass(host,name,puppetclass):
 puppetclassid=foremangetid(host,"puppetclasses",puppetclass)
 #nameid=foremangetid(host,"hosts",name)
 url="http://%s/api/hosts/%s/puppetclass_ids" % (host,name) 
 postdata={"puppetclass_id": puppetclassid}
 foremando(url,actiontype="POST",postdata=postdata)

#example of PUT REQUEST
def foremanupdateip(host,name,ip):
 url="http://%s/api/hosts/%s" % (host,name)
 postdata='{"host":{"ip":"%s" }}' % ip
 foremando(url,actiontype="PUT",postdata=postdata)

parser = optparse.OptionParser("Usage: %prog [options]")
creationgroup = optparse.OptionGroup(parser, "Creation options")
creationgroup.add_option("-n", "--new", dest="name", type="string",help="Create new server")
creationgroup.add_option("-1", "--ip", dest="ip", type="string",help="Ip to use when creating new server")
creationgroup.add_option("-k", "--kill", dest="kill", type="string",help="Kill given machine")
creationgroup.add_option("-m", "--mac", dest="mac", type="string",help="Mac to use when creating new server")
creationgroup.add_option("-M", "--memory", dest="memory", type="int", default=2048, help="Amount of memory to use when creating new server")
creationgroup.add_option("-2", "--cpus", dest="cores", type="int", default=2, help="Numbers of cpus to use when creating new server.Defaults to 1")
creationgroup.add_option("-p", "--powerup", dest="powerup", type="int", default=0, help="Whether to powerup server after creationgroup.Defaults to no")
creationgroup.add_option("-f", "--host", dest="foremanhost", type="string",default="puppet",help="Foreman server or ip to use.Currently default to puppet host if not specified")
creationgroup.add_option("-g", "--group", dest="hostgroup", type="string",help="Hostgroup to use when creating new server ")
creationgroup.add_option("-c", "--computeresource", dest="compute_resource_id", type="int",help="Computeresource_id to use when creating new server")
creationgroup.add_option("-7", "--puppetclass", dest="puppetclass", type="string",help="Add given class to a host")
creationgroup.add_option("-J", "--dns", dest="dns", type="string", help="Dns domain")
parser.add_option_group(creationgroup)
listinggroup = optparse.OptionGroup(parser, "Listing options")
listinggroup.add_option("-a", "--listarchs", dest="listarchs", action="store_true", help="List archs")
listinggroup.add_option("-d", "--listdomains", dest="listdomains", action="store_true", help="List domains")
listinggroup.add_option("-E", "--listenvironments", dest="listenvironments", action="store_true", help="List environments")
listinggroup.add_option("-H", "--listhostgroups", dest="listhostgroups", action="store_true", help="List hostgroups")
listinggroup.add_option("-l", "--listhosts", dest="listhosts", action="store_true", help="List hosts")
listinggroup.add_option("-o", "--listos", dest="listos", action="store_true", help="List os")
listinggroup.add_option("-P", "--listpuppets", dest="listpuppets", action="store_true", help="List puppets")
listinggroup.add_option("-L", "--listclients", dest="listclients", action="store_true", help="list available clients")
listinggroup.add_option("-R", "--listcompute", dest="listcomputes", action="store_true", help="List compute resources")
listinggroup.add_option("-9", "--switchclient", dest="switchclient", type="string", help="Switch default client")
parser.add_option_group(listinggroup)
parser.add_option("-C", "--client", dest="client", type="string", help="Specify Client")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true",help="Verbose mode")
parser.add_option("-u", "--update", dest="update", action="store_true",help="Update existing server")
parser.add_option("-s", "--status", dest="status", action="store_true", help="Get status")
parser.add_option("-D", "--dashboard", dest="dashboard", action="store_true", help="Get Dashboard info")


(options, args) = parser.parse_args()
listenvironments=options.listenvironments
listhosts=options.listhosts
listhostgroups=options.listhostgroups
listarchs=options.listarchs
listos=options.listos
listdomains=options.listdomains
listpuppets=options.listpuppets
name=options.name
kill=options.kill
status=options.status
dashboard=options.dashboard
foremanhost=options.foremanhost
hostgroup=options.hostgroup
powerup=options.powerup
ip=options.ip
mac=options.mac
cores=options.cores
memory=options.memory
listcomputes=options.listcomputes
compute_resource_id=options.compute_resource_id
update=options.update
verbose=options.verbose
puppetclass=options.puppetclass
listclients=options.listclients
switchclient=options.switchclient
client=options.client
dns=options.dns


foremanconffile="%s/foreman.ini" %(os.environ['HOME'])
#parse foreman client auth file
if not os.path.exists(foremanconffile):
 print "Missing %s in your  home directory.Check documentation" % foremanconffile
 sys.exit(1)
try:
 c = ConfigParser.ConfigParser()
 c.read(foremanconffile)
 foremans={}
 default={}
 for cli in c.sections():
  for option in  c.options(cli):
   if cli=="default":
    default[option]=c.get(cli,option)
    continue
   if not foremans.has_key(cli):
    foremans[cli]={option : c.get(cli,option)}
   else:
    foremans[cli][option]=c.get(cli,option)
except KeyError,e:
 print ERR_NOFOREMANFILE
 print e
 os._exit(1)

if listclients:
 print "Available Clients:"
 for cli in  sorted(foremans):
  print cli
 if default.has_key("client"):print "Current default client is: %s" % (default["client"])
 sys.exit(0)

if switchclient:
 if switchclient not in foremans.keys():
  print "Client not defined...Leaving"
 else:
  mod = open(foremanconffile).readlines()
  f=open(foremanconffile,"w")
  for line in mod:
   if line.startswith("client"):
    f.write("client=%s\n" % switchclient)
   else:
    f.write(line)
  f.close()
  print "Default Client set to %s" % (switchclient)
 sys.exit(0)

if not client:
 try:
  client=default['client']
 except:
  print "No client defined as default in your ini file or specified in command line"
  os._exit(1)

#PARSE DEFAULT SECTION
#try:
# if not host and default.has_key("clu"):clu=default["clu"]
# if not numcpu and default.has_key("numcpu"):numcpu=int(default["numcpu"])
# if not diskformat and default.has_key("diskformat"):diskformat=default["diskformat"]
# if default.has_key("low"):low=float(default["low"])
#except:
# print "Problem parsing default section in your ini file"
# os._exit(1)

try:
 foremanhost=foremans[client]["host"]
 if foremans[client].has_key("port"):foremanport=foremans[client]["port"]
 if foremans[client].has_key("user"):foremanuser=foremans[client]["user"]
 if foremans[client].has_key("password"):foremanpassword=foremans[client]["password"]
 if foremans[client].has_key("mac"):mac=foremans[client]["mac"]
 if foremans[client].has_key("os"):foremanos=foremans[client]["os"]
 if foremans[client].has_key("env"):foremanenv=foremans[client]["env"]
 if foremans[client].has_key("arch"):foremanarch=foremans[client]["arch"]
 if foremans[client].has_key("puppet"):foremanpuppet=foremans[client]["puppet"]
 if foremans[client].has_key("org"):foremanptable=foremans[client]["ptable"]
 if not dns and foremans[client].has_key('dns'):dns=foremans[client]['dns']
except KeyError,e:
 print "Problem parsing foreman ini file:Missing parameter %s" % e
 os._exit(1)

if not listhosts and not listhostgroups and not name and not listarchs and not listdomains and not status and not dashboard and not listcomputes and not listos and not listenvironments and not listpuppets and not kill and not update  and not puppetclass:
 print "No actions specified.Leaving..."
 sys.exit(1)

if listhosts:
 url="http://%s/api/hosts" % (foremanhost)
if listhostgroups:
 url="http://%s/api/hostgroups"  % (foremanhost)
if listarchs:
 url="http://%s/api/architectures"  % (foremanhost)
if listdomains:
 url="http://%s/api/domains"  % (foremanhost)
if status:
 url="http://%s/api/status"  % (foremanhost)
if dashboard:
 url="http://%s/api/dashboard"  % (foremanhost)
if listcomputes:
 url="http://%s/api/compute_resources"  % (foremanhost)
if listos:
 url="http://%s/api/operatingsystems"  % (foremanhost)
if listenvironments:
 url="http://%s/api/environments"  % (foremanhost)
if listpuppets:
 url="http://%s/api/smart_proxies?type=puppet"  % (foremanhost)
 #url="http://%s/ptables"  % (foremanhost)


if kill:
 url="http://%s/hosts/%s" % (foremanhost,kill)
 foremando(url,actiontype="DELETE")
 sys.exit(0)

if ip and update:
 #classes=classes.split(",")
 if not name:name=raw_input("enter machine s name:\n")
 if name=="":
  print "name cant be blank"
  sys.exit(1)
 foremanupdateip(foremanhost,name,ip)
 sys.exit(0)

#USE THE FOLLOWING STUFF FOR CLASSES
#CF http://projects.theforeman.org/projects/foreman/wiki/API
#http://192.168.8.2/lookup_keys/2-testdir/

if puppetclass and name:
 foremanaddpuppetclass(foremanhost,name,puppetclass)
 sys.exit(0)

if name:
 #if not ip:ip=raw_input("Enter ip for your new host")
 #if not mac:mac=raw_input("Enter mac for your new host")
 #res =foremancreate(url=url,name=name,ip=ip,osid=osid,envid=envid,archid=archid,puppetid=puppetid,ptableid=ptableid,hostgroup=hostgroup,powerup=powerup,mac=mac,memory=memory,core=core,compute_resource_id=compute_resource_id):
 #res =foremancreate(host=foremanhost,name=name,ip=ip,osid=None,envid=None,archid=None,puppetid=None,ptableid=None,hostgroup=hostgroup,powerup=None,mac=mac,memory=None,core=None,computeid=None)
 res =foremancreate(host=foremanhost,name=name,dns=dns,ip=ip,osid=None,envid=None,archid=None,puppetid=None,ptableid=None,hostgroup=hostgroup,powerup=None,mac=mac,memory=None,core=None,computeid=None)
 print res
 sys.exit(0)

res= foremando(url)
results={}
for  r in res:
 info=r.values()[0]
 name=info["name"]
 del info["name"]
 results[name]=info
if verbose:
 for r in sorted(results):print "%s\n%s\n" % (r,str(results[r]))
else:
 for r in sorted(results):print r

sys.exit(0)
