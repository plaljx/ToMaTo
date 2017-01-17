import datetime, re

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms

from admin_common import RemoveConfirmForm, BootstrapForm, Buttons, ConfirmForm

from lib import wrap_rpc, AuthError
from tomato.crispy_forms.layout import Layout

from lib.error import UserError #@UnresolvedImport


security_software_type_options = {
    ("attack", "Attack",),
    ("defence", "Defence",),
    ("intelligence", "Intelligence",),
}

system_options = {
    ("linux", "Linux"),
    ("windows", "Windows"),
}


@wrap_rpc
def list_(api, request):
    if not api.user:
        raise AuthError()
    ss_list = api.security_software_list()
    return render(request, "security_resources/security_software_list.html" , {'ss_list': ss_list})


@wrap_rpc
def info(api, request, res_id):
    ss_info = api.security_software_info(res_id)
    return render(request, "security_resources/security_software_info.html", {'ss_info': ss_info})


@wrap_rpc
def add(api, request):
    if request.method == 'POST':
        form = AddSecuritySoftwareForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            creation_date = form_data['creation_date']
            attrs = {
                'name': form_data['name'],
                'type': form_data['type'],
                'system': form_data['system'],
                'url': form_data['url'],
                'description': form_data['description'],
                'creation_date': dateToTimestamp(creation_date) if creation_date else None,
            }
            response = api.security_software_create(attrs)
            return HttpResponseRedirect(reverse("security_software_info", kwargs={"res_id": response["id"]}))
        else:
            return render(request, "form.html", {'form': form, "heading": "Add Security Software"})
    else:
        form = AddSecuritySoftwareForm()
        return render(request, "form.html", {'form': form, "heading": "Add Security Software"})


@wrap_rpc
def edit(api, request, res_id):
    res_inf = api.security_software_info(res_id)
    if request.method == 'POST':
        form = EditSecuritySoftwareForm(res_id, request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            creation_date = form_data['creation_date']
            attrs = {
                # 'id': form_data["res_id"],
                'name': form_data['name'],
                'type': form_data['type'],
                'system': form_data['system'],
                'url': form_data['url'],
                'description': form_data['description'],
                'creation_date': dateToTimestamp(creation_date) if creation_date else None,
            }
            api.security_software_modify(res_id, attrs)
            return HttpResponseRedirect(reverse("security_software_info", kwargs={"res_id": res_id}))
        label = request.POST["label"]
        UserError.check(label, UserError.INVALID_DATA, "Form transmission failed.")
        return render(request, "form.html", {'label': label, 'form': form,
                                             "heading": "Edit Security Software Data for '" + label +
                                                        "' (" + res_inf['name'] + ")"})
    else:
        UserError.check(res_id, UserError.INVALID_DATA, "No resource specified.")
        # res_inf['id'] = res_id
        res_inf['creation_date'] = datetime.date.fromtimestamp(float(res_inf['creation_date'] or "0.0"))
        form = EditSecuritySoftwareForm(res_id, res_inf)
        return render(request, "form.html",
                      {'name': res_inf['name'],
                       'form': form,
                       "heading": "Edit Security Software Data for '" + str(res_inf['name'])
                       })

@wrap_rpc
def remove(api, request, res_id=None):
    if request.method == 'POST':
        form = RemoveConfirmForm(request.POST)
        if form.is_valid():
            api.security_software_remove(res_id)
            return HttpResponseRedirect(reverse("security_software_list"))
    else:
        form = RemoveConfirmForm.build(reverse("security_software_remove", kwargs={"res_id": res_id}))
        response = api.security_software_info(res_id)
        return render(request, "form.html",
                      {"heading": "Remove Security Software",
                       "message_before": "Are you sure you want to remove the security software '" + response["name"] + "'?",
                       "form": form})


class SecuritySoftwareForm(BootstrapForm):
    res_id = forms.CharField()
    name = forms.CharField(required=True, max_length=31)
    type = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=security_software_type_options)
    system = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=system_options)
    url = forms.URLField(required=True, max_length=255)
    description = forms.CharField(widget = forms.Textarea, required=False)
    creation_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        super(SecuritySoftwareForm, self).__init__(*args, **kwargs)
        self.fields['creation_date'].initial = datetime.date.today()

    def is_valid(self):
        # TODO: handle this.
        valid = super(SecuritySoftwareForm, self).is_valid()
        return True


class AddSecuritySoftwareForm(SecuritySoftwareForm):
    def __init__(self, *args, **kwargs):
        super(AddSecuritySoftwareForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse(add)
        self.helper.layout = Layout(
            'name',
            'type',
            'system',
            'url',
            'description',
            'creation_date',
            Buttons.cancel_add
        )


class EditSecuritySoftwareForm(SecuritySoftwareForm):
    def __init__(self, res_id, *args, **kwargs):
        super(EditSecuritySoftwareForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse(edit, kwargs={"res_id": res_id})
        self.helper.layout = Layout(
            'res_id',
            'name',
            'type',
            'system',
            'url',
            'description',
            'creation_date',
            Buttons.cancel_save
        )
        self.fields['res_id'].initial = res_id
        self.fields['res_id'].widget.attrs['readonly'] = 'True'


def dateToTimestamp(date):
    td = date - datetime.date(1970, 1, 1)
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
