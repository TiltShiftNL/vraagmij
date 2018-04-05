
def get_container_int():
    return round(int('0x%s' % [l.strip() for l in open('/etc/hosts', 'r')][-1].split('\t')[1], 0) / 10000000000)
