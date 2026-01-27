from django.db import models
import os

from django.contrib.auth.models import User

class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep only last 5
        # Keep only last 5 FOR THIS USER
        # Note: 'self.user' might be not set if not handled in view correctly yet, but default=1 helps.
        if self.user:
            ids_to_keep = list(Dataset.objects.filter(user=self.user).order_by('-uploaded_at')[:5].values_list('id', flat=True))
            if Dataset.objects.filter(user=self.user).count() > 5:
                 to_delete = Dataset.objects.filter(user=self.user).exclude(id__in=ids_to_keep)
                 for ds in to_delete:
                     ds.file.delete()
                     ds.delete()

class EquipmentRecord(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100) # 'Type' in CSV
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
