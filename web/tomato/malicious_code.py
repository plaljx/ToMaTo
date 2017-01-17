import datetime, re

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms

from admin_common import RemoveConfirmForm, BootstrapForm, Buttons, ConfirmForm

from lib import wrap_rpc, AuthError
from tomato.crispy_forms.layout import Layout

from lib.error import UserError #@UnresolvedImport


malicious_code_type_options = {
    ("virus", "Virus",),
    ("trojan", "Trojan",),
    ("worm", "Worm",),
}

system_options = {
    ("linux", "Linux"),
    ("windows", "Windows"),
}


@wrap_rpc
def list_(api, request):
    if not api.user:
        raise AuthError()
    mc_list = api.malicious_code_list()
    return render(request, "security_resources/malicious_code_list.html" , {'mc_list': mc_list})


@wrap_rpc
def info(api, request, res_id):
    mc_info = api.malicious_code_info(res_id)
    return render(request, "security_resources/malicious_code_info.html", {'mc_info': mc_info})


@wrap_rpc
def add(api, request):
    if request.method == 'POST':
        form = AddMaliciousCodeForm(request.POST, request.FILES)
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
            response = api.malicious_code_create(attrs)
            return HttpResponseRedirect(reverse("malicious_code_info", kwargs={"res_id": response["id"]}))
        else:
            return render(request, "form.html", {'form': form, "heading": "Add Malicious Code"})
    else:
        form = AddMaliciousCodeForm()
        return render(request, "form.html", {'form': form, "heading": "Add Malicious Code"})


@wrap_rpc
def edit(api, request, res_id):
    res_inf = api.malicious_code_info(res_id)
    if request.method == 'POST':
        form = EditMaliciousCodeForm(res_id, request.POST)
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
            api.malicious_code_modify(res_id, attrs)
            return HttpResponseRedirect(reverse("malicious_code_info", kwargs={"res_id": res_id}))
        label = request.POST["label"]
        UserError.check(label, UserError.INVALID_DATA, "Form transmission failed.")
        return render(request, "form.html", {'label': label, 'form': form,
                                             "heading": "Edit Malicious Code Data for '" + label +
                                                        "' (" + res_inf['name'] + ")"})
    else:
        UserError.check(res_id, UserError.INVALID_DATA, "No resource specified.")
        # res_inf['id'] = res_id
        res_inf['creation_date'] = datetime.date.fromtimestamp(float(res_inf['creation_date'] or "0.0"))
        form = EditMaliciousCodeForm(res_id, res_inf)
        return render(request, "form.html",
                      {'name': res_inf['name'],
                       'form': form,
                       "heading": "Edit Malicious Code Data for '" + str(res_inf['name'])
                       })


@wrap_rpc
def remove(api, request, res_id=None):
    if request.method == 'POST':
        form = RemoveConfirmForm(request.POST)
        if form.is_valid():
            api.malicious_code_remove(res_id)
            return HttpResponseRedirect(reverse("malicious_code_list"))
    else:
        form = RemoveConfirmForm.build(reverse("malicious_code_remove", kwargs={"res_id": res_id}))
        response = api.malicious_code_info(res_id)
        return render(request, "form.html",
                      {"heading": "Remove Malicious Code",
                       "message_before": "Are you sure you want to remove the malicious code '" + response["name"] + "'?",
                       "form": form})


class MaliciousCodeForm(BootstrapForm):
    res_id = forms.CharField()
    name = forms.CharField(required=True, max_length=31)
    type = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=malicious_code_type_options)
    system = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=system_options)
    url = forms.URLField(required=True, max_length=255)
    description = forms.CharField(widget = forms.Textarea, required=False)
    creation_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        super(MaliciousCodeForm, self).__init__(*args, **kwargs)
        self.fields['creation_date'].initial = datetime.date.today()

    def is_valid(self):
        # TODO: handle this.
        valid = super(MaliciousCodeForm, self).is_valid()
        return True


class AddMaliciousCodeForm(MaliciousCodeForm):
    def __init__(self, *args, **kwargs):
        super(AddMaliciousCodeForm, self).__init__(*args, **kwargs)
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


class EditMaliciousCodeForm(MaliciousCodeForm):
    def __init__(self, res_id, *args, **kwargs):
        super(EditMaliciousCodeForm, self).__init__(*args, **kwargs)
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
