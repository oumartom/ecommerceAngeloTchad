from django.http import HttpResponse
from reportlab.lib.pagesizes import A5  # 📏 Utilisation de A5 au lieu de A6
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


def generate_receipt_pdf(order):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A5,  # ✅ Changement ici
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=0.8 * cm,
        bottomMargin=0.8 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=12,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=3,
        leading=9
    )

    story = []

    # En-tête
    story.append(Paragraph("ANGELO TCHAD", title_style))
    story.append(Paragraph("REÇU DE LIVRAISON", title_style))
    story.append(Spacer(1, 2))

    # Détails commande
    details_text = (
        f"N° Commande : {order.order_number}    Date : {order.created_at.strftime('%d/%m/%Y')}\n"
        f"Client      : {order.client.full_name}\n"
        f"Tél         : {order.client.phone_number}\n"
        f"Quartier    : {order.client.neighborhood}\n"
        f"Total       : {order.total_amount:,.0f} FCFA\n"
    )
    story.append(Preformatted(details_text, small_style))
    story.append(Spacer(1, 3))

    # Articles
    story.append(Paragraph("Articles :", small_style))
    for item in order.items.all():
        line = f"- {item.product.name} x{item.quantity} = {item.subtotal:,.0f} FCFA"
        story.append(Paragraph(line, small_style))

    story.append(Spacer(1, 4))

    # Instructions
    instructions = (
        "Instructions :\n"
        "• Vérifier l'identité du client\n"
        "• Faire signer après livraison\n"
        "• Retourner ce reçu au bureau"
    )
    story.append(Preformatted(instructions, small_style))
    story.append(Spacer(1, 4))

    # ✅ QR CODE (plus petit)
    qr_data = f"Commande #{order.order_number} - Client : {order.client.full_name} - {order.total_amount} FCFA"
    qr_code = qr.QrCodeWidget(qr_data)
    qr_code.barWidth = 2.5 * cm
    qr_code.barHeight = 2.5 * cm

    d = Drawing(3 * cm, 3 * cm)
    d.add(qr_code)
    story.append(d)
    story.append(Spacer(1, 4))

    # Signatures
    signature_data = [
        ["Livreur :", "Client :"],
        ["", ""],
        [f"Date : {datetime.now().strftime('%d/%m/%Y')}", "Signature :"]
    ]
    table = Table(signature_data, colWidths=[6.5*cm, 6.5*cm], rowHeights=[0.5*cm, 1.2*cm, 0.5*cm])
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_receipt_response(order):
    pdf_buffer = generate_receipt_pdf(order)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_livraison_{order.order_number}.pdf"'
    response.write(pdf_buffer.getvalue())

    return response

