import time, zlib, threading, base64
from .db import *
from .lib import anyjson as json

import host
from . import scheduler, config, currentUser
from .lib.error import InternalError, UserError # @UnresolvedImport


# Zero-th part: database stuff
class ErrorDump(EmbeddedDocument):
	source = StringField(required=True)
	dumpId = StringField(db_field='dump_id', required=True) #not unique, different semantics on embedded documents
	description = DictField(required=True)
	data = StringField()
	dataAvailable = BooleanField(default=False, db_field='data_available')
	type = StringField(required=True)
	softwareVersion = DictField(db_field='software_version')
	timestamp = FloatField(required=True)
	meta = {
		'ordering': ['+timestamp'],
	}

	def getSource(self):
		return find_source_by_name(self.source)

	def modify_data(self, data, is_compressed=True):
		if data is None:
			self.data = None
			self.dataAvailable = False
			return
		if is_compressed:
			data_toinsert = data
		else:
			data_toinsert = base64.b64encode(zlib.compress(json.dumps(data), 9))
		self.data = data_toinsert
		self.dataAvailable = True

	def fetch_data_from_source(self):
		d = self.getSource().dump_fetch_with_data(self.dumpId, True)
		self.modify_data(d['data'], True)

	def info(self, include_data=False):
		dump = {
			'source': self.source,
			'dump_id': self.dumpId,
			'description': self.description,
			'type': self.type,
			'software_version': self.softwareVersion,
			'timestamp': self.timestamp
		}
		if include_data:
			if not self.dataAvailable:
				self.fetch_data_from_source()
			dump['data'] = json.loads(zlib.decompress(base64.b64decode(self.data)))
		else:
			dump['data_available'] = self.dataAvailable
		return dump

class ErrorGroup(BaseDocument):
	"""
	:type dumps: list of ErrorDump
	"""
	groupId = StringField(db_field='group_id', required=True, unique=True)
	description = StringField(required=True)
	removedDumps = IntField(default=0, db_field='removed_dumps')
	dumps = ListField(EmbeddedDocumentField(ErrorDump))
	meta = {
		'collection': 'error_group',
		'ordering': ['groupId'],
		'indexes': [
			'groupId'
		]
	}

	def update_description(self, description):
		self.description = description
		self.save()
		
	def shrink(self):
		oldLen = len(self.dumps)
		if oldLen <= 10:
			return
		self.dumps = self.dumps[5:-5]
		self.removedDumps += oldLen - len(self.dumps)
		self.save()

	def info(self):
		res = {
			'group_id': self.groupId,
			'description': self.description,
			'count': self.removedDumps,
			'last_timestamp': 0,
		    'data_available':False,
            'dump_contents':{}
		}

		select_unique_values = ['software_version', 'source', 'type', 'description']
		for val in select_unique_values:
			res['dump_contents'][val] = []

		res['count'] += len(self.dumps)
		for dump in self.dumps:
			if dump.dataAvailable:
				res['data_available'] = True
			if dump.timestamp > res['last_timestamp']:
				res['last_timestamp'] = dump.timestamp
			for val in select_unique_values:
				if not dump[val] in res['dump_contents'][val]:
					res['dump_contents'][val].append(getattr(dump, val))
		return res

	def remove(self):
		self.delete()


def create_group(group_id, description=None):
	desc = description or group_id
	if isinstance(desc, dict) and "message" in desc:
		desc = desc["message"]
	if not isinstance(desc, str):
		desc = str(desc)
	if len(desc) > 100:
		desc = desc[:100] + " ..."
	if not desc:
		desc = group_id
	return ErrorGroup(groupId=group_id, description=desc).save()


def get_group(group_id):
	"""
	:rtype :ErrorGroup or None
	"""
	try:
		return ErrorGroup.objects.get(groupId=group_id)
	except ErrorGroup.DoesNotExist:
		return None

def getAll_group():
	return ErrorGroup.objects.all()


def remove_group(group_id):
	grp = get_group(group_id)
	if grp is not None:
		grp.remove()
		return True
	return False

