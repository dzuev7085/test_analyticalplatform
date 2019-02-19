import diff_match_patch
from django.views.generic.detail import DetailView

from rating_process.models.rating_decision import RatingDecision


def diff_helper(A, B):

    # create a diff_match_patch object
    dmp = diff_match_patch.diff_match_patch()

    # Depending on the kind of text you work with, in term of overall length
    # and complexity, you may want to extend (or here suppress) the
    # time_out feature
    dmp.Diff_Timeout = 0  # or some other value, default is 1.0 seconds

    # All 'diff' jobs start with invoking diff_main()
    diffs = dmp.diff_main(A, B)

    # diff_cleanupSemantic() is used to make the diffs
    #  array more "human" readable
    dmp.diff_cleanupSemantic(diffs)

    # and if you want the results as some ready to display HMTL snippet
    return dmp.diff_prettyHtml(diffs)


class EditorDetailView(DetailView):  # pylint: disable=too-many-ancestors

    model = RatingDecision
    template_name = 'test.html'  # Specify your own template name/location

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        issuer_A = "This is a very good company with a can-do attitbute and profitable margins, which can be attributed to a high profit margin. Listed in Oslo and with 10,000 employees spread globally, this is a key player in the nordic market."  # noqa E501 pylint: disable=line-too-long
        issuer_B = "This is a good company with a can-do attitbute and profitable margins, which can be attributed to a stronger than average profit margin. Listed in Oslo and with 10,000 employees spread globally, this is a key player in the nordic market."  # noqa E501 pylint: disable=line-too-long

        issuer = {
            'finale': issuer_B,
            'diff': diff_helper(issuer_A, issuer_B)
        }

        rating_rationale_A = """Our preliminary 'BB-'rating on NP3 reflects its limited size compared to peers, relatively short operational track record of seven years, a less liquid property portfolio in non-prime locations primarily in tier-2 location in regional Swedish cities, relatively aggressive growth strategy, and a somewhat short debt maturity profile and interest fixing term of 2.5 years  and 1.5 years respectively. The restricting factors are to some extent offset by the strong market fundamentals and outlook for Sweden in general, as well as in the areas of northern Sweden that NP3 operates in, with solid economic and population growth along with low interest rates. Good tenant diversity and regional diversification, as well as solid cash flow generation are also factor supporting the rating. Due to NP3's large share of secured bank funding, we rate the proposed bonds one notch lower than the issuer, i.e. 'B+'.  The preliminary rating will be finalized only upon completion of the proposed bond issuance, as well as our receipt and review of final transaction documents, which should not deviate materially from the proposed material."""  # noqa E501 pylint: disable=line-too-long
        rating_rationale_B = """Our 'BB-'rating on NP3 reflects its limited size compared to peers, relatively short operational track record of seven years, a less liquid property portfolio in non-prime locations primarily in tier-2 location in regional Swedish cities, aggressive growth strategy, and a somewhat short debt maturity profile and interest fixing term of 2.5 years and 1.5 years respectively. The restricting factors are to some extent offset by the market fundamentals and outlook for Sweden in general, as well as in the areas of northern Sweden that NP3 operates in, with solid economic and population growth along with low interest rates. Good tenant diversity and regional diversification, as well as solid cash flow generation are also factor supporting the rating. Due to NP3's large share of secured bank funding, we rate the proposed bonds one notch lower than the issuer, i.e. 'B+'.  The preliminary rating will be finalized only upon completion of the proposed bond issuance, as well as our receipt and review of final transaction documents, which should not deviate materially from the proposed material."""  # noqa E501 pylint: disable=line-too-long

        rating_rationale = {
            'finale': rating_rationale_B,
            'diff': diff_helper(rating_rationale_A, rating_rationale_B)
        }

        outlook_A = "The positive outlook reflects our expectation that NP3\'s asset base will continue to increase, while loan to value (LTV) would remain stable below 60%, trending towards 55%, EBITDA to interest coverage ratio (ICR) remain solid between 3.5-4.0x, and debt to EBITDA around 10x. The positive outlook also reflects our view of a continued favourable economic, low interest rate, environment in Sweden."  # noqa E501 pylint: disable=line-too-long
        outlook_B = "The positive outlook reflects our expectation that NP3\'s asset base will continue to increase, while loan to value (LTV) would remain below 60%, trending towards 55%, EBITDA to interest coverage ratio (ICR) remain solid between 3.5-4.0x, and debt to EBITDA around 10x. The positive outlook also reflects our view of a continued low interest rate environment in Sweden."  # noqa E501 pylint: disable=line-too-long

        outlook = {
            'finale': outlook_B,
            'diff': diff_helper(outlook_A, outlook_B)
        }

        positive_A = "<li> Continued growth and diversification of asset base to a value of more than EUR 750m (SEK 7.3bn) <li> Sustained leverage between 55-60% LTV, ICR 3.5-4.0x <li> Improving the average debt maturity profile to more than 3 years"  # noqa E501 pylint: disable=line-too-long
        positive_B = "<li> Continued growth and diversification of asset base to a value of more than EUR 750m (SEK 7.3bn) <li> Sustained leverage between 55-60% LTV, ICR 3.5-4.0x <li> Improving the debt maturity profile to more than 3 years"  # noqa E501 pylint: disable=line-too-long

        positive_drivers = {
            'finale': positive_B,
            'diff': diff_helper(positive_A, positive_B)
        }

        negative_A = "<li>LTV rises to more than 60% as a result of a more aggressive growth policy or rapidly falling asset values<li>Weakening economic fundamentals in Sweden, or NP3\'s core operating regions<li>Interest coverage fall below 2.5x • Increased reliance on short term debt"  # noqa E501 pylint: disable=line-too-long
        negative_B = "<li>LTV rises to more than 60% as a result of a more aggressive growth policy or rapidly falling asset values<li>Weakening economic fundamentals in Sweden, or NP3\'s core operating regions<li>Interest coverage collapse below 2.5x • Increased reliance on short term debt"  # noqa E501 pylint: disable=line-too-long

        negative_drivers = {
            'finale': negative_B,
            'diff': diff_helper(negative_A, negative_B)
        }

        context['issuer'] = issuer
        context['rating_rationale'] = rating_rationale
        context['outlook'] = outlook
        context['positive_drivers'] = positive_drivers
        context['negative_drivers'] = negative_drivers

        return context
