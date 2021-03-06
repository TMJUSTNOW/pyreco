__FILENAME__ = timestamp
#!/usr/bin/python

import os
import sys
import time

maxtime = 0
for file in sys.argv[1:]:
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
    if (mtime > maxtime):
        maxtime = mtime

sys.stdout.write("%d" % maxtime);

########NEW FILE########
__FILENAME__ = arfile
"""
arfile - A module to parse GNU ar archives.

Copyright (c) 2006-7 Paul Sokolovsky
This file is released under the terms 
of GNU General Public License v2 or later.
"""
import sys
import os
import tarfile 


class FileSection:
    "A class which allows to treat portion of file as separate file object."

    def __init__(self, f, offset, size):
        self.f = f
        self.offset = offset
        self.size = size
        self.seek(0, 0)

    def seek(self, offset, whence = 0):
#        print "seek(%x, %d)" % (offset, whence)
        if whence == 0:
            return self.f.seek(offset + self.offset, whence)
        elif whence == 1:
            return self.f.seek(offset, whence)
        elif whence == 2:
            return self.f.seek(self.offset + self.size + offset, 0)
        else:
            assert False

    def tell(self):
#        print "tell()"
        return self.f.tell() - self.offset

    def read(self, size = -1):
        if (size == -1): size = self.size
#        print "read(%d)" % size
        return self.f.read(size)

class ArFile:

    def __init__(self, f):
        self.f = f
        self.directory = {}
        self.directoryRead = False
        self.filenames = ""

        signature = self.f.readline()
        assert signature == "!<arch>\n"
        self.directoryOffset = self.f.tell()

    def open(self, fname):
        if self.directory.has_key(fname):
            return FileSection(self.f, self.directory[fname][-1], int(self.directory[fname][5]))

        if self.directoryRead:
            raise IOError, (2, "AR member not found: " + fname)

        f = self._scan(fname)
        if f == None:
            raise IOError, (2, "AR member not found: " + fname)
        return f


    def _scan(self, fname):
        self.f.seek(self.directoryOffset, 0)

        while True:
            l = self.f.readline()
            if not l: 
                self.directoryRead = True
                return None

            if l == "\n":
                l = self.f.readline()
                if not l: break
            descriptor = l.split()
#            print descriptor
            memberName = descriptor[0]

            # Handle GNU-style extended filenames
            if memberName[0] == '/':
                if memberName[1] == '/':
                    # Read past the extended directory
                    size = int(descriptor[1])
                    current = 0
                    while (current < size):
                        l = self.f.readline()
                        descriptor = l.split()
                        memberName = descriptor[0]
                        self.filenames = self.filenames + l +"\n"
                        current = current + len(l)
                    l = self.f.readline()
                    descriptor = l.split()
                    memberName = descriptor[0]
                else:
                    size = int(memberName[1:])
                    memberName = self.filenames[size:].split()[0]
                    descriptor[0] = memberName

            # Handle BSD-style extended filenames
            if memberName[0] == '#' and memberName[1] == '1' and memberName[2] == '/':
                # Read the extended directory
                size = int(memberName[3:])
                memberName = self.f.read(size)
                while (memberName[-1] == '\x00'):
                    memberName = memberName[:-1]
                descriptor[0] = memberName
                descriptor[5] = int(descriptor[5]) - size
                
            size = int(descriptor[5])
            if memberName[-1] == '/': memberName = memberName[:-1]
            self.directory[memberName] = descriptor + [self.f.tell()]
#            print "read:", memberName
            if memberName == fname or (memberName.startswith("`") and memberName[1:] == fname):
                # Record directory offset to start from next time
                self.directoryOffset = self.f.tell() + size
                return FileSection(self.f, self.f.tell(), size)

            # Skip data and loop
            if size % 2:
                size = size + 1
            data = self.f.seek(size, 1)
#            print hex(self.f.tell())

    def scan(self):
        self.f.seek(self.directoryOffset, 0)

        while True:
            l = self.f.readline()
            if not l: 
                self.directoryRead = True
                return None

            if l == "\n":
                l = self.f.readline()
                if not l: break
            descriptor = l.split()
