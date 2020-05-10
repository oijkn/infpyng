import sys, os, glob, toml, operator
from functools import reduce

# For debug
from pprint import pprint
# var
globs = ''

def findKeys(node, kv):
    """
       Find all occurrences of a key in nested dictionaries and lists
       Source : https://stackoverflow.com/a/19871956
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
    globs = glob.glob(path + "/*.toml")
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

    allTargets = reduce(operator.concat, allTargets)
    return allTargets

def loadTags(host):
    """
    Loads tags from a TOML file.
    """
    # set path where script is running
    path = os.path.realpath(
        os.path.join(os.getcwd(),
        os.path.dirname(__file__))
    )
    # set globs of all TOML files
    globs = glob.glob(path + "/*.toml")
    # exclude config file from glob
    tomlFiles = [ x for x in globs if "config.toml" not in x ]


    for tomlFile in tomlFiles:
        targets = toml.load(tomlFile)

        #pprint('host: %s' % host)
        #pprint('targets: %s' % targets['targets'])

        for target in targets['targets']:
            if host in target['hosts'] and 'tags' in target:
                tags = ','.join("{!s}={!r}".format(key, val) for (key, val) in target['tags'].items())
                tags = tags.replace("'", "")

                print(tags)
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

def main():
    targets = loadTargets()
    pprint (targets)
    for t in targets:
        loadTags(t)

if __name__ == "__main__":
    main()
