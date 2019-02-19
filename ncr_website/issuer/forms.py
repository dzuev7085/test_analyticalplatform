from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout
from django import forms
from django.contrib.auth.models import User
from issuer.models import IssuerType

from gui.templatetags.template_tags import has_group

from pygleif import GLEIF
from bootstrap_datepicker_plus import DatePickerInput

from config.generic_util.misc import TinyMCEWidget, UserFullnameChoiceField

from .models import Analyst, InsiderList, Issuer, OnboardingProcess
from issuer.models.address import Address
from issuer.models.classification import Classification


class AddIssuerForm(forms.ModelForm):

    def clean(self):
        """Custom method to clean and validate data."""

        cleaned_data = super(AddIssuerForm, self).clean()

        # Add a way to insert issuers manually
        if not cleaned_data['lei'][0:4] == 'LEI_':
            try:
                GLEIF(cleaned_data['lei']).entity.legal_name

            except:  # noqa E722
                raise forms.ValidationError(
                    "There is no issuer with that lei-code."
                )

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(AddIssuerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('lei'), css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div(Field('issuer_type'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_id = 'id-issuer-add-form'

    class Meta:
        model = Issuer
        fields = [
            'lei',
            'issuer_type'
        ]
        labels = {
            'lei': 'Enter the <a href="https://www.gleif.org/en" '
                   'target="_new">lei code</a> of the issuer'
        }


class OnboardingForm(forms.ModelForm):
    """Form to edit onboarding parameters."""

    class Meta:
        """Meta class."""

        model = Issuer
        fields = [
            'relationship_manager',
            'issuer_type',
        ]

    issuer_pk = forms.IntegerField()

    relationship_manager = UserFullnameChoiceField(
        queryset=User.objects.filter(
            groups__name__in=['Commercial']).order_by(
            'first_name', 'last_name'),
        empty_label=None,
    )

    issuer_type = forms.ModelChoiceField(
        queryset=IssuerType.objects.all().order_by('id'),
        empty_label=None,
    )

    target_delivery_date = forms.DateField(
        required=False,
        widget=DatePickerInput(
            options={"format": "YYYY-MM-DD",
                     "useCurrent": False,
                     "daysOfWeekDisabled":
                         [0, 6],
                     "calendarWeeks":
                         True, },
        ),
    )

    engagement_letter_signed = forms.BooleanField(
        label='Engagement letter signed',
        help_text='Clicking this box and pressing \'OK\' '
                  'will inform the CRO.',
        required=False,
    )

    # What type of ratings has the issuer requested?
    CHOICES = [('lt_rating', 'Long-term'),
               ('st_rating', 'Short-term'),
               ('instrument_rating', 'Instrument')]

    requested_rating = forms.MultipleChoiceField(
            choices=CHOICES,
            label="Requested ratings:",
            help_text='Control-click all that apply',
            required=True,)

    # Set primary analyst
    primary_analyst = UserFullnameChoiceField(queryset=User.objects.filter(
        groups__name__in=['Analyst']).distinct().order_by(
                              'first_name', 'last_name'))

    # Set secondary analyst
    secondary_analyst = UserFullnameChoiceField(queryset=User.objects.filter(
        groups__name__in=['Analyst']).distinct().order_by(
                              'first_name', 'last_name'))

    def __init__(self, issuer_pk=None, user=None, *args, **kwargs):
        """Initiate the class."""

        super(OnboardingForm, self).__init__(*args, **kwargs)

        # Load data from models
        issuer_obj = Issuer.objects.get(pk=issuer_pk)
        onboarding_obj = OnboardingProcess.objects.get(issuer=issuer_obj)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()
        self.helper.layout.append(
            Field(
                'issuer_pk',
                type='hidden',
                value=issuer_pk,
            ),
        )

        if has_group(user, 'Commercial'):

            # These fields are not required here
            self.fields['primary_analyst'].required = False
            self.fields['secondary_analyst'].required = False

            _relationship_manager = Field('relationship_manager')
            _issuer_type = Field('issuer_type')
            _requested_rating = Field('requested_rating')
            _target_delivery_date = Field('target_delivery_date')
            _engagement_letter_signed = Field('engagement_letter_signed')

            # Set default values of the choice field form
            requested_ratings_list = []
            if onboarding_obj.issuer_long_term:
                requested_ratings_list.append('lt_rating')

            if onboarding_obj.issuer_short_term:
                requested_ratings_list.append('st_rating')

            if onboarding_obj.instrument_rating:
                requested_ratings_list.append('instrument_rating')

            if onboarding_obj.target_delivery_date:
                self.fields['target_delivery_date'].initial = \
                    onboarding_obj.target_delivery_date

            self.fields["requested_rating"].initial = (requested_ratings_list)

        else:

            # Make sure the view doesn't overwrite with null
            self.helper.layout.append(
                Field(
                    'relationship_manager',
                    type='hidden',
                    value=issuer_obj.relationship_manager,
                ),
            )

            self.helper.layout.append(
                Field(
                    'issuer_type',
                    type='hidden',
                    value=issuer_obj.issuer_type,
                ),
            )

            # We don't need to pass these values when saving as a CRO
            self.fields['engagement_letter_signed'].required = False
            self.fields['requested_rating'].required = False

            _relationship_manager = Div(
                Div(HTML('Relationship manager:')),
                Div(HTML('{}'.format(
                    issuer_obj.relationship_manager.get_full_name()))),
                Div(HTML('&nbsp;'))
            )

            if issuer_obj.issuer_type.id == 1:
                issuer_type = 'Corporates'
            elif issuer_obj.issuer_type.id == 2:
                issuer_type = 'Financial institutions'
            elif issuer_obj.issuer_type.id == 3:
                issuer_type = 'Corporates, real estate'

            _issuer_type = Div(
                Div(HTML('Methodology:')),
                Div(HTML('{}'.format(issuer_type))),
                Div(HTML('&nbsp;'))
            )

            requested_ratings = ''

            if onboarding_obj.issuer_long_term:
                requested_ratings += 'Issuer long-term'

            if onboarding_obj.issuer_short_term:
                requested_ratings += ', Issuer short-term'

            if onboarding_obj.instrument_rating:
                requested_ratings += ', Instrument'

            _requested_rating = Div(
                Div(HTML('Requested rating:')),
                Div(HTML('{}'.format(requested_ratings))),
                Div(HTML('&nbsp;'))
            )

            if onboarding_obj.target_delivery_date is not None:
                _target_delivery_date = Div(
                    Div(HTML('Target delivery date:')),
                    Div(HTML('{}'.format(
                        onboarding_obj.target_delivery_date.strftime(
                            '%Y-%m-%d')))),
                    Div(HTML('&nbsp;'))
                )

            else:
                _target_delivery_date = HTML('A target delivery date has '
                                             'not been specified.')

            _engagement_letter_signed = HTML('The engagement letter has '
                                             'been signed.')

            self.helper.layout.append(
                Div(
                    Div(
                        Field('primary_analyst'),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )
            self.helper.layout.append(
                Div(
                    Div(
                        Field('secondary_analyst'),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        self.helper.layout.append(
            Div(
                Div(
                    _relationship_manager,
                    css_class='col-md-12',
                ),
                css_class='row',
            ),
        )
        self.helper.layout.append(
            Div(
                Div(
                    _issuer_type,
                    css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.layout.append(
            Div(
                Div(
                    _requested_rating,
                    css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.layout.append(
            Div(
                Div(
                    _target_delivery_date,
                    css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.layout.append(
            Div(
                Div(
                    _engagement_letter_signed,
                    css_class='col-md-12'),
                css_class='row',
            ),
        )


class EngagementLetterSignedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EngagementLetterSignedForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('engagement_letter_signed'), css_class='col-md-12'),
                css_class='row',
            ),

        )

    class Meta:
        """Meta class."""

        model = OnboardingProcess
        fields = [
            'engagement_letter_signed',
        ]
        labels = {
            'engagement_letter_signed': 'Enagement letter signed'
        }


class ChoseModelAppointAnalystForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(ChoseModelAppointAnalystForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('issuer_type'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = Issuer
        fields = [
            'issuer_type',
        ]
        labels = {
            'issuer_type': 'Choose methodology'
        }


class EditAnalystForm(forms.ModelForm):

    primary_analyst = UserFullnameChoiceField(queryset=User.objects.filter(
        groups__name__in=['Analyst',
                          'Senior level analyst']).distinct().order_by(
                              'first_name', 'last_name'))

    secondary_analyst = UserFullnameChoiceField(queryset=User.objects.filter(
        groups__name__in=['Analyst',
                          'Senior level analyst']).distinct().order_by(
                              'first_name', 'last_name'))

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditAnalystForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('primary_analyst'), css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div(Field('secondary_analyst'), css_class='col-md-12'),
                css_class='row',
            ),
            HTML('By clicking OK you confirm that there are no '
                 'conflicts of interest between the appointed '
                 'analyst and the issuer, as set out by the policies '
                 'of Nordic Credit Rating.')
        )

    class Meta:
        model = Analyst
        fields = [
            'primary_analyst',
            'secondary_analyst'
        ]


class EditClientServicesForm(forms.ModelForm):

    relationship_manager = UserFullnameChoiceField(
        queryset=User.objects.filter(groups__name__in=['Commercial']))

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditClientServicesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('relationship_manager'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = Issuer
        fields = [
            'relationship_manager',
        ]
        labels = {
            'relationship_manager': 'Client services'
        }


class EditGICSSubIndustry(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditGICSSubIndustry, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('gics_sub_industry'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = Issuer
        fields = [
            'gics_sub_industry',
        ]
        labels = {
            'gics_sub_industry': 'GICS sub-industry'
        }


class EditDescription(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditDescription, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('description'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    description = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False,
                   'cols': 20,
                   'rows': 20}
        )
    )

    class Meta:
        model = Issuer
        fields = [
            'description',
        ]


class EditShortName(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditShortName, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('short_name'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    class Meta:
        """Meta class."""

        model = Issuer
        fields = [
            'short_name',
        ]


class EditLegalName(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditLegalName, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('legal_name'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    class Meta:
        """Meta class."""

        model = Issuer
        fields = [
            'legal_name',
        ]


class EditIssuerForm(forms.ModelForm):
    """Edit any field in the issuer model."""

    # Todo: special case for relationship manager

    issuer_pk = forms.CharField()
#    relationship_manager = UserFullnameChoiceField(
#        queryset=User.objects.filter(groups__name__in=['Commercial']))

    def __init__(self, issuer_pk=None, *args, **kwargs):
        """Initiate the class."""

        field = kwargs.pop('field')

        super(EditIssuerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(form=self)

        self.helper.layout = Layout(
            Div(
                Div(Field(field), css_class='col-md-8'),
                css_class='row',
            ),
            Field(
                'issuer_pk',
                type='hidden',
                value=issuer_pk
            ),
        )

    class Meta:
        model = Issuer
        fields = [
            'issuer_type',
            'description',
            'short_name',
        ]


class IssuerInsiderForm(forms.ModelForm):

    class Meta:
        model = InsiderList
        fields = (
            'company',
            'contact_type',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'issuer'
        )

    def __init__(self, issuer_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(IssuerInsiderForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(

            Div(
                Div(
                    Field('company'),
                    css_class='col-md-12'),
                css_class='row',
            ),

            Div(
                Div(
                    Field('contact_type'),
                    css_class='col-md-12'),
                css_class='row',
            ),

            Div(
                Div(
                    Field('first_name'),
                    css_class='col-md-6'),
                Div(
                    Field('last_name'),
                    css_class='col-md-6'),
                css_class='row',
            ),

            Div(
                Div(
                    Field('email'),
                    css_class='col-md-6'),
                Div(
                    Field('phone_number'),
                    css_class='col-md-6'),
                css_class='row',

            ),

            Div(
                Div(
                    Field('role'),
                    css_class='col-md-12'),
                css_class='row',
            ),

            Field(
                'issuer',
                type='hidden',
                value=issuer_pk
            )
        )


class EditCountry(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditCountry, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('country'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    class Meta:
        """Meta class."""

        model = Address
        fields = [
            'country',
        ]


class EditNCRPeer(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditNCRPeer, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('peer_free_text'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    class Meta:
        """Meta class."""

        model = Classification
        fields = [
            'peer_free_text',
        ]


class EditParent(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditParent, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('parent_company'), css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_show_labels = False

    class Meta:
        """Meta class."""

        model = Issuer
        fields = [
            'parent_company',
        ]
