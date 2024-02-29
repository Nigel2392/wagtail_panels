wagtail_panels
================

A collection of useful panels to be used for your Wagtail snippets.

**Features:**
   * Buttons
      * Download a file by providing the attribute name
      * Any callback which takes an instance ID and a request to return a URL.
      * Any URL.
   * Reading time panel


Quick start
-----------

1. Add 'wagtail_panels' to your INSTALLED_APPS setting like this:

   ```
   INSTALLED_APPS = [
   ...,
   'wagtail_panels',
   ]
   ```

Example of buttons
------------------

```python
from wagtail_panels.panels import DownloadButton, AnchorTag, ButtonPanel

...

class MySnippet(models.Model):
      file = models.FileField(upload_to="files")

      panels = [
         ButtonPanel([
             DownloadButton(
                 _("Download File"),
                 "file",
                 classname="button",
             ),
             AnchorTag(
                 _("Recover"),
                 lambda request, instance: \
                     reverse_lazy("my_view", kwargs={"pk": instance.pk}),
                 classname="button no",
                 HIDE_ON_CREATE=True,
             )
         ]),
      ]
```

Example of reading time panel
-----------------------------

```python
from wagtail_panels.models import (
    PageReadingTimeMixin,
)
from wagtail_panels.panels import (
    ReadingTimePanel,
)


class MyPage(PageReadingTimeMixin, Page):
    content_panels = Page.content_panels + [
        ReadingTimePanel(),
    ]
```
