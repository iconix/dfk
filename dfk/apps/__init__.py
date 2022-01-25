import logging
import os
import sys

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s|%(name)s|%(levelname)s: %(message)s',
    stream=sys.stdout
)
logging.captureWarnings(True)
