from bootstrap_datepicker_plus import DatePickerInput

from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, HTML
from tinymce.widgets import TinyMCE

from django import forms
from django.contrib.auth.models import User

from config.generic_util.misc import UserFullnameChoiceField
from rating_process.models.rating_decision import EventType
from django.urls import reverse

from .models.job_member import JobMember, Role
from .models.internal_score_data import InternalScoreData, RatingDecision
from .models.rating_decision_issue import RatingDecisionIssue
from .models.temporary_storage import Tmp
from .models.insider_link import RatingDecisionInsiderLink
from .models.press_release import PressRelease

from issuer.models import InsiderList, Issuer
from pycreditrating import RATING_LONG_TERM_REVERSE_TUPLE
from gui.templatetags.template_tags import current_rating
from rating_process.models.issue_decision import IssueDecision
from issue.models import Issue

TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)


class StartRatingProcess(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, issuer_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(StartRatingProcess, self).__init__(*args, **kwargs)

        issuer_obj = Issuer.objects.get(pk=issuer_pk)

        existing_rating = current_rating(issuer_obj)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        # For existing ratings, prohibit choosing "initial rating"
        if existing_rating:
            self.fields["event_type"].queryset = EventType.objects.\
                distinct().filter(id__in=[2, 3])
        else:
            self.fields["event_type"].queryset = EventType.objects.\
                distinct().filter(id__in=[1])

        # Event type is always required
        self.helper.layout.append(
            Div(
                Div(Field('event_type'), css_class='col-md-12'),
                css_class='row',
            )
        )

        # For existing ratings, we dont have many options
        if existing_rating:

            self.helper.layout.append(
                Field(
                    'is_preliminary',
                    type='hidden',
                    value=False
                )
            )
            self.helper.layout.append(
                Field(
                    'rating_type',
                    type='hidden',
                    value=existing_rating.rating_type.id
                )
            )
        else:

            # For new ratings, we have some options
            self.helper.layout.append(
                Div(
                    Div(Field('rating_type'), css_class='col-md-12'),
                    css_class='row',
                ),
            )
            self.helper.layout.append(
                Div(
                    Div(Field('is_preliminary'), css_class='col-md-12'),
                    css_class='row',
                ),
            )

        self.helper.layout.append(
            Field(
                'issuer',
                type='hidden',
                value=issuer_pk
            )
        )

    class Meta:
        """Meta class."""
        model = RatingDecision
        fields = [
            'event_type',
            'rating_type',
            'is_preliminary',
            'issuer',
        ]
        widgets = {
            'is_preliminary': forms.Select(
                choices=TRUE_FALSE_CHOICES)
        }
        labels = {
            'event_type': 'This is a',
            'rating_type': 'Type of rating',
            'is_preliminary': 'This is a preliminary rating',
        }


class EditProposedSubfactor(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, edit_weight=None, *args, **kwargs):
        """Initiate the class."""

        super(EditProposedSubfactor, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('proposed_score'), css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div(Field('weight'), css_class='col-md-12'),
                css_class='row',
            ),
        )

        if edit_weight == 0:
            self.fields['weight'].widget = forms.HiddenInput()

    class Meta:
        """Meta class."""
        model = InternalScoreData
        fields = [
            'proposed_score',
            'weight'
        ]
        labels = {
            'proposed_score': 'Recommended score',
            'weight': 'Score impact'
        }


class EditDecidedSubfactor(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, edit_weight=None, *args, **kwargs):
        """Initiate the class."""

        super(EditDecidedSubfactor, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('decided_score'), css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div(Field('weight'), css_class='col-md-12'),
                css_class='row',
            ),
        )

        if edit_weight == 0:
            self.fields['weight'].widget = forms.HiddenInput()

    class Meta:
        """Meta class."""
        model = InternalScoreData
        fields = [
            'decided_score',
            'weight'
        ]
        labels = {
            'decided_score': 'Final score',
            'weight': 'Score impact'
        }


