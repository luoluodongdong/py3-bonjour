import select
import socket
import sys
from pybonjour import *
#import ipaddress

regtype = '_testService._tcp'  # sys.argv[1]
timeout = 5
queried = []
resolved = []


def query_record_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                          rrtype, rrclass, rdata, ttl):
    if errorCode == kDNSServiceErr_NoError:
        print(type(rdata))
        print(rdata)
        #print ('  IP         =', ipaddress.ip_address(rdata))
        print('  IP         =', socket.inet_ntoa(rdata))
        # print ('  IP         =', socket.inet_ntoa(b'\n#\xd1.'))
        queried.append(True)


def resolve_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                     hosttarget, port, txtRecord):
    if errorCode != kDNSServiceErr_NoError:
        return

    print('Resolved service:')
    print('  fullname   =', fullname)
    print('  hosttarget =', hosttarget)
    print('  port       =', port)
    print('  txtRecord  =', txtRecord)

    query_sdRef = DNSServiceQueryRecord(
        interfaceIndex=interfaceIndex,
        fullname=hosttarget,
        rrtype=kDNSServiceType_A,
        callBack=query_record_callback)

    try:
        while not queried:
            ready = select.select([query_sdRef], [], [], timeout)
            if query_sdRef not in ready[0]:
                print('Query record timed out')
                break
            DNSServiceProcessResult(query_sdRef)
        else:
            queried.pop()
    finally:
        query_sdRef.close()

    resolved.append(True)


def browse_callback(sdRef, flags, interfaceIndex, errorCode, serviceName,
                    regtype, replyDomain):
    if errorCode != kDNSServiceErr_NoError:
        return

    if not (flags & kDNSServiceFlagsAdd):
        print('Service removed')
        return

    print('Service added; resolving')

    resolve_sdRef = DNSServiceResolve(0,
                                      interfaceIndex,
                                      serviceName,
                                      regtype,
                                      replyDomain,
                                      resolve_callback)

    try:
        while not resolved:
            ready = select.select([resolve_sdRef], [], [], timeout)
            if resolve_sdRef not in ready[0]:
                print('Resolve timed out')
                break
            DNSServiceProcessResult(resolve_sdRef)
        else:
            resolved.pop()
    finally:
        resolve_sdRef.close()


browse_sdRef = DNSServiceBrowse(regtype=regtype,
                                callBack=browse_callback)

try:
    try:
        while True:
            ready = select.select([browse_sdRef], [], [])
            if browse_sdRef in ready[0]:
                DNSServiceProcessResult(browse_sdRef)
    except KeyboardInterrupt:
        pass
finally:
    browse_sdRef.close()
