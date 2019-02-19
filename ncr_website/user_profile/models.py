from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from user_profile.utils import get_full_name
from a_helper.static_database_table.models.country import CountryRegion

from simple_history.models import HistoricalRecords


User.add_to_class("__str__", get_full_name)


class BaseModel(models.Model):
    """BaseModel class."""

    class Meta:
        """Meta class."""
        abstract = True  # specify this model as an Abstract Model
        app_label = 'user_profile'


class Profile(BaseModel):
    """Additional information about a user."""

    # Add version history to the model
    history = HistoricalRecords()

    def __str__(self):
        return '{} located in {}'.format(
            self.full_name_title,
            self.office_location)

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=60)

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered "
                                         "in the format: '+999999999999'. "
                                         "Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex],
                                    max_length=17,
                                    blank=True)  # validators should be a list

    office_location = models.ForeignKey(
        CountryRegion,
        on_delete=models.PROTECT,
        default=166
    )

    @property
    def full_name(self):
        """Returns the person's full name."""
        return '%s %s' % (self.user.first_name, self.user.last_name)

    @property
    def full_name_title(self):
        """Returns the person's full name."""
        return '%s %s, %s' % (self.user.first_name,
                              self.user.last_name,
                              self.title)


class LeadAnalyst(BaseModel):
    """Lead analyst model."""

    # Add version history to the model
    history = HistoricalRecords()

    def __str__(self):
        return '{} is lead analyst starting {} and ending {}'.format(
            self.profile.full_name,
            self.start_date,
            self.end_date
        )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT
    )

    start_date = models.DateField(
        null=False,
        blank=False,
    )

    end_date = models.DateField(
        null=False,
        blank=False,
        default='2099-12-31'
    )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when creating a user."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
