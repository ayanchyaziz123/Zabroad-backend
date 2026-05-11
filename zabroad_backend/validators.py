from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif']

validate_image_type = FileExtensionValidator(
    allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
    message='Only JPG, JPEG, PNG, WebP, and GIF images are allowed.',
)


def validate_image_size(image):
    max_mb = 5
    if image.size > max_mb * 1024 * 1024:
        raise ValidationError(f'Image must be under {max_mb}MB.')
