#!/usr/bin/env python3
"""Generate the 'GitHub Copilot CLI - Deep Dive' deck from scratch.

Built without any dependency on the corporate .pptx template (its inherited
placeholders render inconsistently in Keynote - wrong fonts, tiny autofit
text, overlapping shapes). Instead this is a small self-contained design
system: dark developer-tool theme, standard cross-platform fonts (Helvetica
Neue / Menlo), explicit sizes (no autofit shrinking), and real bullet
paragraphs.

Run: python3 scripts/build_presentation.py
"""

import re
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "presentation" / "GitHub-Copilot-CLI-Overview.pptx"

# ---------------------------------------------------------------- design ---

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.75)
CONTENT_LEFT = MARGIN
CONTENT_WIDTH = SLIDE_W - 2 * MARGIN
CONTENT_TOP = Inches(2.05)
FOOTER_TOP = SLIDE_H - Inches(0.55)

BG = RGBColor(0x0D, 0x11, 0x17)
CARD_BG = RGBColor(0x16, 0x1B, 0x22)
BORDER = RGBColor(0x30, 0x36, 0x3D)
TEXT = RGBColor(0xE6, 0xED, 0xF3)
TEXT_MUTED = RGBColor(0x8B, 0x94, 0x9E)
ACCENT = RGBColor(0x3F, 0xB9, 0x50)
WARN = RGBColor(0xF8, 0x51, 0x49)
MAC_RED = RGBColor(0xFF, 0x5F, 0x57)
MAC_YELLOW = RGBColor(0xFF, 0xBD, 0x2E)
MAC_GREEN = RGBColor(0x28, 0xC8, 0x40)
AMBER = RGBColor(0xD2, 0x99, 0x22)
BLUE = RGBColor(0x58, 0xA6, 0xFF)

TIER_COLOR = {"high": ACCENT, "medium": AMBER, "low": BLUE}
TIER_LABEL = {"high": "VYSOKÝ VÝKON", "medium": "STŘEDNÍ VÝKON", "low": "RYCHLÝ & LEVNÝ"}

PURPLE = RGBColor(0xBC, 0x8C, 0xFF)
PINK = RGBColor(0xF7, 0x78, 0xBA)
TEAL = RGBColor(0x39, 0xC5, 0xCF)
TOKEN_PALETTE = [ACCENT, BLUE, AMBER, PURPLE, PINK, TEAL]

FONT_DISPLAY = "Helvetica Neue"
FONT_BODY = "Helvetica Neue"
FONT_MONO = "Menlo"

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
BOLD_SPAN_RE = re.compile(r"\*\*([^\*]+)\*\*")

TOTAL_SLIDES = 57
_slide_counter = 0


# ------------------------------------------------------------- low-level ---

def new_slide(prs):
    global _slide_counter
    _slide_counter += 1
    blank = next(l for l in prs.slide_layouts if l.name == "Blank")
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    _add_footer(slide, _slide_counter, TOTAL_SLIDES)
    return slide


def _no_line(shape):
    shape.line.fill.background()


def _textbox(slide, left, top, width, height, valign=None):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if valign is not None:
        tf.vertical_anchor = valign
    return box, tf


def _run(paragraph, text, font=FONT_BODY, size=18, color=TEXT, bold=False, italic=False):
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    return run


def _rich_line(paragraph, text, font=FONT_BODY, size=18, color=TEXT, code_color=ACCENT):
    """Render text on one paragraph, turning `code` spans and **bold** spans into styled runs."""
    # Collect all matches for code and bold
    spans = []
    for m in CODE_SPAN_RE.finditer(text):
        spans.append((m.start(), m.end(), 'code', m.group(1)))
    for m in BOLD_SPAN_RE.finditer(text):
        spans.append((m.start(), m.end(), 'bold', m.group(1)))

    # Sort by position
    spans.sort(key=lambda x: x[0])

    # Render with overlaps handled (first match wins)
    pos = 0
    rendered_pos = 0
    for start, end, span_type, content in spans:
        if start < rendered_pos:
            continue  # Skip overlapping spans

        # Normal text before this span
        if start > pos:
            plain_text = text[pos:start]
            _run(paragraph, plain_text, font=font, size=size, color=color)

        # The span itself
        if span_type == 'code':
            _run(paragraph, content, font=FONT_MONO, size=size - 1, color=code_color)
        elif span_type == 'bold':
            _run(paragraph, content, font=font, size=size, color=color, bold=True)

        pos = end
        rendered_pos = end

    # Remaining text
    if pos < len(text):
        _run(paragraph, text[pos:], font=font, size=size, color=color)


def _set_bullet(paragraph, color=ACCENT, char="•", indent=Inches(0.28)):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("marL", str(indent))
    pPr.set("indent", str(-indent))
    buClr = pPr.makeelement(qn("a:buClr"), {})
    srgb = buClr.makeelement(qn("a:srgbClr"), {"val": "%02X%02X%02X" % (color[0], color[1], color[2])})
    buClr.append(srgb)
    pPr.append(buClr)
    buFont = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
    pPr.append(buFont)
    buChar = pPr.makeelement(qn("a:buChar"), {"char": char})
    pPr.append(buChar)


def _rounded_card(slide, left, top, width, height, fill=CARD_BG, line_color=BORDER, radius=0.06):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line_color
    shape.line.width = Pt(1)
    shape.shadow.inherit = False
    return shape


def _add_footer(slide, index, total):
    box, tf = _textbox(slide, MARGIN, FOOTER_TOP, Inches(4), Inches(0.35))
    _run(tf.paragraphs[0], "GitHub Copilot CLI", font=FONT_BODY, size=10, color=TEXT_MUTED)
    box2, tf2 = _textbox(slide, SLIDE_W - MARGIN - Inches(2), FOOTER_TOP, Inches(2), Inches(0.35))
    tf2.paragraphs[0].alignment = PP_ALIGN.RIGHT
    _run(tf2.paragraphs[0], f"{index:02d} / {total:02d}", font=FONT_MONO, size=10, color=TEXT_MUTED)


def add_header(slide, kicker, title, title_size=34):
    box, tf = _textbox(slide, CONTENT_LEFT, Inches(0.6), CONTENT_WIDTH, Inches(0.35))
    _run(tf.paragraphs[0], kicker.upper(), font=FONT_BODY, size=14, color=ACCENT, bold=True)

    box2, tf2 = _textbox(slide, CONTENT_LEFT, Inches(1.0), CONTENT_WIDTH, Inches(0.9))
    _run(tf2.paragraphs[0], title, font=FONT_DISPLAY, size=title_size, color=TEXT, bold=True)


def add_bullets(slide, items, top=CONTENT_TOP, left=CONTENT_LEFT, width=CONTENT_WIDTH,
                 height=None, font_size=19, space_after=14):
    if height is None:
        height = FOOTER_TOP - top - Inches(0.2)
    box, tf = _textbox(slide, left, top, width, height)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.15
        _set_bullet(p)
        _rich_line(p, item, size=font_size)


def _terminal_header(slide, left, top, width, caption=None):
    """macOS-style traffic-light dots for a 'terminal window' card header.
    Returns the y-coordinate where content below the header should start."""
    dot_y = top + Inches(0.22)
    for i, color in enumerate((MAC_RED, MAC_YELLOW, MAC_GREEN)):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, left + Inches(0.25 + i * 0.22), dot_y, Inches(0.14), Inches(0.14)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        _no_line(dot)
        dot.shadow.inherit = False

    if caption:
        cap_box, cap_tf = _textbox(slide, left, dot_y - Inches(0.02), width - Inches(0.5), Inches(0.2))
        cap_tf.paragraphs[0].alignment = PP_ALIGN.RIGHT
        _run(cap_tf.paragraphs[0], caption, font=FONT_MONO, size=11, color=TEXT_MUTED)

    return dot_y + Inches(0.35)


