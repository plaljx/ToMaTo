from django.shortcuts import render
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from . import AddEditForm, RemoveConfirmForm, ConfirmForm, RenderableForm
from ..crispy_forms.layout import Layout
from ..lib import wrap_rpc, AuthError
from ..admin_common import Buttons


class GroupForm(AddEditForm):

	name = forms.CharField(max_length=64, label="Name", help_text="The group's name. Must be unique.")
	label = forms.CharField(max_length=255, label="Label", help_text="")
	description = forms.CharField(widget=forms.Textarea, label="Description", required=False)
	owner = forms.CharField(label="Owner", required=False)

	buttons = Buttons.cancel_add

	def __init__(self, *args, **kwargs):
		super(GroupForm, self).__init__(*args, **kwargs)
		# self.helper.layout = Layout(
		# 	'name',
		# 	'label',
		# 	'description',
		# 	'owner',
		# 	self.buttons
		# )

	def get_redirect_after(self):
		return HttpResponseRedirect(reverse("admin_group_info", kwargs={"group": self.cleaned_data['name']}))


class AddGroupForm(GroupForm):
	title = 'Add group'

	def __init__(self, *args, **kwargs):
		super(AddGroupForm, self).__init__(*args, **kwargs)
		self.helper.layout = Layout(
			'name',
			'label',
			'description',
			'owner',
			self.buttons
		)
		self.fields['owner'].widget.attrs['readonly'] = 'True'

	def submit(self, api):
		formData = self.get_optimized_data()
		api.group_create({k: v for k, v in formData.iteritems()})


class EditGroupForm(GroupForm):
	title = "Editing group %(name)s"
	buttons = Buttons.cancel_save

	def __init__(self, *args, **kwargs):
		super(EditGroupForm, self).__init__(*args, **kwargs)
		self.helper.layout = Layout(
			'name',
			'label',
			'description',
			'owner',
			self.buttons
		)
		self.fields["name"].widget.attrs['readonly'] = 'True'
		self.fields["name"].help_text = None
		self.fields["owner"].widget.attrs['readonly'] = 'True'

	def submit(self, api):
		formData = self.get_optimized_data()
		api.group_modify(formData['name'], {k: v for k, v in formData.iteritems() if k not in ('name',)})


class RemoveGroupForm(RemoveConfirmForm):
	message = "Are you sure you want to remove the group '%(name)s'?"
	title = "Remove Group '%(name)s'"


class HandleInviteForm(ConfirmForm):
	message = None
	title = None

	def __init__(self, operation, *args, **kwargs):
		if operation is True or operation == 'accept':
			self.message = "Are you sure you want to accept the invite to group '%(name)s'?"
			self.title = "Accept invite to group '%(name)s'?"
		elif operation is False or operation == 'decline':
			self.message = "Are you sure you want to decline the invite to group '%(name)s'?"
			self.title = "Decline invite to group '%(name)s'?"
		super(HandleInviteForm, self).__init__(*args, **kwargs)


class ApplyGroupForm(ConfirmForm):
	message = "Are you sure you want to apply joining group '%(name)s'?"
	title = "Apply Group %(name)s'"


class HandleApplicationForm(RenderableForm):
	message = None
	title = None
	buttons = Buttons.cancel_continue
	formaction_haskeys = True

	def __init__(self, user, group, operation, *args, **kwargs):
		super(HandleApplicationForm, self).__init__(*args, **kwargs)
		self.helper.layout = Layout(self.buttons)
		if operation is True or operation == 'accept':
			self.message = "Are you sure you want to accept the application from user %s to group %s?" % (user, group)
			self.title = "Accept group application"
		elif operation is False or operation == 'decline':
			self.message = "Are you sure you want to decline the application from user %s to group %s?" % (user, group)
			self.title = "Decline group application"


@wrap_rpc
def list_(api, request, user=None, role=None):
	"""
	List the groups.
	If 'user' is None, this will show all groups, and 'role' will be omitted
	Else, 'role' will be checked, if 'role' is not specified, this will show all groups that current user has a role
	"""
	if not api.user:
		raise AuthError()
	if role not in ['owner', 'manager', 'user', 'invited', None]:
		raise Exception('Invalid parameter \'role\': %s' % role)
	groups = api.group_list(user=user, role=role)
	# Add group role info about the current user
	for group in groups:
		group['role'] = api.user.getGroupRole(group['name'])

	return render(request, "group/list.html", {'groups': groups, 'role': role})


@wrap_rpc
def info(api, request, group):
	if not api.user:
		raise AuthError()
	group_info = api.group_info(group)
	role = api.user.getGroupRole(group_info['name'])
	return render(request, "group/info.html", {"group": group_info, "role": role})


@wrap_rpc
def add(api, request):
	if not api.user:
		raise AuthError()
	if request.method == 'POST':
		form = AddGroupForm(data=request.POST)
		if form.is_valid():
			form.submit(api)
			return form.get_redirect_after()
		else:
			return form.create_response(request)
	else:
		data = {'owner': api.user.name}
		form = AddGroupForm(data=data)
		return form.create_response(request)


@wrap_rpc
def edit(api, request, group):
	if not api.user:
		raise AuthError()
	if request.method == 'POST':
		form = EditGroupForm(data=request.POST)
		if form.is_valid():
			form.submit(api)
			return form.get_redirect_after()
		else:
			return form.create_response(request)
	else:
		form = EditGroupForm(data=api.group_info(group))
		return form.create_response(request)


@wrap_rpc
def remove(api, request, group):
	if not api.user:
		raise AuthError()
	if request.method == 'POST':
		form = RemoveGroupForm(name=group, data=request.POST)
		if form.is_valid():
			api.group_remove(group)
			return HttpResponseRedirect(reverse('admin_group_list'))
	form = RemoveGroupForm(name=group)
	return form.create_response(request)


@wrap_rpc
def handle_invite(api, request, user, group, operation):
	if operation not in ['accept', 'decline']:
		raise Exception("Invalid parameter 'operation'")
	if not api.user:
		raise AuthError()
	if user != api.user.name:
		raise Exception("You are not allowed to handle other's invites.")
	if request.method == 'POST':
		form = HandleInviteForm(operation, name=group, data=request.POST)
		if form.is_valid():
			api.account_handle_invite(group, operation)
			return HttpResponseRedirect(reverse('admin_group_list'))
		else:
			raise Exception('Form is not valid')
	else:
		form = HandleInviteForm(operation, name=group)
		return form.create_response(request)


@wrap_rpc
def apply_(api, request, user, group):
	if not api.user:
		raise AuthError()
	if request.method == 'POST':
		form = ApplyGroupForm(name=group, data=request.POST)
		if form.is_valid():
			api.group_apply(user, group)
			return HttpResponseRedirect(reverse('admin_group_list'))
		else:
			raise Exception('form is not valid')
	else:
		form = ApplyGroupForm(name=group)
		return form.create_response(request)


@wrap_rpc
def handle_application(api, request, user, group, operation=None):
	if not api.user:
		raise AuthError()
	if request.method == 'POST':
		form = HandleApplicationForm(user, group, operation, data=request.POST)
		if form.is_valid():
			api.handle_application(user, group, operation)
			return HttpResponseRedirect(reverse('admin_group_list'))
		else:
			raise Exception('Form is not valid')
	else:
		form = HandleApplicationForm(user, group, operation)
		return form.create_response(request)
