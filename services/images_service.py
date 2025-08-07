from imagekit import ImageSpec
from imagekit.processors import ResizeToFit
from django.core.files.base import ContentFile

class ThumbSpec(ImageSpec):
    processors = [ResizeToFit(600, 600)]
    format = 'JPEG'
    options = {'quality': 80}

# Exemple d'utilisation: générer une vignette à la volée pour un FieldFile
# thumb = ThumbSpec(source=instance.photo).generate()
# instance.photo_thumb.save('thumb.jpg', ContentFile(thumb.read()))