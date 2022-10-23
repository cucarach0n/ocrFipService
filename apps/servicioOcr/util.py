from importlib.resources import open_binary
from opcode import opname
from operator import truediv
import os
import time
from django.conf import settings
from decouple import config
from os import remove
from PIL import Image, ImageFilter
from ocrFipService.settings.base import MEDIA_ROOT
import pytesseract
from pdf2image import convert_from_path,convert_from_bytes
from django.utils.crypto import get_random_string
from apps.servicioOcr.models import File
import platform
import gc
import psutil
import requests
import threading
from django.conf import settings
import tempfile

from decouple import config
os.environ['OMP_THREAD_LIMIT'] = '1'
sistema = platform.system()
if(sistema == "Windows"):
    pytesseract.pytesseract.tesseract_cmd = config('TESSERACT_CMD_PATH')#r'C:\Program Files\Tesseract-OCR\tesseract'
def normalisarNameDocument(nameFile):
    caracteres = "%()$&#~`+^*=,;°"
    #caracteres = "!#$%^&*()"
    for caracteres in caracteres:
        nameFile = nameFile.replace(caracteres,'')
    nameFile = nameFile.replace(" ","_")
    return nameFile

def extraerOcr(file,slug,url):
    #print('The CPU usage is: ', psutil.cpu_percent(4)) 
    ramPercent = psutil.virtual_memory()[2]
    #cuentaProcesos = threading.active_count()
    #print("ram actual :" + str(ramPercent))
    #print("Cuenta procesos :" + str(cuentaProcesos))
    print(f'Active Threads: {threading.active_count()}')
    while(ramPercent > 90):
        #print('Esperando conversion...')
        psutil.cpu_percent(4)
        ramPercent = psutil.virtual_memory()[2]
        print("ram actual :" + str(ramPercent))
        #cuentaProcesos = threading.active_count()
        gc.collect()
        print(f'Active Threads: {threading.active_count()}')
        print("-----------")
    print('obteniendo texto de ' + slug)
    documento = DocumentoOCR(file)
    text = documento.obtenerTexto()

    data = {
        'contenidoOCR': str(text),
        'slug': str(slug)
    }

    res = requests.put(url+'/file/ocrService/'+slug+"/",data=data)
    while res.status_code != 200:
        print("Error al enviar el file a OcrSevice")
        print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
        time.sleep(60)
        res = requests.put(url+'/file/ocrService/'+slug+"/",data=data)
    #print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
    #del ramPercent      
    del res
    del documento
    del text
    del data
    gc.collect()
    return

def extraerOcrThask(file,slug,url):
    #print('The CPU usage is: ', psutil.cpu_percent(4)) 
    ramPercent = psutil.virtual_memory()[2]
    #cuentaProcesos = threading.active_count()
    #print("ram actual :" + str(ramPercent))
    #print("Cuenta procesos :" + str(cuentaProcesos))
    print(f'Active Threads: {threading.active_count()}')
    while(ramPercent > 90):
        #print('Esperando conversion...')
        psutil.cpu_percent(4)
        ramPercent = psutil.virtual_memory()[2]
        print("ram actual :" + str(ramPercent))
        #cuentaProcesos = threading.active_count()
        gc.collect()
        print(f'Active Threads: {threading.active_count()}')
        print("-----------")
    print('obteniendo texto de ' + slug)
    archivoToProcess = open(file, 'rb')
    documento = DocumentoOCR(archivoToProcess.read())
    text = documento.obtenerTexto()
    archivoToProcess.close()

    data = {
        'contenidoOCR': str(text),
        'slug': str(slug)
    }

    res = requests.put(url+'/file/ocrService/'+slug+"/",data=data)
    while res.status_code != 200:
        print("Error al enviar el file a OcrSevice")
        print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
        time.sleep(60)
        res = requests.put(url+'/file/ocrService/'+slug+"/",data=data)
    #print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
    #del ramPercent      
    archivoProcesado = File.objects.get(slug=slug)
    archivoProcesado.estadoProceso = 2
    archivoProcesado.save()
    remove(file)
    del res
    del documento
    del text
    del data
    gc.collect()
    return

