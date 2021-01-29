import os
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer, Preformatted, Table, TableStyle

parent_path = os.path.dirname(os.path.abspath(__file__))
# Mono fonts to enable proper tab representation in pdf
pdfmetrics.registerFont(TTFont('DejaVuSansMono', parent_path + '/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansMonoBold', parent_path + '/DejaVuSansMono-Bold.ttf'))
font = 'DejaVuSansMono'
font_bold = 'DejaVuSansMonoBold'

# page size to A5
page_size = (148 * mm, 210 * mm)
# generate platypus template
margins = (15, 15, 30, 30)  # n s e w


def make_pdf(path_to_pdf, note_manager):
    """main function"""
    # platypus default template
    path_to_pdf = os.path.expanduser(path_to_pdf)
    doc = SimpleDocTemplate(path_to_pdf, pagesize=page_size,
                            topMargin=margins[0], bottonMargin=margins[1],
                            leftMargin=margins[2], rightMargin=margins[3])

    # instantiate flowable with first page (table of content)
    all_elements = make_first_page(note_manager.list)

    # add note pages
    for number, note in enumerate(note_manager.list):
        all_elements.extend(add_page(note, number))

    # build pdf ducument
    doc.multiBuild(all_elements)


def add_page(note, number):
    """build the page(s) for a given note"""
    flowables = []

    # drawing elements
    line = Drawing(page_size[0], 1)
    line.add(Line(0, 0, page_size[0] - (margins[2] + margins[3] + 10), 0))
    # spacer
    space = Spacer(1, 4 * mm)

    # title + anchor for link to table of content
    anchor = '<a name="anchor_' + str(number) + '"/>'
    text = anchor + note['title']
    style = make_style('Title', 20, bold=True)
    flowables.append(Paragraph(text, style))

    # subtitle
    if note['subtitle']:
        style = make_style('Title', 12)
        flowables.append(Paragraph(note['subtitle'], style))

    # author and year
    text = note['author'] + ' (' + note['year'] + ')'
    style = make_style('Title', 14)
    flowables.append(Paragraph(text, style))

    # Media type and episode:
    text = note['media_type']
    if note['episode']:
        text = text + ' - episode: ' + note['episode']
    if note['link']:
        text = text + '<br />\n' +\
               '<link href="' + note['link'] + '">' + 'External Resource' + '</link>'
    style = make_style('Title', 10)
    flowables.append(Paragraph(text, style))

    # one liner
    text = note['one_liner']
    style = make_style('BodyText', 12)
    flowables.extend([line,
                      Paragraph(text, style),
                      space, line
                      ])

    # notes
    text = format_str(note['notes'])
    style = make_style('BodyText', 12)
    flowables.append(Preformatted(text, style, maxLineLength=50))

    # go to next page
    flowables.append(PageBreak())
    return flowables


def make_style(name, size, bold=None):
    """set style class"""
    # preset styles in platypus
    style_dict = getSampleStyleSheet()  # styles.list() to print all available
    style = style_dict[name]
    if bold:
        style.fontName = font
    else:
        style.fontName = font
    style.fontSize = size
    return style


def format_str(my_str):
    """deal with tabs because reportlab does not do it"""
    # split text into lines
    split_str = my_str.splitlines()
    tab = 8
    split_str_new = []
    # replace each tab by corresponding numbers of white spaces
    for line in split_str:
        while line.find('\t') != -1:
            tab_pos = line.find('\t')
            white_space = ''.join([' ' for i in range(tab - tab_pos % tab)])
            line = line.replace('\t', white_space, 1)
        split_str_new.append(line)
    # return updated text
    return '\n'.join(split_str_new)


def make_first_page(list_of_notes):
    """make table of content: one column sorted by author and one by title"""
    body_style = make_style('BodyText', 10)
    head_style = make_style('BodyText', 12, bold=True)
    table_style = TableStyle([('VALIGN', (0, 1), (1, -1), 'TOP'),
                              ('INNERGRID', (0, 0), (1, -1), 0.25, colors.black),
                              ('BOTTOMPADDING', (0, 0), (1, 0), 15),
                              ('BOTTOMPADDING', (0, 1), (1, -1), 5),
                              ('TOPPADDING', (0, 1), (1, -1), 5)
                              ])
    # columns head
    table_head = (Paragraph('title', head_style), Paragraph('author', head_style))

    first_page = [Paragraph('Table of content', make_style('Title', 14, bold=True)),
                  Paragraph('ordered by', make_style('Title', 10))]

    # anchors are set in the notes' titles
    list_anchor = ['<link href="#anchor_' + str(i) + '" color="blue">' for i in range(len(list_of_notes))]

    # sort by title
    list_title = [note['title'].casefold().capitalize() + '</link>' for note in list_of_notes]
    sorted_title = sorted(zip(list_anchor, list_title), key=lambda x: x[1])
    title_column = [Paragraph(''.join(x), body_style) for x in list(sorted_title)]

    # sort by author
    list_author = [note['author'].casefold().capitalize() + '</link>' for note in list_of_notes]
    sorted_author = sorted(zip(list_anchor, list_author), key=lambda x: x[1])
    author_column = [Paragraph(''.join(x), body_style) for x in list(sorted_author)]

    # merge both list fot the Table class
    data = list(zip(title_column, author_column))
    # add columns head
    data.insert(0, table_head)
    # create Table
    t = Table(data, colWidths=[page_size[0]/3, page_size[0]/3])
    t.setStyle(table_style)
    # add Table to flowables
    first_page.append(t)
    # go to next page
    first_page.append(PageBreak())

    return first_page
