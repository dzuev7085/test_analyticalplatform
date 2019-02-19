# DJANGO CORE
from contextlib import closing
from decimal import Decimal as D

from bs4 import BeautifulSoup
from django.db import connection

from a_helper.modal_helper.views import AjaxCreateView, AjaxUpdateView
from a_helper.static_database_table.models.currency import Currency

from .forms import AddIssueForm, EditIssueForm, StamdataDataForm
from django.contrib.messages.views import SuccessMessageMixin
from .models import Issue


class StamdataLoadView(AjaxCreateView):  # pylint: disable=too-many-ancestors

    form_class = StamdataDataForm

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):

        kwargs = super(StamdataLoadView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_invalid(self, form):
        print(form.errors)

    def form_valid(self, form):

        html = form.cleaned_data['textarea']
        soup = BeautifulSoup(html, "lxml")

        listoflists = []

        try:
            rows = soup.find('tbody').findAll('tr')

            for row in rows:
                cells = row.findAll('td')

                output = []

                for i, cell in enumerate(cells):

                    cell_value = cell.text.strip()

                    if cell_value == '—':
                        cell_value = None

                    if i == 6:
                        if cell_value is not None:
                            currency = cell_value[-3:].strip()
                            output.append(currency)

                            cell_value = cell_value[
                                :-3].strip().replace(
                                    ' ', '').replace(',', '')
                        else:
                            output.append('')
                            cell_value = ''

                    output.append(cell_value)

                listoflists.append(output)

        except:  # noqa E722
            pass

        issuer_id = self.kwargs['issuer_pk']

        list_result = [entry for entry in Currency.objects.all().values()]

        currency_list = {}
        for index in range(len(list_result)):
            for key in list_result[index]:
                if key == 'currency_code_alpha_3':
                    currency_list[list_result[index][
                        'currency_code_alpha_3']] = list_result[index]['id']

        query_long = ""
        for row in listoflists:

            isin = row[0]
            name = row[1]
            ticker = row[2]
            disbursement = row[3]

            maturity = row[4]
            interest = row[5]

            currency = row[6]
            amount = row[7]

            if len(amount) > 0 and len(currency) > 0:

                currency = currency_list[currency]
                amount = D(amount)

                # Send raw SQL to bypass ORM and optimize inserts
                query = (
                    "INSERT INTO issue_issue (issuer_id, isin, name, ticker, disbursement, maturity, interest, currency_id, amount) "  # noqa E501 pylint: disable=line-too-long
                    "VALUES (%s, '%s', '%s', '%s', '%s', '%s', '%s', %s, %s) "
                    "ON CONFLICT (isin) DO UPDATE SET "
                    "name=EXCLUDED.name, ticker=EXCLUDED.ticker, disbursement=EXCLUDED.disbursement, maturity=EXCLUDED.maturity,"  # noqa E501 pylint: disable=line-too-long
                    "interest=EXCLUDED.interest, currency_id=EXCLUDED.currency_id, amount=EXCLUDED.amount; "  # noqa E501 pylint: disable=line-too-long
                    % (
                        issuer_id,
                        str(isin),
                        str(name),
                        ticker,
                        disbursement,
                        maturity,
                        interest,
                        currency,
                        amount))

                query_long = query_long + query

        with closing(connection.cursor()) as cursor:
            cursor.execute(query_long)

        # If we use standard return method
        # an empty record set is created in the db
        return self.render_json_response({'status': 'ok'})


class IssueUpdateView(SuccessMessageMixin,
                      AjaxUpdateView,  # pylint: disable=too-many-ancestors
                      ):
    """View to update an issue."""

    model = Issue
    form_class = EditIssueForm
    pk_url_kwarg = 'issue_pk'

    def get_success_message(self, cleaned_data):
        """Custom get_success_message method."""

        return "Successfully updated issue with ISIN {}.".format(
            cleaned_data['isin'])

    def get_form_kwargs(self):
        """Custom method for get_form_kwargs."""

        kwargs = super(IssueUpdateView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs


class IssueCreateView(SuccessMessageMixin,
                      AjaxCreateView,  # pylint: disable=too-many-ancestors
                      ):
    """View to create an issue."""

    form_class = AddIssueForm

    def get_success_message(self, cleaned_data):
        """Custom get_success_message method."""

        return "Successfully created issue with ISIN {}.".format(
            cleaned_data['isin'])

    def get_form_kwargs(self):
        """Custom method for get_form_kwargs."""

        kwargs = super(IssueCreateView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def get_success_url(self):
        """Custom method for get_success_url."""

        return self.request.META.get('HTTP_REFERER')
