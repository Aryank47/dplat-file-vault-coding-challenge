import tempfile
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FileAPITestCase(APITestCase):
    def test_upload_file(self):
        url = reverse('file-list')
        upload = SimpleUploadedFile('test.txt', b'hello', content_type='text/plain')
        response = self.client.post(url, {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(File.objects.first().original_filename, 'test.txt')

    def test_list_files(self):
        File.objects.create(
            file=SimpleUploadedFile('a.txt', b'a', content_type='text/plain'),
            original_filename='a.txt',
            file_type='text/plain',
            size=1
        )
        File.objects.create(
            file=SimpleUploadedFile('b.txt', b'b', content_type='text/plain'),
            original_filename='b.txt',
            file_type='text/plain',
            size=1
        )
        url = reverse('file-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
