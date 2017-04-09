def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

GraphAttribute = enum(Type='type', Service='service', Exploits='exploits',
                      Label='label', SubnetIpAddress='subnetip',
                      SubnetMask='mask', IpAddress='ipaddress', VlanId='vlanid',
                      HostIds='hostids', SwitchIds='switchids',
                      RouterIds='routerids', InterfaceIds='interfaceids',
                      ServerIds='serverids', InterfaceName='ifname')

# TODO: move to policy API
Ipv4ProtocolNumbers = enum(all=(0, 255), icmp=1, tcp=6, udp=17, eigrp=88, ospf=89)

RuleEffect = enum(Permit=1, Deny=2)

