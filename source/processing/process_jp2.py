#!/usr/bin/env python

# Copyright (C) 2011, 2012 by Wendy Liu, Andrew Hankinson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import os
import re
import tempfile
import subprocess
import shutil
from optparse import OptionParser

"""
This is a python script that will process all the images in a directory and
try to convert them into the JPEG 2000 image format. You must have the Kakadu
JPEG 2000 tools installed, most importantly the kdu_compress command.

You can download these tools for free at:
http://www.kakadusoftware.com/index.php?option=com_content&task=view&id=26&Itemid=22

Dependencies:
    Python (version < 3.0)
    Kakadu Command-line Utilities
    ImageMagick convert utility

Usage:
    Either run it with
        python process_jp2.py [directory]
    or chmod it to executable (chmod +x process.py) and run it with
        ./process_jp2.py directory

    You can also use this as a Python module:

        import process_jp2
        c = DivaConverter(input_directory, output_directory)
        c.convert()
"""

PATH_TO_IMAGEMAGICK = "/usr/local/bin/convert"
PATH_TO_KDU_COMPRESS = "/usr/local/bin/kdu_compress"
VALID_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".JPG", ".JPEG", ".TIF", ".TIFF", '.png', '.PNG']


class DivaConverter(object):
    def __init__(self, input_directory, output_directory):
        self.input_directory = os.path.abspath(input_directory)
        self.output_directory = os.path.abspath(output_directory)
        self.verbose = True

    def convert(self):
        # If an output directory is supplied, use that one. Else create
        # a folder called "processed" in the original directory.
        # If that directory already exists, fail
        if not os.path.isdir(self.output_directory):
            os.mkdir(self.output_directory)

        to_process = [os.path.join(self.input_directory, f)
                        for f in os.listdir(self.input_directory) if self.__filter_fnames(f)]
        to_process.sort(key=self.alphanum_key)

        for image in to_process:
            tdir = None
            name = os.path.basename(image)
            name, ext = os.path.splitext(name)
            tdir = tempfile.mkdtemp()

            input_file = os.path.join(tdir, "{0}.tiff".format(name))
            output_file = os.path.join(self.output_directory, "{0}.jp2".format(name))

            if self.verbose:
                print "Using ImageMagick to convert {0} to TIFF".format(image)
            subprocess.call([PATH_TO_IMAGEMAGICK,
                                "-compress", "None",
                                image,
                                input_file])

            if self.verbose:
                print "Converting {0} to JPEG2000".format(name)
            subprocess.call([PATH_TO_KDU_COMPRESS,
                                "-i", input_file,
                                "-o", output_file,
                                "Clevels=5",
                                "Cblk={64,64}",
                                "Cprecincts={256,256},{256,256},{128,128}",
                                "Creversible=yes",
                                "Cuse_sop=yes",
                                "Corder=LRCP",
                                "ORGgen_plt=yes",
                                "ORGtparts=R",
                                "-rate", "-,1,0.5,0.25"
                            ])
            if self.verbose:
                print "Cleaning up"
            shutil.rmtree(tdir)

            if self.verbose:
                print "Done converting {0}".format(image)

    def __filter_fnames(self, fname):
        if fname.startswith('.'):
            return False
        if fname.startswith('_'):
            return False
        if fname == "Thumbs.db":
            return False
        if os.path.splitext(fname)[-1].lower() not in VALID_EXTENSIONS:
            return False
        return True

    def __tryint(self, s):
        try:
            return int(s)
        except:
            return s

    def alphanum_key(self, s):
        """ Turn a string into a list of string and number chunks.
            "z23a" -> ["z", 23, "a"]
            See:
            http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html
        """
        return [self.__tryint(c) for c in re.split('([0-9]+)', s)]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "You must specify both an input and an output directory."
        print "Usage: process_jp2.py input_directory output_directory"
        sys.exit(-1)

    c = DivaConverter(sys.argv[1], sys.argv[2])
    c.convert()

    sys.exit(0)
