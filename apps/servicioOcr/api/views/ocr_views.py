from concurrent.futures import thread
from rest_framework import viewsets
from apps.servicioOcr.api.serializers.ocr_serializer import ocrExtractSerializer
from rest_framework.response import Response
from rest_framework import status
import threading
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import gc
from apps.servicioOcr.util import normalisarNameDocument,extraerOcr

class FileOcrViewSet(viewsets.GenericViewSet):
    serializer_class = ocrExtractSerializer
    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            ruta = settings.MEDIA_ROOT+'files/'
            fs = FileSystemStorage(location=ruta)
            nameFile = normalisarNameDocument(request.FILES['document'].name)
            file = fs.save(nameFile,request.FILES['document'])
            fileurl =fs.get_valid_name(file)
            #file = request.FILES['document']

            print(fileurl + " guardado!")
            
            '''t = newThread("Thread "+ serializer.validated_data['slug'], 1,fileurl,serializer.validated_data['slug'])
            t.start()
            t.join()'''
            print(f'Active Threads: {threading.active_count()}')
            t = threading.Thread(target=extraerOcr,args=(fileurl,serializer.validated_data['slug'],))
            t.start()
            '''threads = list()
            threading_text = threading.Thread(target=extraerOcr,args=(fileurl,serializer.validated_data['slug'],))
            threads.append(threading_text)
            threading_text.start()
            
            
            for index, thread in enumerate(threads):
                thread.join()'''

            print(f'Active Threads: {threading.active_count()}')
            del ruta
            del fs
            del nameFile
            del file
            del fileurl
            del serializer
            gc.collect()
            return Response({"mensaje":"Contenido extraido correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)