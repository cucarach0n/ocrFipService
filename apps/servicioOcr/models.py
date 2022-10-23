# -*- coding: utf-8 -*-
from django.db import models


class File(models.Model):
    id = models.AutoField(primary_key = True)
    slug = models.CharField('Sulg',max_length=11,null = True, blank = True)
    nombreDocumento = models.CharField('Nombres del documento',max_length=250,null = True, blank = True)
    urlFrom = models.CharField('Url servidor',max_length=250,null = True, blank = True)
    contenidoOCR = models.TextField('Contenidos del documento', null = True, blank = True)
    documento_file = models.FileField('Archivo del documento',max_length=250, upload_to="files/",blank = True,null = True)
    extension = models.CharField('Extension de los archivos subidos',max_length=20,null = True, blank = True)
    scope = models.BooleanField(default = True)
    estadoProceso = models.IntegerField('Estado del proceso',default = 0)#0:En espera, 1:En proceso, 2:Procesado, 3:Error

    class Meta():
        verbose_name = 'File'
        verbose_name_plural = 'Files'
    
    def __str__(self):
        return "{0},{1}".format(self.nombreDocumento,self.slug)

