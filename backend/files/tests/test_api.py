import tempfile
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(), API_CALL_LIMIT=1000, API_CALL_PERIOD=1)
class FileAPITestCase(APITestCase):
    def test_upload_file(self):
        url = reverse('file-list')
        upload = SimpleUploadedFile('test.txt', b'hello', content_type='text/plain')
        response = self.client.post(url, {'file': upload}, format='multipart', HTTP_UserId='user1')
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
        response = self.client.get(url, HTTP_UserId='user1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_deduplication(self):
        url = reverse('file-list')
        upload1 = SimpleUploadedFile('dup1.txt', b'same', content_type='text/plain')
        upload2 = SimpleUploadedFile('dup2.txt', b'same', content_type='text/plain')
        self.client.post(url, {'file': upload1}, format='multipart', HTTP_UserId='user1')
        self.client.post(url, {'file': upload2}, format='multipart', HTTP_UserId='user1')
        self.assertEqual(File.objects.count(), 2)
        self.assertEqual(File.objects.filter(duplicate_of__isnull=True).count(), 1)

    def test_storage_limit(self):
        url = reverse('file-list')
        with override_settings(USER_STORAGE_LIMIT_MB=0):
            upload = SimpleUploadedFile('big.txt', b'a'*1024, content_type='text/plain')
            response = self.client.post(url, {'file': upload}, format='multipart', HTTP_UserId='user1')
            self.assertEqual(response.status_code, 429)
