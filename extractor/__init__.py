from os import listdir

__all__  = [x[:-3] for x in listdir('extractor') if x[-3:] == '.py' and x[0:2] != '__']

class ServiceNotSupported(Exception):
    message = "ERROR: Service not supported"
    pass

class ServiceNotFound(Exception):
    message = "ERORR: Service not found"
    pass