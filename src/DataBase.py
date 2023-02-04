import json
import operator
from functools import reduce
from typing import Dict, List, Any, Union
import threading
import ijson
import ujson
import time
from io import TextIOWrapper


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s function took %0.3f ms' %
              (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


class Generator:
    """A class that contains a file object that will be closed after the generator ended,
       and a lock that locks the file during the operation.
    """

    def __init__(self, _file: TextIOWrapper, _generator, _lock: threading.Lock, _CloseAfterIter=True) -> None:
        self.__file: TextIOWrapper = _file
        self.__generator = _generator
        self.__lock = _lock
        self.__CloseAfterIter = _CloseAfterIter

    def close(self):
        self.__file.close()
        self.__lock.release()

    @property
    def CloseAfterIter(self) -> bool:
        return self.__CloseAfterIter

    @CloseAfterIter.setter
    def CloseAfterIter(self, value: bool):
        if isinstance(value, bool):
            self.__CloseAfterIter = value

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.__generator)
        except StopIteration:
            if self.__CloseAfterIter:
                self.close()
            raise StopIteration


class File:
    """
    This is a class for reading and writing data to database file

    Attributes:
        filepath (str): the path of the database file

    Return:
        A File object that can read and write data
    """

    def __init__(self, filepath):
        self.__filepath = filepath
        self.__Lock: threading.Lock = threading.Lock()

    @property
    def filepath(self):
        return self.__filepath

    def read(self, target: str = "") -> Generator:
        """Returns a generator of the file"""
        self.__Lock.acquire()

        f = open(self.filepath, "r+", encoding="utf-8")
        return Generator(f, ijson.kvitems(f, target), self.__Lock)

    def readAll(self):
        """Returns all the file's content, could cause severe performance drop if the file is big"""
        with self.__Lock:
            with open(self.filepath, "r+", encoding="utf-8") as f:
                return ujson.load(f)

    def write(self, data: Union[Dict[Any, Any], List[Any]]):
        """Write the data to the file, could cause severe performance drop if the file is big"""
        with self.__Lock:
            with open(self.filepath, "w+", encoding="utf-8") as f:
                f.write(ujson.dumps(data, ensure_ascii=False, indent=4))


class DataBase(File):
    """This is a class handling data using:
        json file format
        ujson for large read/write operation
        ijson for streamed read operation 

    Attributes:
        filepath (str): the path of the database file

    Return: 
        A DataBase object of that file
    """

    def __init__(self, filepath: str):
        File.__init__(self, filepath)

    def __getitem__(self, keys):
        """Get the value from the list of keys"""
        if not isinstance(keys, tuple):
            generator = self.read()
            keys = (keys, )
        else:
            generator = self.read(".".join(keys[:-1]))
        for key, value in generator:
            if key == keys[-1]:
                generator.close()
                return value
        raise KeyError

    def __setitem__(self, keys, value):
        """Get the object from the list of keys, then set it to value"""
        if not isinstance(keys, tuple):
            keys = (keys,)
        data = self.readAll()
        subDict = data
        for ind, key in enumerate(keys[:-1]):
            if not ind:
                if isinstance(data, dict):
                    subDict = data.setdefault(key, {})
                else:
                    subDict = data[key]
                continue
            if isinstance(subDict, dict):
                subDict = subDict.setdefault(key, {})
            else:
                subDict = subDict[key]
        subDict[keys[-1]] = value
        self.write(data)

    def contains(self, keys: List[str], value):
        """Return whether the value is in the object obtained from the keys"""
        try:
            generator = self.read(".".join(keys))
            return value in [key for key, value in generator]
        except KeyError:
            return False

    def getData(self):
        return [value for key, value in self.read()]

    def getKeys(self):
        return [key for key, value in self.read()]

    def append(self, value) -> int:
        if isinstance(self.readAll(), list):
            _data = self.readAll()
            _data.append(value)
            self.write(_data)
            return len(_data)-1
        return -1
