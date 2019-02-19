# DJANGO CORE
from a_helper.modal_helper.views import AjaxCreateView
from django.views.generic import TemplateView
from django.http import HttpResponse
from .forms import EditFinancialItemForm
from financial_data.util.chart import (
    peer_grouped_bar_chart,
    peer_horizontal_bar_chart
)
from financial_data.util.data import chart_data_df
from datalake.findata.tables import FinancialStatement


class FinancialItemEditView(AjaxCreateView):  # pylint: disable=too-many-ancestors # noqa: E501
    """View to edit financial statement items."""

    form_class = EditFinancialItemForm

    def get_success_url(self):
        """Custom get_success_url method."""
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        """Custom get_form_kwargs method."""

        kwargs = super(FinancialItemEditView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):
        """Custom form_valid method."""

        d = {}

        for key, value in sorted(form.cleaned_data.items()):
            a = key.split('|')[0]
            b = key.split('|')[1]

            # Create a new dict for the id, so to be able
            # to update it below
            if a not in d:
                d[a] = {}

            # Store the values from the form into a dict
            if b == 'field':
                d[a].update({'value': value})
            elif b == 'row_id':
                d[a].update({'row_id': value})
            elif b == 'lei':
                d[a].update({'lei': value})
            elif b == 'report_date':
                d[a].update({'report_date': value})
            elif b == 'report_date_type':
                d[a].update({'report_date_type': value})
            elif b == 'target_item':
                d[a].update({'target_item': value})
            elif b == 'currency':
                d[a].update({'currency': value})
            elif b == 'data_source':
                d[a].update({'data_source': value})
            elif b == 'statement_type':
                d[a].update({'statement_type': value})

        for r in d:

            try:

                id = int(d[r]['row_id'])

                try:
                    amount = int(d[r]['value'])
                except TypeError:
                    amount = None

                FinancialStatement.update_row(id,
                                              self.request.user.username,
                                              amount)

            except KeyError:
                # No row id was sent, this is an insert

                FinancialStatement.insert_row(
                    lei=d[r]['lei'],
                    report_date=d[r]['report_date'],
                    report_date_type=d[r]['report_date_type'],
                    target_item=d[r]['target_item'],
                    currency=d[r]['currency'],
                    new_value=d[r]['value'],
                    update_user=self.request.user.username,
                    data_source=d[r]['data_source'],
                    statement_type=d[r]['statement_type'],
                )

        # If we use standard return method
        # an empty record set is created in the db
        return self.render_json_response({'status': 'ok'})


class DisplayPeerChart(TemplateView):
    """View to test chart data."""

    template_name = 'issuer/financials/chart.html'

    def get_context_data(self, **kwargs):
        """Custom get_context_data method."""

        context = super(DisplayPeerChart, self).get_context_data(**kwargs)

        issuer_id = self.kwargs['issuer_id']

        # Get data for the table
        df = chart_data_df(
            self.kwargs['item'],
            issuer_id,
        )

        # Format axis and hover
        format_as = self.kwargs['format_as']

        if format_as == 'multiplier':
            hoverformat = '.1f'
        elif format_as == 'percent':
            hoverformat = '.1%'
        else:
            hoverformat = ',d'

        if self.kwargs['chart_type'] == 'grouped_bar_chart':

            chart_data = peer_grouped_bar_chart(
                self,
                hoverformat,
                df
            )
        else:

            chart_data = peer_horizontal_bar_chart(
                self,
                hoverformat,
                df,
                issuer_id,
            )

        context['graph'] = chart_data

        return context


def return_chart_data_csv(request, item):
    """Create the HttpResponse object with the appropriate CSV header."""
    # https://bl.ocks.org/mbostock/3887051

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # Pivot the DataFrame to the format expected by the chart tool
    table = chart_data_df(item)

    table.to_csv(
        path_or_buf=response,
        sep=',',
        float_format='%.2f',
        index=True,
        decimal=".",
        na_rep=0,
    )

    return response
