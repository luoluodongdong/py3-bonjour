# conding:utf-8

import select
import sys
from pybonjour import *


name = 'TestServiceName'  # sys.argv[1]
regtype = '_testService._tcp'  # sys.argv[2]
port = 1212  # int(sys.argv[3])


def register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', regtype)
        print('  domain  =', domain)


txt = TXTRecord()
txt['foo'] = 'foobar'

sdRef = DNSServiceRegister(name=name,
                           regtype=regtype,
                           port=port,
                           txtRecord=txt,
                           callBack=register_callback
                           )

try:
    try:
        while True:
            ready = select.select([sdRef], [], [])
            if sdRef in ready[0]:
                DNSServiceProcessResult(sdRef)
    except KeyboardInterrupt:
        pass
finally:
    sdRef.close()
