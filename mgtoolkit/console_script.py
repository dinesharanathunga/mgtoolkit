import pkg_resources
import unittest

try:
    FCD_VERSION = pkg_resources.get_distribution("mgtoolkit").version
except pkg_resources.DistributionNotFound:
    FCD_VERSION = "dev"


def console_entry():
    """If come from console entry point"""
    #main()

# !! The main function are only here for debug. The real compiler don't need this`!!
if __name__ == '__main__':
    unittest.main()





