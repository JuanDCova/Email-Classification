import imaplib
import email
from django.shortcuts import render, get_object_or_404
from .models import Correo, ArchivoAdjunto
import tempfile
from django.core.files import File


def lista_correos(request):
    # Conectar al servidor IMAP y obtener los correos
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('ddzabaleta70@misena.edu.co', '(Danny2005)')
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    correo_ids = data[0].split()

    correos_guardados = Correo.objects.all()  # Obtener todos los correos previamente guardados en la base de datos

    correos_nuevos = []
    for correo_id in correo_ids:
        result, data = mail.fetch(correo_id, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        remitente = email_message['From']
        destinatario = email_message['To'] if 'To' in email_message else None

        if 'Subject' in email_message and 'PQRSD' in email_message['Subject']:
            asunto = email_message['Subject']
            contenido = ""
            imagenes_adjuntas = []

            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    contenido = part.get_payload(decode=True).decode()
                elif content_type == 'image/jpeg' or content_type == 'image/png':
                    imagenes_adjuntas.append(part.get_payload(decode=True))

            # Verificar si el asunto ya existe en los correos previamente guardados
            if not correos_guardados.filter(asunto=asunto).exists():
                correo = Correo.objects.create(remitente=remitente, destinatario=destinatario,
                                               asunto=asunto, contenido=contenido)
                correos_nuevos.append(correo)

                # Guardar las imágenes adjuntas en la base de datos
                for img_data in imagenes_adjuntas:
                    temp_file = tempfile.NamedTemporaryFile(delete=True)
                    temp_file.write(img_data)
                    temp_file.flush()

                    archivo_adjunto = ArchivoAdjunto(correo=correo, nombre='imagen.png')
                    archivo_adjunto.archivo.save('imagen.png', File(temp_file))
                    archivo_adjunto.save()

    # Obtener todos los correos, tanto nuevos como previamente guardados
    todos_correos = list(correos_guardados) + correos_nuevos

    return render(request, 'lista.html', {'correos': todos_correos})

def detalle_correo(request, correo_id):
    correo = get_object_or_404(Correo, pk=correo_id)
    archivos_adjuntos = ArchivoAdjunto.objects.filter(correo=correo)
    
    # Verificar si el correo ya existe en la base de datos
    correo_existente = Correo.objects.filter(remitente=correo.remitente, destinatario=correo.destinatario, asunto=correo.asunto, contenido=correo.contenido).exists()

    if not correo_existente:
        # El correo no existe en la base de datos, entonces lo guardamos
        correo.save()
        
        for adjunto in archivos_adjuntos:
            adjunto.correo = correo
            adjunto.save()
    return render(request, 'detalles.html', {'correo': correo, 'archivos_adjuntos': archivos_adjuntos})