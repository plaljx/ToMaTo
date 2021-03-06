# -*- coding: utf-8 -*-
# ToMaTo (Topology management software) 
# Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from ..db import *
from ..generic import *
from .. lib.settings import settings
from ..lib.error import UserError, InternalError #@UnresolvedImport
from ..lib.newcmd import aria2
from ..lib.newcmd.util import fs
from ..lib.constants import TypeName
from .. import scheduler
import os, os.path, shutil, threading


kblang_options = {
	"en-us": "English (US)",
	"en-gb": "English (GB)",
	"de": "German",
	"fr": "French",
	"ja": "Japanese"
}


PATTERNS = {
	TypeName.FULL_VIRTUALIZATION: "%s.qcow2",
	TypeName.CONTAINER_VIRTUALIZATION: "%s.tar.gz",
	TypeName.REPY: "%s.repy",
}

class Template(Entity, BaseDocument):
	"""
	:type host_urls: list of str
	"""
	tech = StringField(required=True)
	name = StringField(required=True, unique_with='tech')
	popularity = FloatField(default=0)
	preference = IntField(default=0)
	urls = ListField()
	host_urls = ListField()
	checksum = StringField()
	size = IntField()
	label = StringField()
	description = StringField()
	restricted = BooleanField(default=False)
	subtype = StringField()
	kblang = StringField(default='en-us')
	nlXTPInstalled = BooleanField(db_field='nlxtp_installed')
	showAsCommon = BooleanField(db_field='show_as_common')
	creationDate = FloatField(db_field='creation_date', required=False)
	hosts = ListField(StringField())
	icon = StringField()

	#add by None at 2016/12/28
	customize = StringField(required = False)

	meta = {
		'ordering': ['tech', '+preference', 'name'],
		'indexes': [
			('tech', 'preference'), ('tech', 'name')
		]
	}

	@property
	def elements(self):
		from ..elements.generic import VMElement
		return VMElement.objects(template=self)

	def update_host_state(self, host, ready):
		if not "templateserver_port" in host.hostInfo:
			return  # old hostmanager
		if not self.checksum:
			return
		_, checksum = self.checksum.split(":")
		url = ("http://%s:%d/" + PATTERNS[self.tech]) % (host.address, host.hostInfo["templateserver_port"], checksum)
		if url in self.host_urls:
			self.host_urls.remove(url)
		if host.name in self.hosts:
			self.hosts.remove(host.name)
		if ready:
			self.hosts.append(host.name)
			self.host_urls.append(url)
		self.save()

	@property
	def all_urls(self):
		return list(self.host_urls)+list(self.urls)

	def getReadyInfo(self):
		from ..host import Host
		return {
			"backend": self.isReady(),
			"hosts": {
				"ready": len(self.hosts),
				"total": Host.objects.count()
			}
		}

	def remove(self, **kwargs):
		if self.tech and os.path.exists(self.getPath()):
			if os.path.isdir(self.getPath()):
				shutil.rmtree(self.getPath())
			else:
				os.remove(self.getPath())
		if self.id:
			self.delete()

	ACTIONS = {
		Entity.REMOVE_ACTION: Action(fn=remove)
	}
	ATTRIBUTES = {
		"id": IdAttribute(),
		"tech": Attribute(field=tech, schema=schema.String(options=PATTERNS.keys())),
		"name": Attribute(field=name, schema=schema.Identifier()),
		"popularity": Attribute(field=popularity, readOnly=True, schema=schema.Number(minValue=0)),
		"urls": Attribute(field=urls, schema=schema.List(items=schema.URL()), set=lambda obj, value: obj.modify_urls(value)),
		"all_urls": Attribute(schema=schema.List(items=schema.URL()), readOnly=True, get=lambda obj: obj.all_urls),
		"preference": Attribute(field=preference, schema=schema.Number(minValue=0)),
		"label": Attribute(field=label, schema=schema.String()),
		"description": Attribute(field=description, schema=schema.String()),
		"restricted": Attribute(field=restricted, schema=schema.Bool()),
		"subtype": Attribute(field=subtype, schema=schema.String()),
		"kblang": Attribute(field=kblang, set=lambda obj, value: obj.modify_kblang(value),
			schema=schema.String(options=kblang_options.keys())),
		"nlXTP_installed": Attribute(field=nlXTPInstalled),
		"show_as_common": Attribute(field=showAsCommon),
		"customize": Attribute(field=customize),
		"creation_date": Attribute(field=creationDate, schema=schema.Number(null=True)),
		"icon": Attribute(field=icon),
		"size": Attribute(get=lambda obj: float(obj.size) if obj.size else obj.size, readOnly=True, schema=schema.Number()),
		"checksum": Attribute(readOnly=True, field=checksum, schema=schema.String()),
		"ready": Attribute(readOnly=True, get=getReadyInfo, schema=schema.StringMap(items={
				'backend': schema.Bool(),
				'hosts': schema.StringMap(items={
					'ready': schema.Int(),
					'total': schema.Int()
				})
			})
		)
	}

	def info_for_hosts(self):
		return {
			"tech": self.tech,
			"name": self.name,
			"urls": self.urls,
			"popularity": self.popularity,
			"checksum": self.checksum,
			"size": self.size,
			"preference": self.preference
		}

	def init(self, **attrs):
		for attr in ["name", "tech", "urls"]:
			UserError.check(attr in attrs, code=UserError.INVALID_CONFIGURATION, message="Template needs attribute",
				data={"attribute": attr})
		if 'kblang' in attrs:
			kblang = attrs['kblang']
			del attrs['kblang']
		else:
			kblang=None
		Entity.init(self, **attrs)
		if kblang:
			self.modify(kblang=kblang)
		self.fetch(detached=True)

	def fetch(self, detached=False):
		if not self.urls:
			return
		if detached:
			return threading.Thread(target=self.fetch).start()
		path = self.getPath()
		aria2.download(self.urls, path)
		self.size = fs.file_size(path)
		old_checksum = self.checksum
		self.checksum = "sha1:%s" % fs.checksum(path, "sha1")
		if old_checksum != self.checksum:
			self.host_urls = []
			self.hosts = []
		self.save()

	def getPath(self):
		return os.path.join(settings.get_template_dir(), PATTERNS[self.tech] % self.name)
	
	def modify_kblang(self, val):
		UserError.check(self.tech == TypeName.FULL_VIRTUALIZATION, UserError.UNSUPPORTED_ATTRIBUTE, "Unsupported attribute for %s template: kblang" % (self.tech), data={"tech":self.tech,"attr_name":"kblang","attr_val":val})
		self.kblang = val

	def modify_urls(self, val):
		self.urls = val
		self.fetch(detached=True)

	def isReady(self):
		return not self.checksum is None

	def info(self, include_torrent_data = False):
		info = Entity.info(self)
		return info

	def on_selected(self):
		self.popularity += 1
		self.save()

	def update_popularity(self):
		self.popularity = 0.9 * (self.popularity + self.elements.count())
		self.save()

	@classmethod
	def get(cls, tech, name):
		try:
			return Template.objects.get(tech=tech, name=name)
		except:
			return None

	@classmethod
	def getPreferred(cls, tech):
		tmpls = Template.objects.filter(tech=tech).order_by("-preference")
		InternalError.check(tmpls, code=InternalError.CONFIGURATION_ERROR, message="No template for this type registered", data={"tech": tech})
		return tmpls[0]

	@classmethod
	def create(cls, **attrs):
		tmpls = Template.objects.filter(name=attrs["name"], tech=attrs["tech"])
		UserError.check(not tmpls, code=UserError.ALREADY_EXISTS,
						message="There exists already a template for this technology with a similar name",
						data={"name": attrs["name"], "tech": attrs["tech"]})
		obj = cls()
		try:
			obj.init(**attrs)
			obj.save()
			return obj
		except:
			obj.remove()
			raise

def update_popularity():
	for t in Template.objects():
		t.update_popularity()

def try_fetch():
	for t in Template.objects(checksum=None):
		t.fetch(True)

scheduler.scheduleRepeated(24*60*60, update_popularity)
scheduler.scheduleRepeated(60*60, try_fetch)
