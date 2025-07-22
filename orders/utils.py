from django.http import HttpResponse
from reportlab.lib.pagesizes import A6
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

def generate_receipt_pdf(order):
    """
    Génère un reçu PDF compact au format texte, sans balises HTML
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(14.8 * cm, 10.5 * cm),
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
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=4,
        leading=10
    )

    story = []

    # En-tête
    story.append(Paragraph("ANGELO TCHAD", title_style))
    story.append(Paragraph("REÇU DE LIVRAISON", title_style))
    story.append(Spacer(1, 4))

    # Détails commande
    details_text = (
        f"N° Commande : {order.order_number}    Date : {order.created_at.strftime('%d/%m/%Y')}\n"
        f"Client      : {order.client.full_name}\n"
        f"Tél         : {order.client.phone_number}\n"
        f"Quartier    : {order.client.neighborhood}\n"
        f"Total       : {order.total_amount:,.0f} FCFA\n"
        
    )
    story.append(Preformatted(details_text, small_style))
    story.append(Spacer(1, 6))

    # Articles
    story.append(Paragraph("Articles :", small_style))
    for item in order.items.all():
        line = f"- {item.product.name} x{item.quantity} = {item.subtotal:,.0f} FCFA"
        story.append(Paragraph(line, small_style))

    story.append(Spacer(1, 8))

    # Instructions
    instructions = (
        "Instructions :\n"
        "• Vérifier l'identité du client\n"
        "• Faire signer après livraison\n"
        "• Retourner ce reçu au bureau"
    )
    story.append(Preformatted(instructions, small_style))
    story.append(Spacer(1, 8))

    # Signatures
    signature_data = [
        ["Livreur :", "Client :"],
        ["", ""],
        [f"Date : {datetime.now().strftime('%d/%m/%Y')}", "Signature :"]
    ]
    table = Table(signature_data, colWidths=[6*cm, 6*cm], rowHeights=[0.5*cm, 1.2*cm, 0.5*cm])
    # table.setStyle(TableStyle([
    #     ('FONTSIZE', (0, 0), (-1, -1), 7),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
    #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    #     ('BOX', (0, 1), (0, 1), 0.5, colors.black),
    #     ('BOX', (1, 1), (1, 1), 0.5, colors.black),
    # ]))
    # story.append(table)

    # Génération PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_receipt_response(order):
    """
    Génère la réponse HTTP avec le reçu PDF
    """
    pdf_buffer = generate_receipt_pdf(order)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_livraison_{order.order_number}.pdf"'
    response.write(pdf_buffer.getvalue())

    return response



# from django.http import HttpResponse
# from django.template.loader import get_template
# from django.conf import settings
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4, letter
# from reportlab.lib.units import cm, mm
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from io import BytesIO
# import os
# from datetime import datetime

# def generate_receipt_pdf(order):
#     """
#     Génère un petit reçu PDF compact pour coller sur la commande
#     """
#     buffer = BytesIO()
    
#     # Configuration du document - format plus petit (A5)
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=(14.8*cm, 10.5*cm),  # Format A6 paysage
#         rightMargin=1*cm,
#         leftMargin=1*cm,
#         topMargin=0.8*cm,
#         bottomMargin=0.8*cm
#     )
    
#     # Styles compacts
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CompactTitle',
#         parent=styles['Heading1'],
#         fontSize=12,
#         spaceAfter=8,
#         alignment=TA_CENTER,
#         textColor=colors.black
#     )
    
#     header_style = ParagraphStyle(
#         'CompactHeader',
#         parent=styles['Heading2'],
#         fontSize=9,
#         spaceAfter=4,
#         textColor=colors.black
#     )
    
#     small_style = ParagraphStyle(
#         'CompactSmall',
#         parent=styles['Normal'],
#         fontSize=7,
#         spaceAfter=2
#     )
    
#     # Contenu du document
#     story = []
    
#     # En-tête compact
#     story.append(Paragraph("<b>ANGELO TCHAD</b>", title_style))
#     story.append(Paragraph("Reçu de Livraison", header_style))
#     story.append(Spacer(1, 4))
    
#     # Informations essentielles en format compact
#     info_data = [
#         [f"<b>N° Commande:</b> {order.order_number}", f"<b>Date:</b> {order.created_at.strftime('%d/%m/%Y')}"],
#         [f"<b>Client:</b> {order.client.full_name}", f"<b>Tél:</b> {order.client.phone_number}"],
#         [f"<b>Quartier:</b> {order.client.neighborhood}", f"<b>Total:</b> {order.total_amount:,.0f} FCFA"],
#     ]
    
#     info_table = Table(info_data, colWidths=[6*cm, 6*cm])
#     info_table.setStyle(TableStyle([
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#     ]))
    
#     story.append(info_table)
#     story.append(Spacer(1, 6))
    
#     # Articles commandés - format très compact
#     story.append(Paragraph("<b>Articles:</b>", header_style))
    
#     items_text = ""
#     for item in order.items.all():
#         items_text += f"• {item.product.name} x{item.quantity} = {item.subtotal:,.0f} FCFA<br/>"
    
#     story.append(Paragraph(items_text, small_style))
#     story.append(Spacer(1, 8))
    
#     # Instructions courtes
#     story.append(Paragraph("<b>Instructions:</b>", header_style))
#     instructions_text = "• Vérifier l'identité du client<br/>• Faire signer après livraison<br/>• Retourner ce reçu au bureau"
#     story.append(Paragraph(instructions_text, small_style))
#     story.append(Spacer(1, 8))
    
#     # Zone de signature compacte
#     signature_data = [
#         ["Livreur:", "Client:"],
#         ["", ""],
#         [f"Date: {datetime.now().strftime('%d/%m/%Y')}", "Signature:"]
#     ]
    
#     signature_table = Table(signature_data, colWidths=[6*cm, 6*cm], rowHeights=[0.5*cm, 1.2*cm, 0.5*cm])
#     signature_table.setStyle(TableStyle([
#         ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ('BOX', (0, 1), (0, 1), 0.5, colors.black),
#         ('BOX', (1, 1), (1, 1), 0.5, colors.black),
#     ]))
    
#     story.append(signature_table)
    
#     # Construire le PDF
#     doc.build(story)
    
#     buffer.seek(0)
#     return buffer

# def generate_receipt_response(order):
#     """
#     Génère une réponse HTTP avec le PDF du reçu compact
#     """
#     pdf_buffer = generate_receipt_pdf(order)
    
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="recu_livraison_{order.order_number}.pdf"'
#     response.write(pdf_buffer.getvalue())
    
#     return response

