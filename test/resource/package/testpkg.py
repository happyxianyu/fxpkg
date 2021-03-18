from fxpkg.core.package import *

class Package(PackageBase):
    def __init__(self, libManager:LibManager):
        self.libManager = libManager
        print('success load testPkg!')

    

