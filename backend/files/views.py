from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import Throttled
from django.conf import settings
from .models import File
from .serializers import FileSerializer
from .throttling import UserIdRateThrottle

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    throttle_classes = [UserIdRateThrottle]

    def throttled(self, request, wait):
        """Raise custom throttling exception with a clear message."""
        raise Throttled(wait, detail="Call Limit Reached")

    def get_queryset(self):
        queryset = File.objects.all()
        params = self.request.query_params
        search = params.get('search')
        if search:
            queryset = queryset.filter(original_filename__icontains=search)

        file_type = params.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)

        min_size = params.get('min_size')
        if min_size is not None:
            try:
                queryset = queryset.filter(size__gte=int(min_size))
            except ValueError:
                pass

        max_size = params.get('max_size')
        if max_size is not None:
            try:
                queryset = queryset.filter(size__lte=int(max_size))
            except ValueError:
                pass

        start_date = params.get('start_date')
        if start_date:
            dt = parse_datetime(start_date)
            if dt:
                queryset = queryset.filter(uploaded_at__gte=dt)

        end_date = params.get('end_date')
        if end_date:
            dt = parse_datetime(end_date)
            if dt:
                queryset = queryset.filter(uploaded_at__lte=dt)

        return queryset

    @action(detail=False, methods=['get'])
    def storage_savings(self, request):
        """Return total bytes saved by deduplication for the requesting user."""
        user_id = request.headers.get('UserId', 'anonymous')
        # Savings is size of duplicate files uploaded by this user
        savings = File.objects.filter(uploaded_by=user_id, duplicate_of__isnull=False).aggregate(total=Sum('size'))['total'] or 0
        return Response({'user_id': user_id, 'storage_savings': savings})

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.headers.get('UserId', 'anonymous')

        # Calculate file hash for deduplication
        file_hash = File.calculate_hash(file_obj)
        existing = File.objects.filter(hash=file_hash, duplicate_of__isnull=True).first()

        # Check user storage quota (only count unique files)
        storage_limit = getattr(settings, 'USER_STORAGE_LIMIT_MB', 10) * 1024 * 1024
        used = File.objects.filter(uploaded_by=user_id, duplicate_of__isnull=True).aggregate(total=Sum('size'))['total'] or 0
        additional_size = 0 if existing else file_obj.size
        if used + additional_size > storage_limit:
            return Response({'detail': 'Storage Quota Exceeded'}, status=429)

        if existing:
            # Create new record referencing existing file
            new_file = File.objects.create(
                file=existing.file,
                original_filename=file_obj.name,
                file_type=file_obj.content_type,
                size=file_obj.size,
                hash=file_hash,
                duplicate_of=existing,
                uploaded_by=user_id,
            )
            serializer = self.get_serializer(new_file)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        data = {
            'file': file_obj,
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size,
            'hash': file_hash,
            'uploaded_by': user_id,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
