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

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from lib import wrap_rpc
from admin_common import RemoveConfirmForm, BootstrapForm, Buttons
from django.core.urlresolvers import reverse

from tomato.crispy_forms.layout import Layout

from django.utils.translation import ugettext_lazy as _

from lib.error import UserError #@UnresolvedImport


class NetworkForm(BootstrapForm):
	kind = forms.CharField(label=_("Kind"),max_length=255)
	label = forms.CharField(max_length=255,label=_("Label"),help_text=_("Visible Name"))
	preference = forms.IntegerField(label=_("Preference"), help_text=_("Sort networks in the editor (higher preference first). The item with the highest preference will be the default one. An integer number."))
	description = forms.CharField(widget = forms.Textarea, required=False, label = _('description'))
	big_icon = forms.BooleanField(label=_("Show as a big icon in the editor"), required=False)
	show_as_common = forms.BooleanField(label=_("Show in Common Elements"), help_text=_("Show this network in the common elements section in the editor"), required=False)
	def __init__(self, *args, **kwargs):
		super(NetworkForm, self).__init__(*args, **kwargs)
		self.helper.form_action = reverse(add)
		self.helper.layout = Layout(
			'kind',
			'label',
			'preference',
            'show_as_common',
			'big_icon',
			'description',
			Buttons.cancel_add
		)
	
class EditNetworkForm(NetworkForm):
	res_id = forms.CharField(max_length=50, widget=forms.HiddenInput)
	def __init__(self, res_id, *args, **kwargs):
		super(EditNetworkForm, self).__init__(*args, **kwargs)
		self.fields["kind"].widget=forms.TextInput(attrs={'readonly':'readonly'})
		self.fields["kind"].help_text=None
		self.helper.form_action = reverse(edit, kwargs={"res_id": res_id})
		self.helper.layout = Layout(
			'res_id',
			'kind',
			'label',
			'preference',
            'show_as_common',
			'big_icon',
			'description',
			Buttons.cancel_save
		)
	
@wrap_rpc
def list(api, request):
	netw_list = api.network_list()
	print netw_list
	return render(request, "external_networks/list.html", {'netw_list': netw_list})

@wrap_rpc
def add(api, request):
	if request.method == 'POST':
		form = NetworkForm(request.POST)
		if form.is_valid():
			formData = form.cleaned_data
			api.network_create(formData['kind'], {
										   _('label'):formData['label'],
										   _('preference'):formData['preference'],
										   _('description'):formData['description'],
										   _('big_icon'):formData['big_icon'],
										   _('show_as_common'): formData['show_as_common']})
			return HttpResponseRedirect(reverse("tomato.external_network.list"))
		else:
			return render(request, "form.html", {'form': form, 'heading':_("Add External Network")})
	else:
		form = NetworkForm
		return render(request, "form.html", {'form': form, 'heading':_("Add External Network")})

@wrap_rpc
def remove(api, request, res_id=None):
	if request.method == 'POST':
		form = RemoveConfirmForm(request.POST)
		if form.is_valid():
			api.network_remove(res_id)
			return HttpResponseRedirect(reverse("tomato.external_network.list"))
	form = RemoveConfirmForm.build(reverse("tomato.external_network.remove", kwargs={"res_id": res_id}))
	res = api.network_info(res_id)
	return render(request, "form.html", {"heading": "Remove External Network", "message_before": "Are you sure you want to remove the external network '"+res["kind"]+"'?", 'form': form})
	

@wrap_rpc
def edit(api, request, res_id = None):
	if request.method=='POST':
		form = EditNetworkForm(res_id, request.POST)
		if form.is_valid():
			formData = form.cleaned_data
			api.network_modify(formData["res_id"],{'label':formData['label'],
													'preference':formData['preference'],
													'description':formData['description'],
									   				'big_icon':formData['big_icon'],
									   				'show_as_common': formData['show_as_common']})
			return HttpResponseRedirect(reverse("tomato.external_network.list"))
		kind = request.POST["kind"]
		UserError.check(kind, UserError.INVALID_DATA, "Form transmission failed.")
		return render(request, "form.html", {'form': form, 'heading':"Edit External Network '"+kind+"'"})
	else:
		UserError.check(res_id, UserError.INVALID_DATA, "No resource specified.")
		res_info = api.network_info(res_id)
		res_info['res_id'] = res_id
		form = EditNetworkForm(res_id, res_info)
		return render(request, "form.html", {'form': form, 'heading':"Edit External Network '"+res_info['label']+"'"})