def extraerOcrProcess():
    
    while(True):
        time.sleep(10)
        cantidadProcesamiento = len(File.objects.filter(estadoProceso=1))
        print('Procesando archivos pendientes...')
        archivosPendientes = File.objects.filter(estadoProceso = 0)
        if len(archivosPendientes) == 0:
            print('No hay archivos pendientes...')
        for file in archivosPendientes:
            if(cantidadProcesamiento <= 10):
                
                print('Cantidad de procesamiento: ' + str(cantidadProcesamiento))
                print('Procesando archivo: ' + file.documento_file.name)
                pathFile = settings.MEDIA_ROOT+file.documento_file.name
                
                try:
                    file.estadoProceso = 1
                    file.save()
                    cantidadProcesamiento = len(File.objects.filter(estadoProceso=1))
                    tarea = threading.Thread(target=extraerOcrThask,args=(pathFile,file.slug,file.urlFrom))
                    tarea.start()
                    '''file.estadoProceso = 2
                    file.save()
                    remove(pathFile)
                    data = {
                        'contenidoOCR': str(text),
                        'slug': file.slug
                    }

                    res = requests.put(file.urlFrom+'/file/ocrService/'+file.slug+"/",data=data)
                    while res.status_code != 200:
                        print("Error al enviar el file a OcrSevice")
                        print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
                        time.sleep(60)
                        res = requests.put(file.urlFrom+'/file/ocrService/'+file.slug+"/",data=data)'''
                except Exception as e:
                    print(e)
                    print('Error al extraer el OCR')
                    archivo.close()
                    file.estadoProceso = 3
                    file.save()


class DocumentoOCR():
    PDF_file = None
    def __init__(self,ruta):
        self.PDF_file = ruta
    def __del__(self): 
        self.PDF_file = None
        print('Destructor called, documento deleted.') 
    def obtenerTexto(self):
        '''doc = self.PDF_file
        absURl = settings.MEDIA_ROOT +'files/'  + doc'''
       
        textGenerado = ""
        with tempfile.TemporaryDirectory() as path:
            if(sistema == "Windows"):
                images_from_path = convert_from_bytes(
                    self.PDF_file,
                    poppler_path=config('POPPLER_PATH_WINDOWS'), output_folder=path
                )
            else:
                images_from_path = convert_from_bytes(
                    self.PDF_file, output_folder=path
                )
            #images_from_path = convert_from_path(absURl, output_folder=path,poppler_path=config('POPPLER_PATH_WINDOWS'))
            '''filename = get_random_string(length=10)
            text = ""
            print('texto obtenido: '+path)
            for image in images_from_path:
                image.save(settings.MEDIA_ROOT+'test/'+filename, 'JPEG')
                filename = get_random_string(length=10)
                text += pytesseract.image_to_string(settings.MEDIA_ROOT+'test/'+filename+".jpg")'''
            
            #return text
            text = ""
            for image in images_from_path:
                #print(image)
                text += pytesseract.image_to_string(image, lang='spa')
                image.close()
                
            textGenerado = text   
            images_from_path[0].close() 
        #remove(settings.MEDIA_ROOT+'files/'+doc)
        '''if(sistema == "Windows"):
            pages = convert_from_path(
                absURl,
                thread_count=1,
                poppler_path=config('POPPLER_PATH_WINDOWS')
            )
        else:
            pages = convert_from_path(
                absURl,
                thread_count=1
            )

        image_counter = 1
        imagenesRutas = []
        for page in pages:
            filename = get_random_string(length=40) + ".jpg"
            imagenesRutas.append(filename)
            page.save(settings.MEDIA_ROOT+'test/'+filename, 'JPEG')
            image_counter = image_counter + 1
            page.close()
        #del pages
        filelimit = image_counter-1
        textGenerado = ""
        del pages
        gc.collect()
        for i in range(1, filelimit + 1):
            #filename = "page_"+str(i)+".jpg"
            filename = imagenesRutas[i -1]
            # open image
            im = Image.open(settings.MEDIA_ROOT+'test/'+filename)

            # preprocessing
            im = im.convert('L')                             # grayscale
            im = im.filter(ImageFilter.MedianFilter())       # a little blur
            im = im.point(lambda x: 0 if x < 140 else 255)   # threshold (binarize)

            text = str(((pytesseract.image_to_string(im))))
            im.close()
            remove(settings.MEDIA_ROOT+'test/'+filename)
            text = text.replace('-\n', '')   
            #percent =  (i*100)/filelimit
            #print(str(round(percent,2)) + " %")
            textGenerado += text
            del text
            del im
            del filename
            gc.collect()'''
        del self.PDF_file
        
        print('contenido extraido por el OCR exitosamente!')
        return textGenerado