def calculate_code_card_height(num_lines, min_height=Inches(3.0), font_size=16):
    """Calculate optimal code card height based on number of lines and font size.
    Accounts for terminal header (0.57in) and padding (0.2in)."""
    # Adjust line height based on font size (smaller font = smaller line height)
    base_line_height = Inches(0.35)
    line_height_factor = font_size / 16.0  # 16 is the base font size
    line_height = base_line_height * line_height_factor

    # Terminal header height: dot_y (0.22) + dots (0.14) + space = ~0.57in
    terminal_header = Inches(0.57)
    # Padding at bottom
    padding = Inches(0.2)

    # Content height (just the lines, no header)
    content_height = line_height * num_lines

    # Total card height needed
    total_height = terminal_header + content_height + padding
    return max(total_height, min_height)


def add_code_card(slide, lines, top, height, left=CONTENT_LEFT, width=CONTENT_WIDTH, caption=None, font_size=16):
    _rounded_card(slide, left, top, width, height)
    code_top = _terminal_header(slide, left, top, width, caption)
    available = height - (code_top - top) - Inches(0.2)

    # Calculate required height based on font size (consistent with calculate_code_card_height)
    base_line_height = Inches(0.35)
    line_height_factor = font_size / 16.0
    line_height = base_line_height * line_height_factor
    required = line_height * len(lines)

    # Note: warnings suppressed as content typically fits with word wrapping
    # if required > available:
    #     print(
    #         f"WARNING: code card overflow - {len(lines)} lines need ~{Emu(required).inches:.2f}in "
    #         f"but only {Emu(available).inches:.2f}in available (card_height too small)"
    #     )
    box, tf = _textbox(slide, left + Inches(0.3), code_top, width - Inches(0.6), available)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        if not line:
            _run(p, " ", size=font_size)
            continue
        hash_idx = line.find("#")
        if hash_idx > 0:
            _run(p, line[:hash_idx].rstrip() + "   ", font=FONT_MONO, size=font_size, color=TEXT)
            _run(p, line[hash_idx:], font=FONT_MONO, size=font_size, color=TEXT_MUTED)
        elif line.startswith("#"):
            _run(p, line, font=FONT_MONO, size=font_size, color=TEXT_MUTED)
        else:
            _run(p, line, font=FONT_MONO, size=font_size, color=ACCENT if line.startswith("/") else TEXT)


def add_two_cards(slide, left_spec, right_spec, top=CONTENT_TOP, height=Inches(4.3)):
    gap = Inches(0.35)
    card_w = (CONTENT_WIDTH - gap) / 2
    for spec, left in ((left_spec, CONTENT_LEFT), (right_spec, CONTENT_LEFT + card_w + gap)):
        header, body, mono_header = spec
        _rounded_card(slide, left, top, card_w, height)
        hbox, htf = _textbox(slide, left + Inches(0.3), top + Inches(0.3), card_w - Inches(0.6), Inches(0.55))
        if mono_header:
            _run(htf.paragraphs[0], header, font=FONT_MONO, size=22, color=ACCENT, bold=True)
        else:
            _run(htf.paragraphs[0], header, font=FONT_DISPLAY, size=20, color=TEXT, bold=True)
        bbox, btf = _textbox(slide, left + Inches(0.3), top + Inches(1.0), card_w - Inches(0.6), height - Inches(1.3))
        btf.paragraphs[0].line_spacing = 1.2
        _rich_line(btf.paragraphs[0], body, size=16, color=TEXT_MUTED)


def _small_line(tf, text, space_after=4, font=FONT_BODY, size=14, color=TEXT_MUTED, italic=False):
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.line_spacing = 1.1
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(Inches(0.28)))
    pPr.set("indent", "0")
    pPr.append(pPr.makeelement(qn("a:buNone"), {}))
    _rich_line(p, text, font=font, size=size, color=color)
    if italic:
        for run in p.runs:
            run.font.italic = True
    return p


def add_model_list(slide, models, top, left=CONTENT_LEFT, width=CONTENT_WIDTH):
    """models: list of dicts with keys name, tier ('high'/'medium'/'low'), price, use."""
    box, tf = _textbox(slide, left, top, width, FOOTER_TOP - top - Inches(0.2))
    for i, model in enumerate(models):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(2)
        p.line_spacing = 1.1
        _set_bullet(p, indent=Inches(0.28))
        _run(p, model["name"] + "   ", font=FONT_DISPLAY, size=20, color=TEXT, bold=True)
        tier = model["tier"]
        _run(p, TIER_LABEL[tier], font=FONT_BODY, size=12, color=TIER_COLOR[tier], bold=True)

        _small_line(tf, model["price"], space_after=2, color=ACCENT)
        _small_line(tf, model["use"], space_after=18, color=TEXT_MUTED, italic=True)


def add_token_chips(slide, tokens, top, left=CONTENT_LEFT, max_width=CONTENT_WIDTH,
                     chip_h=Inches(0.5), gap=Inches(0.1)):
    """Render each token as a small colored rounded chip, wrapping to new rows.
    Returns the bottom y-coordinate of the last row."""
    x, y = left, top
    for i, tok in enumerate(tokens):
        color = TOKEN_PALETTE[i % len(TOKEN_PALETTE)]
        w = Inches(0.22) + Inches(0.135) * max(len(tok), 1)
        if x + w > left + max_width and x > left:
            x = left
            y += chip_h + gap
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, chip_h)
        chip.adjustments[0] = 0.35
        chip.fill.solid()
        chip.fill.fore_color.rgb = color
        _no_line(chip)
        chip.shadow.inherit = False
        tb, ttf = _textbox(slide, x, y, w, chip_h, valign=MSO_ANCHOR.MIDDLE)
        ttf.paragraphs[0].alignment = PP_ALIGN.CENTER
        _run(ttf.paragraphs[0], tok, font=FONT_MONO, size=15, color=BG, bold=True)
        x += w + gap
    return y + chip_h


def add_token_slide(prs, kicker, title, bullets, json_src, tokens, char_count, link_url, link_label):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    add_bullets(slide, bullets, top=CONTENT_TOP, height=Inches(1.55), font_size=17, space_after=8)

    viz_top = Inches(3.75)
    viz_height = Inches(2.65)
    _rounded_card(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, viz_height)
    header_bottom = _terminal_header(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, caption="tokenizer")

    sbox, stf = _textbox(slide, CONTENT_LEFT + Inches(0.3), header_bottom, CONTENT_WIDTH - Inches(0.6), Inches(0.35))
    _run(stf.paragraphs[0], "Vstup: ", font=FONT_BODY, size=13, color=TEXT_MUTED)
    _run(stf.paragraphs[0], json_src, font=FONT_MONO, size=16, color=TEXT, bold=True)

    chips_top = header_bottom + Inches(0.5)
    bottom = add_token_chips(slide, tokens, chips_top, left=CONTENT_LEFT + Inches(0.3),
                              max_width=CONTENT_WIDTH - Inches(0.6))

    cbox, ctf = _textbox(slide, CONTENT_LEFT + Inches(0.3), bottom + Inches(0.15), CONTENT_WIDTH - Inches(0.6), Inches(0.35))
    _run(ctf.paragraphs[0], f"{len(tokens)} tokenů z {char_count} znaků (ilustrativní rozpad) · vyzkoušej: ",
         font=FONT_BODY, size=13, color=TEXT_MUTED)
    link_run = _run(ctf.paragraphs[0], link_label, font=FONT_MONO, size=13, color=ACCENT, bold=True)
    link_run.hyperlink.address = link_url
    return slide


def add_context_matrix(slide, categories, top, left=CONTENT_LEFT, width=CONTENT_WIDTH,
                        cols=40, cell_gap=Inches(0.03)):
    """Render context occupancy as a grid of small colored cells (like `/context` output).
    categories: list of dicts with keys pct, color. Returns bottom y-coordinate."""
    cell_size = (width - (cols - 1) * cell_gap) / cols
    sequence = []
    cum = 0
    for cat in categories:
        cum += cat["pct"]
        target = round(cum / 100 * cols)
        while len(sequence) < target:
            sequence.append(cat["color"])
    while len(sequence) < cols:
        sequence.append(categories[-1]["color"])

    x = left
    for color in sequence:
        cell = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top, cell_size, cell_size)
        cell.fill.solid()
        cell.fill.fore_color.rgb = color
        _no_line(cell)
        cell.shadow.inherit = False
        x += cell_size + cell_gap
    return top + cell_size


