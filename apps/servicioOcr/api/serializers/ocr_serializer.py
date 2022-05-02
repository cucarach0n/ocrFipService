from rest_framework import serializers

class ocrExtractSerializer(serializers.Serializer):
    slug = serializers.CharField()
    document = serializers.FileField()

    def validate(self,data):
    
        return data

