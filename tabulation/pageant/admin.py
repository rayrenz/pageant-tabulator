from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Candidate, Category, Score, User, Talent, Final
# Register your models here.

class FinalAdmin(admin.ModelAdmin):
    fields = ('candidate', 'rank', 'judge')
    list_display =  fields
admin.site.register(Final, FinalAdmin)

class TalentAdmin(admin.ModelAdmin):
    fields = ('candidate', 'points')
    list_display = ('candidate','points', 'weight')
admin.site.register(Talent, TalentAdmin)

class MyUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
admin.site.register(User, MyUserAdmin)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'name', 'id', 'finalist')
    ordering = ('number',)
admin.site.register(Candidate, CandidateAdmin)

class CategoryAdmin(admin.ModelAdmin):
    fields = ('title', 'name', 'readonly', 'order', 'weight')
    list_display = fields
    prepopulated_fields = {
        'name': ('title',)
    }
    ordering = ('order',)


admin.site.register(Category, CategoryAdmin)

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('category', 'candidate', 'judge', 'points')
    ordering = list_display
    list_filter = ('category', 'judge', 'candidate')
admin.site.register(Score, ScoreAdmin)
