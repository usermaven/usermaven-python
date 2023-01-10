import logging
import numbers
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import six

log = logging.getLogger("usermaven")


def remove_trailing_slash(host):
    if host.endswith("/"):
        return host[:-1]
    return host


def clean(item):
    if isinstance(item, Decimal):
        return float(item)
    if isinstance(item, UUID):
        return str(item)
    elif isinstance(item, (six.string_types, bool, numbers.Number, datetime, date, type(None))):
        return item
    elif isinstance(item, (set, list, tuple)):
        return _clean_list(item)
    elif isinstance(item, dict):
        return _clean_dict(item)
    else:
        return _coerce_unicode(item)


def _clean_list(list_):
    return [clean(item) for item in list_]


def _clean_dict(dict_):
    data = {}
    for k, v in six.iteritems(dict_):
        try:
            data[k] = clean(v)
        except TypeError:
            log.warning(
                'Dictionary values must be serializeable to JSON "%s" value %s of type %s is unsupported.',
                k,
                v,
                type(v),
            )
    return data


def _coerce_unicode(cmplx):
    try:
        item = cmplx.decode("utf-8", "strict")
    except AttributeError as exception:
        item = ":".join(exception)
        item.decode("utf-8", "strict")
        log.warning("Error decoding: %s", item)
        return None
    return item

