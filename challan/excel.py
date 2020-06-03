import xlsxwriter as xl
import os
from datetime import date
from tempfile import TemporaryDirectory

def format_date(date : date) -> str:
    return date.strftime('%b %d, %Y')

def main(challan):
    row = 0
    col = 0
    tmp_dir = TemporaryDirectory(prefix='excel')
    file = os.path.join(tmp_dir.name, 'challan_{}_excel.xlsx'.format(challan.number))
    wb = xl.Workbook(file)
    ws = wb.add_worksheet('Expert Traders')
    for product in challan.products.completed():
        data = [
            row+1,
            product.order_number,
            "Dhudheshwar Expert",
            format_date(product.date_shipped),
            product.name,
            product.quantity,
            product.size,
            product.get_fabric_display(),
            product.get_color_display(),
            format_date(product.kit.date_received),
            format_date(product.kit.date_return),
        ]
        for col, value in enumerate(data):
            ws.write(row, col, value)
        row += 1
    wb.close()
    return tmp_dir, file