#            print descriptor
            memberName = descriptor[0]

            # Handle GNU-style extended filenames
            if memberName[0] == '/':
                if memberName[1] == '/':
                    # Read past the extended directory
                    size = int(descriptor[1])
                    current = 0
                    while (current < size):
                        l = self.f.readline()
                        descriptor = l.split()
                        memberName = descriptor[0]
                        self.filenames = self.filenames + l
                        current = current + len(l)
                    l = self.f.readline()
                    descriptor = l.split()
                    memberName = descriptor[0]
                else:
                    size = int(memberName[1:])
                    memberName = self.filenames[size:].split()[0]
                    descriptor[0] = memberName

            # Handle BSD-style extended filenames
            if memberName[0] == '#' and memberName[1] == '1' and memberName[2] == '/':
                # Read the extended directory
                size = int(memberName[3:])
                memberName = self.f.read(size)
                while (memberName[-1] == '\x00'):
                    memberName = memberName[:-1]
                descriptor[0] = memberName
                descriptor[5] = int(descriptor[5]) - size

            size = int(descriptor[5])
            if memberName[-1] == '/': memberName = memberName[:-1]
            self.directory[memberName] = descriptor + [self.f.tell()]
#            print "read:", memberName

            # Skip data and loop
            if size % 2:
                size = size + 1
            data = self.f.seek(size, 1)
#            print hex(f.tell())


if __name__ == "__main__":
    if None:
        f = open(sys.argv[1], "rb")

        ar = ArFile(f)
        tarStream = ar.open("data.tar.gz")
        print "--------"
        tarStream = ar.open("data.tar.gz")
        print "--------"
        tarStream = ar.open("control.tar.gz")
        print "--------"
        tarStream = ar.open("control.tar.gz2")

        sys.exit(0)


    dir = "."
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    for f in os.listdir(dir):
        if not f.endswith(".ipk"): continue

        print "=== %s ===" % f
        f = open(dir + "/" + f, "rb")

        ar = ArFile(f)
        tarStream = ar.open("control.tar.gz")
        tarf = tarfile.open("control.tar.gz", "r", tarStream)
        #tarf.list()

        f2 = tarf.extractfile("./control")
        print f2.read()

########NEW FILE########
__FILENAME__ = ipkg
#!/usr/bin/env python
#   Copyright (C) 2001 Alexander S. Guy <a7r@andern.org>
#                      Andern Research Labs
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330,
#   Boston, MA 02111-1307, USA.  */
#
#   Copyright 2001, Russell Nelson <ipkg.py@russnelson.com>
#   Added reading in of packages.
#   Added missing package information fields.
#   Changed render_control() to __repr__().
#
# Current Issues:
#    The API doesn't validate package information fields.  It should be
#        throwing exceptions in the right places.
#    Executions of tar could silently fail.
#    Executions of tar *do* fail, and loudly, because you have to specify a full filename,
#        and tar complains if any files are missing, and the ipkg spec doesn't require
#        people to say "./control.tar.gz" or "./control" when they package files.
#        It would be much better to require ./control or disallow ./control (either)
#        rather than letting people pick.  Some freedoms aren't worth their cost.

import tempfile
import os
import sys
import glob
import md5
import re
import string
import commands
from stat import ST_SIZE
import arfile
import tarfile

