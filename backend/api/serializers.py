from rest_framework import serializers
from .models import Dataset, EquipmentRecord

class EquipmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRecord
        fields = '__all__'

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'file', 'uploaded_at']
