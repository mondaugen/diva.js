import os
import sys

from fabric.api import local, run, cd, put

from src import settings



def build():
    # Check the path to diva.js environment variable and if it doesn't exist, use
    # the empty string (this should throw an error)
    # An example path is: /home/username/diva.js/source/js/diva.js
    DIVA_JS_PATH = ''
    if os.getenv( 'DIVA_JS_PATH' ) != None:
      DIVA_JS_PATH = os.getenv( 'DIVA_JS_PATH' )
    sys.stderr.write('[FABFILE.PY]: Path to diva.js: ' + DIVA_JS_PATH +'\n')
    with cd(os.path.dirname(__file__)):
        # Generate the site
        print local("python src/generate.py " + DIVA_JS_PATH)
        # Copy the static directory over
        print settings.BUILD_DIR
        local("cp -R static %s" % settings.BUILD_DIR)

def deploy():
    put(settings.BUILD_DIR, 'deploy')

def wc():
    local("wc -w `find content -type f`")
