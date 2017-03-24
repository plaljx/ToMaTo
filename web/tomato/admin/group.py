from django.shortcuts import render
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from . import AddEditForm, RemoveConfirmForm
from tomato.crispy_forms.layout import Layout
from ..lib import wrap_rpc
from ..admin_common import organization_name_list, Buttons, append_empty_choice


class GroupForm(AddEditForm):
	name = forms.CharField(max_length=50, help_text="The group's name. Must be unique.")
	organization = forms.CharField(max_length=255, help_text="The organization this group belongs to.")
	description = forms.CharField(widget=forms.Textarea, label="Description", required=False)

	buttons = Buttons.cancel_add

	def __init__(self, orga_list, *args, **kwargs):
		super(GroupForm, self).__init__(*args, **kwargs)
		self.fields["organization"].widget = forms.widgets.Select(choices=orga_list)
		self.helper.layout = Layout(
			'name',
			'organization',
			'description',
			self.buttons
		)

	def get_redirect_after(self):
		return HttpResponseRedirect(reverse("admin_group_info", kwargs={"name": self.cleaned_data['name']}))


class AddGroupForm(GroupForm):
	title = 'Add group'

	def __init__(self, orga_list, *args, **kwargs):
		super(AddGroupForm, self).__init__(orga_list, *args, **kwargs)
		if orga_list is not None:
			self.fields['organization'].initial = orga_list

	def submit(self, api):
		formData = self.get_optimized_data()
		api.group_create(formData)


class EditGroupForm(GroupForm):
	title = "Editing group %(name)s"
	buttons = Buttons.cancel_save

	def __init__(self, orga_list, *args, **kwargs):
		super(EditGroupForm, self).__init__(orga_list, *args, **kwargs)
		self.fields["name"].widget = forms.TextInput(attrs={'readonly': 'readonly'})
		self.fields["name"].help_text = None
		# if orga_list is not None:
		# 	self.fields['organization'].initial = orga_list
		self.fields["organization"].widget = forms.TextInput(attrs={'readonly': 'readonly'})
		self.fields["organization"].help_text = None

	def submit(self, api):
		formData = self.get_optimized_data()
		api.group_modify(formData['name'], {k: v for k, v in formData.iteritems() if k not in ('name',)})
		print formData['name']
		print {k: v for k, v in formData.iteritems() if k not in ('name',)}


class RemoveGroupForm(RemoveConfirmForm):
	message = "Are you sure you want to remove the group '%(name)s'?"
	title = "Remove Group '%(name)s'"


@wrap_rpc
def list_(api, request, organization=None):
	# TODO: organization filter
	groups = api.group_list()
	return render(request, "group/list.html", {'groups': groups})


@wrap_rpc
def info(api, request, name):
	group = api.group_info(name)
	return render(request, "group/info.html", {"group": group})


@wrap_rpc
def add(api, request):
	if request.method == 'POST':
		form = AddGroupForm(data=request.POST,
							orga_list=append_empty_choice(organization_name_list(api)))
		if form.is_valid():
			form.submit(api)
			return form.get_redirect_after()
		else:
			return form.create_response(request)
	else:
		form = AddGroupForm(
			orga_list=append_empty_choice(organization_name_list(api)))
		return form.create_response(request)


@wrap_rpc
def edit(api, request, name=None):
	if request.method=='POST':
		form = EditGroupForm(data=api.group_info(name),
							 orga_list=append_empty_choice(organization_name_list(api)))
		if form.is_valid():
			form.submit(api)
			return form.get_redirect_after()
		else:
			return form.create_response(request)
	else:
		form = EditGroupForm(data=api.group_info(name),
							 orga_list=append_empty_choice(organization_name_list(api)))
		return form.create_response(request)


@wrap_rpc
def remove(api, request, name):
	if request.method == 'POST':
		form = RemoveGroupForm(name=name, data=request.POST)
		if form.is_valid():
			api.group_remove(name)
			return HttpResponseRedirect(reverse('admin_group_list'))
	form = RemoveGroupForm(name=name)
	return form.create_response(request)
