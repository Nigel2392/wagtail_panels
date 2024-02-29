from django.db import models
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _, ngettext
from wagtail.models import Page

import datetime

from ..settings import WAGTAIL_PANELS_READING_TIME_WPM as WPM


WPS = WPM / 60


def estimate_reading_time(text: str) -> float:
    filtered_text = strip_tags(text)
    total_words = len(filtered_text.split())
    return total_words / WPS



class ReadingTimeMixin(models.Model):
    readime_time_fields = []

    _read_time = models.DurationField(
        default=datetime.timedelta(seconds=0),
        editable=False,
    )

    class Meta:
        abstract = True

    def _calculate_reading_time(self, fields = None):
        if fields is None:
            fields = self.readime_time_fields

        total_s = sum([estimate_reading_time(
            str(getattr(self, f))) 
            for f in self.readime_time_fields
        ])

        return datetime.timedelta(seconds=total_s)

    def save(self, *args, **kwargs):
        self._read_time = self._calculate_reading_time()
        super().save(*args, **kwargs)

    @property
    def reading_time(self):
        total_seconds = self._read_time.total_seconds()
        if total_seconds < 60:
            return _("Less than a minute")

        minutes = total_seconds // 60
        return ngettext(
            "%(minutes)d minute",
            "%(minutes)d minutes",
            minutes,
        ) % {"minutes": minutes}


class PageReadingTimeMixin(ReadingTimeMixin, Page):

    def serve_preview(self, request, mode_name):
        
        self._read_time = self._calculate_reading_time()

        if mode_name == "reading_time":
            return JsonResponse({
                "reading_time": self.reading_time,
            }, status=200)

        return super().serve_preview(request, mode_name)

    class Meta:
        abstract = True
        