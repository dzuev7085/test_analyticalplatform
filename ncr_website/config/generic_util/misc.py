from django import forms
from django.utils.encoding import smart_text

from tinymce.widgets import TinyMCE


class UserFullnameChoiceField(forms.ModelChoiceField):
    """Create a list of full names intead of the user names."""
    def label_from_instance(self, obj):
        return smart_text(obj.get_full_name())


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False
