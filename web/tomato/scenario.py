# by Chang Rui
# TODO: handle with create_time in scenario edit
# TODO: change topology_info from text field to file field ?
# TODO: handle with add form is_valid()

import datetime, re
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms

from admin_common import RemoveConfirmForm, BootstrapForm, Buttons, ConfirmForm
from lib import wrap_rpc, AuthError
from tomato.crispy_forms.layout import Layout

from lib.error import UserError #@UnresolvedImport

accessibility_choices = (
    ('private', 'Private'),
    ('public', 'Public')
)


@wrap_rpc
def list_(api, request, show):
    if api.user:
        user = api.user.name
    else:
        raise AuthError()

    scenario_list = api.scenario_list(user, show)

    return render(request, "scenario/list.html",
                  {
                      'scenario_list' : scenario_list,
                      'show' : show,
                  })


@wrap_rpc
def info(api, request, id_):
    # template = api.template_info(res_id)
    # return render(request, "templates/info.html", {"template": template, "techs_dict": techs_dict})
    scenario = api.scenario_info(id_)
    return render(request, "scenario/info.html", {"scenario": scenario})


@wrap_rpc
def add(api, request):
    if request.method == 'POST':
        form = AddScenarioForm(api.user.name, request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            # create_time = form_data['create_time']
            attrs = {
                'name': form_data['name'],
                'description': form_data['description'],
                'accessibility': form_data['accessibility'],
                'author': form_data['author'],
                # 'creation_date': dateToTimestamp(creation_date) if creation_date else None,
                'topology_info_json': form_data['topology_info_json']
            }
            res = api.scenario_create(attrs)
            return HttpResponseRedirect(reverse("scenario_info", kwargs={"id_": res["id"]}))
        else:
            return render(request, "form.html", {'form': form, "heading": "Add Scenario"})
    else:
        form = AddScenarioForm(api.user.name)
        return render(request, "form.html", {'form': form, "heading": "Add Scenario"})


@wrap_rpc
def remove(api, request, id_=None):
    if request.method == 'POST':
        form = RemoveConfirmForm(request.POST)
        if form.is_valid():
            api.scenario_remove(id_)
            return HttpResponseRedirect(reverse("scenario_list"))
    else:
        form = RemoveConfirmForm.build(reverse("tomato.scenario.remove", kwargs={"id_": id_}))
        response = api.scenario_info(id_)
        return render(request, "form.html",
                      {"heading": "Remove Scenario",
                       "message_before": "Are you sure you want to remove the scenario '"+response["name"]+"'?",
                       "form": form})


@wrap_rpc
def deploy(api, request, id_=None):
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            api.scenario_deploy(id_)
            return HttpResponseRedirect(reverse("topology_list"))
    else:
        form = ConfirmForm.build(reverse("tomato.scenario.deploy", kwargs={"id_": id_}))
        response = api.scenario_info(id_)
        return render(request, "form.html",
                      {"heading": "Deploy Scenario",
                       "message_before": "Are you sure you want to deploy the scenario '" + response["name"] + "'?",
                       "form": form})


@wrap_rpc
def edit(api, request, id_):
    scenario_info = api.scenario_info(id_)
    if request.method == 'POST':
        form = EditScenarioForm(id_, request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            # create_time = form_data["create_time"]
            attrs = {'name': form_data['name'],
                     'description': form_data['description'],
                     'accessibility': form_data['accessibility'],
                     'author': form_data['author'],
                     # TODO: datetime is not serializable
                     # 'create_time': form_data['create_time'],
                     'topology_info_json': form_data['topology_info_json']
                     }
            api.scenario_modify(id_, attrs)
            return HttpResponseRedirect(reverse("tomato.scenario.info", kwargs={"id_": id_}))

        label = request.POST["label"]
        UserError.check(label, UserError.INVALID_DATA, "Form transmission failed.")
        return render(request, "form.html", {'label': label, 'form': form,
                                             "heading": "Edit Scenario Data for '" + label + "' (" + scenario_info[
                                                 'name'] + ")"})
    else:
        UserError.check(id_, UserError.INVALID_DATA, "No resource specified.")
        scenario_info['id_'] = id_
        # scenario_info['create_date'] = datetime.date.fromtimestamp(float(id_['creation_date'] or "0.0"))
        form = EditScenarioForm(id_, scenario_info)
        return render(request, "form.html",
                      {'name': scenario_info['name'],
                       'form': form,
                       "heading": "Edit Scenario Data for '" + str(scenario_info['name'])
                       })

@wrap_rpc
def download_topo(api, request, id_):
    if not api.user:
        raise AuthError()
    scenario = api.scenario_info(id_)
    topo_json = scenario["topology_info_json"]
    filename = re.sub('[^\w\-_\. ]', '_', scenario["name"].lower().replace(" ", "_")) + "__" + id_ + ".tomato4.json"
    response = HttpResponse(topo_json, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response


@wrap_rpc
def upload_topo(api, request, id_):
    if not api.user:
        raise AuthError()

    if request.method == 'POST':
        form = UploadScenarioInfoForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['topologyfile']
            file_content = f.read()
            api.scenario_modify(id_, {'topology_info_json': file_content})
            return redirect("scenario_info", id_=id_)
        else:
            return render(request, "form.html", {'form': form,
                                                 "heading": "Edit Scenario %s" % id_,
                                                 'message_before': "Here you can upload a topology file to update the topology info of the scenario."})
    else:
        form = UploadScenarioInfoForm()
        return render(request, "form.html", {'form': form,
                                             "heading": "Edit Scenario %s" % id_,
                                             'message_before': "Here you can upload a topology file to update the topology info of the scenario."})


class UploadScenarioInfoForm(BootstrapForm):
    topologyfile = forms.FileField(label="Scenario Topology Info File")

    def __init__(self, *args, **kwargs):
        super(UploadScenarioInfoForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'topologyfile',
            Buttons.default(label="Import")
        )


class ScenarioForm(BootstrapForm):
    id_ = forms.CharField()
    name = forms.CharField(required=True, max_length=20)
    description = forms.CharField(required=False, widget=forms.Textarea)
    accessibility = forms.ChoiceField(widget=forms.RadioSelect, choices=accessibility_choices, initial=accessibility_choices[0])
    author = forms.CharField(required=True)
    create_time = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'class': 'datetimepicker'}))
    topology_info_json = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ScenarioForm, self).__init__(*args, **kwargs)


