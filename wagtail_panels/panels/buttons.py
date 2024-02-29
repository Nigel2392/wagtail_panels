from typing import Union
from collections import OrderedDict
from django.urls import reverse
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from wagtail.admin.panels import Panel


class FileDownloadPanel(Panel):
    def __init__(self, file_fields: Union[list, str], permissions=None, *args, **kwargs):
        if isinstance(file_fields, str):
            file_fields = [file_fields]
        self.file_fields = tuple(file_fields)
        self.permissions = permissions
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs["file_fields"] = self.file_fields
        kwargs["permissions"] = self.permissions
        return kwargs

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_panels/panels/buttons/download_panel.html"
        
        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["content_type"] = ContentType.objects.get_for_model(self.instance)
            context["instance"] = self.instance
            context["model_fields"] = OrderedDict(
                (field, {
                    "has_file": not not getattr(self.instance, field),
                    "verbose_name": self.instance._meta.get_field(field).verbose_name,
                })
                for field in self.panel.file_fields
            )
            return context
        
        def is_shown(self):
            if not super().is_shown():
                return False
            
            if self.panel.permissions is None:
                return True
            
            if callable(self.panel.permissions):
                return self.panel.permissions(self.instance)
            
            if isinstance(self.panel.permissions, str):
                return self.request.user.has_perm(self.panel.permissions)
            
            if isinstance(self.panel.permissions, (list, tuple)):
                return self.request.user.has_perms(self.panel.permissions)
            
            raise TypeError("Permissions must be None, a string, a list or a tuple.")
        

class BoundButton:
    template_name = "wagtail_panels/panels/buttons/button.html"

    def __init__(self, request, instance, panel, button):
        self.request = request
        self.instance = instance
        self.panel = panel
        self.button: BaseButton = button

    def get_tag(self):
        return self.button.TAG

    def get_url(self):
        return self.button.get_url(self.request, self.instance)

    def get_classes(self):
        return self.button.get_classes(self.request, self.instance)

    def get_attributes(self):
        return self.button.get_attributes(self.request, self.instance)

    def get_text(self):
        return self.button.get_text(self.request, self.instance)

    def get_context(self):
        return {
            "self": self,
        }

    def render(self, context=None):
        if self.button.HIDE_ON_CREATE:
            if not self.instance.pk:
                return ""

        template = get_template(self.template_name)
        
        if context is None:
            context = self.get_context()
        else:
            if hasattr(context, "flatten"):
                context = context.flatten()
            context.update(self.get_context())

        return template.render(context)


class BaseButton:
    TAG = "a"
    HIDE_ON_CREATE = False

    BoundButton = BoundButton

    def __init__(self, text: str, url: str, classname="button", **kwargs):
        self.text = text
        self.url = url
        self.classname = classname
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, bound_panel: Panel.BoundPanel):
        return self.BoundButton(
            bound_panel.request,
            bound_panel.instance,
            bound_panel.panel,
            self,
        )
    
    def get_url(self, request, instance):
        if callable(self.url):
            return self.url(request, instance)
        return self.url

    def get_classes(self, request, instance):
        if callable(self.classname):
            return self.classname(request, instance)
        return self.classname

    def get_attributes(self, request, instance):
        return {
            "href": self.get_url(request, instance),
            "class": self.get_classes(request, instance),
        }

    def get_text(self, request, instance):
        return self.text

    def deconstruct(self):
        return (
            self.__class__.__qualname__,
            [],
            {
                "text": self.text,
                "url": self.url,
                "classname": self.classname,
            }
        )


class AnchorTag(BaseButton):
    TAG = "a"


class DownloadButton(AnchorTag):
    HIDE_ON_CREATE = True

    def __init__(self, text: str, file_field_attr: str, *args, **kwargs):
        self.file_field_attr = file_field_attr
        super().__init__(text, "", *args, **kwargs)

    def get_url(self, request, instance):
        return reverse("download_panel:panel", kwargs={
            "content_type_pk": ContentType.objects.get_for_model(instance).pk,
            "object_pk": instance.pk,
            "field_name": self.file_field_attr,
        })


class Button(BaseButton):
    TAG = "button"

    def __init__(self, text: str, id="", classname="button button-small"):
        self.id = id
        super().__init__(text, "", classname)

    def get_url(self, request, instance):
        return "#"
    
    def get_id(self, request, instance):
        if callable(self.id):
            return self.id(request, instance)
        return self.id

    def get_attributes(self, request, instance):
        return {
            "id": self.get_id(request, instance),
            "class": self.get_classes(request, instance),
        }


class ButtonPanel(Panel):
    def __init__(self, buttons = (), *args, **kwargs):
        if not isinstance(buttons, (list, tuple)):
            buttons = (buttons,)
        self.buttons: tuple[Button] = buttons
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs["buttons"] = self.buttons
        return kwargs

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_panels/panels/buttons/buttons.html"
        
        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["buttons"] = [button(self) for button in self.panel.buttons]
            return context
        
        def is_shown(self):
            if not super().is_shown():
                return False
            
            return True

