from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your model_files here
from django.utils.html import format_html
from .models import PredictionLog


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'age',
        'bmi',
        'glucose_level',
        'prediction_status',
        'confidence',
        'view_details'
    ]

    list_filter = ['prediction', 'timestamp', 'gender']
    search_fields = ['ip_address', 'age', 'bmi', 'glucose_level']
    readonly_fields = ['timestamp', 'ip_address']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Personal Information', {
            'fields': ('gender', 'age')
        }),
        ('Health Metrics', {
            'fields': ('hypertension', 'heart_disease', 'smoking_history', 'bmi', 'glucose_level')
        }),
        ('Prediction Results', {
            'fields': ('prediction', 'probability_no_diabetes', 'probability_diabetes', 'confidence')
        }),
        ('Technical Information', {
            'fields': ('timestamp', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    def prediction_status(self, obj):
        if obj.prediction:
            return format_html('<span style="color: red; font-weight: bold;">DIABETES</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">NO DIABETES</span>')

    prediction_status.short_description = 'Prediction'

    def view_details(self, obj):
        return format_html('<a href="/admin/diabetes_app/predictionlog/{}/change/">View</a>', obj.id)

    view_details.short_description = 'Details'

    # Add some custom actions
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from io import StringIO

        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Age', 'Gender', 'BMI', 'Glucose', 'Prediction', 'Confidence'])

        for obj in queryset:
            writer.writerow([
                obj.timestamp.strftime('%Y-%m-%d %H:%M'),
                obj.age,
                obj.gender,
                obj.bmi,
                obj.glucose_level,
                'DIABETES' if obj.prediction else 'NO DIABETES',
                f"{obj.confidence:.1f}%"
            ])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=prediction_logs.csv'
        return response

    export_as_csv.short_description = "Export selected predictions as CSV"


# Customize the admin site header and title
admin.site.site_header = "Diabetes Diagnostic System Administration"
admin.site.site_title = "Diabetes Diagnostic System"
admin.site.index_title = "Welcome to the Diabetes Diagnostic System Admin Portal"
