from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_UNDERLINE
from pptx.dml.color import RGBColor
import yaml
import argparse

def create_slide(prs, title):
    blank_slide_layout = prs.slide_layouts[6]  # blank layout
    slide = prs.slides.add_slide(blank_slide_layout)
    textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(14.5), Inches(0.5))
    tf = textbox.text_frame
    p = tf.add_paragraph()
    p.text = title
    p.font.size = Pt(20)
    p.alignment = PP_ALIGN.CENTER
    return slide

def add_textbox(slide, left, top, width, height, text, title):
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

def create_slides(prs, data, positions, h_offset=0.5, v_offset=1.3):
    for use_case in data['Use cases']:
        title = f"{use_case['Project Name']} ({use_case['Date']})"
        slide = create_slide(prs, title)
        for section, (left, top, width, height) in positions.items():
            if section in use_case['Lean Canvas']:
                text = "\n".join(use_case['Lean Canvas'][section])
                add_textbox(slide, left+h_offset, top+v_offset, width, height, text, section)

def prepare_presentation(file_path, scale_width=3, scale_height=2.4):
    # Load data from YAML
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Create a 16:9 presentation
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Define position and size of each Lean Canvas sections
    positions = {
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

    return prs, data, positions

def parse_arguments():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create Lean Canvas presentation from YAML.')
    parser.add_argument('-i', '--input', help='Input YAML file.', default='sample.yaml')
    parser.add_argument('-o', '--output', help='Output PPTX file.', default='sample.pptx')
    return parser.parse_args()

def main():
    args = parse_arguments()

    prs, data, positions = prepare_presentation(args.input)

    # Add a slide for each use case
    create_slides(prs, data, positions)

    # Save the presentation
    prs.save(args.output)

if __name__ == "__main__":
    main()
