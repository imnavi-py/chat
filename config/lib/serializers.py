# create by: ayoub taneh (2024-08-07)
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
import phonenumbers
from django.core.validators import EmailValidator




class PhoneNumberSerializer(serializers.Serializer):
    # create by: ayoub taneh (2024-08-07)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        phone = data.get('phone')
        if not phone:
            raise serializers.ValidationError(_("phone number must be provided."))
        if phone:
            self.validate_phone_number(phone)
        return data

    def validate_phone_number(self, value):
        try:
            phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone_number):
                raise serializers.ValidationError(_("Invalid phone number"))
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(_("Invalid phone number format, correct format is +989112223344"))
   


class EmailSerializer(serializers.Serializer):
    # create by: ayoub taneh (2024-08-07)
    email = serializers.EmailField(validators=[EmailValidator(message=_("Invalid email address"))])

    forbidden_domains = [
        'example.com', 
        'forbidden.com', 
        'test.com'
    ]

    def validate_email(self, value):
        domain = value.split('@')[1]

        if domain in self.forbidden_domains:
            raise serializers.ValidationError(_(f"Emails from '{domain}' are not allowed."))
        return value 


########################################################################################################################################


def validate_unique_title(field_name):
    from BaseUser.models import TagsLabel
    def validator(value):
        if TagsLabel.objects.filter(**{field_name: value}).exists():
            raise serializers.ValidationError({
                'detail': f"{get_error_message(field_name)}"
            })
        if len(value) < 3:
            raise serializers.ValidationError({
                'detail': f"{get_length_error_message(field_name)}"
            })
        return value
    
    return validator

def get_error_message(field_name):
    if field_name == 'title_fa':
        return "The provided Persian title has already been registered."
    elif field_name == 'title_en':
        return "The provided English title has already been registered."
    return ""

def get_length_error_message(field_name):
    if field_name == 'title_fa':
        return "The Persian title must be at least 3 characters long."
    elif field_name == 'title_en':
        return "The English title must be at least 3 characters long."
    return ""
