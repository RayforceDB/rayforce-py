import faulthandler
import sys

faulthandler.enable(file=sys.stderr, all_threads=True)