class Version:
    """A class for holding parsed package version information."""
    def __init__(self, epoch, version):
        self.epoch = epoch
        self.version = version

    def _versioncompare(self, selfversion, refversion):
        if not selfversion: selfversion = ""
        if not refversion: refversion = ""
        while 1:
            ## first look for non-numeric version component
            selfm = re.match('([^0-9]*)(.*)', selfversion)
            #print 'selfm', selfm.groups()
            (selfalpha, selfversion) = selfm.groups()
            refm = re.match('([^0-9]*)(.*)', refversion)
            #print 'refm', refm.groups()
            (refalpha, refversion) = refm.groups()
            if (selfalpha > refalpha):
                return 1
            elif (selfalpha < refalpha):
                return -1
            ## now look for numeric version component
            (selfnum, selfversion) = re.match('([0-9]*)(.*)', selfversion).groups()
            (refnum, refversion) = re.match('([0-9]*)(.*)', refversion).groups()
            #print 'selfnum', selfnum, selfversion
            #print 'refnum', refnum, refversion
            if (selfnum != ''):
                selfnum = int(selfnum)
            else:
                selfnum = -1
            if (refnum != ''):
                refnum = int(refnum)
            else:
                refnum = -1
            if (selfnum > refnum):
                return 1
            elif (selfnum < refnum):
                return -1
            if selfversion == '' and refversion == '':
                return 0

    def compare(self, ref):
        if (self.epoch > ref.epoch):
            return 1
        elif (self.epoch < ref.epoch):
            return -1
        else:
	    self_ver_comps = re.match(r"(.+?)(-r.+)?$", self.version)
	    ref_ver_comps = re.match(r"(.+?)(-r.+)?$", ref.version)
	    #print (self_ver_comps.group(1), self_ver_comps.group(2))
	    #print (ref_ver_comps.group(1), ref_ver_comps.group(2))
	    r = self._versioncompare(self_ver_comps.group(1), ref_ver_comps.group(1))
	    if r == 0:
		r = self._versioncompare(self_ver_comps.group(2), ref_ver_comps.group(2))
	    #print "compare: %s vs %s = %d" % (self, ref, r)
	    return r

    def __str__(self):
        return str(self.epoch) + ":" + self.version

def parse_version(versionstr):
    epoch = 0
    # check for epoch
    m = re.match('([0-9]*):(.*)', versionstr)
    if m:
        (epochstr, versionstr) = m.groups()
        epoch = int(epochstr)
    return Version(epoch, versionstr)

class Package:
    """A class for creating objects to manipulate (e.g. create) ipkg
       packages."""
    def __init__(self, fn=None):
	self.package = None
	self.version = 'none'
	self.parsed_version = None
	self.architecture = None
	self.maintainer = None
	self.source = None
	self.description = None
	self.depends = None
	self.provides = None
	self.replaces = None
	self.conflicts = None
        self.recommends = None
	self.suggests = None
	self.section = None
        self.filename_header = None
	self.file_list = []
        # md5 is lazy attribute, computed on demand
        #self.md5 = None
        self.size = None
        self.installed_size = None
        self.filename = None
        self.isdeb = 0
        self.fn = fn

	if fn:
            # see if it is deb format
            f = open(fn, "rb")
            magic = f.read(4)
            f.seek(0, 0)
            if (magic == "!<ar"):
                self.isdeb = 1

            stat = os.stat(fn)
            self.size = stat[ST_SIZE]    
            self.filename = os.path.basename(fn)
	    ## sys.stderr.write("  extracting control.tar.gz from %s\n"% (fn,)) 
	    if self.isdeb:
        	ar = arfile.ArFile(f)
        	tarStream = ar.open("control.tar.gz")
