import sys, os, glob, toml

def loadConfig():
    """
    Loads infpyng configuration from a TOML file.
    """
    global path
    global config
    global globs
    global count
    global interval
    global timeout
    global backoff
    global retry
    global tos

    path = os.path.realpath(
        os.path.join(os.getcwd(),
        os.path.dirname(__file__))
    )
    globs = glob.glob(path + "/config/*.toml")

    if any("config.toml" in f for f in globs):
        config = toml.load(path + '/config/config.toml')

        if 'count' in config['options']:
            count = int(config['options']['count'])
        else:
            count = int(1)

        if 'interval' in config['options']:
            interval = int(config['options']['interval'])
        else:
            interval = int(10)

        if 'timeout' in config['options']:
            timeout = int(config['options']['timeout'])
        else:
            timeout = int(500)

        if 'backoff' in config['options']:
            backoff = float(config['options']['backoff'])
        else:
            backoff = float(1.5)

        if 'retry' in config['options']:
            retry = int(config['options']['retry'])
        else:
            retry = int(3)

        if 'tos' in config['options']:
            tos = int(config['options']['tos'])
        else:
            tos = int(0)

        loadTargets()
    else:
        print('Error: no config file found !')
        sys.exit(1)

def loadTargets():
    """
    Loads targets from a TOML file.
    """
    allTargets = []
    listTargets = [ x for x in globs if "config.toml" not in x ]
    for l in listTargets:
        targets = toml.load(l)
        if 'targets' in targets:
            if any('hosts' in h for h in targets['targets']):
                hosts = [ sub['hosts'] for sub in targets['targets'] ]
                for sublist in hosts:
                    for i in sublist:
                        allTargets.append(i)
    print(allTargets)
    sys.exit(0)
    return allTargets

def loadTags(host):
    """
    Loads tags from a TOML file.
    """
    listTargets = [ x for x in globs if "config.toml" not in x ]
    for l in listTargets:
        targets = toml.load(l)
        for [idx, val] in enumerate(targets['targets']):
            h = targets['targets'][idx]['hosts']
            for i in h:
                if i == host and 'tags' in targets['targets'][idx]:
                    t = targets['targets'][idx]['tags']
                    #print ("i: '{}'".format(i) + " h: '{}'".format(host))
                    #print ("t: '{}'".format(t))
                    tags = ','.join("{!s}={!r}".format(key,val) for (key,val) in t.items())
                    tags = tags.replace("'", "")

                    return tags