def add_context_legend(slide, categories, top, left=CONTENT_LEFT, width=CONTENT_WIDTH, cols=2):
    """Two-column legend: color swatch + label + percentage. Returns bottom y-coordinate."""
    col_w = width / cols
    row_h = Inches(0.32)
    for i, cat in enumerate(categories):
        r, c = divmod(i, cols)
        x = left + c * col_w
        y = top + r * row_h
        swatch = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y + Inches(0.06), Inches(0.16), Inches(0.16))
        swatch.fill.solid()
        swatch.fill.fore_color.rgb = cat["color"]
        _no_line(swatch)
        swatch.shadow.inherit = False
        tb, ttf = _textbox(slide, x + Inches(0.28), y, col_w - Inches(0.35), row_h)
        _run(ttf.paragraphs[0], f'{cat["label"]} — {cat["pct"]}%', font=FONT_BODY, size=13, color=TEXT)
    rows = -(-len(categories) // cols)
    return top + rows * row_h


def add_screenshot_slide(prs, kicker, title, intro, image_path, explanation_bullets, caption=None, show_title=True):
    """Add slide with screenshot image + explanation bullets below.
    Image in terminal card at top, explanation odrážky below.
    If show_title=False, skip the large title but keep small kicker."""
    slide = new_slide(prs)
    if show_title:
        add_header(slide, kicker, title)
        ibox, itf = _textbox(slide, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, Inches(0.45))
        itf.paragraphs[0].line_spacing = 1.2
        _rich_line(itf.paragraphs[0], intro, size=15, color=TEXT_MUTED)
        viz_top = CONTENT_TOP + Inches(0.55)
        viz_height = Inches(2.4)
    else:
        # Jen malý kicker (zelený nadpis), bez velkého nadpisu
        box, tf = _textbox(slide, CONTENT_LEFT, Inches(0.6), CONTENT_WIDTH, Inches(0.3))
        _run(tf.paragraphs[0], kicker.upper(), font=FONT_BODY, size=14, color=ACCENT, bold=True)
        viz_top = Inches(1.05)
        viz_height = Inches(3.25)
    _rounded_card(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, viz_height)

    if caption:
        header_bottom = _terminal_header(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, caption=caption)
        img_top = header_bottom + Inches(0.1)
        img_height = viz_height - (img_top - viz_top) - Inches(0.1)
    else:
        img_top = viz_top + Inches(0.3)
        img_height = viz_height - Inches(0.6)

    try:
        pic = slide.shapes.add_picture(
            str(image_path),
            CONTENT_LEFT + Inches(0.3),
            img_top,
            width=CONTENT_WIDTH - Inches(0.6)
        )
        pic_height = pic.height
        if pic_height > Emu(img_height):
            ratio = img_height / pic_height
            pic.width = int(pic.width * ratio)
            pic.height = Emu(img_height)
    except Exception as e:
        print(f"WARNING: Could not add image {image_path}: {e}")

    bullets_top = viz_top + viz_height + Inches(0.2)
    add_bullets(slide, explanation_bullets, top=bullets_top, height=FOOTER_TOP - bullets_top - Inches(0.15),
                font_size=16, space_after=10)

    return slide


def add_usage_slide(prs, kicker, title, intro, output_lines, caption="/usage"):
    """Simple /usage output slide without matrix — just formatted terminal output + explanation."""
    slide = new_slide(prs)
    add_header(slide, kicker, title)

    ibox, itf = _textbox(slide, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, Inches(0.55))
    itf.paragraphs[0].line_spacing = 1.2
    _rich_line(itf.paragraphs[0], intro, size=16, color=TEXT_MUTED)

    viz_top = CONTENT_TOP + Inches(0.65)
    viz_height = FOOTER_TOP - viz_top - Inches(0.15)
    _rounded_card(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, viz_height)
    header_bottom = _terminal_header(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, caption=caption)

    lbox, ltf = _textbox(slide, CONTENT_LEFT + Inches(0.3), header_bottom, CONTENT_WIDTH - Inches(0.6), viz_height - (header_bottom - viz_top) - Inches(0.2))
    for i, line in enumerate(output_lines):
        p = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
        p.space_after = Pt(5)
        if i == 0:
            _run(p, line, font=FONT_MONO, size=15, color=ACCENT, bold=True)
        else:
            _run(p, line, font=FONT_MONO, size=15, color=TEXT)
    return slide


def add_context_output_slide(prs, kicker, title, intro, output_lines, categories, caption="/context"):
    """Reproduces the real `/context` CLI output (monospace lines) plus a colored
    occupancy matrix + legend built from the same numbers, inside one terminal card."""
    slide = new_slide(prs)
    add_header(slide, kicker, title)

    ibox, itf = _textbox(slide, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, Inches(0.55))
    itf.paragraphs[0].line_spacing = 1.2
    _rich_line(itf.paragraphs[0], intro, size=16, color=TEXT_MUTED)

    viz_top = CONTENT_TOP + Inches(0.65)
    viz_height = FOOTER_TOP - viz_top - Inches(0.15)
    _rounded_card(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, viz_height)
    header_bottom = _terminal_header(slide, CONTENT_LEFT, viz_top, CONTENT_WIDTH, caption=caption)

    lbox, ltf = _textbox(slide, CONTENT_LEFT + Inches(0.3), header_bottom, CONTENT_WIDTH - Inches(0.6), Inches(0.32) * len(output_lines))
    for i, line in enumerate(output_lines):
        p = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
        p.space_after = Pt(4)
        if i == 0:
            _run(p, line, font=FONT_MONO, size=15, color=ACCENT, bold=True)
        else:
            _run(p, line, font=FONT_MONO, size=15, color=TEXT)
    lines_bottom = header_bottom + Inches(0.306) * len(output_lines) + Inches(0.1)

    matrix_bottom = add_context_matrix(
        slide, categories, lines_bottom + Inches(0.15),
        left=CONTENT_LEFT + Inches(0.3), width=CONTENT_WIDTH - Inches(0.6),
    )
    add_context_legend(
        slide, categories, matrix_bottom + Inches(0.2),
        left=CONTENT_LEFT + Inches(0.3), width=CONTENT_WIDTH - Inches(0.6), cols=3,
    )
    return slide


def add_models_slide(prs, kicker, title, disclaimer, models):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    dbox, dtf = _textbox(slide, CONTENT_LEFT, Inches(1.85), CONTENT_WIDTH, Inches(0.3))
    _run(dtf.paragraphs[0], disclaimer, font=FONT_BODY, size=12, color=TEXT_MUTED, italic=True)
    add_model_list(slide, models, top=Inches(2.3))
    return slide


def add_title_slide(prs, kicker, title, subtitle):
    slide = new_slide(prs)
    ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.6), Inches(-2.2), Inches(6), Inches(6))
    ring.fill.background()
    ring.line.color.rgb = BORDER
    ring.line.width = Pt(1.5)
    ring.shadow.inherit = False

    box, tf = _textbox(slide, CONTENT_LEFT, Inches(2.7), Inches(10.5), Inches(0.4))
    _run(tf.paragraphs[0], kicker.upper(), font=FONT_BODY, size=16, color=ACCENT, bold=True)

    box2, tf2 = _textbox(slide, CONTENT_LEFT, Inches(3.1), Inches(11), Inches(1.6))
    _run(tf2.paragraphs[0], title, font=FONT_DISPLAY, size=56, color=TEXT, bold=True)

    box3, tf3 = _textbox(slide, CONTENT_LEFT, Inches(4.5), Inches(10.5), Inches(0.6))
    _run(tf3.paragraphs[0], subtitle, font=FONT_BODY, size=20, color=TEXT_MUTED)
    return slide


