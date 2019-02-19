from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, HTML
from django import forms
from credit_assessment.models.assessment import AssessmentJob
from credit_assessment.models.subscores import AssessmentSubscoreData
from rating_process.models.internal_score_data import NOTCH_CHOICES
from pycreditrating import (
    BASE_SCORE,
)
from issuer.models import Issuer
from credit_assessment.models.seniority_level_assessment import (
    SeniorityLevelAssessment
)


RA_WEIGHT_CHOICES = (
    (None, '0%'),
    (0.025, '2.5%'),
    (0.05, '5.0%'),
    (0.075, '7.5%'),
    (0.1, '10.0%'),
    (0.125, '12.5%'),
    (0.15, '15.0%'),
    (0.175, '17.5%'),
    (0.2, '20.0%'),
)


class EditRatingAssessment(forms.ModelForm):
    """Edit a financial statement item."""

    class Meta:
        """Meta class."""
        model = AssessmentJob
        fields = [
            'comment',
        ]

    ready_for_approval = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text="Click this box and press 'Save changes' to send the "
                  "proposed assessment for approval. If you "
                  "want to continue working on the assessment later, "
                  "just press 'Save changes' without clicking the "
                  "box.",
        required=False,
    )

    give_final_approval = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text="Click this box and press 'Save changes' to approve the "
                  "assessment proposed above.",
        required=False,
    )

    def __init__(self,
                 assessment_pk=None,
                 *args,
                 **kwargs):
        """Initiate the class."""

        super(EditRatingAssessment, self).__init__(*args, **kwargs)

        DIV_CLASS = 'col-md-12'

        rating_assessment = AssessmentJob.objects.get(
            pk=assessment_pk)

        subscore_obj = AssessmentSubscoreData.objects.filter(
            assessment=rating_assessment,
        )

        current_assessment_sort_order = rating_assessment.assessment_lt

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        #################################################
        # Corporate: Business risk
        #################################################
        bus_risk = subscore_obj.filter(subfactor__factor__in=[1])

        if len(bus_risk):
            self.helper.layout.append(
                Div(
                    HTML('Business risk assessment'),
                    css_class='Subheader',
                )
            )
        for d in subscore_obj.filter(
                subfactor__factor__in=[1]):

            self.fields['s_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=BASE_SCORE,
                initial=d.decided_score,
            )

            self.helper.layout.append(
                Div(
                    Div(Field('s_{}'.format(d.pk)),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        #################################################
        # Corporate: Financial risk
        #################################################
        fin_risk = subscore_obj.filter(subfactor__factor__in=[2])

        if len(fin_risk) > 0:
            self.helper.layout.append(
                Div(
                    HTML('Financial risk assessment'),
                    css_class='Subheader',
                )
            )
        for d in fin_risk:

            self.fields['s_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=BASE_SCORE,
                initial=d.decided_score,
            )

            self.helper.layout.append(
                Div(
                    Div(Field('s_{}'.format(d.pk)),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        #################################################
        # Financial: Operating environment
        #################################################
        fin_risk = subscore_obj.filter(subfactor__factor__in=[5])

        if len(fin_risk) > 0:
            self.helper.layout.append(
                Div(
                    HTML('Operating environment'),
                    css_class='Subheader',
                )
            )
        for d in fin_risk:

            self.fields['w_{}'.format(d.pk)] = forms.ChoiceField(
                label='Impact',
                initial=d.weight,
                choices=RA_WEIGHT_CHOICES,
            )
            if not d.weight_edit_allowed:
                self.fields['w_{}'.format(d.pk)].widget = forms.HiddenInput()

            self.fields['s_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=BASE_SCORE,
                initial=d.decided_score,
            )

            # Cross border
            if d.subfactor.id == 13:
                self.fields['w_{}'.format(d.pk)].required = False
                self.fields['s_{}'.format(d.pk)].required = False

            if d.weight_edit_allowed:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        css_class='row',
                    ),
                )
            else:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        css_class='row',
                    ),
                )

        #################################################
        # Financial: Risk appetite
        #################################################
        fin_risk = subscore_obj.filter(subfactor__factor__in=[6])

        if len(fin_risk) > 0:
            self.helper.layout.append(
                Div(
                    HTML('Risk appetite'),
                    css_class='Subheader',
                )
            )
        for d in fin_risk:

            if d.subfactor.id in [17, 18]:

                if d.subfactor.id == 17:
                    choices = (
                        (0.1, '10%'),
                        (0.075, '7.5%'),
                    )
                else:
                    choices = (
                        (None, '0%'),
                        (0.025, '2.5%'),
                    )

                self.fields['w_{}'.format(d.pk)] = forms.ChoiceField(
                    label='Impact',
                    initial=d.weight,
                    choices=choices,
                )

            else:
                self.fields['w_{}'.format(d.pk)] = forms.FloatField(
                    label='Impact',
                    initial=d.weight,
                )

            if not d.weight_edit_allowed:
                self.fields['w_{}'.format(d.pk)].widget = forms.HiddenInput()

            self.fields['s_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=BASE_SCORE,
                initial=d.decided_score,
            )

            # Market risk is not required
            if d.subfactor.id == 18:
                self.fields['w_{}'.format(d.pk)].required = False
                self.fields['s_{}'.format(d.pk)].required = False

            if d.weight_edit_allowed:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        css_class='row',
                    ),
                )
            else:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        css_class='row',
                    ),
                )

        #################################################
        # Financial: Competitive position
        #################################################
        fin_risk = subscore_obj.filter(subfactor__factor__in=[7])

        if len(fin_risk) > 0:
            self.helper.layout.append(
                Div(
                    HTML('Competitive position'),
                    css_class='Subheader',
                )
            )
        for d in fin_risk:

            self.fields['w_{}'.format(d.pk)] = forms.FloatField(
                label='Impact',
                initial=d.weight,
            )
            if not d.weight_edit_allowed:
                self.fields['w_{}'.format(d.pk)].widget = forms.HiddenInput()

            self.fields['s_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=BASE_SCORE,
                initial=d.decided_score,
            )

            if d.weight_edit_allowed:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-6'),
                        css_class='row',
                    ),
                )
            else:
                self.helper.layout.append(
                    Div(
                        Div(Field('s_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        Div(Field('w_{}'.format(d.pk)),
                            css_class='col-md-12'),
                        css_class='row',
                    ),
                )

        #################################################
        # Adjustment factors
        #################################################
        self.helper.layout.append(
            Div(
                HTML('Adjustment factors'),
                css_class='Subheader',
            )
        )
        for d in subscore_obj.filter(
                subfactor__factor__in=[3]):

            self.fields['n_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=NOTCH_CHOICES,
                initial=d.decided_notch_adjustment,
            )

            self.helper.layout.append(
                Div(
                    Div(Field('n_{}'.format(d.pk)),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        #################################################
        # Support factors
        #################################################
        self.helper.layout.append(
            Div(
                HTML('Support factors'),
                css_class='Subheader',
            )
        )
        for d in subscore_obj.filter(
                subfactor__factor__in=[4]):

            self.fields['n_{}'.format(d.pk)] = forms.ChoiceField(
                label=d.subfactor.name,
                choices=NOTCH_CHOICES,
                initial=d.decided_notch_adjustment,
            )

            self.helper.layout.append(
                Div(
                    Div(Field('n_{}'.format(d.pk)),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        #################################################
        # Issue seniority levels
        #################################################
        i_lvl = SeniorityLevelAssessment.objects.filter(
            assessment=rating_assessment,
        )

        self.helper.layout.append(
            Div(
                HTML('Bond assessment'),
                css_class='Subheader',
            )
        )
        for i in i_lvl:

            try:
                initial_value = current_assessment_sort_order - i.decided_lt
            except TypeError:
                initial_value = 0

            if i.assessment.issuer.issuer_type.id == 2 and i.seniority.id == 4:
                label = 'T2'
            else:
                label = i.seniority

            self.fields['i_{}'.format(i.pk)] = forms.ChoiceField(
                label=label,
                choices=NOTCH_CHOICES,
                initial=initial_value,
            )

            self.helper.layout.append(
                Div(
                    Div(Field('i_{}'.format(i.pk)),
                        css_class='col-md-12'),
                    css_class='row',
                ),
            )

        self.helper.layout.append(
            Div(
                Div(Field('comment'), css_class='col-md-12'),
                css_class='row',
            ),
        )

        if rating_assessment.process_step == 1:
            self.helper.layout.append(
                Div(
                    Div(
                        Div(HTML('Ready for approval:'), css_class=DIV_CLASS),
                        Div('ready_for_approval', css_class=DIV_CLASS)
                    ),
                    css_class='row',
                )
            )
        elif rating_assessment.process_step == 2:
            self.helper.layout.append(
                Div(
                    Div(
                        Div(HTML('Give final approval:'), css_class=DIV_CLASS),
                        Div('give_final_approval', css_class=DIV_CLASS)
                    ),
                    css_class='row',
                )
            )


class CreateRatingAssessment(forms.ModelForm):
    """Create a new credit assessment."""

    class Meta:
        """Meta class."""
        model = AssessmentJob
        fields = [
            'issuer',
        ]

    def __init__(self,
                 *args,
                 **kwargs):
        """Initiate the class."""

        super(CreateRatingAssessment, self).__init__(*args, **kwargs)

        self.fields['issuer'].choices = [
            (l.id, l.legal_name) for l in
            Issuer.objects.list_eligible_for_assessment()
        ]

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        self.helper.layout.append(
            Div(
                Div(Field('issuer'), css_class='col-md-12'),
                css_class='row',
            ),
        )


class CreateUpdatedAssessment(forms.ModelForm):
    """Create a credit assessment based on an approved one."""

    class Meta:
        """Meta class."""
        model = AssessmentJob
        fields = [
            'issuer',
        ]

    def __init__(self,
                 issuer_pk,
                 *args,
                 **kwargs):
        """Initiate the class."""

        super(CreateUpdatedAssessment, self).__init__(*args, **kwargs)

        self.fields['issuer'].queryset = Issuer.objects.filter(pk=issuer_pk)
        self.fields['issuer'].initial = issuer_pk

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        self.helper.layout.append(
            Div(
                Div(Field('issuer'), css_class='col-md-12'),
                css_class='row',
            ),
        )


class EditSubfactorPeer(forms.ModelForm):
    """Form to compare a subfactor over all peers."""

    class Meta:
        """Meta class."""
        model = AssessmentSubscoreData
        fields = [
            'decided_score',
        ]

    def __init__(self,
                 subfactor_id,
                 user,
                 *args,
                 **kwargs):
        """Initiate the class."""

        super(EditSubfactorPeer, self).__init__(*args, **kwargs)

        subfactor_obj = AssessmentSubscoreData.objects.get(pk=subfactor_id)

        # Setup first field of form
        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        # Label the field with the name of the clicked issuer
        self.fields['decided_score'].label = subfactor_obj.assessment.\
            issuer.legal_name

        self.helper.layout.append(
            Div(
                Div(Field('decided_score'), css_class='col-md-12'),
                css_class='row',
            ),
        )

        if subfactor_obj.assessment.issuer.classification.peer_free_text:
            # Get a list of peers, excluding the current issuer
            issuers = Issuer.objects.filter(
                classification__peer_free_text=subfactor_obj.assessment.
                issuer.classification.peer_free_text,
            )
        else:
            # Get a list of peers, excluding the current issuer
            issuers = Issuer.objects.filter(
                gics_sub_industry=subfactor_obj.assessment.issuer.
                gics_sub_industry,
            )

        issuers = issuers.filter(assessmentjob__isnull=False,).exclude(
            pk=subfactor_obj.assessment.issuer.id).distinct()

        for i in issuers:
            try:

                # Check if the issuer has an active assessment and if so,
                # allow editing of it

                # Special case, the assessment is awaiting approval and the
                # current user was the one starting the assessment

                a = AssessmentSubscoreData.objects.get(
                    assessment__issuer=i,
                    assessment__process_step__in=[1, 2],
                    assessment__is_current=False,
                    assessment__date_time_approval__isnull=True,
                    subfactor=subfactor_obj.subfactor,
                )

                if a.assessment.process_step == 2 and \
                        user == a.assessment.initiated_by:

                    # Render field
                    self.helper.layout.append(
                        Div(
                            Div(HTML(a.assessment.issuer.legal_name)),
                            Div(HTML(a.get_decided_score_display() +
                                     ' (cannot be edited)'))
                        )
                    )

                    # Add a blank row
                    self.helper.layout.append(
                        Div(HTML('&nbsp;'))
                    )

                else:

                    self.fields['s_{}'.format(a.pk)] = forms.ChoiceField(
                        label=a.assessment.issuer.legal_name,
                        choices=BASE_SCORE,
                        initial=a.decided_score,
                    )

                    # Make the fields non-required
                    self.fields['s_{}'.format(a.pk)].required = False

                    # Render field
                    self.helper.layout.append(
                        Div(
                            Div(Field('s_{}'.format(a.pk)),
                                css_class='col-md-12'),
                            css_class='row',
                        ),
                    )

            except AssessmentSubscoreData.DoesNotExist:

                # If there is no active assessment, just show the current score
                a = AssessmentSubscoreData.objects.get(
                    assessment__issuer=i,
                    assessment__is_current=True,
                    subfactor=subfactor_obj.subfactor,
                )

                # Render field
                self.helper.layout.append(
                    Div(
                        Div(HTML(a.assessment.issuer.legal_name)),
                        Div(HTML(a.get_decided_score_display() +
                                 ' (cannot be edited)'))
                    )
                )

                # Add a blank row
                self.helper.layout.append(
                    Div(HTML('&nbsp;'))
                )
