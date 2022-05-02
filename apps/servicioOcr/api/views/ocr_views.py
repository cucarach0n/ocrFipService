from rest_framework import viewsets
from apps.servicioOcr.api.serializers.ocr_serializer import ocrExtractSerializer
from rest_framework.response import Response
from rest_framework import status
import threading
import requests
from apps.servicioOcr.util import DocumentoOCR
from decouple import config
from django.core.files.storage import FileSystemStorage
from django.conf import settings
def extraerOcr(file,slug):
    documento = DocumentoOCR(file)
    text = documento.obtenerTexto()

    data = {
        'contenidoOCR': str(text),
        'slug': str(slug)
    }

    res = requests.put(config('URL_SERVER')+'/file/ocrService/'+slug+"/",data=data)
    print(res.text)


class FileOcrViewSet(viewsets.GenericViewSet):
    serializer_class = ocrExtractSerializer
    def list(self,request):
        return Response({"mensaje":"OK!"}, status=status.HTTP_200_OK)
    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            ruta = settings.MEDIA_ROOT+'files/'
            fs = FileSystemStorage(location=ruta)
            file = fs.save(request.FILES['document'].name,request.FILES['document'])
            fileurl =fs.get_valid_name(file)
            print(fileurl)
            threading_text = threading.Thread(target=extraerOcr,args=(fileurl,serializer.validated_data['slug'],))
            threading_text.start()
            return Response({"mensaje":"Contenido extraido correctamente"}, status=status.HTTP_200_OK)