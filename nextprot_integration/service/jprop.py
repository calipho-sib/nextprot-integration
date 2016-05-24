import os
import re
import errno


class JavaPropertyMap:

    def __init__(self, prop_file):
        self.__props = {}
        self.load_properties(prop_file)

    def __interpolate_references(self):
        """replace java variable references by values in dictionary
        """
        pattern = re.compile(r'(\$\{?([^}/]+)\}?)')

        for key in self.__props:
            if pattern.match(self.__props[key]):
                self.__props[key] = pattern.sub(self.__lookup, self.__props[key])

    def __lookup(self, match_obj):
        """get value mapping the matching java property reference from match_obj
        """
        key = match_obj.group(2)

        if key in self.__props:
            return self.__props[key]

        raise IOError("cannot find key " + key + " in properties " + str(self.__props.items()))

    def load_properties(self, prop_file):
        """load properties from prop_file into internal dictionary
        """
        if not os.path.isfile(prop_file):
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), prop_file)

        f = open(prop_file, 'r')
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            kv = line.split('=')
            self.__props[kv[0]] = kv[1]

        if len(self.__props) == 0:
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), "cannot find properties", prop_file)

        self.__interpolate_references()

    def get_properties(self):
        return self.__props

    def add_property(self, property, value):
        self.__props[property] = value

    def get_property(self, property):
        """return java property value given a property name or None if not found
        """
        if property in self.__props:
            return self.__props[property]
        return None

    def count_properties(self):
        """return the number of java properties"""
        return len(self.__props)

