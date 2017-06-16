from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render
from django import forms
import base64, re
from lib import wrap_rpc, serverInfo
from admin_common import RemoveConfirmForm, help_url, BootstrapForm, Buttons, append_empty_choice
import datetime
from lib.reference_library import tech_to_label
from lib.constants import TypeName

from tomato.crispy_forms.layout import Layout
from django.core.urlresolvers import reverse

from lib.error import UserError #@UnresolvedImport
from django.utils.translation import ugettext as _
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

'''techs = [{"name": t, "label": tech_to_label(t)} for t in [TypeName.KVM, TypeName.KVMQM, TypeName.OPENVZ, TypeName.REPY]]

techs_dict = dict([(t["name"], t["label"]) for t in techs])
def techs_choices():
    tlist = [(t["name"], t["label"]) for t in techs]
    return append_empty_choice(tlist)'''
    

'''kblang_options = [
    ("en-us", "English (US)"),
    ("en-gb", "English (GB)"),
    ("de", "German"),
    ("fr", "French"),
    ("ja", "Japanese")
]'''

techs_tmpl = [{"name": t, "label": tech_to_label(t)} for t in [TypeName.KVM, TypeName.KVMQM, TypeName.OPENVZ, TypeName.REPY]]

techs_dict = dict([(t["name"], t["label"]) for t in techs_tmpl])

techs=['tar.gz','rar','zip']
def techs_choices():
    te=[('TAR','tar.gz'),('RAR','rar'),('ZIP','zip')]
    return append_empty_choice(te)


def dateToTimestamp(date):
    td = date - datetime.date(1970, 1, 1)
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


class SecurityForm(BootstrapForm):
    label = forms.CharField(max_length=255, help_text="The displayed label for this security")
    subtype = forms.CharField(max_length=255, required=False)
    description = forms.CharField(widget = forms.Textarea, required=False)
    creation_date = forms.DateField(required=False,widget=forms.TextInput(attrs={'class': 'datepicker'}))
    icon = forms.URLField(label="Icon", help_text="URL of a 32x32 icon to use for elements of this security, leave empty to use the default icon", required=False)
    #kblang = forms.CharField(max_length=50,label="Keyboard Layout",widget = forms.widgets.Select(choices=kblang_options), help_text="Only for KVM security", required=False)   
    urls = forms.CharField(widget = forms.Textarea, required=True, help_text="URLs that point to the security's image file. Enter one or more URLs; one URL per line.")
    available_template = forms.MultipleChoiceField(label=_('available_template'),widget=CheckboxSelectMultiple,choices=[])
    def __init__(self, *args, **kwargs):
        super(SecurityForm, self).__init__(*args, **kwargs)
        self.fields['creation_date'].initial=datetime.date.today()
        #self.fields['kblang'].initial="en_US"
    
class AddSecurityForm(SecurityForm):
    name = forms.CharField(max_length=50,label="Internal Name", help_text="Must be unique for all profiles. Cannot be changed. Not displayed.")
    tech = forms.CharField(max_length=255,widget = forms.widgets.Select(choices=techs_choices()))
    def __init__(self, *args, **kwargs):
        super(AddSecurityForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse(add)
        self.helper.layout = Layout(
            'name',
            'label',
            'subtype',
            'description',
            'tech',
            'icon',
            'creation_date',
            'available_template',
            'urls',
            Buttons.cancel_add
        )
    def change(self,tem_list):
        self.fields['available_template'].choices = tem_list
    def is_valid(self):
        valid = super(AddSecurityForm, self).is_valid()
        if not valid:
            return valid
        if self.cleaned_data['tech'] == 'kvmqm':
            valid = (self.cleaned_data['kblang'] is not None)
        return valid



@wrap_rpc
def list(api,request,tech):
    #templ_list = api.template_list()
    secur_list = api.security_list()
    '''templ_list = api.security_list()
    print templ_list
    html = "add security"
    return HttpResponse(html)'''    
    return render(request, "security/list.html", {'secur_list': templ_list, "tech": tech, "techs_dict": techs_dict})




@wrap_rpc
def info(api, request, res_id):
    security = api.security_info(res_id)
    return render(request, "security/info.html", {"security": security, "techs_dict": techs_dict})




#def add(request):
    #html = "add"
    #return HttpResponse(html)
@wrap_rpc
def add(api, request, tech=None):
    template_list=api.template_list()
    print template_list
    #global tem_list
    tem_list=[]
    for tem in template_list:
        name=tem["name"]
        tem_list.append((name,name))
    if request.method == 'POST':
        form = AddSecurityForm(request.POST, request.FILES)
        form.change(tem_list)
        if form.is_valid():
            formData = form.cleaned_data
            creation_date = formData['creation_date']
            available_template_str = ','.join(formData['available_template'])
            attrs = {   'label':formData['label'],
                        'subtype':formData['subtype'],
                        'description':formData['description'],
                        'creation_date':dateToTimestamp(creation_date) if creation_date else None,
                        'icon':formData['icon'],
                        'available_template':formData['available_template'],
                        'urls': filter(lambda x: x, formData['urls'].splitlines())}
            res = api.security_create(formData['tech'], formData['name'], attrs)
            return HttpResponseRedirect(reverse("tomato.security.info", kwargs={"res_id": res["id"]}))
        else:
            return render(request, "form.html", {'form': form, "heading":"Add Security"})
    else:
        form = AddSecurityForm()
        form.change(tem_list)
        if tech:
            form.fields['tech'].initial = tech
        return render(request, "form.html", {'form': form, "heading":"Add Security", 'hide_errors':True})   





def edit(request):
    html = "edit"
    return HttpResponse(html)




def remove(request):
    html = "remove"
    return HttpResponse(html)
