from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
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
            if analysis.test_type == 'materiality': test_name = "Cálculo de Materialidade"

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

            elif analysis.test_type == 'materiality':
                res = analysis.result
                story.append(Paragraph(f"<b>Materialidade Global: R$ {res.get('global_materiality', 0):,.2f}</b>", styles['Normal']))
                story.append(Paragraph(f"Base de Cálculo: {res.get('benchmark')} (R$ {res.get('benchmark_value', 0):,.2f})", styles['Normal']))
                story.append(Paragraph(f"Percentual Aplicado: {res.get('percentage_global')}%", styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(f"Materialidade de Performance: R$ {res.get('performance_materiality', 0):,.2f}", styles['Normal']))

            story.append(Spacer(1, 0.3 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Gerado automaticamente por AuditFlow", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_confirmation_letter(type, client_data, recipient_data, date_base, logo_bytes=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []

    # Styles
    normal = styles['Normal']
    normal.alignment = TA_JUSTIFY

    header = styles['Normal']
    header.alignment = TA_RIGHT

    # 1. Logo (if available)
    if logo_bytes:
        try:
            logo_io = io.BytesIO(logo_bytes)
            img = Image(logo_io, width=2*inch, height=1*inch, kind='proportional')
            img.hAlign = 'LEFT'
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
        except:
            pass # Ignore if logo fails

    # 2. Date and Location
    story.append(Paragraph(f"Local, {datetime.now().strftime('%d de %B de %Y')}", header))
    story.append(Spacer(1, 0.3 * inch))

    # 3. Recipient Address
    story.append(Paragraph(f"À<br/>{recipient_data['name']}<br/>At.: Departamento Contábil/Financeiro", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # 4. Subject
    subject_map = {
        'bank': 'Confirmação de Saldos Bancários',
        'legal': 'Confirmação de Processos Judiciais',
        'supplier': 'Confirmação de Saldo de Fornecedores',
        'customer': 'Confirmação de Saldo de Clientes',
        'representation': 'Carta de Representação da Administração'
    }
    subject = subject_map.get(type, 'Solicitação de Confirmação')
    story.append(Paragraph(f"<b>Ref.: {subject} - {client_data['name']}</b>", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # 5. Body Text (NBC TA 505 / Standard Templates)

    if type == 'bank':
        text = f"""
        Prezados Senhores,<br/><br/>
        Para fins de auditoria de nossas demonstrações contábeis, solicitamos a gentileza de fornecerem diretamente aos nossos auditores independentes,
        <b>AuditFlow Auditores Independentes</b>, as informações detalhadas abaixo, relativas às nossas operações mantidas com V.Sas. na data base de <b>{date_base}</b>.<br/><br/>
        1. Saldos em contas correntes e aplicações financeiras;<br/>
        2. Detalhes de empréstimos e financiamentos (saldo devedor, taxas, vencimentos, garantias);<br/>
        3. Outras responsabilidades diretas ou indiretas (fianças, avais, derivativos).<br/><br/>
        A resposta deve ser enviada diretamente para o e-mail: auditoria@auditflow.com.
        """

    elif type == 'legal':
        text = f"""
        Prezados Senhores,<br/><br/>
        Solicitamos a gentileza de fornecerem aos nossos auditores independentes, <b>AuditFlow Auditores Independentes</b>,
        informações sobre processos cíveis, trabalhistas, tributários e outros em que nossa empresa figure como Autora ou Ré,
        sob patrocínio desse escritório, com a posição em <b>{date_base}</b>.<br/><br/>
        Favor informar para cada processo: número, natureza, instância atual, valor da causa, estimativa de perda (Provável, Possível, Remota) e valor estimado.<br/><br/>
        """

    elif type == 'representation':
        text = f"""
        Prezados Auditores,<br/><br/>
        Esta carta de representação é fornecida em conexão com a auditoria das demonstrações contábeis da <b>{client_data['name']}</b>
        para o exercício findo em <b>{date_base}</b>, com a finalidade de expressar uma opinião sobre se as demonstrações contábeis
        apresentam adequadamente, em todos os aspectos relevantes, a posição patrimonial e financeira da Entidade.<br/><br/>
        Confirmamos que cumprimos nossas responsabilidades, conforme estabelecido nos termos do contrato de auditoria.<br/><br/>
        Atenciosamente,<br/>
        Administração
        """
    else: # Suppliers / Customers
        text = f"""
        Prezados Senhores,<br/><br/>
        Nossos auditores independentes estão realizando a revisão de nossas contas.
        Solicitamos que confirmem diretamente a eles o saldo de nossa conta em seus registros na data de <b>{date_base}</b>.<br/><br/>
        Caso o saldo não esteja de acordo, favor fornecer o demonstrativo das partidas em aberto.<br/><br/>
        Esta solicitação não representa necessariamente um pedido de pagamento.
        """

    story.append(Paragraph(text, normal))
    story.append(Spacer(1, 0.5 * inch))

    # 6. Signatures
    story.append(Paragraph("Atenciosamente,", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("___________________________________", styles['Normal']))
    story.append(Paragraph(f"{client_data['name']}<br/>Autorizado por: ___________________", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer
