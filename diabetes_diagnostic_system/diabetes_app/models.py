from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PredictionLog(models.Model):
    # Personal information (DON'T CHANGE THESE - they're used by your ML model)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    hypertension = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    smoking_history = models.CharField(max_length=20)
    bmi = models.FloatField()
    glucose_level = models.FloatField()

    # Prediction results (DON'T CHANGE THESE)
    prediction = models.BooleanField()
    probability_no_diabetes = models.FloatField()
    probability_diabetes = models.FloatField()
    confidence = models.FloatField()

    # Technical information
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Prediction Log'
        verbose_name_plural = 'Prediction Logs'

    def __str__(self):
        return f"Prediction for {self.gender}, {self.age}y - {self.get_prediction_display()}"

    def get_prediction_display(self):
        return "DIABETES" if self.prediction else "NO DIABETES"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} Profile'


# This linking table connects users to their predictions
class UserPredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction = models.ForeignKey(PredictionLog, on_delete=models.CASCADE)  # Changed from Prediction to PredictionLog
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'prediction']

    def __str__(self):
        return f"{self.user.username} - Prediction {self.prediction.id}"


# Signals to automatically create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()