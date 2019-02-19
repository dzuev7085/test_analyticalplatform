from config.generic_util.validators import FileValidator

# Django
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
# Crispy forms
from crispy_forms.layout import Div, Hidden, Layout, Submit
from django import forms
from upload.models import DocumentType

# Upload
from .models import AnalyticalDocument


class AnalyticalDocumentForm(forms.ModelForm):

    class Meta:
        model = AnalyticalDocument
        fields = (
            'upload',
            'security_class',
            'document_type',
            'rating_decision'
        )

    def __init__(self, *args, **kwargs):
        """ Use for wrapping bootstrap
        This is crispy stuff.
        """

        # This must be stored in this specific order of pop and then super
        try:
            rating_decision_obj = kwargs.pop('rating_decision_obj')
        except:  # noqa E722
            rating_decision_obj = False

        super(AnalyticalDocumentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_id = 'id-method1Form'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-4'
        self.helper.form_method = 'post'

        self.fields['upload'].label = "Select file to be uploaded"
        self.fields['security_class'].label = "Document security class"
        self.fields['document_type'].label = "Type of document"

        self.fields['document_type'].queryset = DocumentType.objects.exclude(
            id__in=[10, 11, 12, 13, 14, 15]
        ).order_by('name')

        self.helper.layout = Layout(
            'upload',
            'security_class',
            'document_type',
        )

        self.helper.add_input(Submit('save-document', 'Upload'))

        if rating_decision_obj:
            self.helper.add_input(Hidden('rating_decision',
                                         rating_decision_obj.id))


class EditAnalyticalDocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditAnalyticalDocumentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('document_type'), css_class='col-md-8'),
                css_class='row',
            ),
            Div(
                Div(Field('security_class'), css_class='col-md-8'),
                css_class='row',
            ),
        )

    class Meta:
        model = AnalyticalDocument
        fields = (
            'security_class',
            'document_type',
        )


class EditAnalyticalDocumentManagementMeetingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditAnalyticalDocumentManagementMeetingForm, self).__init__(
            *args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('document_type'), css_class='col-md-8'),
                css_class='row',
            ),
            Div(
                Div(Field('security_class'), css_class='col-md-8'),
                css_class='row',
            ),
            Div(
                Div(Field('date_value'), css_class='col-md-8'),
                css_class='row',
            ),
        )

    class Meta:
        model = AnalyticalDocument
        fields = (
            'security_class',
            'document_type',
            'date_value'
        )
        labels = {
            'date_value': 'Meeting date'
        }


class RatingDecisionAddDocument(forms.ModelForm):
    """Add a document to a rating decision."""

    upload = forms.FileField(
        validators=[FileValidator(content_types='application/pdf')]
    )

    class Meta:
        """Meta class."""
        model = AnalyticalDocument

        fields = [
            'issuer',
            'upload',
            'document_type',
            'rating_decision'
        ]
        labels = {
            'upload': '',
        }
        help_texts = {
            'upload': 'The uploaded file must be in pdf format.',
        }

    security_class_id = forms.IntegerField()

    def __init__(self,
                 document_type_pk=None,
                 rating_decision_pk=None,
                 issuer_pk=None,
                 security_class=None,
                 *args, **kwargs):
        """Initiate the class."""

        super(RatingDecisionAddDocument, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('upload'), css_class='col-md-12'),
                css_class='row',
            ),
            Field(
                'security_class_id',
                type='hidden',
                value=security_class
            ),
            Field(
                'document_type',
                type='hidden',
                value=document_type_pk
            ),
            Field(
                'issuer',
                type='hidden',
                value=issuer_pk
            ),
            Field(
                'rating_decision',
                type='hidden',
                value=rating_decision_pk
            )
        )