class AddScenarioForm(ScenarioForm):
    def __init__(self, username, *args, **kwargs):
        super(AddScenarioForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse(add)
        self.helper.layout = Layout(
            'name',
            'description',
            'accessibility',
            'author',
            # 'create_time',
            'topology_info_json',
            Buttons.cancel_add,
        )
        self.fields['create_time'].initial = datetime.datetime.now()
        self.fields['create_time'].widget.attrs['readonly'] = 'True'
        self.fields['author'].initial = username
        self.fields['author'].widget.attrs['readonly'] = 'True'

    def is_valid(self):
        # TODO: handle this !
        valid = super(AddScenarioForm, self).is_valid()
        return True


class EditScenarioForm(ScenarioForm):
    # id_ = forms.CharField(max_length=50, widget=forms.HiddenInput)
    def __init__(self, id_, *args, **kwargs):
        super(EditScenarioForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse(edit, kwargs={"id_": id_})
        self.helper.layout = Layout(
            'id_',
            'name',
            'description',
            'accessibility',
            'author',
            'create_time',
            'topology_info_json',
            Buttons.cancel_save
        )
        self.fields['create_time'].initial = datetime.datetime.now()
        self.fields['id_'].widget.attrs['readonly'] = True
        self.fields['author'].widget.attrs['readonly'] = True
        self.fields['create_time'].widget.attrs['readonly'] = True  # TODO: datetime is not serializable


