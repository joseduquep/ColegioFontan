from django.contrib import admin
from .models import Student, Attendance
# Register your models here.

class studentAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'block', 'date', 'status', 'marked_by', 'marked_at']
    list_filter = ['date', 'status', 'block__workshop']
    search_fields = ['student__name', 'student__lastname']
    ordering = ['-date', 'block__block_number']
    readonly_fields = ['marked_at']

admin.site.register(Student, studentAdmin)
admin.site.register(Attendance, AttendanceAdmin)