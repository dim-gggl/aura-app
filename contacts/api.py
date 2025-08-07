from rest_framework import viewsets, permissions
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user).only(
            "id", "name", "email", "phone", "contact_type"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)