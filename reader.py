# -*- coding: utf-8 -*-

import sys, os, glob, toml, operator
from functools import reduce

# For debug
from pprint import pprint

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

def findKeys(node, kv):
    """
    Find all occurrences of a key in nested dictionaries and lists
    --> https://stackoverflow.com/a/19871956
    """
    if isinstance(node, list):
        for i in node:
            for x in findKeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findKeys(j, kv):
                yield x

def loadTargets():
    """
    Loads targets from a TOML file(s).
    """
    # set path where script is running
    path = os.path.realpath(
        os.path.join(os.getcwd(),
        os.path.dirname(__file__))
    )
    # set globs of all TOML files
    globs = glob.glob(path + "/config/*.toml")
    # exclude config file from glob
    tomlFiles = [ x for x in globs if "config.toml" not in x ]

    # set list for all targets
    allTargets = []
    # loop in all file to find value(s) of 'hosts' keys
    for tomlFile in tomlFiles:
        targets = toml.load(tomlFile)
        list2d = findKeys(targets, 'hosts')
        allTargets = list(list2d) + allTargets
        #pprint(allTargets)

    # make flat list out of list of lists
    # --> https://stackoverflow.com/a/39493960
    allTargets = reduce(operator.concat, allTargets)

    return allTargets

def loadTags(host):
    """
    Loads tags from a TOML file.
    """
    # exclude config file from glob
    tomlFiles = [ x for x in globs if "config.toml" not in x ]

    # parse targets and match keys 'tags' for wanted host
    # --> https://stackoverflow.com/q/61714213/6281137
    for tomlFile in tomlFiles:
        targets = toml.load(tomlFile)

        #pprint('host: %s' % host)
        #pprint('targets: %s' % targets['targets'])

        for target in targets['targets']:
            if host in target['hosts'] and 'tags' in target:
                tags = ','.join("{!s}={!r}".format(key, val) for (key, val) in target['tags'].items())
                tags = tags.replace("'", "")

                return tags

        """ Alternative """
        """
        hosts = operator.itemgetter('hosts')
        tags = operator.itemgetter('tags')
        fmt = 'country={country},server={server}'
        space = targets['targets']

        term = host
        # filter
        items = (item for item in space if term in hosts(item))
        for item in items:
            #print(f'host:{term}')
            #print(fmt.format(**tags(item)))
        # or
            print(','.join(f'{key}={value}' for key,value in tags(item).items()))
        """
