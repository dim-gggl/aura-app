from rest_framework import viewsets, permissions
from .models import Note
from .serializers import NoteSerializer

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Note.objects.filter(user=self.request.user)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(content__icontains=search)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)