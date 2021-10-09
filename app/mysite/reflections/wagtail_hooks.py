from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from mysite.reflections.models import DailyReflectionPage


class DailyReflectionModelAdmin(ModelAdmin):
    model = DailyReflectionPage
    menu_label = "Daily Reflections"  # ditch this to use verbose_name_plural from model
    menu_icon = "fa-heartbeat"  # change as required
    list_display = (
        "__str__",
        "title",
        "scripture",
        "live",
        "owner",
    )
    list_filter = ("live",)
    search_fields = ("title", "content", "scripture", "owner")
    list_export = (
        "reflection_date",
        "title",
        "scripture",
        "content",
        "additional_resources",
    )
    list_per_page = 31
    inspect_view_enabled = True


modeladmin_register(DailyReflectionModelAdmin)
