"""Module to generate data for the charts."""
from gui.templatetags.financial_statement import item_value
import pandas as pd
from pyfindata import (
    AnalyzeCompany,
    ResultStatement
)
from issuer.models import Issuer
from datalake import DB_CONNECTION


def chart_data_df(item, issuer_id=None):
    """Return chart data as a DataFrame"""

    # Create a peer list from all in the same sector
    sector = Issuer.objects.get(
        pk=issuer_id).gics_sub_industry.industry.industry_group.sector.id
    lei_list = list(Issuer.objects.filter(
        gics_sub_industry__industry__industry_group__sector=sector
    ).values_list('lei', flat=True))

    INPUT = ResultStatement(DB_CONNECTION,
                            lei_list,
                            '2012-12-31',
                            '2017-12-31')

    OUT_DATA = []

    for lei in INPUT.output:
        DATA = AnalyzeCompany(INPUT.output[lei])

        try:
            lei = Issuer.objects.get(lei=lei).short_name
        except Issuer.DoesNotExist:
            pass

        for period in DATA.financial_data.period:
            row = {}

            v = item_value(period, item)

            row.update({'Date': period.generic_information.report_date,
                        'LEI': lei,
                        'Value': v})

            OUT_DATA.append(row)

    labels = ['Date', 'LEI', 'Value']

    # Create a DataFrame of all the values from the db
    df = pd.DataFrame.from_records(OUT_DATA, columns=labels)

    # Pivot the DataFrame to the format expected by the chart tool
    table = df.pivot(index='Date', columns='LEI', values='Value')

    return table
