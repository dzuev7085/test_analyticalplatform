from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Fieldset, HTML
from django import forms

from .models import Issue


ISSUE_HELP_FIELDS = {
    'program': "Choose 'Issue outside of program' if the issue is not made "
               "under a specific program.",
    'disbursement': "Date format YYYY-MM-DD",
    'maturity': "Date format YYYY-MM-DD. Use 9999-12-31 for perpetual debt.",
    'amount': "Enter whole amount, eg 100000000 for 100 m.",
    'ticker': "Eg: SOAG20 PRO",
    'name': "Eg: Spb 1 Østfold Akershus 14/19 FRN",
}

ISSUE_REQUIRED_FIELDS = {
    'disbursement': True,
    'currency': True,
    'amount': True,
}


class StamdataDataForm(forms.ModelForm):
    """Parse raw HTML from Stamdata"""

    class Meta:
        model = Issue
        fields = [
            'issuer',
        ]

    textarea = forms.CharField(
        widget=forms.Textarea(),
        help_text='Go to the issuer page of Stamdata (eg: '
                  '<a href="https://www.stamdata.com/Issuer/199936836" '
                  'target="_blank">NP3</a>), right click on the page, '
                  'select "Show source", copy the contents and paste into '
                  'this field. Press "OK". This will load all issues of the '
                  'issuer.'
    )

    def __init__(self, issuer_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(StamdataDataForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Field('textarea', rows="3", css_class='input-xlarge'),
            ),
            Div(
                Field(
                    'issuer',
                    type='hidden',
                    value=issuer_pk
                )
            )
        )


class EngagementLetterSignedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EngagementLetterSignedForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('enagement_letter_signed'), css_class='col-md-12'),
                css_class='row',
            ),

        )


class CommonIssueLayout(Layout):
    """Common layout for create and edit issue."""

    def __init__(self, *args, **kwargs):
        super(CommonIssueLayout, self).__init__(
            Fieldset(
                'Required information',

                Div(
                    Div('isin', css_class='col-md-6', ),
                    css_class='row',
                ),

                Div(
                    Div('program', css_class='col-md-6', ),
                    Div('seniority', css_class='col-md-6', ),
                    css_class='row',
                ),

                Div(
                    Div('disbursement', css_class='col-md-6', ),
                    Div('maturity', css_class='col-md-6', ),
                    css_class='row',
                ),

                Div(
                    Div('currency', css_class='col-md-6', ),
                    Div('amount', css_class='col-md-6', ),
                    css_class='row',
                ),

            ),
            HTML('<hr>'),
            Fieldset(
                'Optional information',

                Div(
                    Div('ticker', css_class='col-md-6', ),
                    Div('name', css_class='col-md-6', ),
                    css_class='row',
                ),

            )
        )


class EditIssueForm(forms.ModelForm):
    """Edit parameters linked to an issue."""

    class Meta:
        """Meta class."""
        model = Issue
        fields = [
            'isin',
            'seniority',
            'disbursement',
            'maturity',
            'currency',
            'amount',
            'ticker',
            'name',
            'program',
        ]

    def __init__(self, issue_pk, *args, **kwargs):
        """Initiate the class."""

        super(EditIssueForm, self).__init__(*args, **kwargs)

        # These fields are not required in the model but should be
        # Add as per below instead of making required to avoid fixing
        # null values in the database.
        for field in ISSUE_REQUIRED_FIELDS:
            self.fields[field].required = ISSUE_REQUIRED_FIELDS[field]

        # Provide some help text for the user
        for field in ISSUE_HELP_FIELDS:
            self.fields[field].help_text = ISSUE_HELP_FIELDS[field]

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            CommonIssueLayout(),
        )


class AddIssueForm(forms.ModelForm):
    """Edit parameters linked to an issue."""

    class Meta:
        """Meta class."""
        model = Issue
        fields = [
            'issuer',
            'isin',
            'seniority',
            'disbursement',
            'maturity',
            'currency',
            'amount',
            'ticker',
            'name',
            'program',
        ]

    def __init__(self, issuer_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(AddIssueForm, self).__init__(*args, **kwargs)

        # These fields are not required in the model but should be
        # Add as per below instead of making required to avoid fixing
        # null values in the database.
        for field in ISSUE_REQUIRED_FIELDS:
            self.fields[field].required = ISSUE_REQUIRED_FIELDS[field]

        # Provide some help text for the user
        for field in ISSUE_HELP_FIELDS:
            self.fields[field].help_text = ISSUE_HELP_FIELDS[field]

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            CommonIssueLayout(),
        )

        self.helper.layout.append(
            Field(
                'issuer',
                type='hidden',
                value=issuer_pk
            )
        )
