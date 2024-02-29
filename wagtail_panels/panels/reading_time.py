from django.utils.translation import gettext_lazy
from wagtail.admin.panels import Panel
from wagtail.admin.ui.side_panels import BaseSidePanel


class ReadingTimePanel(Panel):

    class SidePanel(BaseSidePanel):
        class SidePanelToggle(BaseSidePanel.SidePanelToggle):
            aria_label = gettext_lazy("Toggle reading time panel")
            icon_name = "rotate"
    
        name = "wagtail_panels_reading_time"
        title = gettext_lazy("Reading Time")
        template_name = "wagtail_panels/panels/reading_time/reading_time.html"
        order = 250
    
        def get_context_data(self, parent_context):
            context = super().get_context_data(parent_context)
            context["instance"] = self.object
            return context

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_panels/panels/reading_time/reading_time.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["instance"] = self.instance
            context["request"] = self.request
            return context

        class Media:
            css = {
                "all": ("wagtail_panels/panels/reading_time/reading_time.css",)
            }
            js = ("wagtail_panels/panels/reading_time/reading_time.js",)

