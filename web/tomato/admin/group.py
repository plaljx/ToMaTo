from django.shortcuts import render
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from . import AddEditForm, RemoveConfirmForm
from tomato.crispy_forms.layout import Layout
from ..lib import wrap_rpc
from ..admin_common import Buttons


class GroupForm(AddEditForm):
	# TODO
	pass


class AddGroupForm(GroupForm):
	# TODO
	pass


class EditGroupForm(GroupForm):
	# TODO
	pass


class RemoveGroupForm(RemoveConfirmForm):
	# TODO
	pass


@wrap_rpc
def list_(api, request, show_all=True):
	# TODO: permission, need login
	# TODO: show_all
	groups = api.group_list()

	# Add group role info about the current user
	for group_role in groups:
		# 'owner', 'manager', 'user', or None
		group_role.role = api.user.getGroupRole(group_role.group)

	return render(request, "group/list.html", {'groups': groups})


@wrap_rpc
def info(api, request, group):
	# TODO: permission, need login
	group = api.group_info(group)
	role = api.user.getGroupRole(group)
	return render(request, "group/info.html", {"group": group, "role": role})



@wrap_rpc
def edit(api, request, group):
	# TODO
	pass




