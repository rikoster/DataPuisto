"""
Forms module according to Django boilerplate structure. The forms that
are used to obtain race data from the internet or a file.

Author: Riku Österman
Most recent version: 2020-11-10

"""
from django import forms
from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext_lazy as _
from NavigantAnalyzer.models import Race
from NavigantAnalyzer.downloaders import download_from_url, download_from_file

class UploadRaceForm(forms.Form):
    """ The form obtains an url, makes a call to download data, and
    checks that the downloaded data is a new race.
    """
    url = forms.URLField(
        label = "Anna URL NaviSportin/Rastilipun luomiin ihmisluettaviin tuloksiin",
        help_text = "DataPuisto ei käytä URLia sellaisenaan, vaan erottaa siitä ID:n",
        # ***** The widget definition now replaced by CSS min-width *****
        #widget=forms.TextInput(attrs={'size': '50'})
        )
    # A hidden field, intended for passing data
    ext_input = forms.CharField(required=False)

    def clean(self):
        if self._errors:
            for error in self._errors:
                raise ValidationError(error)

        data = self.cleaned_data
        ext_data = download_from_url(data['url'])
        if ext_data:
            if not Race.races.can_be_added(ext_data):
                ext_data = None
                raise ValidationError("Kilpailu on jo tietokannassa!")
        else:
            raise ValidationError("Dataa ei löytynyt")

        data['ext_input'] = ext_data
        return data


class UploadRaceFileForm(forms.Form):
    """ The form obtains a file and checks that the the data in the file
    is a new race.
    """
    file = forms.FileField(
        label = "Valitse tiedosto",
        help_text = "Max 2 megatavua."
        )
    # A hidden field, intended for passing data
    ext_input = forms.CharField(required=False)

    def clean(self):
        if self._errors:
            for error in self._errors:
                raise ValidationError(error)

        data = self.cleaned_data
        ext_data = download_from_file(data['file'])
        if ext_data:
            if not Race.races.can_be_added(ext_data):
                ext_data = None
                raise ValidationError("Kilpailu on jo tietokannassa!")
        else:
            raise ValidationError("Dataa ei löytynyt")

        data['ext_input'] = ext_data
        return data

# Copied straight from MSFT template - RÖ 2018-10-26
# May be unnecessary if BuiltIn plain-vanilla Authentication form is used

#class BootstrapAuthenticationForm(AuthenticationForm):
#    """Authentication form which uses boostrap CSS."""
#    username = forms.CharField(max_length=254,
#                               widget=forms.TextInput({
#                                   'class': 'form-control',
#                                   'placeholder': 'User name'}))
#    password = forms.CharField(label=_("Password"),
#                               widget=forms.PasswordInput({
#                                   'class': 'form-control',
#                                   'placeholder':'Password'}))
