from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models
from app.tasks import send_mail
from users.models import User


class EmailLeadCampaignQuerySet(DefaultQuerySet):
    def with_lead_count(self):
        return self.annotate(lead_count=Count('leadcampaignlogentry'))


class EmailLeadMagnetCampaign(TimestampedModel):
    objects = EmailLeadCampaignQuerySet.as_manager()  # type: EmailLeadCampaignQuerySet

    name = models.CharField(_('Name'), max_length=32)
    slug = models.SlugField(unique=True)

    template_id = models.CharField(_('Letter template id'), max_length=255, help_text=_('Will be sent upon lead registration'))

    class Meta:
        verbose_name = _('Email Lead Magnet Campaign')
        verbose_name_plural = _('Email Lead Magnet Campaigns')

    def execute(self, user: User):
        send_mail.delay(
            to=user.email,
            template_id=self.template_id,
            ctx={
                'campaign_name': self.name,
                'firstname': user.first_name,
                'lastname': user.last_name,
            },
        )


class LeadCampaignLogEntry(TimestampedModel):
    campaign = models.ForeignKey(EmailLeadMagnetCampaign, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)