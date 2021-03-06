"""
DDTSS-Django - A Django implementation of the DDTP/DDTSS website.
Copyright (C) 2011-2014 Martijn van Oosterhout <kleptog@svana.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import re
import hashlib
import subprocess

from collections import defaultdict
from datetime import date
from debian.deb822 import Deb822
from ddtp.database import db, ddtp
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Imports a package file into the database"
    args = "tag [Translation-en] <Packages Packages ...>"

    requires_model_validation = False

    comma_sep_RE = re.compile(r'\s*,\s*')

    def _open(self, filename):
        if filename.endswith('.bz2'):
            f = subprocess.Popen(['bzcat', filename], stdout=subprocess.PIPE)
            return f.stdout
        if filename.endswith('.gz'):
            f = subprocess.Popen(['zcat', filename], stdout=subprocess.PIPE)
            return f.stdout
        f = open(filename, "r")
        return f

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Require a tag, e.g. sid, wheezy, squeeze, etc...")
        tag = args[0]
        filenames = args[1:]
        if not tag.isalpha() or not tag.islower():
            raise CommandError("First argument must be tag, e.g. sid, wheezy, squeeze, etc...")

        self.session = db.get_db_session()
#        self.session.bind.echo=False

        self.descr_text_map = {}
        self.descr_map = {}
        self.stats = defaultdict(int)

        for file in filenames:
            self.stderr.write('Processing %s\n' % file)
            f = self._open(file)
            for para in Deb822.iter_paragraphs(f):
                if 'Description-en' in para:
                    self._handle_translation_en(para)
                if 'Version' in para:
                    try:
                        self._handle_packages(tag, para)
                    except Exception, e:
                        self.stdout.write("Problem processing %r\n%s\n" % (para, e))
            self.session.commit()

        self.stdout.write("Processed descriptions %d, unique %d, new %d\n" %
                          (self.stats['count-descr'], self.stats['fetch-descr'], self.stats['new-descr']))
        self.stdout.write("New tags %d, updated tags %d, new package versions %d, new parts %d\n" %
                          (self.stats['new-tag'], self.stats['upd-tag'], self.stats['new-package_version'], self.stats['new-part']))

    def _handle_translation_en(self, para):
        """ para is the paragraph in the Translation-en file """

        md5 = para['Description-md5']
        text = para['Description-en'] + "\n"

        assert md5 == hashlib.md5(text.encode('utf-8')).hexdigest()

        self.descr_text_map[md5] = text

    def _handle_packages(self, tag, para):
        """ Take a packages paragraph and merges it with the database. Tag is sid, wheezy, etc """
        if 'Description-md5' in para:
            # New style
            md5 = para['Description-md5']
            text = self.descr_text_map.get(md5)
            if not text:
                raise CommandError("Couldn't find description for md5 %s, did you provide the correct Translations-en file?" % md5)
        else:
            text = para['Description'] + "\n"
            md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

        self.stats['count-descr'] += 1
        description = self.descr_map.get(md5)
        if not description:
            description=self.session.query(ddtp.Description).filter(ddtp.Description.description_md5==md5).first()
            self.stats['fetch-descr'] += 1

        package = para['Package']
        source = para.get('Source', package)  # Source defaults to Package
        version = para['Version']

        if not description:
            # New description, everything new
            description = ddtp.Description(description_md5=md5,
                                           description=text,
                                           package=package,   # These fields will go
                                           source=source)     # away eventually
            self.session.add(description)
            self.stats['new-descr'] += 1
        else:
            # Cheap test to enusre the database contents are OK
            if description.description != text:
                description.description = text

        self.descr_map[md5] = description

        # update Tags
        tag_obj = description.has_tag(tag)
        if tag_obj:
            if tag_obj.date_end < date.today():
                tag_obj.date_end = date.today()
                self.stats['upd-tag'] += 1
        else:
            description_tag = ddtp.DescriptionTag(tag=tag,
                                                  description=description,
                                                  date_begin=date.today(),
                                                  date_end=date.today())
            self.session.add(description_tag)
            self.stats['new-tag'] += 1

        # add PackageVersions
        package_version = description.has_package_version(package, version)
        if package_version:
            package_version.source = source
        else:
            package_version = ddtp.PackageVersion(package=package,
                                                  version=version,
                                                  description=description,
                                                  source=source)
            self.session.add(package_version)
            self.stats['new-package_version'] += 1

        # add Parts
        parts_list = description.get_description_part_objects()
        for part_text, part_md5, part_obj in parts_list:
            if not part_obj:
                part_obj = ddtp.PartDescription(part_md5=part_md5)
                part_obj.description = description
                self.session.add(part_obj)
                self.stats['new-part'] += 1

        self.session.flush()