def create_dump(dump, source):
	return ErrorDump(
		source=source.dump_source_name(),
		dumpId=dump['dump_id'],
		groupId=dump['group_id'],
		timestamp = dump['timestamp'],
		description = dump['description'],
		type = dump['type'],
		software_version = dump['software_version']
	)

#First part: fetching dumps from all the sources.

#this class should not be instantiated. There are two subclasses available: one that can connect to a host, and one that connects to this backend.
class DumpSource(object):
	#dump_last_fetch = None

	#to be implemented in subclass
	#fetches all dumps from the source, which were thrown after *after*.
	#after is a float and will be used unchanged.
	#if this throws an exception, the fetching is assumed to have been unsuccessful.
	def dump_fetch_list(self, after):
		raise NotImplemented()

	def dump_get_last_fetch(self):
		raise NotImplemented()

	#to be implemented in subclass
	#fetches all data about the given dump.
	#if this throws an exception, the fetching is assumed to have been unsuccessful.
	def dump_fetch_with_data(self, dump_id, keep_compressed=True):
		raise NotImplemented()

	#to be implemented in a subclass
	#if the source has its clock before the backend, and an error is thrown in exactly this difference,
	#the dump would be skipped.
	#Thus, use the known clock offset to fetch dumps that might have occurred in this phase (i.e., right after the last fetch)
	#returns a float. should be ==0 if the source's clock is ahead, and >0 if the source's clock is behind
	def dump_clock_offset(self):
		raise NotImplemented()

	#to be implemented in a subclass
	#returns a string to uniquely identify the source
	def dump_source_name(self):
		raise NotImplemented()

	#override for HostDumpSource. Return true if the given host is this one
	def dump_matches_host(self, host_obj):
		raise NotImplemented()

	#override in subclass
	def dump_set_last_fetch(self, last_fetch):
		raise NotImplemented()

	def dump_getUpdates(self):
		this_fetch_time = time.time() - self.dump_clock_offset()
		try:
			fetch_results = self.dump_fetch_list(self.dump_get_last_fetch())
			if len(fetch_results)>0: #if the list is empty, no need to set this. However, if the list is empty for incorrect reasons (i.e., errors), 
									#we may still be able to get the dumps when the error is resolved.
				self.dump_set_last_fetch(this_fetch_time)
			return fetch_results
		except Exception as exc:
			InternalError(code=InternalError.UNKNOWN, message="Failed to retrieve dumps: %s" % exc, data={"source": repr(self)}).dump()
			return []


#fetches from this backend
class BackendDumpSource(DumpSource):
	keyvaluestore_key = "dumpmanager:lastBackendFetch"

	def dump_fetch_list(self, after):
		import dump
		return dump.getAll(after=after, list_only=False, include_data=False, compress_data=True)

	def dump_fetch_with_data(self, dump_id, keep_compressed=True):
		import dump
		d = dump.get(dump_id, include_data=True, compress_data=True)
		if not keep_compressed:
			d['data'] = json.loads(zlib.decompress(base64.b64decode(d['data'])))
		return d

	def dump_clock_offset(self):
		return 0

	def dump_source_name(self):
		return "backend"

	def dump_set_last_fetch(self, last_fetch):
		data.set(self.keyvaluestore_key, last_fetch)

	def dump_get_last_fetch(self):
		return data.get(self.keyvaluestore_key, 0)

backend_dumpsource = BackendDumpSource()

def getDumpSources():
	sources = [backend_dumpsource]
	hosts = host.getAll()
	for h in hosts:
		if h.enabled:
			sources.append(h)
	return sources

#only one thread may write to the dump table at a time.
lock_db = threading.RLock()


def find_source_by_name(source_name):
	for s in getDumpSources():
		if s.dump_source_name() == source_name:
			return s
	return None


