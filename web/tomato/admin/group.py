from django.shortcuts import render
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from . import AddEditForm, RemoveConfirmForm
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


@wrap_rpc
def list_(api, request, user=None, role=None):
	"""
	List the groups.
	If 'user' is None, this will show all groups, and 'role' will be omitted
	Else, 'role' will be checked, if 'role' is not specified, this will show all groups that current user has a role
	"""
	if not api.user:
		raise AuthError()
	groups = api.group_list(user=user, role=role)
	# Add group role info about the current user
	for group in groups:
		# 'owner', 'manager', 'user', or None
		group['role'] = api.user.getGroupRole(group['name'])

	return render(request, "group/list.html", {'groups': groups})


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
