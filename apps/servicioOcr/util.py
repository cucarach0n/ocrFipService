import os
from django.conf import settings
from decouple import config
from os import remove
from PIL import Image, ImageFilter
import pytesseract
from pdf2image import convert_from_path
from django.utils.crypto import get_random_string
import platform
import gc
import psutil
import requests
import threading
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

def extraerOcr(file,slug):
    #print('The CPU usage is: ', psutil.cpu_percent(4)) 
    #ramPercent = psutil.virtual_memory()[2]
    cuentaProcesos = threading.active_count()
    #print("ram actual :" + str(ramPercent))
    print("Cuenta procesos :" + str(cuentaProcesos))
    print(f'Active Threads: {threading.active_count()}')
    while(cuentaProcesos > 25):
        #print('Esperando conversion...')
        psutil.cpu_percent(4)
        ramPercent = psutil.virtual_memory()[2]
        cuentaProcesos = threading.active_count()
        gc.collect()
        print(f'Active Threads: {threading.active_count()}')
        print("-----------")
    documento = DocumentoOCR(file)
    text = documento.obtenerTexto()

    data = {
        'contenidoOCR': str(text),
        'slug': str(slug)
    }

    res = requests.put(config('URL_SERVER')+'/file/ocrService/'+slug+"/",data=data)
    
    print("imprimiendo respuesta de fip.api.edu.pe: "+res.text)
    #del ramPercent      
    del res
    del documento
    del text
    del data
    gc.collect()
    return
class DocumentoOCR():
    PDF_file = None
    def __init__(self,ruta):
        self.PDF_file = ruta
    def __del__(self): 
        print('Destructor called, documento deleted.') 
    def obtenerTexto(self):
        doc = self.PDF_file
        absURl = settings.MEDIA_ROOT +'files/'  + doc
        print('obteniendo texto de ')
        if(sistema == "Windows"):
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
            gc.collect()
            
        self.PDF_file = None
        
        print('contenido extraido por el OCR exitosamente!')
        return textGenerado