def insert_dump(dump, source):
	with lock_db:
		source_name = source.dump_source_name()
		must_fetch_data = False

		# check whether the group ID already exists. If not, create it,
		# remember to fetch dump data in the end, and email developer users
		group = get_group(dump['group_id'])
		if not group:
			from auth import mailFlaggedUsers, Flags
			must_fetch_data = True
			group = create_group(dump['group_id'], dump['description'])
			mailFlaggedUsers(Flags.ErrorNotify, "[ToMaTo Devs] New Error Group",
				"A new group of error has been found, with ID %s. It has first been observed on %s." % (
				dump['group_id'], source.dump_source_name()))

		#insert the dump.
		for d in group.dumps:
			if d.dumpId == dump['dump_id'] and d.source == source_name:
				return
		dump_db = create_dump(dump, source)

		#if needed, load data
		if must_fetch_data:
			dump_db.fetch_data_from_source()


def update_source(source):
	try:
		new_entries = source.dump_getUpdates()
		for e in new_entries:
			insert_dump(e, source)
	finally:
		for group in getAll_group():
			with lock_db:
				group.shrink()



def update_all(async=True):
	for s in getDumpSources():
		if async:
			scheduler.scheduleOnce(0, update_source, s)
		else:
			update_source(s)
	return len(getDumpSources())


def init():
	scheduler.scheduleRepeated(config.DUMP_COLLECTION_INTERVAL, update_all, immediate=True)


# Second Part: Access to known dumps for API

def checkPermissions():
	from auth import Flags
	user = currentUser()
	UserError.check(user, code=UserError.NOT_LOGGED_IN, message="Unauthorized")
	UserError.check(user.hasFlag(Flags.Debug), code=UserError.DENIED, message="Not enough permissions")


def api_errorgroup_list(show_empty=False):
	checkPermissions()
	with lock_db:
		res = []
		for grp in getAll_group():
			if show_empty or (grp.dumps.count()>0):
				res.append(grp.info())
		return res


def api_errorgroup_modify(group_id, attrs):
	checkPermissions()
	with lock_db:
		for i in attrs.keys():
			UserError.check(i == "description", code=UserError.UNSUPPORTED_ATTRIBUTE,
				message="Unsupported attribute for error group", data={"attribute": i})
		grp = get_group(group_id)
		UserError.check(grp is not None, code=UserError.ENTITY_DOES_NOT_EXIST, message="error group does not exist", data={"group_id":group_id})
		grp.update_description(attrs['description'])


def api_errorgroup_info(group_id, include_dumps=False):
	checkPermissions()
	with lock_db:
		group = get_group(group_id)
		UserError.check(group is not None, code=UserError.ENTITY_DOES_NOT_EXIST, message="error group does not exist", data={"group_id":group_id})
		res = group.info()
		if include_dumps:
			res['dumps'] = []
			for i in group.dumps:
				res['dumps'].append(i.info())
		return res

def api_errordump_info(group_id, source, dump_id, include_data=False):
	checkPermissions()
	with lock_db:
		group = get_group(group_id)
		UserError.check(group, code=UserError.ENTITY_DOES_NOT_EXIST, message="error group does not exist", data={"group_id":group_id})
		dump = None
		for d in group.dumps:
			if d.dumpId == dump_id and d.source == source:
				dump = d
				break
		UserError.check(dump, code=UserError.ENTITY_DOES_NOT_EXIST, message="error dump does not exist", data={"dump_id":dump_id,"source":source})
		return dump.info(include_data)

def api_errorgroup_remove(group_id):
	checkPermissions()
	with lock_db:
		res = remove_group(group_id)
		UserError.check(res, code=UserError.ENTITY_DOES_NOT_EXIST, message="error group does not exist", data={"group_id":group_id})

def api_errordump_list(group_id, source=None, data_available=None):
	checkPermissions()
	with lock_db:
		group = get_group(group_id)
		UserError.check(group, code=UserError.ENTITY_DOES_NOT_EXIST, message="error group does not exist", data={"group_id":group_id})
		res = []
		for d in group.dumps:
			di = d.info(include_data=False)
			append_to_res = True
			if not source is None and di['source'] != source:
				append_to_res = False
			if not data_available is None and di['data_available'] != data_available:
				append_to_res = False
			if append_to_res:
				res.append(di)
		return res

def api_force_refresh():
	checkPermissions()
	return update_all(async=False)
