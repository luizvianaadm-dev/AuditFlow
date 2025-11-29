from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import io
from datetime import datetime

def generate_audit_report(engagement, analysis_results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = ParagraphStyle(
        name='AuditTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor('#003366')
    )

    heading_style = ParagraphStyle(
        name='AuditHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00AEEF'),
        spaceBefore=15,
        spaceAfter=10
    )

    # 1. Header / Cover
    story.append(Paragraph("Relatório de Auditoria Digital", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Engagement Details
    data = [
        ['Cliente:', engagement.client.name],
        ['Auditoria:', engagement.name],
        ['Ano Base:', str(engagement.year)],
        ['Data do Relatório:', datetime.now().strftime("%d/%m/%Y")]
    ]

    t = Table(data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * inch))

    # 2. Executive Summary
    story.append(Paragraph("Resumo Executivo", heading_style))
    summary_text = f"""
    Este documento apresenta os resultados da auditoria automatizada realizada para o cliente <b>{engagement.client.name}</b>.
    Foram analisadas {len(engagement.transactions)} transações financeiras utilizando testes estatísticos e forenses
    conforme as normas NBC TA 240 e 520.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # 3. Analysis Results
    if not analysis_results:
        story.append(Paragraph("Nenhuma análise foi registrada para este trabalho.", styles['Normal']))
    else:
        for analysis in analysis_results:
            # Section Title
            test_name = "Lei de Benford" if analysis.test_type == 'benford' else "Pagamentos Duplicados"
            story.append(Paragraph(f"Resultado: {test_name}", heading_style))

            # Date
            story.append(Paragraph(f"Executado em: {analysis.executed_at.strftime('%d/%m/%Y %H:%M')}", styles['Italic']))
            story.append(Spacer(1, 0.1 * inch))

            # Content based on type
            if analysis.test_type == 'benford':
                anomalies = analysis.result.get('anomalies', [])
                if anomalies:
                    story.append(Paragraph(f"<b>{len(anomalies)} Anomalias Estatísticas Detectadas</b>", styles['Normal']))
                    story.append(Paragraph("Os seguintes dígitos apresentaram desvio significativo (>5%) da frequência esperada:", styles['Normal']))
                    story.append(Spacer(1, 0.1 * inch))

                    # Table of anomalies
                    details = analysis.result.get('details', [])
                    table_data = [['Dígito', 'Esperado', 'Observado', 'Desvio']]
                    for d in details:
                        if d['is_anomaly']:
                            table_data.append([
                                str(d['digit']),
                                f"{d['expected']*100:.1f}%",
                                f"{d['observed']*100:.1f}%",
                                f"{d['deviation']*100:.1f}%"
                            ])

                    t_benford = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    t_benford.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#003366')),
                        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
                        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                    ]))
                    story.append(t_benford)
                else:
                    story.append(Paragraph("Nenhuma anomalia estatística detectada. A distribuição segue o padrão esperado.", styles['Normal']))

            elif analysis.test_type == 'duplicates':
                groups = analysis.result.get('duplicates', [])
                if groups:
                    story.append(Paragraph(f"<b>{len(groups)} Grupos de Pagamentos Suspeitos</b>", styles['Normal']))
                    story.append(Spacer(1, 0.1 * inch))

                    for i, group in enumerate(groups[:10]): # Limit to 10 groups to save space
                        story.append(Paragraph(f"Grupo {i+1} - Valor: R$ {group['amount']:.2f} (Similaridade: {group['similarity_score']}%)", styles['Normal']))
                        for tx in group['transactions']:
                            story.append(Paragraph(f"- {tx['vendor']} (ID: {tx['id']})", styles['Bullet']))
                        story.append(Spacer(1, 0.1 * inch))

                    if len(groups) > 10:
                        story.append(Paragraph(f"...e mais {len(groups)-10} grupos.", styles['Italic']))
                else:
                    story.append(Paragraph("Nenhum pagamento duplicado encontrado com os critérios atuais.", styles['Normal']))

            story.append(Spacer(1, 0.3 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Gerado automaticamente por AuditFlow", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer
