"""Module to generate a financial statement and relevant credit metrics."""
from pyfindata import (
    AnalyzeCompany,
    ResultStatement
)

from datalake import DB_CONNECTION


def generate_financial_statement(issuer_obj):
    """Renders a financial statement and metrics."""

    try:
        INPUT = ResultStatement(DB_CONNECTION,
                                [issuer_obj.lei],
                                '2012-12-31',
                                '2017-12-31').output

        # Define what items to show in the income statement
        key_credit_metrics = []
        key_financial_metrics = []
        income_statement_items = []
        balance_sheet_items = []
        cash_flow_items = []

        # Key credit metrics
        key_credit_metrics.append(
            {
                'header': 'FFO/Debt',  # used for row header and in chart
                'item_name': 'ratios.ffo_debt',  # value to pick from pyfindata
                'edit': False,  # do we allow edit of the value?
                'format_as': 'percent',  # how to format output
                'format_precision': '0'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'Debt/EBITDA',
                'item_name': 'ratios.debt_ebitda',
                'edit': False,
                'format_as': 'multiplier',
                'format_precision': '0'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'FOCF/Debt',
                'item_name': 'ratios.focf_debt',
                'edit': False,
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'DCF/Debt',
                'item_name': 'ratios.dcf_debt',
                'edit': False,
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'EBITDA/Interest',
                'item_name': 'ratios.ebitda_interest',
                'edit': False,
                'format_as': 'multiplier',
                'format_precision': '1'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'LTV',
                'item_name': 'ratios.ltv',
                'edit': False,
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        key_credit_metrics.append(
            {
                'header': 'Debt / (Debt + Equity)',
                'item_name': 'ratios.debt_debt_equity',
                'edit': False,
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        # Key credit metrics
        key_financial_metrics.append(
            {
                'header': 'Revenue',
                'item_name': 'income_statement.revenue',
                'edit': False,
            }
        )
        key_financial_metrics.append(
            {
                'header': 'Total assets',
                'item_name': 'balance_sheet.total_assets',
                'edit': False,
            }
        )
        key_financial_metrics.append(
            {
                'header': 'EBITDA',
                'item_name': 'income_statement.ebitda',
                'edit': False,
            }
        )
        key_financial_metrics.append(
            {
                'header': 'Debt',
                'item_name': 'calculation_adjustment.adjusted_debt',
                'edit': False,
            }
        )
        key_financial_metrics.append(
            {
                'header': 'FFO',
                'item_name': 'calculation_adjustment.adjusted_ffo',
                'edit': False,
            }
        )
        key_financial_metrics.append(
            {
                'header': 'FOCF',
                'item_name': 'calculation_adjustment.adjusted_focf',
                'edit': False,
            }
        )

        key_financial_metrics.append({'is_blank': True, })

        # Income statement
        income_statement_items.append(
            {
                'header': 'Revenue',
                'item_name': 'income_statement.revenue',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Cost of goods sold (COGS)',
                'item_name': 'income_statement.cogs',
                'edit': True,
                # passed when inserting data to the database
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Gross profit',
                'item_name': 'income_statement.gross_profit',
                'edit': False,
                'tr_class': 'subtotal',  # Custom css to style the row
            }
        )
        income_statement_items.append(
            {
                'header': 'Gross margin',
                'item_name': 'ratios.gross_margin',
                'edit': False,
                'tr_class': 'small_row',
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append(
            {
                'header': 'SG&A',
                'item_name': 'income_statement.sga',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'R & D',
                'item_name': 'income_statement.research_development',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Other operating expenses',
                'item_name': 'income_statement.other_admin_cost',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'EBIT',
                'item_name': 'income_statement.ebit',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        income_statement_items.append(
            {
                'header': 'EBIT margin',
                'item_name': 'ratios.ebit_margin',
                'edit': False,
                'tr_class': 'small_row',
                'format_as': 'percent',
                'format_precision': '0'
            }
        )
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append(
            {
                'header': 'Share of profit from associates and JV\'s',
                'item_name': 'income_statement.share_of_profit_jv',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Change in property value',
                'item_name':
                    'income_statement.revaluation_of_financial_assets',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Change in financial instruments',
                'item_name': 'income_statement.revaluation_of_properties',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append(
            {
                'header': 'Interest cost',
                'item_name': 'income_statement.interest_cost',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Interest income',
                'item_name': 'income_statement.interest_income',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Interest on shareholder loans',
                'item_name': 'income_statement.interest_shareholder_loan',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Other financial cost',
                'item_name': 'income_statement.interest_other',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Pre tax profit',
                'item_name': 'income_statement.pre_tax_profit',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append(
            {
                'header': 'Current tax',
                'item_name': 'income_statement.actual_tax',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Deferred tax',
                'item_name': 'income_statement.deferred_tax',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Net profit',
                'item_name': 'income_statement.net_profit',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append({'is_blank': True, })
        income_statement_items.append(
            {
                'header': 'Depreciation and amortisation',
                'item_name': 'income_statement.depreciation',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'Write-downs and impairments',
                'item_name': 'income_statement.writedowns',
                'edit': True,
                'statement_type': 'income_statement',
            }
        )
        income_statement_items.append(
            {
                'header': 'EBITDA',
                'item_name': 'income_statement.ebitda',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        income_statement_items.append({'is_blank': True, })

        # Balance sheet
        balance_sheet_items.append(
            {
                'header': 'Property, plant & equipment',
                'item_name':
                    'balance_sheet.non_current_assets.'
                    'property_plant_equipment',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Investment properties',
                'item_name':
                    'balance_sheet.non_current_assets.'
                    'investment_properties',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Work in progress',
                'item_name': 'balance_sheet.non_current_assets.wip',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Intangible assets and goodwill',
                'item_name':
                    'balance_sheet.non_current_assets.intangibles',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Investments in associated companies '
                          'and joint ventures',
                'item_name':
                    'balance_sheet.non_current_assets.joint_ventures',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Deferred tax asset',
                'item_name':
                    'balance_sheet.non_current_assets.nca_deferred_tax',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Derivatives Non-current assets',
                'item_name':
                    'balance_sheet.non_current_assets.nca_derivatives',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Long term financial assets',
                'item_name':
                    'balance_sheet.non_current_assets.'
                    'long_term_financial_assets',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Other long term assets',
                'item_name': 'balance_sheet.non_current_assets.nca_other',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Non-current assets',
                'item_name': 'balance_sheet.non_current_assets.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Inventory',
                'item_name': 'balance_sheet.current_assets.inventory',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Trade receivables',
                'item_name': 'balance_sheet.current_assets.receivables',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Short term financial assets',
                'item_name': 'balance_sheet.current_assets.financial_assets',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Derivatives current assets',
                'item_name': 'balance_sheet.current_assets.ca_derivatives',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Assets held for sale',
                'item_name': 'balance_sheet.current_assets.afs',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Other short term assets',
                'item_name': 'balance_sheet.current_assets.ca_other',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Cash and cash equivalents',
                'item_name': 'balance_sheet.current_assets.cash',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Current assets',
                'item_name': 'balance_sheet.current_assets.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Total assets',
                'item_name': 'balance_sheet.total_assets',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Share capital',
                'item_name': 'balance_sheet.equity.share_capital',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Retained earnings',
                'item_name': 'balance_sheet.equity.retained_earnings',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Other equity',
                'item_name': 'balance_sheet.equity.equity_other',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Total equity',
                'item_name': 'balance_sheet.equity.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Long term interest bearing loans',
                'item_name':
                    'balance_sheet.non_current_liabilities.'
                    'ncl_interest_bearing_loans',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Long term interest bearing bonds',
                'item_name':
                    'balance_sheet.non_current_liabilities.'
                    'ncl_interest_bearing_bonds',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Shareholder loans',
                'item_name':
                    'balance_sheet.non_current_liabilities.shareholder_loans',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Pension liabilities',
                'item_name': 'balance_sheet.non_current_liabilities.pensions',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Deferred tax liabilities',
                'item_name':
                    'balance_sheet.non_current_liabilities.ncl_deferred_tax',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Provisions Non-current liabilities',
                'item_name':
                    'balance_sheet.non_current_liabilities.ncl_provisions',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Derivatives Non-current liabilities',
                'item_name':
                    'balance_sheet.non_current_liabilities.ncl_derivatives',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Other long term liabilities',
                'item_name':
                    'balance_sheet.non_current_liabilities.ncl_other',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Non current liabilities',
                'item_name': 'balance_sheet.non_current_liabilities.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Short term interest bearing debt',
                'item_name':
                    'balance_sheet.current_liabilities.'
                    'cl_interest_bearing_loans',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Short term interest bearing bonds',
                'item_name':
                    'balance_sheet.current_liabilities.'
                    'cl_interest_bearing_bonds',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Trade payables',
                'item_name':
                    'balance_sheet.current_liabilities.accounts_payable',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Current tax payable',
                'item_name':
                    'balance_sheet.current_liabilities.tax_payable',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Provisions Current liabilities',
                'item_name':
                    'balance_sheet.current_liabilities.cl_provisions',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Derivatives Non-current liabilities',
                'item_name':
                    'balance_sheet.current_liabilities.cl_derivatives',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Other short term liabilities',
                'item_name': 'balance_sheet.current_liabilities.cl_other',
                'edit': True,
                'statement_type': 'balance_sheet',
            }
        )
        balance_sheet_items.append(
            {
                'header': 'Current liabilities',
                'item_name': 'balance_sheet.current_liabilities.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Total equity and liabilities',
                'item_name': 'balance_sheet.total_equity_and_liabilities',
                'edit': False,
                'tr_class': 'subtotal', })
        balance_sheet_items.append({'is_blank': True, })
        balance_sheet_items.append(
            {
                'header': 'Control row',
                'item_name': 'balance_sheet.balance_difference',
                'edit': False,
                'tr_class': 'small_row', })
        balance_sheet_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Pre tax profit',
                'item_name': 'cash_flow_statement.operations_gross_wc.'
                             'pre_tax_profit',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Depreciation and amortisation',
                'item_name':
                    'cash_flow_statement.operations_gross_wc.'
                    'depreciation_amortisations',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Capital gains',
                'item_name':
                    'cash_flow_statement.operations_gross_wc.capital_gains',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Tax paid',
                'item_name':
                    'cash_flow_statement.operations_gross_wc.tax_paid',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Other items',
                'item_name':
                    'cash_flow_statement.operations_gross_wc.other',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Cash flow before changes in working capital',
                'item_name': 'cash_flow_statement.operations_gross_wc.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Inventory',
                'item_name':
                    'cash_flow_statement.changes_working_capital.inventory',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Operating receivables',
                'item_name':
                    'cash_flow_statement.changes_working_capital.receivables',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Operating liabilities',
                'item_name':
                    'cash_flow_statement.changes_working_capital.liabilities',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Other changes in working capital',
                'item_name':
                    'cash_flow_statement.changes_working_capital.other',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Changes in working capital',
                'item_name':
                    'cash_flow_statement.changes_working_capital.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Operating cash flow',
                'item_name': 'cash_flow_statement.operating_cash_flow',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Investments in property, plant & equipment',
                'item_name':
                    'cash_flow_statement.investing.investment_property',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Sale of property plant & equipment',
                'item_name':
                    'cash_flow_statement.investing.sale_property',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Investments in intangible assets',
                'item_name':
                    'cash_flow_statement.investing.investment_intangible',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Sale of intangible assets',
                'item_name':
                    'cash_flow_statement.investing.sale_intangible',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Acquisition of property',
                'item_name':
                    'cash_flow_statement.investing.aquisition_property',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Sale of property',
                'item_name':
                    'cash_flow_statement.investing.sale_aq_property',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Acquisition of subsidiaries',
                'item_name':
                    'cash_flow_statement.investing.acquisition_subsidiaries',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Divestment of subsidiaries',
                'item_name':
                    'cash_flow_statement.investing.sale_subsidiaries',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Other net investments',
                'item_name': 'cash_flow_statement.investing.other',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Cash flow from investing activities',
                'item_name': 'cash_flow_statement.investing.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Proceeds from equity issuance',
                'item_name': 'cash_flow_statement.financing.equity',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Paid dividends',
                'item_name': 'cash_flow_statement.financing.dividend',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Borrowings',
                'item_name':
                    'cash_flow_statement.financing.borrowing_proceeds',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Repayment of borrowings',
                'item_name':
                    'cash_flow_statement.financing.borrowing_repayment',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Other net financing activities',
                'item_name': 'cash_flow_statement.financing.other',
                'edit': True,
            }
        )
        cash_flow_items.append(
            {
                'header': 'Cash flow from financing activities',
                'item_name': 'cash_flow_statement.financing.total',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )
        cash_flow_items.append({'is_blank': True, })
        cash_flow_items.append(
            {
                'header': 'Cash flow for the year',
                'item_name': 'cash_flow_statement.cash_flow_for_the_year',
                'edit': False,
                'tr_class': 'subtotal',
            }
        )

        financial_statement = {
            'data':
                AnalyzeCompany(
                    INPUT[issuer_obj.lei]).financial_data.period,
            'income_statement_items': income_statement_items,
            'balance_sheet_items': balance_sheet_items,
            'cash_flow_items': cash_flow_items,
            'key_credit_metrics': key_credit_metrics,
            'key_financial_metrics': key_financial_metrics,
        }

    except:  # noqa: E722
        financial_statement = False
        pass

    return financial_statement
