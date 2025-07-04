from django.contrib import admin
from med_app.models import *


class DistrictTabularInline(admin.TabularInline):
    model = District
    fk_name = 'city'
    extra = 5


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [DistrictTabularInline]

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city")
    list_filter = ("city",)
    search_fields = ("name",)


@admin.register(MedCard)
class MedCardAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name", "first_name", "surname", "birth_date", "city", "district")
    list_filter = ("city", "district", "birth_date")
    search_fields = ("first_name", "last_name", "surname")


# ------------------------------------------------------------------
class CallQuestionInline(admin.TabularInline):
    model = CallQuestion
    extra = 1

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'operator', 'created_at')
    inlines = [CallQuestionInline]
    search_fields = ('phone_number',)
    readonly_fields = ('created_at',)
    list_display_links = ('phone_number',)

    def save_model(self, request, obj, form, change):
        if not obj.operator:
            obj.operator = request.user
        super().save_model(request, obj, form, change)


class QuestionInline(admin.TabularInline):
    model = Question
    fields = ('question',)
    extra = 1

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('question',)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('med_card', 'visit_time', 'operator', 'reason')
    list_filter = ('visit_time', 'operator')
    search_fields = ('med_card__last_name', 'med_card__first_name', 'reason', 'notes')
    readonly_fields = ('operator', 'created_at')
    fields = ('med_card', 'visit_time', 'reason', 'notes', 'created_at', 'operator')


    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.operator = request.user
        super().save_model(request, obj, form, change)
