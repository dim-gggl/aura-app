from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id", "name", "contact_type", "email", "phone", "address",
            "website", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]