#                print tarStream
#                print tarStream.read()
        	tarf = tarfile.open("control.tar.gz", "r", tarStream)

        	try:
        	    control = tarf.extractfile("control")
        	except KeyError:
        	    control = tarf.extractfile("./control")
	    else:
		control = os.popen("tar --wildcards -xzO -f " + fn + " '*control.tar.gz' | tar xfzO - './control'", "r")

            self.read_control(control)
            control.close()

	self.scratch_dir = None
	self.file_dir = None
	self.meta_dir = None

    def __getattr__(self, name):
        if name == "md5":
            self._computeFileMD5()
            return self.md5
        else:
            raise AttributeError, name

    def _computeFileMD5(self):
        # compute the MD5.
        f = open(self.fn, "rb")
        sum = md5.new()
        while 1:
            data = f.read(1024)
            if not data: break
            sum.update(data)
        f.close()
        self.md5 = sum.hexdigest()

    def read_control(self, control):
        import os

        line = control.readline()
        while 1:
            if not line: break
            line = string.rstrip(line)
            lineparts = re.match(r'([\w-]*?):\s*(.*)', line)
            if lineparts:
                name = string.lower(lineparts.group(1))
                value = lineparts.group(2)
                while 1:
                    line = control.readline()
                    if not line: break
                    if line[0] != ' ': break
                    value = value + '\n' + line
                if name == 'size':
                    self.size = int(value)
	        elif name == 'md5sum':
                    self.md5 = value
                elif self.__dict__.has_key(name):
                    self.__dict__[name] = value
		else:
		    #print "Lost field %s, %s" % (name,value)
                    pass

                if line and line[0] == '\n':
                    return # consumes one blank line at end of package descriptoin
            else:
                line = control.readline()
                pass
        return    

    def _setup_scratch_area(self):
	self.scratch_dir = "%s/%sipkg" % (tempfile.gettempdir(),
					   tempfile.gettempprefix())
	self.file_dir = "%s/files" % (self.scratch_dir)
	self.meta_dir = "%s/meta" % (self.scratch_dir)

	os.mkdir(self.scratch_dir)
	os.mkdir(self.file_dir)
	os.mkdir(self.meta_dir)

    def set_package(self, package):
	self.package = package

    def get_package(self):
	return self.package
		
    def set_version(self, version):
	self.version = version
        self.parsed_version = parse_version(version)

    def get_version(self):
	return self.version

    def set_architecture(self, architecture):
	self.architecture = architecture

    def get_architecture(self):
	return self.architecture

    def set_maintainer(self, maintainer):
	self.maintainer = maintainer

    def get_maintainer(self):
	return self.maintainer

    def set_source(self, source):
	self.source = source

    def get_source(self):
	return self.source

    def set_description(self, description):
	self.description = description

    def get_description(self):
	return self.description

    def set_depends(self, depends):
	self.depends = depends

    def get_depends(self, depends):
	return self.depends

    def set_provides(self, provides):
	self.provides = provides

    def get_provides(self, provides):
	return self.provides

    def set_replaces(self, replaces):
	self.replaces = replaces

    def get_replaces(self, replaces):
	return self.replaces

    def set_conflicts(self, conflicts):
	self.conflicts = conflicts

    def get_conflicts(self, conflicts):
	return self.conflicts

    def set_suggests(self, suggests):
	self.suggests = suggests

    def get_suggests(self, suggests):
	return self.suggests

    def set_section(self, section):
	self.section = section

    def get_section(self, section):
	return self.section

    def get_file_list(self):
        if not self.fn:
            return []
	
	if self.isdeb:
    	    f = open(self.fn, "rb")
    	    ar = arfile.ArFile(f)
    	    tarStream = ar.open("data.tar.gz")
    	    tarf = tarfile.open("data.tar.gz", "r", tarStream)
    	    self.file_list = tarf.getnames()
    	    f.close()
	else:
            f = os.popen("tar xfzO " + self.fn + " '*data.tar.gz' | tar tfz -","r") 
            while 1: 
                line = f.readline() 
                if not line: break 
                self.file_list.append(string.rstrip(line)) 
            f.close() 

        # Make sure that filelist has consistent format regardless of tar version
        self.file_list = map(lambda a: ["./", ""][a.startswith("./")] + a, self.file_list)
        return self.file_list

    def write_package(self, dirname):
        buf = self.render_control()
	file = open("%s/control" % self.meta_dir, 'w')
	file.write(buf)

	self._setup_scratch_area()
	cmd = "cd %s ; tar cvfz %s/control.tar.gz control" % (self.meta_dir,
							      self.scratch_dir)

	cmd_out, cmd_in, cmd_err = os.popen3(cmd)
	
	while cmd_err.readline() != "":
	    pass

	cmd_out.close()
	cmd_in.close()
	cmd_err.close()

	bits = "control.tar.gz"

	if self.file_list:
		cmd = "cd %s ; tar cvfz %s/data.tar.gz" % (self.file_dir,
					   		   self.scratch_dir)

		cmd_out, cmd_in, cmd_err = os.popen3(cmd)

		while cmd_err.readline() != "":
		    pass

		cmd_out.close()
		cmd_in.close()
		cmd_err.close()

		bits = bits + " data.tar.gz"

	file = "%s_%s_%s.ipk" % (self.package, self.version, self.architecture)
	cmd = "cd %s ; tar cvfz %s/%s %s" % (self.scratch_dir,
					     dirname,
					     file,
					     bits)

	cmd_out, cmd_in, cmd_err = os.popen3(cmd)

	while cmd_err.readline() != "":
	    pass

	cmd_out.close()
	cmd_in.close()
	cmd_err.close()

    def compare_version(self, ref):
        """Compare package versions of self and ref"""
        if not self.version:
            print 'No version for package %s' % self.package
        if not ref.version:
            print 'No version for package %s' % ref.package
        if not self.parsed_version:
            self.parsed_version = parse_version(self.version)
        if not ref.parsed_version:
            ref.parsed_version = parse_version(ref.version)
        return self.parsed_version.compare(ref.parsed_version)

    def __repr__(self):
	out = ""

	# XXX - Some checks need to be made, and some exceptions
	#       need to be thrown. -- a7r

        if self.package: out = out + "Package: %s\n" % (self.package)
        if self.version: out = out + "Version: %s\n" % (self.version)
        if self.depends: out = out + "Depends: %s\n" % (self.depends)
        if self.provides: out = out + "Provides: %s\n" % (self.provides)
        if self.replaces: out = out + "Replaces: %s\n" % (self.replaces)
        if self.conflicts: out = out + "Conflicts: %s\n" % (self.conflicts)
        if self.suggests: out = out + "Suggests: %s\n" % (self.suggests)
        if self.recommends: out = out + "Recommends: %s\n" % (self.recommends)
        if self.section: out = out + "Section: %s\n" % (self.section)
        if self.architecture: out = out + "Architecture: %s\n" % (self.architecture)
        if self.maintainer: out = out + "Maintainer: %s\n" % (self.maintainer)
        if self.md5: out = out + "MD5Sum: %s\n" % (self.md5)
        if self.size: out = out + "Size: %d\n" % int(self.size)
        if self.installed_size: out = out + "InstalledSize: %d\n" % int(self.installed_size)
        if self.filename: out = out + "Filename: %s\n" % (self.filename)
        if self.source: out = out + "Source: %s\n" % (self.source)
        if self.description: out = out + "Description: %s\n" % (self.description)
	out = out + "\n"

	return out

    def __del__(self):
	# XXX - Why is the `os' module being yanked out before Package objects
	#       are being destroyed?  -- a7r
        pass