class EditProposedAdjustmentFactor(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditProposedAdjustmentFactor, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('proposed_notch_adjustment'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        """Meta class."""
        model = InternalScoreData
        fields = [
            'proposed_notch_adjustment',
        ]
        labels = {
            'proposed_notch_adjustment': 'Recommended adjustment',
        }


class EditDecidedAdjustmentFactor(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(EditDecidedAdjustmentFactor, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('decided_notch_adjustment'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        """Meta class."""
        model = InternalScoreData
        fields = [
            'decided_notch_adjustment',
        ]
        labels = {
            'decided_notch_adjustment': 'Final adjustment',
        }


class EditRatingDecision(forms.ModelForm):
    """Edit any field in the rating description object."""

    class Meta:
        """Meta class."""
        model = RatingDecision
        fields = [
            'proposed_lt_outlook',
            'proposed_st',

            'decided_lt_outlook',
            'decided_st',

            'date_time_committee',

            'committee_comments',

            'chair',

            'event',

            'recommendation_rationale'
        ]
        labels = {
            'proposed_lt_outlook': 'Recommended outlook',
            'decided_lt_outlook': 'Decided outlook',
            'proposed_st': 'Recommended short-term rating',
            'decided_st': 'Decided short-term rating',
        }

    date_time_committee = forms.DateTimeField(
        required=False,
        widget=DatePickerInput(
            options={"format": "YYYY-MM-DD HH:mm",
                     "daysOfWeekDisabled":
                         [0, 6],
                     "calendarWeeks":
                         True,
                     "enabledHours":
                         [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                     "sideBySide":
                         True}),
        label='')

    def __init__(self, field=None, rating_decision_obj=None, *args, **kwargs):
        """Initiate the class."""

        super(EditRatingDecision, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)

        exclude_list = []

        try:
            exclude_list.append(
                rating_decision_obj.issuer.analyst.primary_analyst.username)
        except:  # noqa: E722
            pass

        try:
            exclude_list.append(
                rating_decision_obj.issuer.analyst.secondary_analyst.username)
        except:  # noqa: E722
            pass

        self.fields["chair"].queryset = User.objects.distinct().filter(
            groups__name__in=[
                'Senior level analyst']).exclude(
            username__in=exclude_list)

        self.fields['chair'].required = False

        chair = rating_decision_obj.chair \
            if rating_decision_obj.chair else ''
        date_time_committee = rating_decision_obj.date_time_committee \
            if rating_decision_obj.date_time_committee else ''

        proposed_lt_outlook = rating_decision_obj.proposed_lt_outlook if \
            rating_decision_obj.proposed_lt_outlook else ''
        proposed_st = rating_decision_obj.proposed_st if \
            rating_decision_obj.proposed_st else ''

        decided_lt_outlook = rating_decision_obj.decided_lt_outlook if \
            rating_decision_obj.decided_lt_outlook else ''
        decided_st = rating_decision_obj.decided_st if \
            rating_decision_obj.decided_st else ''

        committee_comments = rating_decision_obj.committee_comments if \
            rating_decision_obj.committee_comments else ''

        event = rating_decision_obj.event if rating_decision_obj.event else ''

        recommendation_rationale = \
            rating_decision_obj.recommendation_rationale if \
            rating_decision_obj.recommendation_rationale else ''

        if field in ['proposed_st', 'decided_st']:

            if field == 'proposed_st':
                field_value = getattr(rating_decision_obj, 'proposed_lt')
            else:
                field_value = getattr(rating_decision_obj, 'decided_lt')

            if field_value <= 9:  # above 'BBB'
                """From methodology
                'AAA': 'N-1+',
                'AA+': 'N-1+',
                'AA': 'N-1+',
                'AA-': 'N-1+',
                'A+': 'N-1+',
                'A': 'N-1+',
                'A-': 'N-1+',
                'BBB+': 'N-1+',
                'BBB': 'N-1+',
                """
                CHOICES = (
                    (1, 'N-1+'),
                )

            elif field_value == 10:  # 'BBB-'
                # From methodology
                # 'BBB-': 'N-1+, N-1'
                CHOICES = (
                    (1, 'N-1+'),
                    (2, 'N-1'),
                )
            elif field_value == 11:  # 'BB+'
                # From methodology
                # 'BB+': 'N-1'

                CHOICES = (
                    (2, 'N-1'),
                )
            elif field_value == 12:  # 'BB'
                # From methodology
                # 'BB': 'N-1, N-2'
                CHOICES = (
                    (2, 'N-1'),
                    (3, 'N-2'),
                )
            elif field_value == 13:  # 'BB-'
                # From methodology
                # 'BB-': 'N-2'
                CHOICES = (
                    (3, 'N-2'),
                )
            elif field_value == 14:  # 'B+'
                # From methodology
                # 'B+': 'N-2, N-3'
                CHOICES = (
                    (3, 'N-2'),
                    (4, 'N-3')
                )
            elif field_value == 15:  # 'B'
                # From methodology
                # 'B': 'N-3'
                CHOICES = (
                    (4, 'N-3'),
                )
            elif field_value == 16:  # 'B-'
                # From methodology
                # 'B-': 'N-3, N-4'
                CHOICES = (
                    (4, 'N-3'),
                    (5, 'N-4')
                )
            elif 16 < field_value <= 19:  # 'Cxx'
                # From methodology
                # 'CCC'-'C': 'N-4'
                CHOICES = (
                    (5, 'N-4'),
                )
            else:
                CHOICES = (None, 'A long-term rating must be recommended.')

            self.fields[field].choices = CHOICES

        # Add date selector
        if field == 'date_time_committee':

            self.helper.layout = Layout(
                Div(
                    Div(
                        Field(field,
                              title='',
                              css_class='form-control datepicker',
                              id='datepicker'),
                        css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'chair':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-8'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'proposed_st':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'proposed_lt_outlook':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'decided_lt_outlook':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'decided_st',
                    type='hidden',
                    value=decided_st
                ),

                Field(
                    'committee_comments',
                    type='hidden',
                    value=committee_comments
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'decided_st':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'decided_lt_outlook',
                    type='hidden',
                    value=decided_lt_outlook
                ),

                Field(
                    'committee_comments',
                    type='hidden',
                    value=committee_comments
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'committee_comments':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'decided_lt_outlook',
                    type='hidden',
                    value=decided_lt_outlook
                ),

                Field(
                    'decided_st',
                    type='hidden',
                    value=decided_st
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'event':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'decided_lt_outlook',
                    type='hidden',
                    value=decided_lt_outlook
                ),

                Field(
                    'decided_st',
                    type='hidden',
                    value=decided_st
                ),

                Field(
                    'committee_comments',
                    type='hidden',
                    value=committee_comments
                ),

                Field(
                    'recommendation_rationale',
                    type='hidden',
                    value=recommendation_rationale
                ),

            )

        elif field == 'recommendation_rationale':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),

                Field(
                    'proposed_lt_outlook',
                    type='hidden',
                    value=proposed_lt_outlook
                ),

                Field(
                    'proposed_st',
                    type='hidden',
                    value=proposed_st
                ),

                Field(
                    'date_time_committee',
                    type='hidden',
                    value=date_time_committee
                ),

                Field(
                    'chair',
                    type='hidden',
                    value=chair
                ),

                Field(
                    'decided_lt_outlook',
                    type='hidden',
                    value=decided_lt_outlook
                ),

                Field(
                    'decided_st',
                    type='hidden',
                    value=decided_st
                ),

                Field(
                    'committee_comments',
                    type='hidden',
                    value=committee_comments
                ),

                Field(
                    'event',
                    type='hidden',
                    value=event
                ),

            )

        # We need to store the name of the chairperson
        else:

            raise ValueError('Field %s does not exist' % field)


class AddCommitteeMemberForm(forms.ModelForm):
    """Edit member of rating committee."""

    member = UserFullnameChoiceField(
        queryset=User.objects.distinct().filter(
            groups__name__in=[
                'Analyst',
                'Senior level analyst']))

    def __init__(self, rating_decision_pk=None, *args, **kwargs):
        """Initiate the class."""
        super(AddCommitteeMemberForm, self).__init__(*args, **kwargs)

        self.fields['role'].queryset =\
            Role.objects.filter(
                id=1) | Role.objects.filter(id=2)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('member'), css_class='col-md-8'),
                css_class='row',
            ),
            Div(
                Div(Field('role'), css_class='col-md-8'),
                css_class='row',
            ),
            Field(
                'rating_decision',
                type='hidden',
                value=rating_decision_pk
            )
        )

    class Meta:
        model = JobMember
        fields = [
            'member',
            'rating_decision',
            'role'
        ]


class AddEditorForm(forms.ModelForm):
    """Edit member of rating committee."""

    member = UserFullnameChoiceField(
        queryset=User.objects.distinct().filter(
            groups__name__in=[
                'Editor']))

    def __init__(self, rating_decision_pk=None, *args, **kwargs):
        """Initiate the class."""
        super(AddEditorForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('member'), css_class='col-md-8'),
                css_class='row',
            ),
            Field(
                'rating_decision',
                type='hidden',
                value=rating_decision_pk
            )
        )

    class Meta:
        model = JobMember
        fields = [
            'member',
            'rating_decision',
        ]


