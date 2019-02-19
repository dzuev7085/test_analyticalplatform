"""Task to refresh static data."""
from a_helper.static_database_table.models.country import CountryRegion
from a_helper.static_database_table.models.currency import Currency
from a_helper.static_database_table.models.gics import (
    GICSIndustry,
    GICSIndustryGroup,
    GICSSector,
    GICSSubIndustry,
)
from datalake.static.country import CountryRegion as TCountryRegion
from datalake.static.currency import Currency as TCurrency
from datalake.static.gics import (
    GICSIndustry as TGICSIndustry,
    GICSIndustryGroup as TGICSIndustryGroup,
    GICSSector as TGICSSector,
    GICSSubIndustry as TGICSSubIndustry,
)


def refresh_country_region():
    """Refresh all records in countryregion model."""

    # Delete all records
    TCountryRegion.delete_all_data()

    # Get all objects in static database
    d = CountryRegion.objects.all()

    # Pass all data to insert function
    TCountryRegion.populate_data(d)


def refresh_currency():
    """Refresh all records in currency model."""

    # Delete all records
    TCurrency.delete_all_data()

    # Get all objects in static database
    d = Currency.objects.all()

    # Pass all data to insert function
    TCurrency.populate_data(d)


def refresh_gics():
    """Refresh all records in gics model."""

    # Delete all records
    TGICSIndustry.delete_all_data()
    TGICSIndustryGroup.delete_all_data()
    TGICSSector.delete_all_data()
    TGICSSubIndustry.delete_all_data()

    # Get all objects in static database
    # and pass all data to insert function
    # Sector
    d = GICSSector.objects.all()
    TGICSSector.populate_data(d)

    # Sub industry group
    d = GICSIndustryGroup.objects.all()
    TGICSIndustryGroup.populate_data(d)

    # Sub industry group
    d = GICSIndustry.objects.all()
    TGICSIndustry.populate_data(d)

    # Sub industry group
    d = GICSSubIndustry.objects.all()
    TGICSSubIndustry.populate_data(d)
