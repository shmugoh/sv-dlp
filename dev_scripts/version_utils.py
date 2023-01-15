'''
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
'''
import sys
import contextlib
import subprocess
from datetime import datetime

def read_file(fname):
    with open(fname, encoding='utf-8') as f:
        return f.read()
def write_file(fname, content):
    with open(fname, 'w', encoding='utf-8') as f:
        return f.write(content)

def read_version(fname='sv_dlp/version.py'):
    exec(compile(read_file(fname), fname, 'exec'))
    return locals()['__version__']
def get_git_head():
    with contextlib.suppress(Exception):
        sp = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE)
        return sp.communicate()[0].decode().strip() or None

def get_new_version(revision):
    version = datetime.utcnow().strftime('%Y.%m.%d')
    if revision:
        assert revision.isdigit(), 'Revision must be a number'
    else:
        old_version = read_version().split('.')
        if version.split('.') == old_version[:3]:
            revision = str(int((old_version + [0])[3]) + 1)

    return f'{version}.{revision}' if revision else version

if __name__ == '__main__':
    VERSION = get_new_version((sys.argv + [''])[1])
    GIT_HEAD = get_git_head()
    VERSION_FILE = f'''\
# Autogenerated by dev_scripts/update-version.py
__version__ = {VERSION!r}
RELEASE_GIT_HEAD = {GIT_HEAD!r}
VARIANT = None
UPDATE_HINT = None
    '''

    write_file('sv_dlp/version.py', VERSION_FILE)
    print(f'::set-output name=sv-dlp_version::{VERSION}')
    print(f'\nVersion = {VERSION}, Git HEAD = {GIT_HEAD}')