foreman
=======

python foreman bindings POC
EXAMPLES
#create a machine ( in domain kb ) with its ip and belonging to prout group
foreman.py -f 192.168.8.8  -n  good3.kb -1 192.168.10.3 -g prout
#delete this machine
foreman.py -k good3.kb
#add puppet class test to it
foreman.py -7 test2 -n good3.kb
#update ip of the host
foreman.py -u -n good3.kb -1 192.168.8.220

