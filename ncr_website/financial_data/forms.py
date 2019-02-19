from crispy_forms.bootstrap import Field, PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from issuer.models import Issuer
from datalake.findata.tables import FinancialStatement
from datalake import DB_CONNECTION


class EditFinancialItemForm(forms.ModelForm):
    """Edit a financial statement item."""

    class Meta:
        """Meta class."""
        model = Issuer
        fields = [
            'id',
        ]

    def __init__(self,
                 target_item=None,
                 issuer_id=None,
                 report_date_type=None,
                 currency=None,
                 statement_type=None,
                 data_source=None,
                 date=None,
                 *args,
                 **kwargs):
        """Initiate the class."""

        super(EditFinancialItemForm, self).__init__(*args, **kwargs)

        lei = Issuer.objects.get(pk=issuer_id).lei

        rs = DB_CONNECTION.session.query(
            FinancialStatement).filter_by(
            lei=lei,
            report_date=date,
            target_item=target_item,)

        self.helper = FormHelper(form=self)
        self.helper.layout = Layout()

        if rs.count() > 0:

            for i, r in enumerate(rs):

                self.fields['{}|field'.format(i)] = forms.DecimalField(
                    label=r.source_item,
                    required=False,
                )

                self.fields['{}|row_id'.format(i)] = forms.IntegerField()

                self.helper.layout.append(
                    Div(
                        PrependedAppendedText(
                            Field(
                                '{}|field'.format(i),
                                value=r.amount,
                            ),
                            '$',
                            '.00',
                        )
                    )
                )

                self.helper.layout.append(
                    Div(
                        Field(
                            '{}|row_id'.format(i),
                            type='hidden',
                            value=r.id
                        )
                    )
                )

        else:
            # The logic in the view is built around looping over integers
            # To avoid building something new in the view, just pass
            # values using 0 as index
            i = 0

            # Define form fields
            self.fields['{}|field'.format(i)] = forms.DecimalField(
                label=target_item,
            )
            self.fields['{}|target_item'.format(i)] = forms.CharField()
            self.fields['{}|lei'.format(i)] = forms.CharField()
            self.fields['{}|report_date_type'.format(i)] = forms.CharField()
            self.fields['{}|currency'.format(i)] = forms.CharField()
            self.fields['{}|statement_type'.format(i)] = forms.CharField()
            self.fields['{}|data_source'.format(i)] = forms.CharField()
            self.fields['{}|report_date'.format(i)] = forms.CharField()

            self.helper.layout.append(
                Div(
                    PrependedAppendedText(
                        Field(
                            '{}|field'.format(i),
                            value=0,
                        ),
                        '$',
                        '.00',
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|target_item'.format(i),
                        type='hidden',
                        value=target_item
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|lei'.format(i),
                        type='hidden',
                        value=lei
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|report_date_type'.format(i),
                        type='hidden',
                        value=report_date_type
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|currency'.format(i),
                        type='hidden',
                        value=currency
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|statement_type'.format(i),
                        type='hidden',
                        value=statement_type
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|data_source'.format(i),
                        type='hidden',
                        value=data_source
                    )
                )
            )

            self.helper.layout.append(
                Div(
                    Field(
                        '{}|report_date'.format(i),
                        type='hidden',
                        value=date
                    )
                )
            )
