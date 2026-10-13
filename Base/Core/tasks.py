from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from .models import ContactMessage

@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=600, max_retries=5)
def enviarEmailContacto(mensajeid):
    mensaje = ContactMessage.objects.filter(pk=mensajeid, issent=False).first()
    if not mensaje: # Ya se mandó (o se borró): nunca se manda dos veces
        return
    asunto = ' '.join(mensaje.subject.split()) # Sin saltos de línea: Django rechaza headers con \n
    email = EmailMessage(
        subject=f"[jersdev.com] {asunto}",
        body=f"Nombre: {mensaje.name}\nEmail: {mensaje.email}\n\n{mensaje.message}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[mensaje.email],
    )
    email.send()
    mensaje.issent = True
    mensaje.sent_at = timezone.now()
    mensaje.save(update_fields=['issent', 'sent_at', 'updated_at'])