class UpdateAdminControlEditorForm(forms.ModelForm):
    """Edit tmp control object."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""
        super(UpdateAdminControlEditorForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('editor_admin_control_link'),
                    css_class='col-md-12'),
                css_class='row',
            )
        )

    class Meta:
        model = Tmp
        fields = [
            'editor_admin_control_link',
        ]


class UpdateAdminControlIssuerForm(forms.ModelForm):
    """Edit tmp control object."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""
        super(UpdateAdminControlIssuerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('issuer_admin_control_link'),
                    css_class='col-md-12'),
                css_class='row',
            )
        )

    class Meta:
        model = Tmp
        fields = [
            'issuer_admin_control_link',
        ]


class RatingDecisionIssueAddSeniority(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, rating_decision_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(RatingDecisionIssueAddSeniority, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('seniority'), css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div(Field('proposed_lt'), css_class='col-md-12'),
                css_class='row',
            ),

            Field(
                'rating_decision',
                type='hidden',
                value=rating_decision_pk
            )
        )

    class Meta:
        model = RatingDecisionIssue
        fields = [
            'seniority',
            'proposed_lt',
            'rating_decision'
        ]
        labels = {
            'proposed_lt': 'Recommended rating'
        }


class RatingDecisionIssueEditProposed(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(RatingDecisionIssueEditProposed, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('proposed_lt'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = RatingDecisionIssue
        fields = [
            'proposed_lt'
        ]
        labels = {
            'proposed_lt': 'Recommended rating',
        }


class RatingDecisionIssueEditDecided(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, *args, **kwargs):
        """Initiate the class."""

        super(RatingDecisionIssueEditDecided, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('decided_lt'), css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = RatingDecisionIssue
        fields = [
            'decided_lt'
        ]
        labels = {
            'decided_lt': 'Final rating'
        }


class RatingDecisionInsiderLinkForm(forms.ModelForm):
    """Edit the description field of the issuer."""

    def __init__(self, rating_decision_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(RatingDecisionInsiderLinkForm, self).__init__(*args, **kwargs)

        rating_decision_obj = RatingDecision.objects.get(pk=rating_decision_pk)

        self.fields['insider'].queryset = \
            InsiderList.objects.filter(
                issuer=rating_decision_obj.issuer)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(Field('insider'), css_class='col-md-12'),
                css_class='row',
            ),
            Field(
                'rating_decision',
                type='hidden',
                value=rating_decision_obj.id
            )
        )

    class Meta:
        model = RatingDecisionInsiderLink
        fields = [
            'insider',
            'rating_decision'
        ]


class EditPressReleaseForm(forms.ModelForm):
    """Edit any field in the rating description object."""

    class Meta:
        """Meta class."""
        model = PressRelease
        fields = [
            'header',
            'pre_amble',
            'body',
        ]

    def __init__(self, field=None, press_release_obj=None, *args, **kwargs):
        """Initiate the class."""

        super(EditPressReleaseForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(form=self)

        header = press_release_obj.header \
            if press_release_obj.header else ''

        pre_amble = press_release_obj.pre_amble \
            if press_release_obj.pre_amble else ''

        body = press_release_obj.body \
            if press_release_obj.body else ''

        if field == 'header':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),
                Field(
                    'pre_amble',
                    type='hidden',
                    value=pre_amble
                ),
                Field(
                    'body',
                    type='hidden',
                    value=body
                ),

            )

        elif field == 'pre_amble':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),
                Field(
                    'header',
                    type='hidden',
                    value=header
                ),
                Field(
                    'body',
                    type='hidden',
                    value=body
                ),

            )

        elif field == 'body':

            self.helper.layout = Layout(
                Div(
                    Div(Field(field), css_class='col-md-12'),
                    css_class='row',
                ),
                Field(
                    'header',
                    type='hidden',
                    value=header
                ),
                Field(
                    'pre_amble',
                    type='hidden',
                    value=pre_amble
                ),

            )

        else:
            raise ValueError('Field %s does not exist' % field)


