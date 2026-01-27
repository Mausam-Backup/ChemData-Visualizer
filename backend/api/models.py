from django.db import models
import os

class Dataset(models.Model):
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep only last 5
        ids_to_keep = list(Dataset.objects.order_by('-uploaded_at')[:5].values_list('id', flat=True))
        if Dataset.objects.count() > 5:
             # Delete datasets not in the keep list
             # Note: logic slightly adjusted to ensure we don't delete new one if it's the 6th before sort?
             # actually, saving first then checking is safer.
             # ids_to_keep has the 5 most recent.
             to_delete = Dataset.objects.exclude(id__in=ids_to_keep)
             for ds in to_delete:
                 ds.file.delete() # delete file from disk
                 ds.delete()

class EquipmentRecord(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100) # 'Type' in CSV
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
