from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import io
from datetime import datetime

def add_heading(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    run = heading.runs[0]
    run.font.color.rgb = RGBColor(0, 51, 102) if level == 0 else RGBColor(0, 174, 239)
    if level == 0:
        run.font.size = Pt(24)
    else:
        run.font.size = Pt(14)

def add_paragraph(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    # Simple HTML-like parsing for bold
    parts = text.split('<b>')
    for i, part in enumerate(parts):
        if '</b>' in part:
            subparts = part.split('</b>')
            # Bold part
            run = p.add_run(subparts[0])
            run.bold = True
            # Normal part
            if len(subparts) > 1:
                p.add_run(subparts[1])
        else:
            # First part or no closing tag
            run = p.add_run(part)
            if bold: run.bold = True
            if italic: run.italic = True

def generate_audit_report_docx(engagement, analysis_results, mistatement_summary=None):
    doc = Document()

    # 1. Header / Cover
    add_heading(doc, "Relatório de Auditoria Digital", level=0)

    # Engagement Details Table
    table = doc.add_table(rows=4, cols=2)
    data = [
        ('Cliente:', engagement.client.name),
        ('Auditoria:', engagement.name),
        ('Ano Base:', str(engagement.year)),
        ('Data do Relatório:', datetime.now().strftime("%d/%m/%Y"))
    ]
    for i, (label, value) in enumerate(data):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[1].text = value

    doc.add_paragraph() # Spacer

    # 2. Executive Summary
    add_heading(doc, "Resumo Executivo", level=1)
    summary_text = f"Este documento apresenta os resultados da auditoria automatizada realizada para o cliente <b>{engagement.client.name}</b>. Foram analisadas {len(engagement.transactions)} transações financeiras utilizando testes estatísticos e forenses conforme as normas NBC TA 240 e 520."
    add_paragraph(doc, summary_text)
    doc.add_paragraph()

    # 3. Analysis Results
    if not analysis_results:
        doc.add_paragraph("Nenhuma análise foi registrada para este trabalho.")
    else:
        for analysis in analysis_results:
            test_name = "Lei de Benford" if analysis.test_type == 'benford' else "Pagamentos Duplicados"
            if analysis.test_type == 'materiality': test_name = "Cálculo de Materialidade"

            add_heading(doc, f"Resultado: {test_name}", level=1)
            add_paragraph(doc, f"Executado em: {analysis.executed_at.strftime('%d/%m/%Y %H:%M')}", italic=True)

            if analysis.test_type == 'benford':
                anomalies = analysis.result.get('anomalies', [])
                if anomalies:
                    add_paragraph(doc, f"<b>{len(anomalies)} Anomalias Estatísticas Detectadas</b>")
                    doc.add_paragraph("Os seguintes dígitos apresentaram desvio significativo (>5%) da frequência esperada:")

                    # Table
                    table = doc.add_table(rows=1, cols=4)
                    table.style = 'Table Grid'
                    hdr_cells = table.rows[0].cells
                    hdr_cells[0].text = 'Dígito'
                    hdr_cells[1].text = 'Esperado'
                    hdr_cells[2].text = 'Observado'
                    hdr_cells[3].text = 'Desvio'

                    details = analysis.result.get('details', [])
                    for d in details:
                        if d['is_anomaly']:
                            row_cells = table.add_row().cells
                            row_cells[0].text = str(d['digit'])
                            row_cells[1].text = f"{d['expected']*100:.1f}%"
                            row_cells[2].text = f"{d['observed']*100:.1f}%"
                            row_cells[3].text = f"{d['deviation']*100:.1f}%"
                else:
                    doc.add_paragraph("Nenhuma anomalia estatística detectada. A distribuição segue o padrão esperado.")

            elif analysis.test_type == 'duplicates':
                groups = analysis.result.get('duplicates', [])
                if groups:
                    add_paragraph(doc, f"<b>{len(groups)} Grupos de Pagamentos Suspeitos</b>")

                    for i, group in enumerate(groups[:10]):
                        p = doc.add_paragraph(f"Grupo {i+1} - Valor: R$ {group['amount']:.2f} (Similaridade: {group['similarity_score']}%)")
                        for tx in group['transactions']:
                            doc.add_paragraph(f"- {tx['vendor']} (ID: {tx['id']})", style='List Bullet')

                    if len(groups) > 10:
                        add_paragraph(doc, f"...e mais {len(groups)-10} grupos.", italic=True)
                else:
                    doc.add_paragraph("Nenhum pagamento duplicado encontrado com os critérios atuais.")

            elif analysis.test_type == 'materiality':
                res = analysis.result
                add_paragraph(doc, f"<b>Materialidade Global: R$ {res.get('global_materiality', 0):,.2f}</b>")
                doc.add_paragraph(f"Base de Cálculo: {res.get('benchmark')} (R$ {res.get('benchmark_value', 0):,.2f})")
                doc.add_paragraph(f"Percentual Aplicado: {res.get('percentage_global')}%")
                doc.add_paragraph(f"Materialidade de Performance: R$ {res.get('performance_materiality', 0):,.2f}")

            doc.add_paragraph()

    # 4. Summary of Mistatements
    if mistatement_summary and mistatement_summary.get('items'):
        add_heading(doc, "Sumário de Erros Não Corrigidos", level=1)
        doc.add_paragraph("Abaixo listamos as divergências identificadas durante os trabalhos de auditoria:")

        items = mistatement_summary['items']
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Descrição'
        hdr_cells[1].text = 'Tipo'
        hdr_cells[2].text = 'Status'
        hdr_cells[3].text = 'Valor (R$)'

        for m in items:
            row_cells = table.add_row().cells
            row_cells[0].text = m.description
            row_cells[1].text = m.type.capitalize()
            row_cells[2].text = "Ajustado" if m.status == 'adjusted' else "Não Ajustado"
            row_cells[3].text = f"{m.amount_divergence:,.2f}"

        doc.add_paragraph()
        add_paragraph(doc, f"<b>Total Ajustado: R$ {mistatement_summary['total_adjusted']:,.2f}</b>")
        add_paragraph(doc, f"<b>Total Não Ajustado: R$ {mistatement_summary['total_unadjusted']:,.2f}</b>")

        # Conclusion
        materiality_val = 0
        for res in analysis_results:
            if res.test_type == 'materiality':
                materiality_val = res.result.get('global_materiality', 0)
                break

        if materiality_val > 0:
            doc.add_paragraph(f"Materialidade Global: R$ {materiality_val:,.2f}")

            if mistatement_summary['total_unadjusted'] > materiality_val:
                conclusion = "CONCLUSÃO: O total de erros não ajustados excede a materialidade global. As demonstrações contábeis podem conter distorções relevantes."
                p = doc.add_paragraph()
                run = p.add_run(conclusion)
                run.bold = True
                run.font.color.rgb = RGBColor(255, 0, 0)
            else:
                conclusion = "CONCLUSÃO: O total de erros não ajustados é inferior à materialidade global. As distorções não são consideradas relevantes individualmente ou em conjunto."
                p = doc.add_paragraph()
                run = p.add_run(conclusion)
                run.bold = True
                run.font.color.rgb = RGBColor(0, 128, 0)

    # Footer
    doc.add_paragraph()
    add_paragraph(doc, "Gerado automaticamente por AuditFlow", italic=True)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generate_confirmation_letter_docx(type, client_data, recipient_data, date_base, logo_bytes=None):
    doc = Document()

    # 1. Logo
    if logo_bytes:
        try:
            image_stream = io.BytesIO(logo_bytes)
            doc.add_picture(image_stream, width=Inches(2.0))
            last_paragraph = doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except Exception as e:
            print(f"Error adding logo: {e}")

    # 2. Date and Location
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"Local, {datetime.now().strftime('%d de %B de %Y')}")
    doc.add_paragraph() # Spacer

    # 3. Recipient
    p = doc.add_paragraph()
    p.add_run(f"À\n{recipient_data['name']}\nAt.: Departamento Contábil/Financeiro")
    doc.add_paragraph()

    # 4. Subject
    subject_map = {
        'bank': 'Confirmação de Saldos Bancários',
        'legal': 'Confirmação de Processos Judiciais',
        'supplier': 'Confirmação de Saldo de Fornecedores',
        'customer': 'Confirmação de Saldo de Clientes',
        'representation': 'Carta de Representação da Administração'
    }
    subject = subject_map.get(type, 'Solicitação de Confirmação')
    p = doc.add_paragraph()
    run = p.add_run(f"Ref.: {subject} - {client_data['name']}")
    run.bold = True
    doc.add_paragraph()

    # 5. Body
    body_text = ""
    if type == 'bank':
        body_text = f"Prezados Senhores,\n\nPara fins de auditoria de nossas demonstrações contábeis, solicitamos a gentileza de fornecerem diretamente aos nossos auditores independentes, AuditFlow Auditores Independentes, as informações detalhadas abaixo, relativas às nossas operações mantidas com V.Sas. na data base de {date_base}.\n\n1. Saldos em contas correntes e aplicações financeiras;\n2. Detalhes de empréstimos e financiamentos (saldo devedor, taxas, vencimentos, garantias);\n3. Outras responsabilidades diretas ou indiretas (fianças, avais, derivativos).\n\nA resposta deve ser enviada diretamente para o e-mail: auditoria@auditflow.com."
    elif type == 'legal':
        body_text = f"Prezados Senhores,\n\nSolicitamos a gentileza de fornecerem aos nossos auditores independentes, AuditFlow Auditores Independentes, informações sobre processos cíveis, trabalhistas, tributários e outros em que nossa empresa figure como Autora ou Ré, sob patrocínio desse escritório, com a posição em {date_base}.\n\nFavor informar para cada processo: número, natureza, instância atual, valor da causa, estimativa de perda (Provável, Possível, Remota) e valor estimado."
    elif type == 'representation':
        body_text = f"Prezados Auditores,\n\nEsta carta de representação é fornecida em conexão com a auditoria das demonstrações contábeis da {client_data['name']} para o exercício findo em {date_base}, com a finalidade de expressar uma opinião sobre se as demonstrações contábeis apresentam adequadamente, em todos os aspectos relevantes, a posição patrimonial e financeira da Entidade.\n\nConfirmamos que cumprimos nossas responsabilidades, conforme estabelecido nos termos do contrato de auditoria.\n\nAtenciosamente,\nAdministração"
    else:
        body_text = f"Prezados Senhores,\n\nNossos auditores independentes estão realizando a revisão de nossas contas. Solicitamos que confirmem diretamente a eles o saldo de nossa conta em seus registros na data de {date_base}.\n\nCaso o saldo não esteja de acordo, favor fornecer o demonstrativo das partidas em aberto.\n\nEsta solicitação não representa necessariamente um pedido de pagamento."

    p = doc.add_paragraph(body_text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.add_paragraph()
    doc.add_paragraph()

    # 6. Signatures
    doc.add_paragraph("Atenciosamente,")
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph("___________________________________")
    doc.add_paragraph(f"{client_data['name']}")
    doc.add_paragraph("Autorizado por: ___________________")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
