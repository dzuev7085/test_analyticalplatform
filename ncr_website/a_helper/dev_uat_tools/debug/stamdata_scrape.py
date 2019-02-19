from bs4 import BeautifulSoup
from django.db import connection
from decimal import Decimal as D

html = """


<!doctype html>

<html class="ui-user">

<head><meta charset="utf-8" />
	<meta http-equiv="Expires" content="Thu, 07 Jun 2018 13:38:31 GMT">
	<meta http-equiv="X-UA-Compatible" content="IE=edge, chrome=1" /><meta id="ctl00_viewport" name="viewport" content="width=device-width" /><meta name="description" content="Stamdata delivers reference data for Nordic debt securities. The data includes detailed information on i.a. bonds, certificates and structured debt securities issued by governments, municipals, banks and corporate borrowers. Reference data is available either through a web-interface or as a daily data-file used for automatic import into financial systems." /><title>
	
    NP3 Fastigheter AB (publ) - Stamdata
    
</title>

	<link rel="shortcut icon" type="image/png" href="/Content/next/assets/img/favicon.png">
	<link rel="apple-touch-icon" href="/Content/next/assets/img/icon.png">
    <meta name="application-name" content="Stamdata" /><meta name="msapplication-TileColor" content="#031b39" /><link href="/content/next/vendor/ionicons/css/ionicons.min.css" rel="stylesheet" type="text/css" media="all"/>
<link href="/content/next/assets/css/animations.css" rel="stylesheet" type="text/css" media="all"/>
<link href="/content/next/assets/css/main.css" rel="stylesheet" type="text/css" media="screen"/>
<link href="/content/next/assets/css/print.css" rel="stylesheet" type="text/css" media="print"/>
<link href="/content/toastr.min.css" rel="stylesheet" type="text/css" media="all"/>
</head>

<body>



<header>
    
    <div class="overlay hide" data-module="toggle" data-class="ui-menu"></div>
    
    <h1><a href="/">Stamdata</a></h1>
    
    <a class="first noprint" href="/" data-module="toggle" data-class="ui-menu"><i class="icon ion-navicon"></i></a>
    
    <a class="last noprint" href="/">
        
            <i class="icon ion-ios-search-strong"></i>
        
    </a>

</header>


<main>
    

<aside class="user">

    <div class="top">
        <h1>
            <a href="/">Stamdata</a>
        </h1>
        <form id="searchform" method="post" action="/SearchAll">
            <div class="input text">
                <div class="first"><i class="icon ion-ios-search-strong"></i></div>
                <input type="text" name="searchText" autocomplete="off" placeholder="Search Stamdata...">
            </div>
	    </form>
    </div>

    <ul>
        <li><a href="/"><i class="icon ion-ios-arrow-forward"></i> <span>Home</span></a></li>

        <li class="auth"><a href="/Search.mvc/NewDeals"><i class="icon ion-ios-arrow-forward"></i> <span>Latest deals</span></a></li>
        <li class="auth">
            <a href="/LeagueTable/Managers/Year"><i class="icon ion-ios-arrow-forward"></i> <span>League tables</span></a>
            <ul class="disabled">
                <li><a href="/LeagueTable/Managers/Year?year=2018">Yearly Managers</a></li>
                <li><a href="/LeagueTable/Managers/Month">Monthly Managers</a></li>
                <li><a href="/LeagueTable/Statistics/Basic">Basic Statistics</a></li>
                <li><a href="/LeagueTable/Statistics/Complete/Bonds">Complete Statistics</a></li>
                
            </ul>
        </li>
        <li class="auth"><a href="/Statistics/Issue"><i class="icon ion-ios-arrow-forward"></i> <span>Statistics</span></a></li>
    </ul>
    
    
    
    <h2>Search</h2>
    <ul>
        <li class="auth"><a href="/Issuers"><i class="icon ion-ios-arrow-forward"></i> <span>Issuers</span></a></li>
        <li class="auth"><a href="/Issues"><i class="icon ion-ios-arrow-forward"></i> <span>Securities</span></a></li>
        <li class="auth"><a href="/News"><i class="icon ion-ios-arrow-forward"></i> <span>Market news</span></a></li>
    </ul> 

    
        
        <h2>Account</h2>
        <ul>
            <li><a href="/Subscription.mvc/Index">
                <i class="icon ion-ios-arrow-forward"></i> 
                <span>My account</span>
            </a></li>
            <li><a href="/Settings.mvc/Settings">
                <i class="icon ion-ios-arrow-forward"></i> 
                <span>Markets and formats</span>
            </a></li>
            <li><a href="/FormsAuthentication.mvc/Logout">
                <i class="icon ion-ios-arrow-forward"></i> 
                <span>Sign out</span>
            </a></li>
        </ul>
        
        
            <div class="favorites hide">
                <h2>Favorites</h2>
                <ul>
                    
                </ul>
            </div>
        
    
    <h2>Tools</h2>
    <ul>

        <li> <a href="/Calculator"><i class="icon ion-ios-arrow-forward"></i> <span>Calculators</span></a> </li>

    </ul>

</aside>

    <article>
        

    

        <h1 class="first">
            <span>NP3 Fastigheter AB (publ)</span>
        </h1>
    
    
        

        <div class="grid" data-module="truncate" data-selector="em, span">
            <div class="row">

                <div class="cell cell-content">
                    <h3>Issuer details</h3>
                    <ul class="details">
                        <li class="emph">
                            <span>Name</span>
                            <em>NP3 Fastigheter AB (publ)</em>
                        </li>
                        <li class="emph">
                            <span>Issuer's reg. number</span>
                            <em>SE-556749-1963</em>
                        </li>
                        <li>
                            <span>LEI</span>
                            <em>549300MGVITW8GYJHZ50</em>
                        </li>
                        <li>
                            <span>Contact info</span>
                            <em><a href="" target="_blank"></a></em>
                        </li>
                        
                            <li>
                                <span>Ratings</span>
                                <em>N/A</em>
                            </li>
                        
                    </ul>
                </div>

                <div class="cell cell-content">
                    <h3>Classification</h3>
                    <ul class="details">
                        <li class="emph">
                            <span>Region</span>
                            <em>Sweden (9106/SE)</em>
                        </li>
                        
                            <li>
                                <span>Sector Code (Insect 2000)</span>
                                <em>Non-financial corporations (110)</em>
                            </li>
                        
                        <li>
                            <span>Indstr. Class (NACE)</span>
                            <em>Man. real estate fee/contract basis (68320)</em>
                        </li>
                        <li>
                            <span>Industry</span>
                            <em>Real Estate, Commercial</em>
                        </li>
                        <li>
                            <span>Business</span>
                            <em>Private enterprise</em>
                        </li>
                    </ul>
                </div>

            </div>
        </div>

    
        

            <h1>
                Bonds, Bills and Commercial Papers

                <a 
                    href="#"
                    class="action hide"
                    data-module="toggle"
                    data-hide="true"
                    data-target=".matured">
                    <i class="icon ion-checkmark"></i>
                    Show matured
                </a>
            </h1>

            <table data-module="table truncate" data-sort="0 asc" data-selector="span, a" data-max="26">
                <thead>
                    <tr>
                        <th>ISIN</th>
                        <th>Name</th>
                        <th>Ticker</th>
                        <th class="res-2">Disbursment</th>
                        <th class="res-1">Maturity</th>
                        <th class="res-3">Interest</th>
                        <th class="last">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    
                        <tr class="">
                            <td  class="table-width10">
                                <i class="icon ion-document"></i> 
                                <a href="/Issue/SE0007491253">SE0007491253</a>
                            </td>
                            <td class="table-width10">
                                <a href="/Issue/SE0007491253">NP3 Fastigheter AB  15/18 FRN C</a>
                            </td>
                            <td>
                                NP3 101
                            </td>
                            <td class="res-2" data-order="2015-09-10 00:00:00Z">
                                <em class="date">2015-09-10</em>
                            </td>
                            <td class="res-1" data-order="2018-10-15 00:00:00Z">
                                <em class="date">2018-10-15</em>
                            </td>
                            <td class="res-3">
                                FRN
                            </td>
                            <td class="last" data-order="425000000,0000">
                                
                                    <em class="amount">425 000 000 SEK</em>
                                
                            </td>                   
                        </tr>
                    
                        <tr class="">
                            <td  class="table-width10">
                                <i class="icon ion-document"></i> 
                                <a href="/Issue/SE0009805054">SE0009805054</a>
                            </td>
                            <td class="table-width10">
                                <a href="/Issue/SE0009805054">NP3 Fastigheter AB  17/21 FRN C</a>
                            </td>
                            <td>
                                NP3 102
                            </td>
                            <td class="res-2" data-order="2017-04-13 00:00:00Z">
                                <em class="date">2017-04-13</em>
                            </td>
                            <td class="res-1" data-order="2021-04-13 00:00:00Z">
                                <em class="date">2021-04-13</em>
                            </td>
                            <td class="res-3">
                                FRN
                            </td>
                            <td class="last" data-order="600000000,0000">
                                
                                    <em class="amount">600 000 000 SEK</em>
                                
                            </td>                   
                        </tr>
                    
                        <tr class="">
                            <td  class="table-width10">
                                <i class="icon ion-document"></i> 
                                <a href="/Issue/SE0011205665">SE0011205665</a>
                            </td>
                            <td class="table-width10">
                                <a href="/Issue/SE0011205665">NP3 Fastigheter AB  18/22 FRN C</a>
                            </td>
                            <td>
                                &mdash;
                            </td>
                            <td class="res-2" data-order="2018-05-23 00:00:00Z">
                                <em class="date">2018-05-23</em>
                            </td>
                            <td class="res-1" data-order="2022-05-23 00:00:00Z">
                                <em class="date">2022-05-23</em>
                            </td>
                            <td class="res-3">
                                FRN
                            </td>
                            <td class="last" data-order="375000000,0000">
                                
                                    <em class="amount">375 000 000 SEK</em>
                                
                            </td>                   
                        </tr>
                    
                </tbody>
            </table>  

            <div class="tfoot">
                Sum:
                1 400 000 000
                SEK
            </div>
        
        
        
        
            
            
        
        

<div class="clear"></div>

<footer>
    &copy; 2018 Stamdata, 
    a <a href="http://www.nordictrustee.com">Nordic Trustee</a> Company 
    <div>
        <a href="/Disclaimer.mvc">Disclaimer</a> 
        <a href='/Sitemap'>Sitemap</a>
        <a href="/Home.mvc/ContactUs">Contact Us</a>
    </div>
</footer>
    </article>
</main>
    
<script src="/content/next/vendor/jquery/jquery.js"></script>
<script src="/content/next/vendor/jquery/jquery.browser.js"></script>
<script src="/content/next/vendor/underscore/underscore.js"></script>
<script src="/content/next/vendor/datatables/jquery.dataTables.min.js"></script>
<script src="/content/next/vendor/moment/moment.js"></script>
<script src="/content/next/vendor/retina/retina.min.js"></script>
<script src="/content/next/assets/js/helpers/jquery.js"></script>
<script src="/content/next/assets/js/main.js"></script>
<script src="/content/next/assets/js/modules/favorite.js"></script>
<script src="/content/next/assets/js/modules/marketsize.js"></script>
<script src="/content/next/assets/js/modules/refresh.js"></script>
<script src="/content/next/assets/js/modules/register.js"></script>
<script src="/content/next/assets/js/modules/search.js"></script>
<script src="/content/next/assets/js/modules/submit.js"></script>
<script src="/content/next/assets/js/modules/table.js"></script>
<script src="/content/next/assets/js/modules/toggle.js"></script>
<script src="/content/next/assets/js/modules/truncate.js"></script>
<script src="/content/next/vendor/toastr/toastr.min.js"></script>

<script type="text/javascript">
    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-22989974-3']);
    _gaq.push(['_trackPageview']);

    (function () {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
    })();
</script>

</body>
</html>


"""

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

                    cell_value = cell_value[:-3].strip().replace(' ', '')
                else:
                    output.append('')
                    cell_value = ''

            output.append(cell_value)

        listoflists.append(output)

except:
    pass


from pprint import pprint
pprint(listoflists)


issuer_id = 6
for row in listoflists:

    isin = row[0]
    name = row[1]
    ticker = row[2]
    disbursement = row[3]

    maturity = row[4]
    interest = row[5]

    currency = row[6]

    if len(currency) > 0:
#        try:
#            currency = Currency.objects.get(currency_code_alpha_3=currency)
#        except:
#            currency = None
        currency = 1
    else:
        currency = None

    amount = row[7]

    if len(amount) > 0:
        amount = D(amount)
    else:
        amount = None

    query = "INSERT INTO issue_issue (issuer_id, isin, name, ticker, disbursement, maturity, interest, currency_id, amount) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
            "ON CONFLICT (isin) DO UPDATE SET " \
            "name=EXCLUDED.name, ticker=EXCLUDED.ticker, disbursement=EXCLUDED.disbursement, maturity=EXCLUDED.maturity," \
            "interest=EXCLUDED.interest, currency_id=EXCLUDED.currency_id, amount=EXCLUDED.amount" % (issuer_id, isin, name, ticker,
                                                                                                  disbursement,
                                                                                                  maturity, interest,
                                                                                                  currency, amount)

    print(query)



def my_custom_sql(self):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])

    return row
