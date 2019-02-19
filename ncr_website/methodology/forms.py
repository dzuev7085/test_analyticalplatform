# Django
# Crispy forms
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms

# This model
from .models import Methodology


class MethodologyForm(forms.ModelForm):

    class Meta:
        model = Methodology
        fields = (
            'category',
            'date_decision',
            'upload',
        )

    def __init__(self, category_id=None, *args, **kwargs):
        """Initiate the class."""

        super(MethodologyForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(

            Div(
                Div(
                    Field('date_decision'),
                    css_class='col-md-12'),
                css_class='row',
            ),

            Div(
                Div(
                    Field('upload'),
                    css_class='col-md-12'),
                css_class='row',
            ),

            Field(
                'category',
                type='hidden',
                value=category_id
            ),

        )
