# -*- coding: utf-8 -*-
import decimal
import datetime
from collections import namedtuple
from . import AbstractCornExtenser
from ...requests.types import Type, Dict, List


class FixedOffsetTimeZone(datetime.tzinfo):
    """Fixed offset in hours and minutes from UTC.

    >>> fixed = FixedOffsetTimeZone(-2, 30)
    >>> dt = datetime.date(2007, 1, 25)
    >>> fixed.utcoffset(dt)
    datetime.timedelta(-1, 81000)
    >>> fixed.tzname(dt)
    'UTC-02:30'
    >>> fixed.dst(dt)
    datetime.timedelta(0)

    """
    def __init__(self, offset_hours, offset_minutes):
        """Initialize timezone information with given offsets and name."""
        super(FixedOffsetTimeZone, self).__init__()
        self.__offset = datetime.timedelta(
            hours=offset_hours, minutes=offset_minutes)
        self.__name = "UTC%+03i:%02i" % (offset_hours, offset_minutes)

    def utcoffset(self, _):
        """Return offset of local time from UTC, in minutes east of UTC."""
        return self.__offset

    def tzname(self, _):
        """Return the time zone name as a string."""
        return self.__name

    def dst(self, _):
        """Return daylight saving time adjustment, in minutes east of UTC."""
        return datetime.timedelta(0)


def to_datetime(value):
    """Cast ``value`` into :class:`datetime.datetime` object.

    >>> to_datetime(datetime.date(2010, 8, 4))
    datetime.datetime(2010, 8, 4, 0, 0)
    >>> to_datetime(datetime.datetime(2010, 8, 4, 0, 0))
    datetime.datetime(2010, 8, 4, 0, 0)
    >>> to_datetime("20100804")
    datetime.datetime(2010, 8, 4, 0, 0)
    >>> to_datetime("2010-08-04")
    datetime.datetime(2010, 8, 4, 0, 0)
    >>> to_datetime("2010-08-04T20:34:31")
    datetime.datetime(2010, 8, 4, 20, 34, 31)
    >>> to_datetime("2010-08-04T20:34:31Z")
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    datetime.datetime(2010, 8, 4, 20, 34, 31,
        tzinfo=<kalamar.value.FixedOffsetTimeZone object at ...>)
    >>> to_datetime("20100804-203431Z")
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    datetime.datetime(2010, 8, 4, 20, 34, 31,
        tzinfo=<kalamar.value.FixedOffsetTimeZone object at ...>)
    >>> to_datetime("2010-08-04T20:34:31+02:30")
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    datetime.datetime(2010, 8, 4, 20, 34, 31,
        tzinfo=<kalamar.value.FixedOffsetTimeZone object at ...>)
    >>> to_datetime("2010-08-04T20:34:31+02:30")
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    datetime.datetime(2010, 8, 4, 20, 34, 31,
        tzinfo=<kalamar.value.FixedOffsetTimeZone object at ...>)
    >>> to_datetime(10) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
        ....
    ValueError: 10 cannot be cast to datetime.

    """
    if isinstance(value, datetime.datetime):
        return value
    elif isinstance(value, datetime.date):
        return datetime.datetime(value.year, value.month, value.day)
    elif isinstance(value, basestring):
        value = value.replace("-", "").replace(":", "").replace("T", "")
        if len(value) == 8:
            return datetime.datetime.strptime(value, "%Y%m%d")
        elif len(value) == 14:
            return datetime.datetime.strptime(value, "%Y%m%d%H%M%S")
        elif len(value) == 15 and value.endswith("Z"):
            value = value[:-1] + "+0000"
        if len(value) == 19:
            time, timezone = value[:14], value[14:]
            hours, minutes = timezone[:2], timezone[2:]
            time = datetime.datetime.strptime(time, "%Y%m%d%H%M%S")
            return time.replace(
                tzinfo=FixedOffsetTimeZone(int(hours), int(minutes)))
    raise ValueError("%s cannot be cast to datetime." % value)


