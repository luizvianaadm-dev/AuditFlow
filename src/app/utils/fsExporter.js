import html2pdf from 'html2pdf.js';
import ExcelJS from 'exceljs';
import { Document, Packer, Paragraph, Table, TableRow, TableCell, TextRun, AlignmentType, WidthType, BorderStyle, HeadingLevel, Footer } from 'docx';
import { saveAs } from 'file-saver';

// --- PDF Export ---
export const exportToPDF = (elementId, filename) => {
  const element = document.getElementById(elementId);
  if (!element) {
      console.error("Element not found for PDF export");
      return;
  }
  const opt = {
    margin:       10,
    filename:     filename || 'Demonstracoes_Financeiras.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  html2pdf().set(opt).from(element).save();
};

// --- Excel Export ---
export const exportToExcel = async (reportData, filename) => {
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'AuditFlow';
    workbook.created = new Date();

    const { balance_sheet, income_statement, notes, validations } = reportData;

    // Helper to add sheet with common styling
    const createSheet = (name) => {
        const sheet = workbook.addWorksheet(name);
        sheet.properties.defaultColWidth = 15;
        return sheet;
    };

    // 1. Balanço Patrimonial
    const bpSheet = createSheet('Balanço Patrimonial');
    bpSheet.columns = [
        { header: 'Grupo', key: 'group', width: 40 },
        { header: 'Saldo (R$)', key: 'balance', width: 20, style: { numFmt: '#,##0.00' } }
    ];

    // Add Header
    bpSheet.getRow(1).font = { bold: true, size: 12 };
    bpSheet.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } };

    const addBPSection = (title, items) => {
        bpSheet.addRow([title.toUpperCase(), '']).font = { bold: true };
        items.forEach(item => {
            bpSheet.addRow([item.label, item.value]);
        });
        bpSheet.addRow([]); // Spacer
    };

    if (balance_sheet) {
        addBPSection('Ativo Circulante', [
            { label: 'Circulante', value: balance_sheet.ativo.circulante },
            { label: 'Não Circulante', value: balance_sheet.ativo.nao_circulante },
            { label: 'Total Ativo', value: balance_sheet.ativo.total }
        ]);
        addBPSection('Passivo e PL', [
            { label: 'Passivo Circulante', value: balance_sheet.passivo.circulante },
            { label: 'Passivo Não Circulante', value: balance_sheet.passivo.nao_circulante },
            { label: 'Patrimônio Líquido', value: balance_sheet.passivo.patrimonio_liquido },
            { label: 'Total Passivo + PL', value: balance_sheet.passivo.total }
        ]);
    }

    // 2. DRE
    const dreSheet = createSheet('DRE');
    dreSheet.columns = [
        { header: 'Descrição', key: 'desc', width: 40 },
        { header: 'Valor (R$)', key: 'val', width: 20, style: { numFmt: '#,##0.00' } }
    ];
    dreSheet.getRow(1).font = { bold: true };
    dreSheet.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } };

    if (income_statement) {
        const dreRows = [
            { desc: 'Receita Líquida', val: income_statement.receita_liquida },
            { desc: 'Lucro Bruto', val: income_statement.lucro_bruto },
            { desc: 'Despesas Operacionais', val: -Math.abs(income_statement.despesas_operacionais) }, // Excel usually shows expenses as negative or parenthesis
            { desc: 'Lucro Líquido', val: income_statement.lucro_liquido }
        ];
        dreRows.forEach(r => dreSheet.addRow(r));
    }

    // 3. Notas
    const notesSheet = createSheet('Notas Explicativas');
    notesSheet.getColumn(1).width = 100;
    notesSheet.getColumn(1).alignment = { wrapText: true };

    if (notes) {
        Object.entries(notes).forEach(([key, text]) => {
            const titleRow = notesSheet.addRow([key.toUpperCase().replace('_', ' ')]);
            titleRow.font = { bold: true };
            const textRow = notesSheet.addRow([text]);
            textRow.height = 60; // Approximate height for wrapping
            notesSheet.addRow([]);
        });
    }

    // Write Buffer
    const buffer = await workbook.xlsx.writeBuffer();
    saveAs(new Blob([buffer]), filename || 'DF.xlsx');
};

