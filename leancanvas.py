from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_UNDERLINE
from pptx.dml.color import RGBColor
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import yaml
import argparse

class PPTXCreator:
    def __init__(self, data, scale_width=3, scale_height=2.4):
        self.data = data
        self.prs = Presentation()
        self.prs.slide_width = Inches(16)
        self.prs.slide_height = Inches(9)

        # Define positions here
        self.positions = {
            'Problem': (0, 0, scale_width, scale_height*2),
            'Solution': (scale_width, 0, scale_width, scale_height),
            'Key Metrics': (scale_width, scale_height, scale_width, scale_height),
            'Unique Value Proposition': (scale_width*2, 0, scale_width, scale_height*2),
            'Unfair Advantage': (scale_width*3, 0, scale_width, scale_height),
            'Channels': (scale_width*3, scale_height, scale_width, scale_height),
            'Customer Segments': (scale_width*4, 0, scale_width, scale_height*2),
            'Cost Structure': (0, scale_height*2, scale_width*2, scale_height),
            'Revenue Streams': (scale_width*2, scale_height*2, scale_width*3, scale_height),
        }

    def create_slide(self, title):
        blank_slide_layout = self.prs.slide_layouts[6]  # blank layout
        slide = self.prs.slides.add_slide(blank_slide_layout)
        textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(14.5), Inches(0.5))
        tf = textbox.text_frame
        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(20)
        p.alignment = PP_ALIGN.CENTER
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
        p.font.color.rgb = RGBColor(0x00, 0x80, 0x00)  # Green color
        p.font.underline = MSO_UNDERLINE.SINGLE_LINE

        # Add content with bullet points
        for line in text.split('\n'):
            p = tf.add_paragraph()
            p.text = f"・{line}"
            p.level = 0
            p.font.size = Pt(9)

        # Add border to textbox
        line = textbox.line
        line.color.rgb = RGBColor(0, 0, 0)  # Black color
        line.width = Pt(1.0)

        return slide

    def create_presentation(self, h_offset=0.5, v_offset=1.3):
        for use_case in self.data['Use cases']:
            title = f"{use_case['Project Name']} ({use_case['Date']})"
            slide = self.create_slide(title)
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


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default="sample.pptx", help='Input YAML file')
    parser.add_argument('-p', '--pptx-output', default="sample.pptx", help='Output file (PPTX)')
    parser.add_argument('-x', '--xlsx-output', default="sample.xlsx", help='Output file (XLSX)')
    args = parser.parse_args()
    return args


def main():
    #args = parse_arguments()
    args = argparse.Namespace(input='sample.yaml', pptx_output='sample.pptx', xlsx_output='sample.xlsx')

    with open(args.input, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    pptx_creator = PPTXCreator(data)
    pptx_creator.create_presentation()
    pptx_creator.save(args.pptx_output)

    xlsx_creator = XLSXCreator(data)
    xlsx_creator.create_worksheet()
    xlsx_creator.save(args.xlsx_output)


if __name__ == "__main__":
    main()