class Packages:
    """A currently unimplemented wrapper around the ipkg utility."""
    def __init__(self):
        self.packages = {}
        return

    def add_package(self, pkg):
        package = pkg.package
        arch = pkg.architecture
        name = ("%s:%s" % (package, arch))
        if (not self.packages.has_key(name)):
            self.packages[name] = pkg
        
        if pkg.compare_version(self.packages[name]) >= 0:
            self.packages[name] = pkg
            return 0
        else:
            return 1

    def read_packages_file(self, fn):
        f = open(fn, "r")
        while 1:
            pkg = Package()
            pkg.read_control(f)
            if pkg.get_package():
                self.add_package(pkg)
            else:
                break
        f.close()    
        return

    def write_packages_file(self, fn):
        f = open(fn, "w")
        names = self.packages.keys()
        names.sort()
        for name in names:
            f.write(self.packages[name].__repr__())
        return    

    def keys(self):
        return self.packages.keys()

    def __getitem__(self, key):
        return self.packages[key]

if __name__ == "__main__":

    assert Version(0, "1.2.2-r1").compare(Version(0, "1.2.3-r0")) == -1
    assert Version(0, "1.2.2-r0").compare(Version(0, "1.2.2+cvs20070308-r0")) == -1
    assert Version(0, "1.2.2+cvs20070308").compare(Version(0, "1.2.2-r0")) == 1
    assert Version(0, "1.2.2-r0").compare(Version(0, "1.2.2-r0")) == 0
    assert Version(0, "1.2.2-r5").compare(Version(0, "1.2.2-r0")) == 1

    package = Package()

    package.set_package("FooBar")
    package.set_version("0.1-fam1")
    package.set_architecture("arm")
    package.set_maintainer("Testing <testing@testing.testing>")
    package.set_depends("libc")
    package.set_description("A test of the APIs.")

    print "<"
    sys.stdout.write(package)
    print ">"

    package.write_package("/tmp")


########NEW FILE########
