from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Avg, Count
from django.http import HttpResponse

from .models import Dataset, EquipmentRecord
from .serializers import DatasetSerializer, EquipmentRecordSerializer

import pandas as pd
from reportlab.pdfgen import canvas
import io

class DatasetUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_serializer = DatasetSerializer(data=request.data)
        if file_serializer.is_valid():
            dataset = file_serializer.save()
            
            # Process CSV
            try:
                df = pd.read_csv(dataset.file.path)
                # Expected columns: "Equipment Name,Type,Flowrate,Pressure,Temperature"
                
                records = []
                for _, row in df.iterrows():
                    records.append(EquipmentRecord(
                        dataset=dataset,
                        equipment_name=row['Equipment Name'],
                        equipment_type=row['Type'],
                        flowrate=row['Flowrate'],
                        pressure=row['Pressure'],
                        temperature=row['Temperature']
                    ))
                EquipmentRecord.objects.bulk_create(records)
                
                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                dataset.delete()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DatasetListView(generics.ListAPIView):
    queryset = Dataset.objects.all().order_by('-uploaded_at')
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

class DatasetRecordsView(generics.ListAPIView):
    serializer_class = EquipmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        dataset_id = self.kwargs['id']
        return EquipmentRecord.objects.filter(dataset_id=dataset_id)

class DatasetStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        records = EquipmentRecord.objects.filter(dataset_id=id)
        if not records.exists():
             return Response({"error": "Dataset not found or empty"}, status=404)
        
        total_count = records.count()
        avg_flow = records.aggregate(Avg('flowrate'))['flowrate__avg']
        avg_press = records.aggregate(Avg('pressure'))['pressure__avg']
        avg_temp = records.aggregate(Avg('temperature'))['temperature__avg']
        
        type_dist = records.values('equipment_type').annotate(count=Count('equipment_type'))
        dist_dict = {item['equipment_type']: item['count'] for item in type_dist}
        
        return Response({
            "total_count": total_count,
            "average_flowrate": avg_flow,
            "average_pressure": avg_press,
            "average_temperature": avg_temp,
            "type_distribution": dist_dict
        })

class DatasetPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        p.drawString(100, 800, f"Report for Dataset ID {id}")
        
        records = EquipmentRecord.objects.filter(dataset_id=id)
        total = records.count()
        if total == 0:
            p.drawString(100, 780, "No data available.")
        else:
            avg_flow = records.aggregate(Avg('flowrate'))['flowrate__avg']
            avg_press = records.aggregate(Avg('pressure'))['pressure__avg']
            avg_temp = records.aggregate(Avg('temperature'))['temperature__avg']
            
            p.drawString(100, 760, f"Total Records: {total}")
            p.drawString(100, 740, f"Avg Flowrate: {avg_flow:.2f}")
            p.drawString(100, 720, f"Avg Pressure: {avg_press:.2f}")
            p.drawString(100, 700, f"Avg Temperature: {avg_temp:.2f}")
            
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
