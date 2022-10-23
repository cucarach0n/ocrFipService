from rest_framework import serializers
from apps.servicioOcr.models import File

class ocrExtractSerializer(serializers.Serializer):
    slug = serializers.CharField()
    document = serializers.FileField()
    url = serializers.CharField()
    def validate(self,data):
    
        return data

class FileOcr(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['slug','extension','estadoProceso','documento_file','urlFrom']