class IssueRatingDecisionAddForm(forms.ModelForm):
    """Edit any field in the rating description object."""

    class Meta:
        """Meta class."""
        model = IssueDecision
        fields = [
            'decided_lt',
        ]

    decided_lt = forms.ChoiceField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        label=False,
        initial=200,
    )

    is_preliminary = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text='Only click if the rating is preliminary.',
        required=False,
    )

    """
    term_sheet = forms.FileField(
        label=False,
        help_text='Upload the term sheet for this issue, if available.',
        required=False,
    )

    final_terms = forms.FileField(
        label=False,
        help_text='Upload the final terms for this issue, if available.',
        required=False,
    )
    """

    rationale = forms.CharField(
        widget=TinyMCE(attrs={'cols': 60, 'rows': 15}),
        label=False,
        help_text='Give a brief rationale for the recommended rating.',
        required=True,
    )

    ready_for_decision = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text="Click this box and press 'Save changes' to send the "
                  "proposed rating decision for final approval. If you "
                  "want to continue working on the decision later, "
                  "just press 'Save changes' without clicking the "
                  "box.",
        required=False,
    )

    issue_id = forms.IntegerField()
    rating_decision_issue_id = forms.IntegerField()

    def __init__(self, issue_pk=None,
                 rating_decision_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(IssueRatingDecisionAddForm, self).__init__(*args, **kwargs)

        issue = Issue.objects.get(pk=issue_pk)

        rating_decision_issue = RatingDecisionIssue.objects.get(
            seniority=issue.seniority,
            rating_decision__id=rating_decision_pk,
        )

        cmp_url = reverse(
            'issuer_rating_job_committee_package',
            kwargs={
                'rating_decision_id': rating_decision_pk})

        DIV_CLASS = 'col-md-12'

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(HTML('Program:'), css_class='col-md-12'),
                    Div(HTML(issue.program), css_class='col-md-12'),
                ),
                Div(
                    Div(HTML('Seniority:'), css_class='col-md-12'),
                    Div(HTML(issue.seniority), css_class='col-md-12'),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(
                        HTML(
                            'Last decided rating for {}:'.format(
                                str(issue.seniority).lower())),
                        css_class='col-md-12'),
                    Div(
                        HTML("'{}'".format(
                            rating_decision_issue.get_decided_lt_display())),
                        css_class='col-md-12'),
                    Div(
                        HTML("<a href='{}' target='_blank'>Download "
                             "committee pack</a>".format(cmp_url), ),
                        css_class='col-md-12'),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('ISIN:'), css_class=DIV_CLASS),
                    Div(HTML(issue.isin), css_class=DIV_CLASS),
                ),
                Div(
                    Div(HTML('Currency:'), css_class=DIV_CLASS),
                    Div(HTML(issue.currency), css_class=DIV_CLASS),
                ),
                Div(
                    Div(HTML('Amount:'), css_class=DIV_CLASS),
                    Div(HTML(issue.amount/1000000), css_class=DIV_CLASS),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),
                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Proposed rating:'), css_class=DIV_CLASS),
                    Div('decided_lt', css_class=DIV_CLASS),
                ),

                Div(
                    Div(HTML('Preliminary rating:'), css_class=DIV_CLASS),
                    Div('is_preliminary', css_class=DIV_CLASS),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Rationale:'), css_class=DIV_CLASS),
                    Div('rationale', css_class=DIV_CLASS)
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Ready for decision:'), css_class=DIV_CLASS),
                    Div('ready_for_decision', css_class=DIV_CLASS)
                ),

                css_class='row',
            ),

            Field(
                'issue_id',
                type='hidden',
                value=issue_pk,
            ),

            Field(
                'rating_decision_issue_id',
                type='hidden',
                value=rating_decision_issue.id,
            )

        )


