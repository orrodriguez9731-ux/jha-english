"""
build_jha_pdf.py  — Recreates the JHA form with submitted data.
Usage: python3 build_jha_pdf.py data.json output.pdf
"""
import json, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas

W, H = letter   # 612 x 792 pts

BLACK = colors.black
WHITE = colors.white
LGRAY = colors.HexColor('#E8E8E8')
DGRAY = colors.HexColor('#666666')

ML = 36          # left margin
MR = 576         # right margin
PW = MR - ML     # 540 pts usable width

def build(data_path, out_path):
    with open(data_path) as f:
        d = json.load(f)

    c = rl_canvas.Canvas(out_path, pagesize=letter)

    def txt(x, y, s, sz=8, bold=False, col=BLACK, align='left'):
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', sz)
        c.setFillColor(col)
        s = str(s) if s else ''
        if align == 'center': c.drawCentredString(x, y, s)
        elif align == 'right': c.drawRightString(x, y, s)
        else: c.drawString(x, y, s)

    def rect(x, y, w, h, fill=None, lw=0.5):
        c.setLineWidth(lw)
        c.setStrokeColor(BLACK)
        c.setFillColor(fill if fill else WHITE)
        c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1)

    def hline(x1, y, x2, lw=0.5):
        c.setLineWidth(lw); c.setStrokeColor(BLACK)
        c.line(x1, y, x2, y)

    def vline(x, y1, y2, lw=0.5):
        c.setLineWidth(lw); c.setStrokeColor(BLACK)
        c.line(x, y1, x, y2)

    def cb(x, y, sz=7, checked=False):
        c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
        c.rect(x, y, sz, sz, fill=1, stroke=1)
        if checked:
            c.setFillColor(BLACK)
            c.setFont('Helvetica-Bold', sz)
            c.drawString(x+1, y+0.8, 'X')

    def val(k, default=''):
        v = d.get(k, default)
        return str(v).strip() if v and str(v).strip() and str(v).strip() != '—' else default

    # ══════════════════════════════════════════════════════════════════
    # PAGE 1
    # ══════════════════════════════════════════════════════════════════
    TOP = 700
    BOT = 60

    txt(W/2, 738, 'Job Hazard', sz=18, bold=True, align='center')
    txt(W/2, 718, 'Analysis (JHA)', sz=18, bold=True, align='center')

    txt(380, 704, 'Reviewer:', sz=9, bold=True)
    txt(424, 704, val('reviewer'), sz=9)
    hline(421, 702, MR)

    rect(ML, BOT, PW, TOP-BOT, lw=1)
    y = TOP

    # Company
    hline(ML, y, MR, lw=1)
    txt(ML+3, y-10, 'Company:', sz=8, bold=True)
    txt(ML+46, y-10, val('company'), sz=8)
    hline(ML, y-14, MR)

    # Name
    txt(ML+3, y-25, 'Name:', sz=8, bold=True)
    txt(ML+30, y-25, val('name'), sz=8)
    hline(ML, y-28, MR)

    SPLIT = ML + PW*0.49

    # Date / Weather row 1
    txt(ML+3, y-39, 'Date:', sz=8, bold=True)
    txt(ML+28, y-39, val('date'), sz=8)
    txt(SPLIT+4, y-39, 'Weather', sz=8, bold=True)
    wx = val('weather')
    wx1 = [('Clear', wx=='Clear'), ('Rain', wx=='Rain'), ('Overcast', wx=='Overcast')]
    cx = SPLIT + 46
    for lbl, chk in wx1:
        cb(cx, y-42, checked=chk); txt(cx+9, y-39, lbl, sz=7); cx += 46
    hline(ML, y-43, SPLIT)
    hline(ML, y-43, MR)

    # Location / Weather row 2
    txt(ML+3, y-54, 'Location:', sz=8, bold=True)
    txt(ML+42, y-54, val('location'), sz=8)
    wx2 = [('Sunny', wx=='Sunny'), ('Drizzle', wx=='Drizzle'), ('Foggy', wx=='Foggy')]
    cx = SPLIT + 46
    for lbl, chk in wx2:
        cb(cx, y-57, checked=chk); txt(cx+9, y-54, lbl, sz=7); cx += 46
    hline(ML, y-60, MR)

    # Weather Other
    cx = SPLIT + 46
    cb(cx, y-72, checked=(wx=='Other')); txt(cx+9, y-69, 'Other', sz=7)
    hline(ML, y-74, MR)

    # Scope / Temperature / Wind / Notes
    txt(ML+3, y-85, 'Scope:', sz=8, bold=True)
    scope = val('scope')
    words = scope.split(); lines = []; line = ''
    for w in words:
        if len(line)+len(w)+1 <= 42: line = (line+' '+w).strip()
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    sy = y - 97
    for ln in lines[:4]:
        txt(ML+3, sy, ln, sz=8); sy -= 10

    txt(SPLIT+4, y-85, 'Temperature', sz=8, bold=True)
    txt(SPLIT+60, y-85, val('temp'), sz=8)

    wind = val('wind')
    txt(SPLIT+4, y-100, 'Wind', sz=8, bold=True)
    wind_opts = [('Very Light', wind=='Very Light'), ('Windy', wind=='Windy'), ('Very Windy', wind=='Very Windy')]
    cx = SPLIT+34
    for lbl, chk in wind_opts:
        cb(cx, y-103, checked=chk); txt(cx+9, y-100, lbl, sz=7); cx += 50

    txt(SPLIT+4, y-115, 'Notes:', sz=8, bold=True)
    txt(SPLIT+34, y-115, val('wxNotes'), sz=8)

    hline(ML, y-120, MR, lw=1)
    vline(SPLIT, y-43, y-120)
    y -= 120

    # Emergency Procedures
    txt(ML+3, y-11, 'Emergency Procedures', sz=9, bold=True)
    hline(ML, y-14, MR)

    txt(ML+3, y-24, 'Are you aware to notify D. Wilson in case of accident?', sz=8)
    notw = val('notifyW')
    cb(ML+232, y-27, checked=(notw=='Yes')); txt(ML+241, y-24, 'Yes', sz=8)
    cb(ML+261, y-27, checked=(notw=='No'));  txt(ML+270, y-24, 'No', sz=8)

    txt(ML+3, y-36, 'Were you injured today?', sz=8)
    inj = val('injured')
    cb(ML+103, y-39, checked=(inj=='Yes')); txt(ML+112, y-36, 'Yes', sz=8)
    cb(ML+130, y-39, checked=(inj=='No'));  txt(ML+139, y-36, 'No', sz=8)
    hline(ML, y-42, MR)
    y -= 42

    emerg = d.get('emergChecks', [])
    LEFT_EMERG = [
        ('firstAid',   'First Aid Kit Location'),
        ('stretcher',  'Stretcher Location/ Basket/ High-Rise Rescue'),
        ('msds',       'M.S.D.S Location/ S.D.S Location'),
        ('evacuation', 'Evacuation Points'),
        ('fireExt',    'Fire Extinguisher Location(s)'),
    ]
    ey = y
    for key, lbl in LEFT_EMERG:
        cb(ML+3, ey-12, checked=(key in emerg))
        txt(ML+13, ey-9, lbl, sz=7.5)
        ey -= 13

    RCOL = SPLIT + 4
    txt(RCOL,     y-9,  'Clinic Name:',              sz=7.5, bold=True)
    txt(RCOL+52,  y-9,  val('clinicName'),            sz=7.5)
    txt(RCOL,     y-22, 'Clinic Location:',           sz=7.5, bold=True)
    txt(RCOL+60,  y-22, val('clinicLoc'),             sz=7.5)

    proto = val('clinicProto')
    txt(RCOL,     y-35, 'Clinic Protocols:',          sz=7.5, bold=True)
    cb(RCOL+66,   y-38, checked=(proto=='Yes')); txt(RCOL+75,  y-35, 'Yes', sz=7.5)
    cb(RCOL+93,   y-38, checked=(proto=='No'));  txt(RCOL+102, y-35, 'No',  sz=7.5)

    txt(RCOL,     y-48, 'Nearest Hospital Name:',     sz=7.5, bold=True)
    txt(RCOL+92,  y-48, val('hospName'),              sz=7.5)
    txt(RCOL,     y-61, 'Nearest Hospital Location:', sz=7.5, bold=True)
    txt(RCOL+102, y-61, val('hospLoc'),               sz=7.5)

    vline(SPLIT, ey, y)
    hline(ML, ey, MR, lw=1)
    y = ey

    # Steps Involved
    txt(ML+3, y-11, 'Steps Involved:', sz=9, bold=True)
    hline(ML, y-14, MR)
    steps = d.get('steps', [])
    for i in range(5):
        ry = y-14-(i*13)
        txt(ML+3, ry-10, f'{i+1}.', sz=8, bold=True)
        txt(ML+16, ry-10, steps[i] if i < len(steps) else '', sz=8)
        hline(ML, ry-13, MR)
    y = y-14-(5*13)

    # Potential Hazards header
    txt(W/2, y-10, 'Potential Hazards Check List', sz=9, bold=True, align='center')
    hline(ML, y-13, MR)
    y -= 13

    haz = d.get('hazards', [])
    def hck(k): return k in haz

    CB_SZ = 8
    COL_W = PW/5

    HAZ_GRID = [
      ([('Access / Egress','Access/ Egress',''),('Crane','Crane',''),('Fire Hazards','Fire Hazards',''),('Impalement Hazards','Impalement Hazards',''),('Material Handling','Material Handling','')], 13),
      ([('Access to General Public','Access to','General Public'),('Demolition','Demolition',''),('Floor / Wall Openings','Floor/Wall Openings',''),('Ladders (Tied Off / Inspected)','Ladders (Tied','Off/Inspected)'),('Overhead Power Lines','Overhead Power','Lines')], 20),
      ([('Barricades / Signage','Barricades/','Signage'),('Electrical Hazards','Electrical Hazards',''),('Guardrails / Toeboards / Bracing','Guardrails/','Toeboards/bracing'),('Lifts','Lifts',''),('Pinch Points','Pinch Points','')], 18),
      ([('Chemical Hazards','Chemical','Hazards'),('Excavation / Trench','Excavation/Trench',''),('Hearing Protection','Hearing Protection',''),('Lighting','Lighting',''),('Powder Actuated Tools','Powder Actuated','Tools')], 18),
      ([('Confined Spaces','Confined Spaces',''),('Fall Hazards','Fall Hazards',''),('Heavy Equipment','Heavy Equipment',''),('Lockout / Tagout','Lockout/Tagout',''),('Traffic Control','Traffic Control','')], 13),
      ([('Inspection Current','Inspection','Current'),('Proper Tools for the Job','Proper Tools for','the job'),('Tools in Good Working Condition','Tools in Good','Working Condition'),('Qualification Required','Qualification Required',''),('Lift Equipment Properly Inspected by Qualified Person','Lift Equipment','Properly Inspected\nby Qualified person')], 24),
      ([('Manual Lifting Equipment','Manual Lifting','Equipment'),('Proper Rigging Practices','Proper Rigging','Practices'),('Manual Lifting (Using Your Legs) <50 lbs','Manual Lifting (using','Your Legs) <50 lbs'),('Hole Covers','Hole Covers',''),('Overhead Work / Other','Overhead Work','Other')], 20),
      ([('Work Crews Heavy Equipment','Work Crews','Heavy'),('Underground Utilities','Equipment',''),('Scaffold (Properly Inspected by Competent Person)','Underground','Utilities'),('Personal Basket (Inspected and Approved)','Scaffold (Properly','Inspected by\nCompetent Person)'),('__none__','Personal Basket','(Inspected and\nApproved)')], 26),
    ]

    for row_items, rh in HAZ_GRID:
        mid_y = y - rh/2
        for ci, (key, l1, l2) in enumerate(row_items):
            cx2 = ML + ci*COL_W
            num_lines = 1 + (len(l2.split('\n')) if l2 else 0)
            text_block_h = num_lines * 8
            text_top = mid_y + text_block_h/2
            cb_y = mid_y - CB_SZ/2
            c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
            c.rect(cx2+2, cb_y, CB_SZ, CB_SZ, fill=1, stroke=1)
            if hck(key) and key != '__none__':
                c.setFillColor(BLACK); c.setFont('Helvetica-Bold', CB_SZ)
                c.drawString(cx2+3, cb_y+1, 'X')
            tx = cx2 + CB_SZ + 5
            ty = text_top - 7
            txt(tx, ty, l1, sz=6.5)
            if l2:
                for li, line in enumerate(l2.split('\n')):
                    txt(tx, ty-(li+1)*8, line, sz=6.5)
            if ci > 0: vline(cx2, y-rh, y, lw=0.3)
        hline(ML, y-rh, MR, lw=0.3)
        y -= rh

    c.showPage()

    # ══════════════════════════════════════════════════════════════════
    # PAGE 2
    # ══════════════════════════════════════════════════════════════════
    TOP2 = 756
    BOT2 = 60
    rect(ML, BOT2, PW, TOP2-BOT2, lw=1)
    y2 = TOP2

    P2_HAZ = [
      ([('Aerial Lift / Certification','Aerial Lift/','Certification'),('Confined Space (Entry)','Confined Space',''),('Try Start / Stop Switch','Try Start/ Stop','Switch'),('GFCI','GFCI',''),('Slip / Trip Potential','Slip/ Trip Potential','')], 20),
      ([('Body Position / Line of Fire','Body Position/','Line of Fire'),('Crush By / Struck By / Contact With','Crush By/Struck','By/ Contact With'),('Adequate Anchorage Points','Adequate Anchorage','Points'),('Sharp Objects','Sharp Objects',''),('__other__','Other:','')], 18),
    ]
    other_haz = val('otherHaz')

    for ri, (row_items, rh) in enumerate(P2_HAZ):
        mid_y = y2 - rh/2
        for ci, (key, l1, l2) in enumerate(row_items):
            cx2 = ML + ci*COL_W
            if key == '__other__':
                cb_y = mid_y - CB_SZ/2
                c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
                c.rect(cx2+2, cb_y, CB_SZ, CB_SZ, fill=1, stroke=1)
                if other_haz:
                    c.setFillColor(BLACK); c.setFont('Helvetica-Bold', CB_SZ)
                    c.drawString(cx2+3, cb_y+1, 'X')
                txt(cx2+CB_SZ+5, mid_y+1, 'Other:', sz=6.5)
                txt(cx2+CB_SZ+30, mid_y+1, other_haz[:20], sz=6.5)
            else:
                num_lines = 1 + (len(l2.split('\n')) if l2 else 0)
                text_block_h = num_lines * 8
                text_top = mid_y + text_block_h/2
                cb_y = mid_y - CB_SZ/2
                c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
                c.rect(cx2+2, cb_y, CB_SZ, CB_SZ, fill=1, stroke=1)
                if hck(key):
                    c.setFillColor(BLACK); c.setFont('Helvetica-Bold', CB_SZ)
                    c.drawString(cx2+3, cb_y+1, 'X')
                tx = cx2 + CB_SZ + 5
                ty = text_top - 7
                txt(tx, ty, l1, sz=6.5)
                if l2:
                    for li, line in enumerate(l2.split('\n')):
                        txt(tx, ty-(li+1)*8, line, sz=6.5)
            if ci>0: vline(cx2, y2-rh, y2, lw=0.3)
        hline(ML, y2-rh, MR, lw=0.3)
        y2 -= rh

    # Preventive Measures
    txt(W/2, y2-10, 'Preventive Measures for Each Hazard', sz=9, bold=True, align='center')
    hline(ML, y2-13, MR)
    pm = d.get('preventive', [])
    PMID = ML + PW/2
    for i in range(4):
        ry = y2-13-(i*13)
        txt(ML+3,    ry-10, f'{i+1}.', sz=8, bold=True)
        txt(ML+16,   ry-10, pm[i]   if i   < len(pm) else '', sz=8)
        txt(PMID+3,  ry-10, f'{i+5}.', sz=8, bold=True)
        txt(PMID+16, ry-10, pm[i+4] if i+4 < len(pm) else '', sz=8)
        hline(ML, ry-13, MR, lw=0.3)
    vline(PMID, y2-13, y2-13-(4*13), lw=0.3)
    y2 -= (13 + 4*13)

    # Ergonomics + PPE
    EMID = ML + PW/2
    rect(ML,   y2-12, EMID-ML,  12, fill=LGRAY)
    rect(EMID, y2-12, MR-EMID,  12, fill=LGRAY)
    txt(ML+(EMID-ML)/2, y2-9,       'Ergonomic Risk Factors Identified', sz=7.5, bold=True, align='center')
    txt(EMID+(MR-EMID)/2, y2-9,     'PPE Required',                       sz=7.5, bold=True, align='center')
    hline(ML, y2-12, MR)

    ergo = d.get('ergos', [])
    ppe  = d.get('ppe',  [])
    ECMID = ML + (EMID-ML)/2
    ERG_L = ['Awkward Positioning','Excessive Force','Lifting','Overhead Work']
    ERG_R = ['Reach/Clear Access','Repetitive Movements','Sharp Work Surfaces','Vibrating Tools/Equipment']
    PPE_I = ['Hard Hat','Safety Glasses','Safety Vest','Work Boots']
    RH_E  = 11
    for i in range(4):
        ry = y2-12-(i*RH_E)
        cb(ML+3,    ry-RH_E+3, checked=(ERG_L[i] in ergo)); txt(ML+13,    ry-RH_E+5, ERG_L[i], sz=7)
        cb(ECMID+3, ry-RH_E+3, checked=(ERG_R[i] in ergo)); txt(ECMID+13, ry-RH_E+5, ERG_R[i], sz=7)
        cb(EMID+3,  ry-RH_E+3, checked=(PPE_I[i] in ppe));  txt(EMID+13,  ry-RH_E+5, PPE_I[i], sz=7)
        vline(ECMID, ry-RH_E, ry, lw=0.3)
        hline(ML, ry-RH_E, MR, lw=0.3)
    y2 -= (12 + 4*RH_E)

    other_ppe = val('otherPPE')
    if other_ppe:
        txt(EMID+3, y2-9, f'Additional PPE: {other_ppe}', sz=7)
        hline(ML, y2-12, MR, lw=0.3)
        y2 -= 12

    hline(ML, y2, MR, lw=1)

    # Civil Work
    civil_na = not val('soilType') and not val('excavDepth')
    txt(ML+3, y2-10, 'Complete for Civil Work', sz=8, bold=True)
    txt(ML+126, y2-10, "(Please Note: Engineer Approved Trenching Plan Required for Trenches >5')", sz=6.5)
    hline(ML, y2-13, MR)
    y2 -= 13

    if civil_na:
        txt(ML+3, y2-10, "N/A — Civil work not applicable for today's scope.", sz=8, col=DGRAY)
        hline(ML, y2-14, MR, lw=0.3)
        y2 -= 14
    else:
        txt(ML+3, y2-10, '1. Describe type and depth of excavations:', sz=7.5)
        soil = val('soilType')
        scx = ML+165
        for sv, sl in [('Type A Soil/Rock','Type A Soil/Rock'),('Type B Soil/Rock','Type B Soil/Rock'),('Type C Soil/Rock','Type C Soil/Rock')]:
            cb(scx, y2-13, checked=(soil==sv)); txt(scx+10, y2-10, sl, sz=7); scx+=82
        hline(ML, y2-14, MR, lw=0.3); y2 -= 14
        txt(ML+3, y2-10, val('excavDepth'), sz=8)
        hline(ML, y2-14, MR, lw=0.3); y2 -= 14

        txt(ML+3, y2-10, '2. Cave-in/Engulfment control measures to be used if excavation will be greater than 5 feet:', sz=7)
        hline(ML, y2-13, MR, lw=0.3); y2 -= 13

        ci = d.get('civilControls', [])
        RH_CIVIL = 16
        ci_opts = [('Sloping','Sloping'),('Benching','Benching'),('Trenching','Trenching'),
                   ('Shoring','Shoring'),('Shield / Box','Shield/box'),
                   ("Ladder in Trench >5 ft and Every 25'","Ladder in Trench >5 Feet and Every 25'"),
                   ('Sump Pump','Sump Pump')]
        ccx = ML+3
        for ck2, cl in ci_opts:
            cb_y2 = y2 - RH_CIVIL + (RH_CIVIL-7)/2
            txt_y2 = cb_y2 + 5
            cb(ccx, cb_y2, checked=(ck2 in ci))
            txt(ccx+10, txt_y2, cl, sz=7)
            ccx += 72
        hline(ML, y2-RH_CIVIL, MR, lw=0.3); y2 -= RH_CIVIL

        loto_cb_y = y2 - RH_CIVIL + (RH_CIVIL-7)/2
        cb(ML+3, loto_cb_y, checked=('LOTO' in ci))
        txt(ML+13, loto_cb_y+5, 'LOTO:', sz=7)
        hline(ML, y2-RH_CIVIL, MR, lw=0.3); y2 -= RH_CIVIL

        RH_TEXT = 26
        for lbl, key in [
            ('3. Describe elevation/site terrain/environmental concerns/hazards:','terrain'),
            ('4. Describe hazards with site/vehicle access (High Traffic, Heavy Haul, Boom Cranes, HAZMAT):','vehicleAccess'),
            ('5. Describe type of electrical or gas concerns (e.g. Electrical/Gas/Fiber Optic):','elecGas'),
        ]:
            txt(ML+3, y2-9,  lbl,      sz=7)
            txt(ML+3, y2-20, val(key), sz=8)
            hline(ML, y2-RH_TEXT, MR, lw=0.3); y2 -= RH_TEXT

        RH_YN = 18
        def yn_pair(lbl_l, k_l, lbl_r, k_r, y):
            mid = y - RH_YN/2
            cb_y3 = mid - 3.5
            txt_y3 = mid + 2
            txt(ML+3, txt_y3, lbl_l, sz=7)
            vl = d.get(k_l,'')
            cb(ML+190, cb_y3, checked=(vl=='Yes')); txt(ML+200, txt_y3, 'Yes', sz=7)
            cb(ML+218, cb_y3, checked=(vl=='No'));  txt(ML+228, txt_y3, 'No',  sz=7)
            vline(PMID, y-RH_YN, y, lw=0.3)
            txt(PMID+3, txt_y3, lbl_r, sz=7)
            vr = d.get(k_r,'')
            cb(MR-60, cb_y3, checked=(vr=='Yes')); txt(MR-51, txt_y3, 'Yes', sz=7)
            cb(MR-42, cb_y3, checked=(vr=='No'));  txt(MR-33, txt_y3, 'No',  sz=7)

        yn_pair('6. Have existing utilities been potholed/located?','utilLoc',
                '7. Has Texas 811 hot-line been contacted:','tx811', y2)
        hline(ML, y2-RH_YN, MR, lw=0.3); y2 -= RH_YN

        yn_pair('8. Have Utility shut valves been located?','shutValves',
                '9. Have excavations been inspected by a trained competent person?','excavInsp', y2)
        hline(ML, y2-RH_YN, MR, lw=0.3); y2 -= RH_YN

        txt(ML+3, y2-9,  '10. Weather Conditions? (Wet, Mud, Excavation Hazards, Dry, Cracks):', sz=7)
        txt(ML+3, y2-20, val('civilWx'), sz=8)
        hline(ML, y2-26, MR, lw=0.3); y2 -= 26

    hline(ML, y2, MR, lw=1)

    # Crew Signatures
    txt(W/2, y2-10, 'Crew Member Signature (Including Subcontractors)', sz=9, bold=True, align='center')
    hline(ML, y2-13, MR)

    N1 = ML+PW*0.38
    N2 = ML+PW*0.62
    HDR_H = 14
    rect(ML, y2-13-HDR_H, N1-ML,  HDR_H, fill=LGRAY)
    rect(N1, y2-13-HDR_H, N2-N1,  HDR_H, fill=LGRAY)
    rect(N2, y2-13-HDR_H, MR-N2,  HDR_H, fill=LGRAY)
    hdr_txt_y = y2 - 13 - HDR_H/2 - 3
    txt(ML+3, hdr_txt_y, 'Printed:',         sz=7.5, bold=True)
    txt(N1+3, hdr_txt_y, 'Hard Hat Number:',  sz=7.5, bold=True)
    txt(N2+3, hdr_txt_y, 'Signature:',        sz=7.5, bold=True)
    hline(ML, y2-13-HDR_H, MR, lw=0.5)

    crew = d.get('crew', [])
    cy2 = y2 - 13 - HDR_H
    CRH = 22

    def crew_row(y, name='', hh='', filled=False):
        if y - CRH < BOT2: return False
        txt_y = y - CRH + 7
        if filled:
            txt(ML+3,  txt_y, name, sz=8, bold=True)
            txt(N1+3,  txt_y, hh,   sz=8)
        else:
            txt(ML+3,  txt_y, 'Printed:',         sz=7, col=DGRAY)
            txt(N1+3,  txt_y, 'Hard Hat Number:',  sz=7, col=DGRAY)
            txt(N2+3,  txt_y, 'Signature:',        sz=7, col=DGRAY)
        vline(N1, y-CRH, y, lw=0.3)
        vline(N2, y-CRH, y, lw=0.3)
        hline(ML, y-CRH, MR, lw=0.3)
        return True

    p2_crew = []
    p3_crew = []
    EMPTY_ROWS = 12

    for i in range(len(crew)):
        if cy2 - CRH < BOT2:
            p3_crew = crew[i:]
            break
        crew_row(cy2, crew[i].get('name',''), crew[i].get('hh',''), filled=True)
        p2_crew.append(crew[i])
        cy2 -= CRH

    for i in range(EMPTY_ROWS):
        if cy2 - CRH < BOT2: break
        crew_row(cy2, filled=False)
        cy2 -= CRH

    c.showPage()

    # ══════════════════════════════════════════════════════════════════
    # PAGE 3
    # ══════════════════════════════════════════════════════════════════
    TOP3 = 756
    rect(ML, BOT2, PW, TOP3-BOT2, lw=1)
    txt(W/2, TOP3-11, '(JHA) Job Hazard Analysis', sz=10, bold=True, align='center')
    hline(ML, TOP3-14, MR, lw=1)

    cy3 = TOP3-14
    rect(ML, cy3-HDR_H, N1-ML,  HDR_H, fill=LGRAY)
    rect(N1, cy3-HDR_H, N2-N1,  HDR_H, fill=LGRAY)
    rect(N2, cy3-HDR_H, MR-N2,  HDR_H, fill=LGRAY)
    hdr3_y = cy3 - HDR_H/2 - 3
    txt(ML+3, hdr3_y, 'Printed:',         sz=7.5, bold=True)
    txt(N1+3, hdr3_y, 'Hard Hat Number:',  sz=7.5, bold=True)
    txt(N2+3, hdr3_y, 'Signature:',        sz=7.5, bold=True)
    hline(ML, cy3-HDR_H, MR, lw=0.3)
    cy3 -= HDR_H

    total_p3 = len(p3_crew) + 12
    for i in range(total_p3):
        if cy3 - CRH < BOT2: break
        filled = i < len(p3_crew)
        crew_row(cy3, p3_crew[i].get('name','') if filled else '',
                       p3_crew[i].get('hh','')   if filled else '', filled=filled)
        cy3 -= CRH

    c.showPage()
    c.save()
    print(f"PDF saved -> {out_path}")

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
