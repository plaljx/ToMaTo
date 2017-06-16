# -*- coding: utf-8 -*-

# ToMaTo (Topology management software) 
# Copyright (C) 2012 Integrated Communication Systems Lab, University of Kaiserslautern
#
# This file is part of the ToMaTo project
#
# ToMaTo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from django.shortcuts import render
from django import forms
from django.conf import settings  # noqa
from django import shortcuts
from django import http
from django.utils import translation
from admin_common import BootstrapForm, Buttons
from tomato.crispy_forms.layout import Layout
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from lib import wrap_rpc

'django.core.context_processors.i18n',

TEMPLATE_CONTEXT_PROCESSORS = (
    'tools.context_processors.set',
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
)

def _one_year():
	now = datetime.utcnow()
	return datetime(now.year + 1, now.month, now.day, now.hour,
					now.minute, now.second, now.microsecond, now.tzinfo)
class SysConfigForm(BootstrapForm):
	language = forms.ChoiceField(label=_("Language"))
	def __init__(self, *args, **kwargs):
		super(SysConfigForm, self).__init__(*args, **kwargs)

		def get_language_display_name(code, desc):
			try:
				desc = translation.get_language_info(code)['name_local']
			except KeyError:
				# If a language is not defined in django.conf.locale.LANG_INFO
				# get_language_info raises KeyError
				pass
			return "%s (%s)" % (desc, code)
		languages = [(k, get_language_display_name(k, v))
					  for k, v in settings.LANGUAGES]
		self.fields['language'].choices = languages
		self.helper.form_action = reverse(config)
		self.helper.layout = Layout(
			'language', 
			Buttons.cancel_save
		)

@wrap_rpc
def config(api, request):
	if request.method == "GET":
		form = SysConfigForm(initial={"language":request.LANGUAGE_CODE})
		response = render(request, "form.html", {"form": form, "heading": _("System Configuration")})
		return response
	if request.method == "POST":
		response = shortcuts.redirect(request.build_absolute_uri())
		language = request.POST.get('language',None)               
		if language and translation.check_for_language(language):
			if hasattr(request, 'session'):
				request.session['django_language'] = language
				form = SysConfigForm(request.REQUEST)
			response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, expires=_one_year())               
		return response