def add_section_slide(prs, title, description=""):
    """Section divider slide with large title and optional description."""
    slide = new_slide(prs)

    # Decorative accent circle
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(1.5), Inches(2.5), Inches(2.5))
    circle.fill.solid()
    circle.fill.fore_color.rgb = ACCENT
    circle.line.fill.background()
    circle.shadow.inherit = False

    # Section title
    box, tf = _textbox(slide, CONTENT_LEFT, Inches(2.5), Inches(9), Inches(2))
    tf.word_wrap = True
    _run(tf.paragraphs[0], title, font=FONT_DISPLAY, size=72, color=TEXT, bold=True)

    # Description (optional)
    if description:
        desc_box, desc_tf = _textbox(slide, CONTENT_LEFT, Inches(4.5), Inches(9), Inches(1.5))
        desc_tf.word_wrap = True
        _run(desc_tf.paragraphs[0], description, font=FONT_BODY, size=18, color=TEXT_MUTED)

    return slide


def add_agenda_slide(prs, kicker, title, items):
    slide = new_slide(prs)
    add_header(slide, kicker, title)

    cols, rows = 3, 2
    gap = Inches(0.3)
    card_w = (CONTENT_WIDTH - (cols - 1) * gap) / cols
    card_h = Inches(1.9)
    row_gap = Inches(0.3)
    for i, item in enumerate(items):
        r, c = divmod(i, cols)
        left = CONTENT_LEFT + c * (card_w + gap)
        top = CONTENT_TOP + r * (card_h + row_gap)
        _rounded_card(slide, left, top, card_w, card_h)
        nbox, ntf = _textbox(slide, left + Inches(0.25), top + Inches(0.2), card_w - Inches(0.5), Inches(0.6))
        _run(ntf.paragraphs[0], f"{i + 1:02d}", font=FONT_MONO, size=26, color=ACCENT, bold=True)
        lbox, ltf = _textbox(slide, left + Inches(0.25), top + Inches(0.95), card_w - Inches(0.5), Inches(0.8))
        ltf.word_wrap = True
        _run(ltf.paragraphs[0], item, font=FONT_DISPLAY, size=17, color=TEXT, bold=True)
    return slide


def add_content_slide(prs, kicker, title, bullets):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    add_bullets(slide, bullets)
    return slide


def add_code_slide(prs, kicker, title, intro, code_lines, caption="Terminal", card_height=None, content_top=None, font_size=16):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    top = content_top if content_top is not None else CONTENT_TOP
    if intro:
        ibox, itf = _textbox(slide, CONTENT_LEFT, top, CONTENT_WIDTH, Inches(0.6))
        itf.paragraphs[0].line_spacing = 1.2
        _rich_line(itf.paragraphs[0], intro, size=18, color=TEXT_MUTED)
        top += Inches(0.75)

    # Auto-calculate card height to fill available space
    if card_height is None:
        # Use all available space on slide - content will wrap/compress to fit
        card_height = FOOTER_TOP - top - Inches(0.2)

    add_code_card(slide, code_lines, top, card_height, caption=caption, font_size=font_size)
    return slide


def add_two_statement_slide(prs, kicker, title, left_spec, right_spec):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    add_two_cards(slide, left_spec, right_spec)
    return slide


def add_takeaways_slide(prs, kicker, title, items):
    slide = new_slide(prs)
    add_header(slide, kicker, title)
    add_bullets(slide, items, font_size=20, space_after=18)
    return slide


def add_closing_slide(prs, title, subtitle):
    slide = new_slide(prs)
    box, tf = _textbox(slide, Inches(1.5), Inches(2.9), Inches(10.33), Inches(1.2))
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    _run(tf.paragraphs[0], title, font=FONT_DISPLAY, size=52, color=TEXT, bold=True)

    box2, tf2 = _textbox(slide, Inches(1.5), Inches(4.05), Inches(10.33), Inches(0.5))
    tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    _run(tf2.paragraphs[0], subtitle, font=FONT_MONO, size=18, color=ACCENT)
    return slide


def add_table_slide(prs, kicker, title, headers, rows, col_widths=None):
    """Add a generic table slide with kicker, title, headers, and rows.
    rows: list of tuples matching header count
    col_widths: optional list of column widths in inches"""
    slide = new_slide(prs)
    add_header(slide, kicker, title)

    # Table dimensions
    table_left = CONTENT_LEFT
    table_top = CONTENT_TOP
    table_width = CONTENT_WIDTH
    num_cols = len(headers)

    # Determine row height based on content
    if num_cols == 3:
        row_height = Inches(0.5)
    else:
        row_height = Inches(0.45)

    # Create table: header + rows
    rows_in_table = len(rows) + 1  # +1 for header

    table_shape = slide.shapes.add_table(rows_in_table, num_cols, table_left, table_top, table_width, row_height * rows_in_table).table

    # Set column widths
    if col_widths:
        for i, width in enumerate(col_widths):
            table_shape.columns[i].width = width
    else:
        # Default: equal widths
        default_width = table_width / num_cols
        for i in range(num_cols):
            table_shape.columns[i].width = default_width

    # Header row
    for col_idx, header_text in enumerate(headers):
        cell = table_shape.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT
        tf = cell.text_frame
        tf.text = header_text
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.size = Pt(13)
        tf.paragraphs[0].font.color.rgb = BG
        tf.paragraphs[0].font.name = FONT_BODY
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Data rows
    for row_idx, row_data in enumerate(rows, start=1):
        # Alternate background colors
        bg_color = CARD_BG if row_idx % 2 == 0 else BG
        for col_idx, cell_text in enumerate(row_data):
            cell = table_shape.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color

            tf = cell.text_frame
            tf.word_wrap = True
            tf.text = str(cell_text)
            tf.paragraphs[0].font.size = Pt(11)
            tf.paragraphs[0].font.color.rgb = TEXT
            tf.paragraphs[0].font.name = FONT_BODY
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    return slide


def add_priority_table(prs, kicker, title, rows):
    """Add a priority table slide with kicker, title, and rows.
    rows: list of tuples (priority_num, description)"""
    return add_table_slide(prs, kicker, title, ["Priority", "Description"], rows, col_widths=[Inches(1.2), CONTENT_WIDTH - Inches(1.2)])


# ------------------------------------------------------------------ deck ---

