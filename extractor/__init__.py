from os import listdir

__all__  = [x[:-3] for x in listdir('extractor') if x[-3:] == '.py' and x != '__init__.py']