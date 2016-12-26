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
from .. import scheduler
import os, os.path, shutil, threading
from .template import Template


kblang_options = {
	"en-us": "English (US)",
	"en-gb": "English (GB)",
	"de": "German",
	"fr": "French",
	"ja": "Japanese"
}


'''PATTERNS = {
	"kvm": "%s.qcow2",
	"kvmqm": "%s.qcow2",
	"openvz": "%s.tar.gz",
	"repy": "%s.repy",
}'''
PATTERNS = {
	"TAR": "%s.tar.gz",
	"RAR": "%s.rar",
	"ZIP": "%s.zip",
}

class Security(Entity, BaseDocument):
	"""
	:type host_urls: list of str
	"""
	tech = StringField(required=True)
	name = StringField(required=True, unique_with='tech')
	urls = ListField()
	host_urls = ListField()
	checksum = StringField()
	size = IntField()
	label = StringField()
	description = StringField()
	subtype = StringField()
	creationDate = FloatField(db_field='creation_date', required=False)
	hosts = ListField(StringField())
	available_template = ListField()
	#templates = ReferenceField(Template, required=True, reverse_delete_rule=DENY)
	icon = StringField()
	meta = {
		'ordering': ['tech', 'name'],
		'indexes': [
			('tech', 'name')
		]
	}

	@property
	def elements(self):
		from ..elements.generic import VMElement
		return VMElement.objects(security=self)

	def update_host_state(self, host, ready):
		if not "securityserver_port" in host.hostInfo:
			return  # old hostmanager
		if not self.checksum:
			return
		_, checksum = self.checksum.split(":")
		url = ("http://%s:%d/" + PATTERNS[self.tech]) % (host.address, host.hostInfo["securityserver_port"], checksum)
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
		"urls": Attribute(field=urls, schema=schema.List(items=schema.URL()), set=lambda obj, value: obj.modify_urls(value)),
		"all_urls": Attribute(schema=schema.List(items=schema.URL()), readOnly=True, get=lambda obj: obj.all_urls),
		"label": Attribute(field=label, schema=schema.String()),
		"description": Attribute(field=description, schema=schema.String()),
		"subtype": Attribute(field=subtype, schema=schema.String()),
		"creation_date": Attribute(field=creationDate, schema=schema.Number(null=True)),
		"icon": Attribute(field=icon),
		"available_template": Attribute(field=available_template, schema=schema.List(items=schema.String()), set=lambda obj, value: obj.modify_templates(value)),
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
			#"popularity": self.popularity,
			"checksum": self.checksum,
			"size": self.size,
			#"preference": self.preference
		}

	def init(self, **attrs):
		for attr in ["name", "tech", "urls"]:
			UserError.check(attr in attrs, code=UserError.INVALID_CONFIGURATION, message="Security needs attribute",
				data={"attribute": attr})
		Entity.init(self, **attrs)
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
		return os.path.join(settings.get_security_dir(), PATTERNS[self.tech] % self.name)
	
	'''def modify_kblang(self, val):
		UserError.check(self.tech == "kvmqm", UserError.UNSUPPORTED_ATTRIBUTE, "Unsupported attribute for %s template: kblang" % (self.tech), data={"tech":self.tech,"attr_name":"kblang","attr_val":val})
		self.kblang = val'''

	def modify_urls(self, val):
		self.urls = val
		self.fetch(detached=True)

	def modify_templates(self,val):
		self.templates = val



	def isReady(self):
		return not self.checksum is None

	def info(self, include_torrent_data = False):
		info = Entity.info(self)
		return info

	'''def on_selected(self):
		self.popularity += 1
		self.save()'''

	'''def update_popularity(self):
		self.popularity = 0.9 * (self.popularity + self.elements.count())
		self.save()'''

	@classmethod
	def get(cls, tech, name):
		try:
			return Security.objects.get(tech=tech, name=name)
		except:
			return None

	'''@classmethod
	def getPreferred(cls, tech):
		tmpls = Template.objects.filter(tech=tech).order_by("-preference")
		InternalError.check(tmpls, code=InternalError.CONFIGURATION_ERROR, message="No template for this type registered", data={"tech": tech})
		return tmpls[0]'''

	@classmethod
	def create(cls, **attrs):
		secur = Security.objects.filter(name=attrs["name"], tech=attrs["tech"])
		UserError.check(not secur, code=UserError.ALREADY_EXISTS,
						message="There exists already a security for this technology with a similar name",
						data={"name": attrs["name"], "tech": attrs["tech"]})
		obj = cls()
		try:
			obj.init(**attrs)
			obj.save()
			return obj
		except:
			obj.remove()
			raise

'''def update_popularity():
	for t in Template.objects():
		t.update_popularity()'''

def try_fetch():
	for t in Security.objects(checksum=None):
		t.fetch(True)

#scheduler.scheduleRepeated(24*60*60, update_popularity)
scheduler.scheduleRepeated(60*60, try_fetch)
