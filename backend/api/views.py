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
            # Attach user
            dataset = file_serializer.save(user=request.user)
            
            
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
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user).order_by('-uploaded_at')

class GlobalDatasetListView(generics.ListAPIView):
    queryset = Dataset.objects.all().order_by('-uploaded_at')
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

class DatasetRecordsView(generics.ListAPIView):
    serializer_class = EquipmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    
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
        
        # --- HEADER ---
        p.setFont("Helvetica-Bold", 18)
        p.setFillColorRGB(0.2, 0.2, 0.6) # Indigo-ish
        p.drawString(50, 800, "ChemData Visualizer Report")
        
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0.5, 0.5, 0.5)
        p.drawString(50, 785, f"Dataset Report ID: {id}")
        p.line(50, 775, 550, 775)
        
        # --- SUMMARY SECTION ---
        records = EquipmentRecord.objects.filter(dataset_id=id)
        total = records.count()

        if total == 0:
            p.drawString(50, 750, "No data available in this dataset.")
        else:
            avg_flow = records.aggregate(Avg('flowrate'))['flowrate__avg']
            avg_press = records.aggregate(Avg('pressure'))['pressure__avg']
            avg_temp = records.aggregate(Avg('temperature'))['temperature__avg']
            
            p.setFont("Helvetica-Bold", 12)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(50, 750, "Summary Metrics")
            
            p.setFont("Helvetica", 10)
            p.drawString(50, 730, f"Total Individual Records: {total}")
            
            # Simple Metrics Box
            p.rect(50, 680, 500, 40, stroke=1, fill=0)
            p.line(216, 680, 216, 720)
            p.line(382, 680, 382, 720)
            
            p.setFont("Helvetica-Bold", 10)
            p.drawCentredString(133, 705, "Avg Flowrate")
            p.drawCentredString(299, 705, "Avg Pressure")
            p.drawCentredString(465, 705, "Avg Temp")
            
            p.setFont("Helvetica", 10)
            p.drawCentredString(133, 690, f"{avg_flow:.2f}")
            p.drawCentredString(299, 690, f"{avg_press:.2f}")
            p.drawCentredString(465, 690, f"{avg_temp:.2f}")

            # --- DATA TABLE ---
            y = 640
            p.setFont("Helvetica-Bold", 10)
            p.setFillColorRGB(0.2, 0.2, 0.2)
            
            # Table Headers
            p.drawString(50, y, "Equipment Name")
            p.drawString(200, y, "Type")
            p.drawString(300, y, "Flowrate")
            p.drawString(400, y, "Pressure")
            p.drawString(500, y, "Temp")
            
            p.setStrokeColorRGB(0.8, 0.8, 0.8)
            p.line(50, y-5, 550, y-5)
            y -= 25
            
            p.setFont("Helvetica", 9)
            
            for record in records:
                if y < 50:
                    p.showPage()
                    y = 800
                
                p.drawString(50, y, str(record.equipment_name)[:20])
                p.drawString(200, y, str(record.equipment_type))
                p.drawString(300, y, f"{record.flowrate:.2f}")
                p.drawString(400, y, f"{record.pressure:.2f}")
                p.drawString(500, y, f"{record.temperature:.2f}")
                
                # Zebra striping (optional, keeping clean white for print)
                p.line(50, y-5, 550, y-5)
                y -= 20

        p.showPage()
        p.save()
        
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
