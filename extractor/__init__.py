from os import listdir

# try:
__all__  = [x[:-3] for x in listdir('extractor') if x[-3:] == '.py' and x[0:2] != '__']
# except FileNotFoundError:
#     __all__  = [x[:-3] for x in listdir() if x[-3:] == '.py' and x[0:2] != '__']

class ServiceNotSupported(Exception):
    message = "ERROR: Service does not support this function"
    pass

class ServiceNotFound(Exception):
    message = "ERORR: Service not found"
    pass

class ServiceShortURLFound(Exception):
    message = "ERORR: Short URL used. Avoid using them as they don't work with this service"
    pass