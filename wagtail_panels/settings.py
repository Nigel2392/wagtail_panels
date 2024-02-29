from django.conf import settings


WAGTAIL_PANELS_READING_TIME_WPM = getattr(settings, "WAGTAIL_PANELS_READING_TIME_WPM", 180)


