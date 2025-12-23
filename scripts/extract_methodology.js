import ExcelJS from 'exceljs';
import path from 'path';

const filePath = path.join(process.cwd(), 'docs/Agent Partner AI/02 - Metodologia Vorcon/Cálculo_da_Materialidade_-_METODOLOGIA 2024.xlsx');

async function readExcel() {
    const workbook = new ExcelJS.Workbook();
    try {
        await workbook.xlsx.readFile(filePath);

        console.log("Worksheet Names:", workbook.worksheets.map(w => w.name));

        workbook.worksheets.forEach(sheet => {
            console.log(`\n--- Sheet: ${sheet.name} ---`);
            // Print first 20 rows
            sheet.eachRow((row, rowNumber) => {
                if (rowNumber <= 60) {
                    console.log(`R${rowNumber}:`, JSON.stringify(row.values));
                }
            });
        });
    } catch (err) {
        console.error("Error reading excel:", err);
    }
}

readExcel();