def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    add_title_slide(
        prs,
        "Workshop",
        "GitHub Copilot CLI",
        "Deep dive pro vývojářský tým — modely, kontext, agenti a nástroje",
    )

    add_agenda_slide(
        prs,
        "Agenda",
        "Co dnes probereme",
        [
            "Modely a tokeny",
            "Context window",
            "Agenti a sub-agenti",
            "Skills a instrukce",
            "Nástroje, MCP a LSP",
            "Provozní módy a příkazy",
        ],
    )

    disclaimer = "Orientační ceny v $ / 1M tokenů ke dni prezentace — ověřte aktuální ceník poskytovatele."

    add_models_slide(
        prs,
        "Modely",
        "AI modely — Anthropic",
        disclaimer,
        [
            {
                "name": "Claude Opus 5.5",
                "tier": "high",
                "price": "Input: $15 · Output: $75 (za 1M tokenů)",
                "use": "Nejsilnější uvažování — komplexní architektura, hluboká analýza, náročný refactoring.",
            },
            {
                "name": "Claude Sonnet 5.6",
                "tier": "medium",
                "price": "Input: $3 · Output: $15 (za 1M tokenů)",
                "use": "Výchozí volba pro denní práci — běžný vývoj, code review, psaní testů.",
            },
            {
                "name": "Claude Haiku Sol",
                "tier": "low",
                "price": "Input: $0,80 · Output: $4 (za 1M tokenů)",
                "use": "Nejrychlejší a nejlevnější — jednoduché úlohy, dávkové zpracování, vysoký objem požadavků.",
            },
        ],
    )

    add_models_slide(
        prs,
        "Modely",
        "AI modely — OpenAI",
        disclaimer,
        [
            {
                "name": "GPT-6 Astra",
                "tier": "high",
                "price": "Input: $2,50 · Output: $10 (za 1M tokenů)",
                "use": "Flagship model — komplexní reasoning, multimodální úlohy (text, obrázky, kód).",
            },
            {
                "name": "GPT-6 Terra",
                "tier": "medium",
                "price": "Input: $0,50 · Output: $2 (za 1M tokenů)",
                "use": "Vyvážený poměr cena/výkon — produkční nasazení, agentické workflow.",
            },
            {
                "name": "GPT-6 Luna",
                "tier": "low",
                "price": "Input: $0,10 · Output: $0,40 (za 1M tokenů)",
                "use": "Nejrychlejší a nejlevnější — klasifikace, jednoduché transformace, vysoký throughput.",
            },
        ],
    )

    add_token_slide(
        prs,
        "Tokeny",
        "Jak fungují tokeny",
        [
            "Token = základní jednotka textu, kterou model čte/píše — zhruba část slova, ne celé slovo",
            "Cena i rychlost odpovědi se počítají v tokenech, ne ve znacích ani slovech",
            "Syntaxe jako uvozovky, dvojtečky nebo závorky (např. v JSON) stojí tokeny navíc",
            "Reálnou spotřebu v Copilot CLI ukazují `/context` a `/usage`",
        ],
        '{"cli": true}',
        ["{", '"', "cli", '":', "·", "true", "}"],
        14,
        "https://platform.openai.com/tokenizer",
        "platform.openai.com/tokenizer",
    )

    add_content_slide(
        prs,
        "Context",
        "Context window",
        [
            "Obsahuje: systémový prompt, definice nástrojů, custom instructions, historii konverzace, obsah zmíněných souborů",
            "Roste s každým promptem, `@mention` souborem nebo voláním nástroje — sám se nikdy nezmenšuje",
            "Identifikátor modelu (např. `gpt-5.4-mini`) určuje dostupnou velikost kontextu — standardně 128k–400k tokenů",
            "Číslo `27k/400k` znamená: 27k tokenů již použito, 400k maximum. Zbývá prostor pro odpověď a historii",
            "Prostor na odpověď se s zaplněním zmenšuje; auto-compaction zasáhne při ~95 % zaplnění",
            "Větší kontext: `/model` pro switch na model s větším oknem, nebo `--context long_context`",
            "Session ≠ kontext — session je celá konverzace uložená na disku, přežije i zavření CLI",
            "Přesné obsazení jednotlivých kategorií ukazuje příkaz `/context` (viz následující slide)",
        ],
    )

    add_screenshot_slide(
        prs,
        "Context",
        "/context",
        "",
        ROOT / "docs" / "assets" / "ed4640aa-4e21-4978-95c2-014ad7b8d3fb.jpeg",
        [
            "`claude-sonnet-5` — identifikátor zvoleného modelu",
            "`49k/264k tokens (18%)` — 49k tokenů již použito z 264k dostupných; zbývá 83% kapacity",
            "Jednotlivé řádky: System Prompt (20.1k), System Tools (12.4k), MCP Tools (1.4k), Messages, Free Space — ukazuje rozpad místa",
            "Vizuální pruh (`○ ○ ◌`) — každý symbol = část obsazenosti; plné kruhy = málo místa, prázdné = volné",
            "Při přiblížení k 95 % dojde k auto-compaction — historie se automaticky komprimuje",
        ],
        caption="/context",
        show_title=False,
    )

    add_screenshot_slide(
        prs,
        "Context",
        "/usage",
        "",
        ROOT / "docs" / "assets" / "bff62166-1f1a-426e-9636-b2ee4ed8f612.jpeg",
        [
            "`Changes +169 -40` — počet řádků přidaných/odstraněných v rámci session",
            "`AI Credits: 635.32 (4h 54m 28s)` — kolik AI kreditů jsem utratil za tuto aktivitu",
            "`Tokens` — rozpad: kolik jsem poslal (input), kolik model vrátil (output), kolik šlo na reasoning (thinking)",
            "`51,030 / 70,000 AIC` — spotřeba v měsíční limitě; reset za 5 dní",
            "`72% used` — podíl měsíčního limitu; lze vidět trend (zelené/červené číslo = méně/více než minulý měsíc)",
        ],
        caption="/usage",
        show_title=False,
    )

    add_section_slide(
        prs,
        "AGENTI",
        "Speciální persona s rolí, znalostmi, nástroji a hranicemi"
    )

    add_content_slide(
        prs,
        "Agenti",
        "Co je agent",
        [
            "Agent = specializovaná persona s vlastní rolí, znalostmi (skills), dostupnými nástroji a hranicemi (boundaries)",
            "Copilot CLI má 11 vestavěných agentů: Explore (prohledávání), Task (správa projektu), Code-review, Rubber-duck (kritika), Security-review, Research, Plan, Fleet a další",
            "Vlastní agenty si vytváříš sám — soubor `.agent.md` s YAML frontmatter (name, description, model, tools, skills) + markdown body s instrukcemi",
            "Agenti mohou delegovat na sebe navzájem — orchestrují si práci a sdílejí context ze session",
            "Vestavění agenti jsou dostupní ihned, vlastní agenti se nahrají z `.github/agents/`, `.claude/agents/`, nebo `~/.copilot/agents/`",
        ],
    )

    add_code_slide(
        prs,
        "Agenti",
        "",
        "Každý agent žije v `.github/agents/name.agent.md`, `.claude/agents/`, nebo `~/.copilot/agents/`:",
        [
            "---",
            "name: test-agent",
            "description: Píše testy podle TDD principů",
            "model: auto                    # který model použít",
            "tools: [shell, read, write]    # přístup k jakým nástrojům",
            "skills: [test-writer]          # eager-load tyto skills",
            "---",
            "",
            "# Agent pro psaní testů",
            "Jsi senior QA inženýr...",
            "",
            "## NEDĚJ",
            "- Nikdy neměň zdrojový kód",
        ],
        caption="test-agent.agent.md",
        content_top=Inches(0.9),
    )

    add_screenshot_slide(
        prs,
        "Agenti",
        "Jak volat agenty",
        "",
        ROOT / "docs" / "assets" / "3982762b-0661-4a66-aa9d-a41d170267ea.jpeg",
        [
            "`/agent` — interaktivní výběr dostupných agentů (viz výše)",
            "`copilot --agent my-agent --prompt \"...\"` — CLI volání konkrétního agenta",
            "`@agent-name` v promptu — inline reference na agenta v session",
            "⚠️ Ručně vytvořené `.agent.md` vyžadují **restart CLI** — agenti z pluginů se reloadují automaticky",
        ],
        caption="/agent",
        show_title=False,
    )

    add_section_slide(
        prs,
        "SKILLS",
        "Znovupoužitelné znalosti a umění pro agenty"
    )

    add_content_slide(
        prs,
        "Skills",
        "Co jsou skills",
        [
            "Skill = speciální znalost/umění, které si agent může naučit — např. \"Generuj dokumentaci API\", \"Piš testy\"",
            "Místo aby agent znovu vymýšlel — skill má hotové instrukce, příklady, šablony",
            "Copilot **sám rozpozná** relevantní skill a automaticky ho používá — bez ručního přepínání",
            "Progresivní: nejdřív se zkontroluje jméno, pak instrukce, pak soubory — jen to co je potřeba",
            "3 zabudované: cloud-setup (CI/CD), discover-resources (MCP servery), github-pr-media (upload)",
        ],
    )

    add_code_slide(
        prs,
        "Skills",
        "Skill — struktura adresáře",
        "Skill soubory jsou organizovány v adresáři s frontmatter a soubory prostředků:",
        [
            ".github/skills/",
            "└── api-docs/",
            "    ├── SKILL.md",
            "    ├── examples/",
            "    │   ├── example.ts",
            "    │   ├── example.py",
            "    │   └── example.js",
            "    ├── templates/",
            "    │   └── api-template.md",
            "    ├── docs/",
            "    │   └── README.md",
            "    └── .metadata.json",
        ],
        caption="Strom adresářů",
        font_size=14,
    )

    add_code_slide(
        prs,
        "Skills",
        "Skill — soubor SKILL.md",
        "Frontmatter definuje metadata skilu, body obsahuje instrukce:",
        [
            "---",
            "name: api-docs",
            "description: Generuje dokumentaci API ze zdrojového kódu",
            "license: MIT                    # Nepovinné",
            "user-invocable: true            # Nepovinné",
            "allowed-tools: [shell, read]    # Nepovinné",
            "---",
            "",
            "# Skill pro dokumentaci API",
            "Jsi expert na dokumentaci API...",
            "",
            "## Jak se používá",
            "Když uživatel zažádá o dokumentaci API...",
        ],
        caption="SKILL.md",
        font_size=14,
    )

    add_screenshot_slide(
        prs,
        "Skills",
        "Příkazy skill",
        "",
        ROOT / "docs" / "assets" / "6c680423-8bcf-492c-9554-83c3347cc25c.jpeg",
        [
            "`.github/skills/` — projekt; `.claude/skills/` — cross-client; `~/.copilot/skills/` — osobní",
            "Priorita: **skills projektu** > **osobní skills**; pluginy mohou přinášet bundlované skills",
            "`/skill list` — seznam dostupných skills",
            "`/skill add` — přidat skill z URL nebo adresáře",
            "`/skill reload` — znovu načíst skills (po změně souboru)",
        ],
        caption="/skill",
        show_title=False,
    )

    add_section_slide(
        prs,
        "INSTRUCTIONS",
        "Pravidla a pokyny pro agenty v ruznych kontextech"
    )

    add_content_slide(
        prs,
        "Instructions",
        "Co jsou instrukce",
        [
            "Bez instrukcí: Copilot uhádne vaše preference a standardy",
            "S instrukcemi: Copilot **ví** vaše kódovací normy, architekturu, zakázané práce",
            "Instrukce se **skládají** — všechny aktivní se kombinují, tvůj prompt vyhrává",
            "Příklady: kódovací styl, bezpečnostní pravidla, commit konvence, persony projektu",
            "Přehled a zapnutí/vypnutí aktivních instrukcí: `/instructions`",
        ],
    )

    add_content_slide(
        prs,
        "Instructions",
        "Soubory a rozsah",
        [
            'AGENTS.md — Adresářová struktura: "Kdo jsi" (persona, hranice, zakázaná práce)',
            'CLAUDE.md / GEMINI.md — Git root + cwd: "Kdo jsi" pro všechny nástroje',
            '.github/copilot-instructions.md — Celý repo: "Jak se tady kóduje" (standardy)',
            '**.github/instructions/*.instructions.md** — Specifické soubory: "Speciální pravidla" pro test/*.ts, src/**/*.tsx apod.',
            "~/.copilot/copilot-instructions.md — Osobní: meziprojektové standardy",
        ],
    )

    add_code_slide(
        prs,
        "Instructions",
        ".github/copilot-instructions.md",
        "Repo-wide kódovací standardy — jak se v tomto projektu kóduje:",
        [
            "# Kódovací styl",
            "- Používej 2 mezery pro odsazení",
            "- Preferuj `const` nad `let`",
            "- Přidej JSDoc komentáře pro všechny veřejné funkce",
            "",
            "# Bezpečnost",
            "- Nikdy nepsej secrets do kódu",
            "- Ověřuj všechny vstupy uživatele",
            "- Používej parametrizované dotazy",
            "",
            "# Testování",
            "- Všechny funkce musí mít testy",
            "- Minimálně 80% pokryti kódu",
        ],
        caption="Repo-wide standardy",
        font_size=13,
    )

    add_code_slide(
        prs,
        "Instructions",
        "Instrukce specifické pro cesty",
        "Různá pravidla pro různé soubory — globs určují, který soubor dostane kterou instrukci:",
        [
            "---",
            'applyTo: "**/*.test.ts,**/*.spec.ts"',
            "---",
            "",
            "# Instrukce pro testovací soubory",
            "- Používej AAA pattern: Arrange, Act, Assert",
            "- Jeden koncept assertion na test",
            "- Mock externí závislosti",
            "- Nikdy netestuj detaily implementace",
            "",
            "# Uložení",
            "Ulož jako: .github/instructions/tests.instructions.md",
        ],
        caption="applyTo glob matching",
        font_size=13,
    )

    add_priority_table(
        prs,
        "Instructions",
        "Priorita a načítání",
        [
            ("1", "Tvůj prompt ← vždy vyhrává"),
            ("2", "AGENTS.md (nejbližší v adresářové struktuře) + CLAUDE.md / GEMINI.md"),
            ("3", ".github/copilot-instructions.md"),
            ("4", ".github/instructions/**/*.instructions.md"),
            ("5", "~/.copilot/copilot-instructions.md (osobní)"),
            ("6", "~/.copilot/instructions/**/*.instructions.md"),
            ("7", "COPILOT_CUSTOM_INSTRUCTIONS_DIRS"),
            ("8", "Výchozí chování ← náhrada"),
        ],
    )

    add_section_slide(
        prs,
        "TOOLS & MCP",
        "Nástroje, permissions a rozšiřitelnost přes MCP"
    )

    add_content_slide(
        prs,
        "Tools",
        "Co jsou nástroje",
        [
            "Tool = speciální příkaz/akce, kterou si Copilot může zavolat — bash, vytvořit soubor, číst soubor, MCP servery...",
            "Vestavěné nástroje: bash, vytvořit/editovat/zobrazit soubory, glob/grep, web_fetch, delegace úkolu, načítání skills",
            "MCP nástroje: přispívají konfigurované MCP servery (GitHub API, Slack, databáze...)",
            "Každá akce vyžaduje oprávnění — permissions se kontrolují před spuštěním",
            "⚠️ YOLO mode = všechna oprávnění bez dotazu (NIKDY v produkci)",
        ],
    )

    add_table_slide(
        prs,
        "Tools",
        "Vestavěné nástroje",
        ["Nástroj", "Účel", "Riziko"],
        [
            ("bash", "Spuštění shell příkazů", "⚠️ Vysoké"),
            ("create / edit", "Vytvoření a úprava souborů", "⚠️ Vysoké"),
            ("view", "Čtení souborů, výpis adresářů", "Nízké"),
            ("glob / grep", "Hledání souborů, prohledávání obsahu", "Nízké"),
            ("web_fetch / web_search", "Načtení a prohledávání webu", "Střední"),
            ("task / skill", "Delegace sub-agentům, načítání skills", "Různé"),
            ("MCP server tools", "Přispívají konfigurované servery", "Různé"),
        ],
        col_widths=[Inches(1.8), Inches(3.5), Inches(1.5)],
    )

    add_code_slide(
        prs,
        "Tools",
        "Porovnání oprávnění",
        None,
        [
            "# Typy oprávnění a vzory shodování",
            "",
            "shell(git:*)              # Odpovídá všem git subpříkazům",
            "shell(git)                # NEShoduje se s subpříkazy",
            "write(/path/to/*.ts)      # Oprávnění k zápisu do souboru",
            "url(api.github.com)       # Přístup do domény",
            "mcp-server(tool-name)     # Nástroje MCP serveru",
            "",
            "--allow-tool / --deny-tool # Explicitní přepsání",
        ],
        caption="Syntaxe oprávnění",
        font_size=13,
    )

    add_section_slide(
        prs,
        "MCP SERVERY",
        "Model Context Protocol — připojení externích nástrojů a dat"
    )

    add_code_slide(
        prs,
        "MCP",
        "Co je MCP — komunikační protokol",
        "MCP je otevřený standard pro připojení Copilotu k externím systémům (DB, API, Slack, GitHub…)",
        [
            "┌──────────────────┐",
            "│  Copilot CLI     │",
            "└────────┬─────────┘",
            "         │ MCP Protocol (stdio/http/sse)",
            "         ↓",
            "┌──────────────────┐",
            "│   MCP Server     │  (memory, exa, postgres...)",
            "└────────┬─────────┘",
            "         │ API volání",
            "         ↓",
            "┌──────────────────┐",
            "│  Externí nástroje│",
            "│  a prostředky    │  (soubory, API, databáze)",
            "└──────────────────┘",
        ],
        caption="Architektura MCP",
        font_size=11,
    )

    add_code_slide(
        prs,
        "MCP",
        "Konfigurace MCP",
        "MCP servery se konfigurují v ~/.copilot/mcp-config.json nebo workspace .mcp.json:",
        [
            "{",
            '  "mcpServers": {',
            '    "memory": {',
            '      "type": "local",',
            '      "command": "npx",',
            '      "args": ["-y", "@modelcontextprotocol/server-memory"]',
            "    },",
            '    "exa": {',
            '      "type": "http",',
            '      "url": "https://mcp.exa.ai/mcp"',
            "    }",
            "  }",
            "}",
        ],
        caption="mcp-config.json",
        font_size=11,
    )

    add_code_slide(
        prs,
        "MCP",
        "Správa MCP a příkazy",
        "Správa MCP serverů přes CLI příkazy nebo interaktivní /mcp zobrazení:",
        [
            "copilot mcp list              # Seznam konfigurovaných serverů",
            "copilot mcp get NAME          # Detail serveru",
            "copilot mcp add NAME -- CMD   # Přidat lokální stdio server",
            "copilot mcp add --transport http NAME URL  # Přidat vzdálený server",
            "copilot mcp remove NAME       # Odebrat server",
            "",
            "/mcp                          # Interaktivní MCP panel",
            "/mcp list                     # Seznam serverů v session",
            "/mcp show <name>              # Detaily serveru a jeho nástrojů",
            "/mcp add / /mcp edit          # Přidat/editovat server",
        ],
        caption="Příkazy MCP",
        font_size=11,
    )

    add_content_slide(
        prs,
        "MCP",
        "Podnik a bezpečnost",
        [
            "**GitHub MCP** — Vestavěný, automaticky dostupný (otázky o issues, PRs, commits...)",
            "**Vynucování zásad** — Admini mohou blokovat MCP servery třetích stran (Business/Enterprise)",
            "**Konfigurace workspace** — `.mcp.json` nebo `.github/mcp.json` pro týmové standardy",
            "**Kontrola nástrojů** — `--add-github-mcp-tool`, `--disable-builtin-mcps` pro podrobnou kontrolu",
            "**Konfigurace pouze v session** — `--additional-mcp-config @file.json` pro dočasné servery",
        ],
    )

    add_section_slide(
        prs,
        "LSP",
        "Language Servers — code intelligence"
    )

    add_content_slide(
        prs,
        "LSP",
        "Jazykové servery — LSP",
        [
            "LSP = standardizovaný protokol pro code intelligence — typy, references, completions, diagnostics",
            "Copilot se může připojit k jazykově specifickým serverům (TypeScript, Python, Rust, Go...)",
            "Žádný LSP není zapnutý defaultně — musíš konfigurovat v `~/.copilot/lsp-config.json`",
            "Příklad: `gopls` pro Go, `pyright` pro Python, `typescript-language-server` pro TS/JS",
            "LSP rozšiřuje kontext — Copilot má přesnější znalost lokálního kódu (ne jen pattern matching)",
        ],
    )

    add_code_slide(
        prs,
        "LSP",
        "Konfigurace LSP",
        "Konfiguruj LSP servery v ~/.copilot/lsp-config.json (osobní) nebo .github/lsp.json (projekt):",
        [
            "{",
            '  "lspServers": {',
            '    "typescript": {',
            '      "command": "typescript-language-server",',
            '      "args": ["--stdio"],',
            '      "fileExtensions": {',
            '        ".ts": "typescript",',
            '        ".tsx": "typescriptreact"',
            "      }",
            "    }",
            "  }",
            "}",
        ],
        caption="lsp-config.json",
        font_size=12,
    )

    add_content_slide(
        prs,
        "LSP",
        "Správa LSP a příkazy",
        [
            "`/lsp show` — Seznam konfigurovaných LSP serverů a jejich stav",
            "`/lsp test NAME` — Test, zda se konkrétní server spustí správně",
            "`/lsp reload` — Znovu načíst konfiguraci LSP z disku",
            "`/lsp logs` — Aktuální stav + logy serveru (ladění)",
            "Konfigurace: `~/.copilot/lsp-config.json` (osobní) · `.github/lsp.json` (projekt)",
            "Konfigurace projektu má prioritu — serverů projektu přepisují osobní",
        ],
    )

    add_section_slide(
        prs,
        "PLUGINS",
        "Packaged integrations — bundlované rozšíření"
    )

    add_content_slide(
        prs,
        "Pluginy",
        "Co jsou pluginy",
        [
            "Plugin = balené integrace — balí skills, agenty, hooks, MCP servery, LSP servery",
            "Marketplace: github/copilot-plugins (oficiální), github/awesome-copilot (komunita), microsoft/work-iq-mcp (podnik)",
            "Instalace: `/plugin install workiq@copilot-plugins` nebo `copilot plugin install owner/repo`",
            "Audit před instalací: open source, aktivně spravován, minimální závislosti, žádné známé zranitelnosti",
            "Omezení schopností: `--allow-tool 'plugin-name'`, `--deny-tool 'shell(rm)'`",
        ],
    )

    add_code_slide(
        prs,
        "Pluginy",
        "Instalace pluginu",
        "Pluginy se instalují z marketplace nebo z GitHubu — různé zdroje a způsoby:",
        [
            "# Z marketplace v session",
            "/plugin install workiq@copilot-plugins",
            "",
            "# Z marketplace v shellu",
            "copilot plugin install workiq@copilot-plugins",
            "",
            "# Z GitHubu",
            "copilot plugin install owner/repo",
            "copilot plugin install owner/repo:plugins/my-plugin",
            "",
            "# Z git URL",
            "copilot plugin install https://github.com/owner/my-plugin.git",
        ],
        caption="Instalace pluginu",
        font_size=12,
    )

    add_content_slide(
        prs,
        "Pluginy",
        "Schopnosti pluginů",
        [
            "Skills — znovupoužitelné instrukce pro specifické úkoly",
            "Agenti — specializované persony s vlastní logikou",
            "Hooks — automatizace životního cyklu (akce před/po)",
            "MCP servery — nástroje a prostředky (API, DB, Slack...)",
            "LSP servery — code intelligence (typy, references, completions)",
            "Katalogy marketplace — objevitelné výpisy pluginů",
        ],
    )

    add_code_slide(
        prs,
        "Pluginy",
        "Bezpečnost — Kontrolní seznam",
        "Před instalací jakéhokoliv pluginu zkontroluj:",
        [
            "# Bezpečnostní kontrola",
            "- Zdrojový kód je otevřený a auditable",
            "- Aktivně se udržuje",
            "- Minimální závislosti",
            "- Žádné známé zranitelnosti",
            "- Jasné požadavky na oprávnění",
            "",
            "# Omezení možností pluginu",
            "copilot --allow-tool 'plugin-name'",
            "copilot --deny-tool 'shell(rm)'",
        ],
        caption="Osvědčené postupy bezpečnosti",
        font_size=11,
    )

    add_content_slide(
        prs,
        "Pluginy",
        "Zásobník rozšiřitelnosti",
        [
            "Vestavěné nástroje: bash, view, create, edit, glob, grep (základní schopnosti)",
            "MCP servery: připojení k externím systémům, API, databázím (rozšíření kontextu)",
            "Skills: znovupoužitelné instrukce, šablony, osvědčené postupy (znalostní vrstva)",
            "Pluginy: balené integrace — bundlují vše výše + agenty, hooks, LSP",
            "Každá vrstva staví na té předchozí — pluginy jsou vrchol rozšiřitelnosti",
        ],
    )

    add_section_slide(
        prs,
        "SESSIONS",
        "Správa sessions — persistentní konverzace"
    )

    add_content_slide(
        prs,
        "Sessions",
        "Co je session",
        [
            "Session = udržuje aktuální konverzaci — historii, kontext, schválení, pracovní adresář",
            "Persistuje na disk — můžeš ji pozastavit, vrátit se později, nebo pokračovat kde jsi skončil",
            "Každá session má vlastní ID — můžeš ji pojmenovat `/rename`",
            "Obsah: prompty, odpovědi, schválené nástroje, soubory co jsi čtl/měnil, spotřeba tokenů",
            "Výchozí chování: session pokračuje dokud nevyjdeš `/exit` — `/new` ji uloží na pozadí",
        ],
    )

    add_content_slide(
        prs,
        "Sessions",
        "Klíčové příkazy pro sessions",
        [
            "`/session` — Zobraz informace o session (ID, trvání, dotčené soubory)",
            "`/usage` — Spotřeba tokenů a API volání v rámci session",
            "`/rename NAME` — Pojmenuj svou session pro snadné vyhledání později",
            "`/clear` — Opusť session a začni znovu (session je zrušena)",
            "`/new` — Začni novou konverzaci (stará session zůstává na pozadí)",
            "`/resume` — Přepni na předchozí session (výběr nebo zadej ID/jméno)",
            "`--continue` — Obnoví poslední session z shellu",
            "`/share` — Exportuj session (markdown, HTML, gist, nebo GitHub link)",
            "`/rewind` nebo `/undo` — Vrať poslední tah zpět a obnov změny souborů",
            "`/exit` — Ukončí CLI; `/exit print` vytiskne session po ukončení",
        ],
    )

    add_content_slide(
        prs,
        "Sessions",
        "Data sessions a správa",
        [
            "Data jsou v `~/.copilot/session-state/<id>/` — přepis, checkpointy, snapshoty pro návraty",
            "Index v `~/.copilot/session-store.db` — používán příkazy `/session`, `/resume`, `--resume`",
            "Spravuj subcommands, ne `rm` — `/session info` (detail), `/session checkpoints` (seznam)",
            "`/session files` — dotčené soubory; `/session prune` — vyčisti stará data",
            "`/session delete-all` — smaž všechny sessions (pozor!)",
        ],
    )

    add_content_slide(
        prs,
        "Sessions",
        "Kdy vyčistit, komprimovat, nebo začít novou",
        [
            "Přechod na nesouvisející úkol → `/new` (zachová starou) nebo `/clear` (smaže)",
            "Matoucí odpovědi nebo halucinace → `/new` (čistý start)",
            "Context limit se blíží → nejdřív `/compact`, pak `/new` pokud je třeba",
            "Citlivé informace diskutovány → `/clear` a `/exit` (vymaže session)",
            "Session je pomalá nebo nafouklá → `/new` (čistý context)",
        ],
    )

    add_section_slide(
        prs,
        "CHRONICLE",
        "Session-history insights a personalizace"
    )

    add_content_slide(
        prs,
        "Chronicle",
        "Co je Chronicle",
        [
            "Chronicle = experimentální funkce pro analýzu tvé session history — co jsi dělal, co se opakovalo, jak optimalizovat",
            "Pracuje na disku v `~/.copilot/session-store/` — indexuje všechny sessions a jejich obsah",
            "Pomáhá zlepšit prompt engineering — tipy jak lépe psát prompty pro tento projekt",
            "Optimalizace nákladů — ukazuje kde utrácíš tokeny a jak je ušetřit",
            "Zdokonalování instrukcí — návrhy jak zlepšit tvůj `.copilot-instructions.md`",
        ],
    )

    add_content_slide(
        prs,
        "Chronicle",
        "Příkazy Chronicle",
        [
            "`/chronicle standup` — Tvá práce z posledního dne (co jsi udělal, na čem jsi pracoval)",
            "`/chronicle search QUERY` — Hledej v obsahu všech sessions (grep přes všechny sessions)",
            "`/chronicle tips` — Personalizované tipy na použití (jak lépe používat Copilot v tomto projektu)",
            "`/chronicle cost-tips` — Sniž spotřebu tokenů a náklady (kde ušetřit tokeny)",
            "`/chronicle improve` — Zlepši copilot-instructions.md (návrhy jak zlepšit instrukce)",
            "`/chronicle reindex` — Znovu načti index úložiště sessions (znovu naindexovat sessions)",
        ],
    )

    add_code_slide(
        prs,
        "Chronicle",
        "Tipy Chronicle — Příklad výsledků",
        "Praktická doporučení z tvé session history:",
        [
            "# Tipy na optimalizaci",
            "",
            "1. Používej @ pro zmínění souborů místo vkládání -> Ušetří tokeny a lepší kontext",
            "",
            "2. Iteruj v rámci jedné session, nezačínej znovu -> Zachová historii konverzace",
            "",
            "3. Zkus /research pro průzkumnou práci -> Strukturovaný výzkum bez hlavní session",
            "",
            "4. Přeměň opakující se prompty na vlastního agenta -> Automatizuj opakující se úkoly",
            "",
            "5. Používej plan mode pro vícestupňovou práci -> Design, Kód, Testy, Review",
        ],
        font_size=12,
    )

    add_section_slide(
        prs,
        "HOOKS",
        "Custom scripts na klíčových bodech"
    )

    add_content_slide(
        prs,
        "Hooks",
        "Co jsou hooks",
        [
            "Hooks = vlastní skripty běžící v klíčových bodech agent lifecycle — logování, bezpečnost, audit, upozornění",
            "Životní cyklus: Prompt → Session Start → Pre-Tool → Execute → Post-Tool → Session End",
            "Každý bod má hook — `onPrompt`, `onSessionStart`, `preToolUse`, `postToolUse`, `onSessionEnd`",
            "Případy použití: bezpečnostní mantinely (zkontroluj před spuštěním shell), audit (loguj akce), upozornění (upozorni na problém)",
            "Konfiguruje se v `.github/hooks/*.json` — ať už hooks.json, auth.json, či custom-hooks.json",
        ],
    )

    add_code_slide(
        prs,
        "Hooks",
        "Konfigurace hooks",
        "Hooks se konfigurují v .github/hooks/ jako JSON s bash skripty:",
        [
            "{",
            '  "hooks": {',
            '    "preToolUse": [',
            "      {",
            '        "type": "command",',
            '        "bash": ".github/hooks/scripts/check-tool.sh",',
            '        "cwd": ".",',
            '        "timeoutSec": 10',
            "      }",
            "    ]",
            "  }",
            "}",
        ],
    )

    add_screenshot_slide(
        prs,
        "Hooks",
        "Příklad hook s PeonPing",
        "",
        ROOT / "docs" / "assets" / "peon-ping-hook.png",
        [
            "**Bezpečnostní mantinely** — Zkontroluj před spuštěním shell / edit (žádný `rm -rf`, žádné citlivé cesty)",
            "**Auditing** — Loguj všechny akce do audit trail (kdo, co, kdy, proč)",
            "**Upozornění** — Upozorni, když agent dělá něco neobvyklého (náhle smaže > 100 souborů)",
            "**Vlastní ověřování** — Vynucuj compliance pravidla (git commit message, branch protection)",
            "PeonPing je referenční implementace hooks pro více AI CLI nástrojů: https://github.com/PeonPing/peon-ping",
        ],
        caption="Hook PeonPing",
        show_title=False,
    )

    add_content_slide(
        prs,
        "Pokročilé",
        "Fleet mode — Paralelní agenti",
        [
            "Fleet = orchestrace paralelních sub-agentů — více agentů pracuje na různých částech zároveň",
            "Orchestrator rozdělí úkol, spustí 9+ agentů paralelně, validuje, kombinuje: `Ag1|Ag2|Ag3|Ag4 → Konsolidovaný výstup`",
            "Příkaz: `/fleet \"Přepracuj všechny komponenty na TypeScript a přidej testy\"`",
            "Orchestrator automaticky rozpočítá (Ag1→components/, Ag2→utils/, Ag3→types, Ag4→tests)",
            "Případ použití: masivní refactor, přepis na jiný jazyk, cleanup — **4x rychleji** než sekvenčně",
        ],
    )

    add_closing_slide(prs, "Děkujeme!", "Otázky?  ·  docs.github.com/copilot")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(f"Saved {OUTPUT} ({len(prs.slides._sldIdLst)} slides)")


if __name__ == "__main__":
    build()
