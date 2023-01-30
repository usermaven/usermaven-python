from six import string_types
import numbers
from uuid import UUID
from usermaven.version import VERSION


ID_TYPES = (numbers.Number, string_types, UUID)

MAX_MSG_SIZE = 32 << 10
# Our servers only accept batches less than 500KB. Here limit is set slightly
# lower to leave space for extra data that will be added later, eg. "sentAt".
BATCH_SIZE_LIMIT = 475000

DEFAULT_HOST = "https://events.usermaven.com"
USER_AGENT = "usermaven-python/" + VERSION
