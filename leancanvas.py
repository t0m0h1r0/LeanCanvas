from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_UNDERLINE
from pptx.dml.color import RGBColor
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import yaml
import argparse

# PPTXファイルを作成するためのクラスを定義します
class PPTXCreator:
    def __init__(self, data, font_name='Yu Gothic UI', scale_width=3, scale_height=2.4):
        self.data = data
        self.prs = Presentation()
        self.prs.slide_width = Inches(16)
        self.prs.slide_height = Inches(9)
        self.font_name = font_name

        # Define positions here
        self.positions = {
            'Problem': (0, 0, scale_width, scale_height*2),
            'Solution': (scale_width, 0, scale_width, scale_height),
            'Key Metrics': (scale_width, scale_height, scale_width, scale_height),
            'Unique Value Proposition': (scale_width*2, 0, scale_width, scale_height*2),
            'Unfair Advantage': (scale_width*3, 0, scale_width, scale_height),
            'Channels': (scale_width*3, scale_height, scale_width, scale_height),
            'Customer Segments': (scale_width*4, 0, scale_width, scale_height*2),
            'Cost Structure': (0, scale_height*2, scale_width*2.5, scale_height),
            'Revenue Streams': (scale_width*2.5, scale_height*2, scale_width*2.5, scale_height),
        }

    def create_slide(self, project_name, date):
        blank_slide_layout = self.prs.slide_layouts[6]  # blank layout
        slide = self.prs.slides.add_slide(blank_slide_layout)
        
        # Add Project Name box
        project_name_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(0.5))
        tf = project_name_box.text_frame
        p = tf.add_paragraph()
        p.text = project_name
        p.font.size = Pt(20)
        p.font.name = self.font_name
        p.alignment = PP_ALIGN.LEFT
    
        # Add Date box
        date_box = slide.shapes.add_textbox(Inches(13), Inches(0.5), Inches(2), Inches(0.5))
        tf = date_box.text_frame
        p = tf.add_paragraph()
        p.text = str(date)  # Change here
        p.font.size = Pt(20)
        p.font.name = self.font_name
        p.alignment = PP_ALIGN.RIGHT
    
        return slide



    def add_textbox(self, slide, left, top, width, height, text, title):
        textbox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = textbox.text_frame
        tf.word_wrap = True
        tf.auto_size = False
        tf.text_anchor = MSO_ANCHOR.TOP
        tf.clear()

        # Add title with larger font size, green color, and underline
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.name = self.font_name
        p.font.color.rgb = RGBColor(0x00, 0x80, 0x00)  # Green color
        p.font.underline = MSO_UNDERLINE.SINGLE_LINE

        # Add content with bullet points
        for line in text.split('\n'):
            p = tf.add_paragraph()
            p.text = f"\u2022{line}"
            p.level = 0
            p.font.size = Pt(10)
            p.font.name = self.font_name

        # Add border to textbox
        line = textbox.line
        line.color.rgb = RGBColor(0, 0, 0)  # Black color
        line.width = Pt(1.0)

        return slide

    def create_presentation(self, h_offset=0.5, v_offset=1.3):
        for use_case in self.data['Use cases']:
            slide = self.create_slide(use_case['Project Name'], use_case['Date'])
            for section, (left, top, width, height) in self.positions.items():
                if section in use_case['Lean Canvas']:
                    text = "\n".join(use_case['Lean Canvas'][section])
                    self.add_textbox(slide, left+h_offset, top+v_offset, width, height, text, section)

    def save(self, output):
        self.prs.save(output)

class XLSXCreator:
    def __init__(self, data):
        self.data = data
        self.wb = Workbook()

    def create_worksheet(self):
        ws = self.wb.active
        ws.title = "Use cases"

        # ヘッダーの作成
        headers = ['Project Name', 'Date'] + list(self.data['Use cases'][0]['Lean Canvas'].keys())
        ws.append(headers)

        for use_case in self.data['Use cases']:
            row = [use_case['Project Name'], use_case['Date']]
            for section, content in use_case['Lean Canvas'].items():
                row.append('\n'.join(content))
            ws.append(row)

            # Adjust column width
            for idx, column in enumerate(ws.columns, start=1):
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[get_column_letter(idx)].width = adjusted_width

    def save(self, output):
        self.wb.save(output)


# コマンドライン引数を解析する関数です
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default="sample.pptx", help='Input YAML file')
    parser.add_argument('-p', '--pptx-output', default="sample.pptx", help='Output file (PPTX)')
    parser.add_argument('-x', '--xlsx-output', default="sample.xlsx", help='Output file (XLSX)')
    args = parser.parse_args()
    return args

# ファイル処理を行う関数です
def process_files(input_file, pptx_output, xlsx_output):
    with open(input_file, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    pptx_creator = PPTXCreator(data)
    pptx_creator.create_presentation()
    pptx_creator.save(pptx_output)

    xlsx_creator = XLSXCreator(data)
    xlsx_creator.create_worksheet()
    xlsx_creator.save(xlsx_output)

if __name__ == "__main__":
    args = parse_arguments()
    process_files(args.input, args.pptx_output, args.xlsx_output)
