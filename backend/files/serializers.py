from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id', 'file', 'original_filename', 'file_type', 'size',
            'uploaded_at', 'duplicate_of', 'uploaded_by', 'hash'
        ]
        read_only_fields = ['id', 'uploaded_at', 'duplicate_of', 'uploaded_by']
        extra_kwargs = {
            'hash': {'write_only': True}
        }
