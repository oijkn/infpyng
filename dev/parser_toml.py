import sys, os, glob, toml, operator
from functools import reduce

# For debug
from pprint import pprint

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
    pprint(allTargets)
    return allTargets

def main():
    loadTargets()

if __name__ == "__main__":
    main()
