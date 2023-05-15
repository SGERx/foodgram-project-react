from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from foodgram.settings import DEFAULT_FROM_EMAIL


def create_code_and_send_email(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Добро пожаловать на проект YaMDb!',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=(user.email,),
        message=confirmation_code,
        fail_silently=False
    )
