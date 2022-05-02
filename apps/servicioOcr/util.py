import os

from django.conf import settings

from decouple import config
from os import remove
from PIL import Image, ImageFilter
import pytesseract
from pdf2image import convert_from_path,convert_from_bytes
from django.utils.crypto import get_random_string
import platform
from django.db.models import Q

os.environ['OMP_THREAD_LIMIT'] = '2'
sistema = platform.system()
if(sistema == "Windows"):
    pytesseract.pytesseract.tesseract_cmd = config('TESSERACT_CMD_PATH')#r'C:\Program Files\Tesseract-OCR\tesseract'

class DocumentoOCR():
    PDF_file = None
    def __init__(self,ruta):
        self.PDF_file = ruta
    def obtenerTexto(self):
        doc = self.PDF_file
        absURl = settings.MEDIA_ROOT +'files/'  + doc
        print('obteniendo texto de ')
        if(sistema == "Windows"):
            pages = convert_from_path(
                absURl,
                thread_count=5,
                poppler_path=config('POPPLER_PATH_WINDOWS')
            )
        else:
            pages = convert_from_path(
                absURl,
                thread_count=5
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
            remove(settings.MEDIA_ROOT+'test/'+filename)
            text = text.replace('-\n', '')   
            percent =  (i*100)/filelimit
            #print(str(round(percent,2)) + " %")
            textGenerado += text
        
        
        print('contenido extraido por el OCR exitosamente!')
        return textGenerado