def to_date(value):
    """Cast ``value`` into :class:`datetime.date` object.

    >>> to_date(datetime.date(2010, 8, 4))
    datetime.date(2010, 8, 4)
    >>> to_date(datetime.datetime(2010, 8, 4, 0, 0))
    datetime.date(2010, 8, 4)
    >>> to_date("20100804")
    datetime.date(2010, 8, 4)
    >>> to_date("2010-08-04")
    datetime.date(2010, 8, 4)
    >>> to_date(10) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
        ....
    ValueError: 10 cannot be cast to date.

    """
    if isinstance(value, datetime.datetime):
        return value.date()
    elif isinstance(value, datetime.date):
        return value
    elif isinstance(value, basestring):
        value = value.replace("-", "").replace(":", "")
        return datetime.datetime.strptime(value, "%Y%m%d").date()
    raise ValueError("%s cannot be cast to date." % value)

def to_bytes(value, encoding="utf-8"):
    """Cast ``value`` into bytes.

    This function works with Python 2.x and 3.x and can be used in Kalamar.

    >>> spam = to_bytes("spam")
    >>> spam.decode("utf-8") == to_unicode("spam")
    True
    >>> type(spam) == bytes
    True
    >>> touche = to_bytes("Touché")
    >>> touche.decode("utf-8") == to_unicode("Touché")
    True
    >>> type(touche) == bytes
    True
    >>> ten = to_bytes("10")
    >>> type(ten) == bytes
    True
    >>> int(ten)
    10

    """
    if type(value) == bytes:
        return value
    else:
        try:
            return bytes(value, encoding=encoding)
        except:
            try:
                return bytes(value)
            except:
                return value.encode(encoding)


def to_unicode(value, encoding="utf-8"):
    """Cast ``value`` into unicode string.

    This function works with Python 2.x and 3.x and can be used in Kalamar.

    >>> spam = to_unicode("spam")
    >>> spam.encode("utf-8") == to_bytes("spam")
    True
    >>> type(spam) == unicode
    True
    >>> touche = to_unicode("Touché")
    >>> touche.encode("utf-8") == to_bytes("Touché")
    True
    >>> type(touche) == unicode
    True
    >>> ten = to_unicode("10")
    >>> type(ten) == unicode
    True
    >>> int(ten)
    10

    """
    if type(value) == unicode:
        return value
    else:
        try:
            string = unicode(value, encoding=encoding)
        except:
            string = unicode(value)
        return unicodedata.normalize("NFC", string)


def to_type(value, data_type):
    """Return ``value`` if instance of ``data_type`` else raise error.

    >>> to_type(1, int)
    1
    >>> eggs = to_type("eggs", unicode)
    >>> eggs == "eggs"
    True
    >>> type(eggs) == unicode
    True
    >>> to_type("1+j", complex)
    (1+1j)
    >>> to_type("eggs", float) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
        ....
    ValueError: eggs cannot be cast to float.

    """
    if isinstance(value, data_type) or value is None:
        return value
    else:
        try:
            return data_type(value)
        except:
            raise ValueError("%s cannot be cast to %s." % (
                    value, data_type.__name__))

def to_number(value, data_type):
    if isinstance(value, data_type) or value is None:
        return value
    if not value:
        return data_type(0)
    return to_type(value, data_type)

Converter = namedtuple('Converter', ['down', 'up'])

class TypeExtenser(AbstractCornExtenser):

    default_converters = {
        unicode: to_unicode,
        bytes: to_bytes,
        int: lambda value: to_number(value, int),
        float: lambda value: to_number(value, float),
        decimal.Decimal: lambda value: to_number(value, decimal.Decimal),
        datetime.datetime: to_datetime,
        datetime.date: to_date,
        bool: bool,
        dict: dict,
        object: lambda value: value,
    }

    def __init__(self, name, wrapped_corn, type_converters=None):
        super(TypeExtenser, self).__init__(name, wrapped_corn)
        self.converters = self.default_converters.copy()
        # Contains a mapping of property name to downward/upward
        # convertors
        self.named_convertors = {}
        if type_converters:
            self.converters.update(type_converters)

    def register(self, name, type=object, custom_down=None, custom_up=None):
        if name not in self.wrapped_corn.properties:
            raise KeyError('Cannot register a type converter for nonexistent property')
        self.properties[name] = Type(corn=self, type=type, name=name)
        if custom_down:
            down_converter = custom_down
        else:
            down_converter = self.converters[self.wrapped_corn.properties[name].type]
        if custom_up:
            up_converter = custom_up
        else:
            up_converter = self.converters[type]
        self.named_convertors[self.properties[name]] = Converter(down=down_converter, up=up_converter)

    def execute(self, query):
        #TODO: convert query so that every type is casted appropriately
        pass