// --- Word Export (DOCX) ---
export const exportToWord = async (reportData, contextData, filename) => {
    const { balance_sheet, income_statement, notes } = reportData;
    const { bloco_1_identificacao, bloco_2_periodo_contabil } = contextData || {};

    const companyName = bloco_1_identificacao?.razao_social || "Empresa Exemplo";
    const period = `Exercício findo em ${bloco_2_periodo_contabil?.data_encerramento_exercicio || "31/12/2024"}`;

    const createTable = (rows) => {
        return new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            rows: rows.map(r =>
                new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph({ text: r[0], alignment: AlignmentType.LEFT })], width: { size: 70, type: WidthType.PERCENTAGE } }),
                        new TableCell({ children: [new Paragraph({ text: typeof r[1] === 'number' ? r[1].toLocaleString('pt-BR', {minimumFractionDigits: 2}) : r[1], alignment: AlignmentType.RIGHT })], width: { size: 30, type: WidthType.PERCENTAGE } }),
                    ]
                })
            )
        });
    };

    const sections = [];

    // 1. Capa
    sections.push({
        properties: {},
        children: [
            new Paragraph({ text: companyName, heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { before: 2000 } }),
            new Paragraph({ text: "DEMONSTRAÇÕES FINANCEIRAS", heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { before: 500 } }),
            new Paragraph({ text: period, alignment: AlignmentType.CENTER, spacing: { after: 2000 } }),
            new Paragraph({ text: `Gerado em: ${new Date().toLocaleDateString()}`, alignment: AlignmentType.CENTER }),
        ]
    });

    // 2. Balanço
    const bpRows = [
        ["ATIVO", ""],
        ["Ativo Circulante", balance_sheet?.ativo.circulante || 0],
        ["Ativo Não Circulante", balance_sheet?.ativo.nao_circulante || 0],
        ["TOTAL DO ATIVO", balance_sheet?.ativo.total || 0],
        ["", ""],
        ["PASSIVO E PATRIMÔNIO LÍQUIDO", ""],
        ["Passivo Circulante", balance_sheet?.passivo.circulante || 0],
        ["Passivo Não Circulante", balance_sheet?.passivo.nao_circulante || 0],
        ["Patrimônio Líquido", balance_sheet?.passivo.patrimonio_liquido || 0],
        ["TOTAL DO PASSIVO E PL", balance_sheet?.passivo.total || 0],
    ];

    sections.push({
        properties: {},
        children: [
            new Paragraph({ text: "Balanço Patrimonial", heading: HeadingLevel.HEADING_2, pageBreakBefore: true }),
            createTable(bpRows)
        ]
    });

    // 3. DRE
    const dreRows = [
        ["Receita Líquida", income_statement?.receita_liquida || 0],
        ["Lucro Bruto", income_statement?.lucro_bruto || 0],
        ["Despesas Operacionais", income_statement?.despesas_operacionais || 0],
        ["Lucro Líquido do Exercício", income_statement?.lucro_liquido || 0],
    ];

    sections.push({
        properties: {},
        children: [
            new Paragraph({ text: "Demonstração do Resultado", heading: HeadingLevel.HEADING_2, spacing: { before: 500 } }),
            createTable(dreRows)
        ]
    });

    // 4. Notas
    const noteParagraphs = [
        new Paragraph({ text: "Notas Explicativas", heading: HeadingLevel.HEADING_2, pageBreakBefore: true })
    ];

    if (notes) {
        Object.entries(notes).forEach(([key, text], idx) => {
            noteParagraphs.push(new Paragraph({ text: `Nota ${idx + 1}: ${key.replace(/nota_\d+/i, '').replace(/_/g, ' ').toUpperCase()}`, heading: HeadingLevel.HEADING_3, spacing: { before: 300 } }));
            noteParagraphs.push(new Paragraph({ text: text, spacing: { after: 300 } }));
        });
    }

    sections.push({
        properties: {},
        children: noteParagraphs
    });

    // 5. Rodapé (Assinaturas)
    sections.push({
        properties: {},
        children: [
            new Paragraph({ text: "___________________________", alignment: AlignmentType.CENTER, spacing: { before: 1000 } }),
            new Paragraph({ text: "Contador Responsável", alignment: AlignmentType.CENTER }),
            new Paragraph({ text: "CRC XX.XXX/O-X", alignment: AlignmentType.CENTER }),
        ]
    });

    const doc = new Document({
        sections: sections,
        styles: {
            paragraphStyles: [
                {
                    id: "Normal",
                    name: "Normal",
                    run: {
                        font: "Arial",
                        size: 24, // 12pt
                    },
                },
            ],
        },
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, filename || "Demonstracoes_Financeiras.docx");
};
