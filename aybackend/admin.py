from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import Count
from django.http import HttpResponse
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from import_export import resources
from aybackend.models import Event, Registration
from import_export.admin import ImportExportModelAdmin, ExportMixin
from admin_views.admin import AdminViews



# Register your models here.

class RegistrationExporterResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = ('name','mob_number','college','event__name','event__reg_cost','email','time_registered','source')
        export_order = ('name', 'mob_number', 'college', 'event__name', 'event__reg_cost', 'email', 'time_registered', 'source')

class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = (
        'name', 'mob_number', 'college', 'event__name', 'event__reg_cost', 'email', 'time_registered', 'source')

    def get_export_headers(self):
        headers = []
        for field in self.get_fields():
            model_fields = self.Meta.model._meta.get_fields()
            header = next((x.verbose_name for x in model_fields if x.name == field.column_name), field.column_name)
            headers.append(header)
        return headers


class EventAdmin(ImportExportModelAdmin):
    list_display = ('name','type','venue', 'when', 'primary_coord_name', 'primary_coord_contact', 'no_registered')

    def get_queryset(self,request):
        qs = super(EventAdmin,self).get_queryset(request)
        return qs.annotate(no_regd=Count('registration'))

    def no_registered(self,obj):
        return obj.no_regd
    no_registered.short_description = "Number of Registrations"
    no_registered.admin_order_field = 'no_regd'

class RegistrationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RegistrationResource
    list_display = ('name', 'get_event_name', 'mob_number', 'college','email')
    search_fields = ['name', 'event__name']
    list_filter = [('college', DropdownFilter), ('event__name', DropdownFilter)]



    # admin_views = (
    #     ('Export Registrations to Excel Sheet', 'export_xlsx')
    # )
    #
    # def export_xslx(self, *args, **kwargs):
    #     exported = RegistrationExporterResource().export().xlsx
    #     response = HttpResponse(exported, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #     response['Content-Disposition'] = 'attachment; filename = "export_ayframework.xlsx"'
    #     return response

    def get_event_name(self, obj):
            return obj.event.name
    get_event_name.short_description = 'Event Name'
    get_event_name.admin_order_field = 'event__name'


# class DirectExportAdmin(AdminViews):
#     admin_views = ('Export Registrations to Excel Sheet', 'export_xlsx')
#
#     def export_xslx(self, *args, **kwargs):
#         exported = RegistrationExporterResource().export().xlsx
#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename = "export_ayframework.xlsx"'
#         return response


admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
#admin.site.unregister(User)
#admin.site.unregister(Group)
# admin.site.register(DirectExportAdmin)