class IssueRatingDecisionEditForm(forms.ModelForm):
    """Edit any field in the rating description object."""

    class Meta:
        """Meta class."""
        model = IssueDecision
        fields = [
            'decided_lt',
            'rationale',
            'is_preliminary',
            'proposed_by',
        ]

    decided_lt = forms.ChoiceField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        label=False,
        initial=200,
    )

    is_preliminary = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text='Only click if the rating is preliminary.',
        required=False,
    )

    rationale = forms.CharField(
        widget=TinyMCE(attrs={'cols': 60, 'rows': 15}),
        label=False,
        help_text='Give a brief rationale for the recommended rating.',
        required=True,
    )

    ready_for_decision = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text="Click this box and press 'Save changes' to send the "
                  "proposed rating decision for final approval. If you "
                  "want to continue working on the decision later, "
                  "just press 'Save changes' without clicking the "
                  "box.",
        required=False,
    )

    give_final_approval = forms.BooleanField(
        initial=False,
        label='Yes',
        help_text="Click this box and press 'Save changes' to decide on "
                  "rating proposed above.",
        required=False,
    )

    def __init__(self, issue_decision_pk=None, *args, **kwargs):
        """Initiate the class."""

        super(IssueRatingDecisionEditForm, self).__init__(*args, **kwargs)

        DIV_CLASS = 'col-md-12'

        rating_decision_issue = IssueDecision.objects.get(
            pk=issue_decision_pk)
        issue = rating_decision_issue.issue

        cmp_url = reverse(
            'issuer_rating_job_committee_package',
            kwargs={
                'rating_decision_id':
                    rating_decision_issue.rating_decision_issue.
                    rating_decision.id})

        # Custom settings for the proposed by field
        self.fields['proposed_by'].disabled = True
        self.fields['proposed_by'].label = ''

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(HTML('Proposed by :'), css_class='col-md-12'),
                    Div(Field('proposed_by'), css_class='col-md-12'),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Program:'), css_class='col-md-12'),
                    Div(HTML(issue.program), css_class='col-md-12'),
                ),
                Div(
                    Div(HTML('Seniority:'), css_class='col-md-12'),
                    Div(HTML(issue.seniority), css_class='col-md-12'),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(
                        HTML(
                            'Last decided rating for {}:'.format(
                                str(issue.seniority).lower())),
                        css_class='col-md-12'),
                    Div(
                        HTML("'{}'".format(
                            rating_decision_issue.get_decided_lt_display())),
                        css_class='col-md-12'),
                    Div(
                        HTML("<a href='{}' target='_blank'>Download "
                             "committee pack</a>".format(cmp_url), ),
                        css_class='col-md-12'),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('ISIN:'), css_class=DIV_CLASS),
                    Div(HTML(issue.isin), css_class=DIV_CLASS),
                ),
                Div(
                    Div(HTML('Currency:'), css_class=DIV_CLASS),
                    Div(HTML(issue.currency), css_class=DIV_CLASS),
                ),
                Div(
                    Div(HTML('Amount:'), css_class=DIV_CLASS),
                    Div(HTML(issue.amount/1000000), css_class=DIV_CLASS),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),
                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Proposed rating:'), css_class=DIV_CLASS),
                    Div('decided_lt', css_class=DIV_CLASS),
                ),

                Div(
                    Div(HTML('Preliminary rating:'), css_class=DIV_CLASS),
                    Div('is_preliminary', css_class=DIV_CLASS),
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                Div(
                    Div(HTML('Rationale:'), css_class=DIV_CLASS),
                    Div(Field('rationale'), css_class=DIV_CLASS)
                ),

                Div(
                    HTML('&nbsp;'), css_class='w-100',
                ),

                css_class='row',
            ),
        )

        if rating_decision_issue.process_step == 1:
            self.helper.layout.append(
                Div(
                    Div(
                        Div(HTML('Ready for decision:'), css_class=DIV_CLASS),
                        Div('ready_for_decision', css_class=DIV_CLASS)
                    ),
                    css_class='row',
                )
            )
        elif rating_decision_issue.process_step == 2:
            self.helper.layout.append(
                Div(
                    Div(
                        Div(HTML('Give final approval:'), css_class=DIV_CLASS),
                        Div('give_final_approval', css_class=DIV_CLASS)
                    ),
                    css_class='row',
                )
            )
