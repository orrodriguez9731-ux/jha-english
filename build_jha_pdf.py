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

    lang = d.get('lang', 'en')

    # ── PDF label strings (bilingual) ─────────────────────────
    if lang == 'es':
        L = {
            # Exact wording from official D. Wilson Spanish JHA PDF
            'title1': 'Análisis de Peligros', 'title2': 'del Trabajo (JHA)',
            'reviewer': 'Crítico:', 'company': 'Empresa:', 'name': 'Nombre:',
            'date': 'Fecha:', 'weather': 'Clima', 'location': 'Localización:',
            'scope': 'Alcance:', 'temp': 'La Temperature', 'wind': 'Viento', 'notes': 'Notas:',
            'clear':'Claro','sunny':'Soleado','rain':'Lluvia','overcast':'Cubierto',
            'drizzle':'Llovizna','foggy':'Nebuloso','other':'Otro',
            'vlight':'Muy Claro','windy':'Ventoso','vwindy':'Muy Ventoso',
            'emerg': 'Procedimientos de Emergencia',
            'notifyQ': 'Es consciente de notificar a D Wilson en caso de accidente?',
            'injuredQ': 'Te lesionaste hoy?',
            'firstAid':'Ubicación del Botiquín de Primeros Auxilios – Oficina DWCC',
            'stretcher':'Ubicaciones de la Camilla/ el Cesto/ Rescate de Gran Altura – N/A',
            'msds':'Ubicaciones de S.D.S – Oficina DWCC',
            'evacuation':'Puntos de Evacuación – Estacionamiento',
            'fireExt':'Ubicaciones de Extintores – Espacios Renovados / Baños',
            'clinicName':'Nombre de la Clínica:', 'clinicLoc':'Ubicación de la Clínica:',
            'clinicProto':'Protocolos de la Clínica:', 'yes':'Si', 'no':'No',
            'hospName':'Nombre del Hospital Más Cercano:', 'hospLoc':'Ubicación del Hospital Más Cercano:',
            'steps': 'Pasos Involucrados:',
            'hazards': 'Lista de Verificación de Peligros Potenciales',
            'prevMeasures': 'Medidas Preventivas para Cada Peligro',
            'ergo': 'Factores de Riesgo Ergonómico Identificados',
            'ppe': 'Requiere PPE',
            'civilWork': 'Completa para Obra Civil',
            'civilNote': "(Tenga en cuenta: Se requiere un plan de excavación de zanjas aprobado por un ingeniero para las zanjas >5')",
            'soil1': '1. Describir el tipo y la profundidad de las excavaciones:',
            'typeA':'Tierra Tipo A','typeB':'Tierra Tipo B','typeC':'Tierra Tipo C',
            'cave2': '2. Derrumbe/ se utilizarán medidas de control de inmersión si la excavación será mayor de 5 pies:',
            'terrain3': '3. Describir la elevación/ terreno del sitio/ preocupaciones ambientales/ peligros:',
            'vehicle4': '4. Describir los peligros con el sitio/ acceso de vehículos (mucho tráfico, transporte pesado, grúa pluma, almacenamiento de materiales/HAZMAT):',
            'elecgas5': '5. Describir el tipo de problemas o peligros eléctricos o de gas (e.g. eléctrico, gas, línea de fibra óptica):',
            'util6': '6. Se han perforado los servicios públicos existentes/ válvulas',
            'tx8117': '7. Se ha contactado la línea directa de Texas 811:',
            'valves8': '8. Se han ubicado las válvulas de cierre de los servicios públicos',
            'inspect9': '9. Que una persona capacitada en entrenado en zanja inspeccionado la excavación',
            'wx10': '10. Condiciones climáticas? (mojado, lodo, peligros de excavación, seco, grietas):',
            'crew': 'Firma del Miembro de la Tripulación (Incluidos los Subcontratistas)',
            'printed': 'Imprimir:', 'hh': 'Número de Casco:', 'signature': 'Firma:',
            'naText': 'N/A — Obra civil no aplica para el alcance de hoy.',
            'awkward':'Posicionamiento Incómodo','reach':'Llegar/ Claro Acceso',
            'force':'Fuerza Excesiva','repetitive':'Movimientos Repetitivos',
            'lifting':'Levantamiento','sharpsurf':'Superficies de Trabajo Afiladas',
            'overhead':'Trabajo por Encima de la Cabeza','vibrating':'Herramientas Vibrantes/ Equipo',
            'hardhat':'Casco de Seguridad','glasses':'Lentes de Seguridad',
            'vest':'Chaleco de Seguridad','boots':'Botas de Trabajo',
        }
    else:
        L = {
            'title1': 'Job Hazard', 'title2': 'Analysis (JHA)',
            'reviewer': 'Reviewer:', 'company': 'Company:', 'name': 'Name:',
            'date': 'Date:', 'weather': 'Weather', 'location': 'Location:',
            'scope': 'Scope:', 'temp': 'Temperature', 'wind': 'Wind', 'notes': 'Notes:',
            'clear':'Clear','sunny':'Sunny','rain':'Rain','overcast':'Overcast',
            'drizzle':'Drizzle','foggy':'Foggy','other':'Other',
            'vlight':'Very Light','windy':'Windy','vwindy':'Very Windy',
            'emerg': 'Emergency Procedures',
            'notifyQ': 'Are you aware to notify D. Wilson in case of accident?',
            'injuredQ': 'Were you injured today?',
            'firstAid':'First Aid Kit Location',
            'stretcher':'Stretcher Location/ Basket/ High-Rise Rescue',
            'msds':'M.S.D.S Location/ S.D.S Location',
            'evacuation':'Evacuation Points',
            'fireExt':'Fire Extinguisher Location(s)',
            'clinicName':'Clinic Name:', 'clinicLoc':'Clinic Location:',
            'clinicProto':'Clinic Protocols:', 'yes':'Yes', 'no':'No',
            'hospName':'Nearest Hospital Name:', 'hospLoc':'Nearest Hospital Location:',
            'steps': 'Steps Involved:',
            'hazards': 'Potential Hazards Check List',
            'prevMeasures': 'Preventive Measures for Each Hazard',
            'ergo': 'Ergonomic Risk Factors Identified',
            'ppe': 'PPE Required',
            'civilWork': 'Complete for Civil Work',
            'civilNote': "(Please Note: Engineer Approved Trenching Plan Required for Trenches >5')",
            'soil1': '1. Describe type and depth of excavations:',
            'typeA':'Type A Soil/Rock','typeB':'Type B Soil/Rock','typeC':'Type C Soil/Rock',
            'cave2': '2. Cave-in/Engulfment control measures to be used if excavation will be greater than 5 feet:',
            'terrain3': '3. Describe elevation/site terrain/environmental concerns/hazards:',
            'vehicle4': '4. Describe hazards with site/vehicle access (High Traffic, Heavy Haul, Boom Cranes, HAZMAT):',
            'elecgas5': '5. Describe type of electrical or gas concerns (e.g. Electrical/Gas/Fiber Optic):',
            'util6': '6. Have existing utilities been potholed/located?',
            'tx8117': '7. Has Texas 811 hot-line been contacted:',
            'valves8': '8. Have Utility shut valves been located?',
            'inspect9': '9. Have excavations been inspected by a trained competent person?',
            'wx10': '10. Weather Conditions? (Wet, Mud, Excavation Hazards, Dry, Cracks):',
            'crew': 'Crew Member Signature (Including Subcontractors)',
            'printed': 'Printed:', 'hh': 'Hard Hat Number:', 'signature': 'Signature:',
            'naText': "N/A — Civil work not applicable for today's scope.",
            'awkward':'Awkward Positioning','reach':'Reach/Clear Access',
            'force':'Excessive Force','repetitive':'Repetitive Movements',
            'lifting':'Lifting','sharpsurf':'Sharp Work Surfaces',
            'overhead':'Overhead Work','vibrating':'Vibrating Tools/Equipment',
            'hardhat':'Hard Hat','glasses':'Safety Glasses',
            'vest':'Safety Vest','boots':'Work Boots',
        }

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

    txt(W/2, 738, L['title1'], sz=18, bold=True, align='center')
    txt(W/2, 718, L['title2'], sz=18, bold=True, align='center')

    txt(380, 704, L['reviewer'], sz=9, bold=True)
    txt(424, 704, val('reviewer'), sz=9)
    hline(421, 702, MR)

    rect(ML, BOT, PW, TOP-BOT, lw=1)
    y = TOP

    # Company
    hline(ML, y, MR, lw=1)
    txt(ML+3, y-10, L['company'], sz=8, bold=True)
    txt(ML+46, y-10, val('company'), sz=8)
    hline(ML, y-14, MR)

    # Name
    txt(ML+3, y-25, L['name'], sz=8, bold=True)
    txt(ML+30, y-25, val('name'), sz=8)
    hline(ML, y-28, MR)

    SPLIT = ML + PW*0.49

    # Date / Weather row 1
    txt(ML+3, y-39, L['date'], sz=8, bold=True)
    txt(ML+28, y-39, val('date'), sz=8)
    txt(SPLIT+4, y-39, L['weather'], sz=8, bold=True)
    wx = val('weather')
    wx1 = [(L['clear'], wx=='Clear'), (L['rain'], wx=='Rain'), (L['overcast'], wx=='Overcast')]
    cx = SPLIT + 46
    for lbl, chk in wx1:
        cb(cx, y-42, checked=chk); txt(cx+9, y-39, lbl, sz=7); cx += 46
    hline(ML, y-43, SPLIT)
    hline(ML, y-43, MR)

    # Location / Weather row 2
    txt(ML+3, y-54, L['location'], sz=8, bold=True)
    txt(ML+42, y-54, val('location'), sz=8)
    wx2 = [(L['sunny'], wx=='Sunny'), (L['drizzle'], wx=='Drizzle'), (L['foggy'], wx=='Foggy')]
    cx = SPLIT + 46
    for lbl, chk in wx2:
        cb(cx, y-57, checked=chk); txt(cx+9, y-54, lbl, sz=7); cx += 46
    hline(ML, y-60, MR)

    # Weather Other
    cx = SPLIT + 46
    cb(cx, y-72, checked=(wx=='Other')); txt(cx+9, y-69, L['other'], sz=7)
    hline(ML, y-74, MR)

    # Scope / Temperature / Wind / Notes
    txt(ML+3, y-85, L['scope'], sz=8, bold=True)
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

    txt(SPLIT+4, y-85, L['temp'], sz=8, bold=True)
    txt(SPLIT+60, y-85, val('temp'), sz=8)

    wind = val('wind')
    txt(SPLIT+4, y-100, L['wind'], sz=8, bold=True)
    wind_opts = [(L['vlight'], wind=='Very Light'), (L['windy'], wind=='Windy'), (L['vwindy'], wind=='Very Windy')]
    cx = SPLIT+34
    for lbl, chk in wind_opts:
        cb(cx, y-103, checked=chk); txt(cx+9, y-100, lbl, sz=7); cx += 50

    txt(SPLIT+4, y-115, L['notes'], sz=8, bold=True)
    txt(SPLIT+34, y-115, val('wxNotes'), sz=8)

    hline(ML, y-120, MR, lw=1)
    vline(SPLIT, y-43, y-120)
    y -= 120

    # Emergency Procedures
    txt(ML+3, y-11, L['emerg'], sz=9, bold=True)
    hline(ML, y-14, MR)

    txt(ML+3, y-24, L['notifyQ'], sz=8)
    notw = val('notifyW')
    cb(ML+232, y-27, checked=(notw=='Yes')); txt(ML+241, y-24, L['yes'], sz=8)
    cb(ML+261, y-27, checked=(notw=='No'));  txt(ML+270, y-24, L['no'], sz=8)

    txt(ML+3, y-36, L['injuredQ'], sz=8)
    inj = val('injured')
    cb(ML+103, y-39, checked=(inj=='Yes')); txt(ML+112, y-36, L['yes'], sz=8)
    cb(ML+130, y-39, checked=(inj=='No'));  txt(ML+139, y-36, L['no'], sz=8)
    hline(ML, y-42, MR)
    y -= 42

    emerg = d.get('emergChecks', [])
    LEFT_EMERG = [
        ('firstAid',   L['firstAid']),
        ('stretcher',  L['stretcher']),
        ('msds',       L['msds']),
        ('evacuation', L['evacuation']),
        ('fireExt',    L['fireExt']),
    ]
    ey = y
    for key, lbl in LEFT_EMERG:
        cb(ML+3, ey-12, checked=(key in emerg))
        txt(ML+13, ey-9, lbl, sz=7.5)
        ey -= 13

    RCOL = SPLIT + 4
    txt(RCOL,     y-9,  L['clinicName'], sz=7.5, bold=True)
    txt(RCOL+52,  y-9,  val('clinicName'),            sz=7.5)
    txt(RCOL,     y-22, L['clinicLoc'], sz=7.5, bold=True)
    txt(RCOL+60,  y-22, val('clinicLoc'),             sz=7.5)

    proto = val('clinicProto')
    txt(RCOL,     y-35, L['clinicProto'], sz=7.5, bold=True)
    cb(RCOL+66,   y-38, checked=(proto=='Yes')); txt(RCOL+75,  y-35, L['yes'], sz=7.5)
    cb(RCOL+93,   y-38, checked=(proto=='No'));  txt(RCOL+102, y-35, L['no'],  sz=7.5)

    txt(RCOL,     y-48, L['hospName'], sz=7.5, bold=True)
    txt(RCOL+92,  y-48, val('hospName'),              sz=7.5)
    txt(RCOL,     y-61, L['hospLoc'], sz=7.5, bold=True)
    txt(RCOL+102, y-61, val('hospLoc'),               sz=7.5)

    vline(SPLIT, ey, y)
    hline(ML, ey, MR, lw=1)
    y = ey

    # Steps Involved
    txt(ML+3, y-11, L['steps'], sz=9, bold=True)
    hline(ML, y-14, MR)
    steps = d.get('steps', [])
    for i in range(5):
        ry = y-14-(i*13)
        txt(ML+3, ry-10, f'{i+1}.', sz=8, bold=True)
        txt(ML+16, ry-10, steps[i] if i < len(steps) else '', sz=8)
        hline(ML, ry-13, MR)
    y = y-14-(5*13)

    # Potential Hazards header
    txt(W/2, y-10, L['hazards'], sz=9, bold=True, align='center')
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
    txt(W/2, y2-10, L['prevMeasures'], sz=9, bold=True, align='center')
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
    txt(ML+(EMID-ML)/2, y2-9, L['ergo'], sz=7.5, bold=True, align='center')
    txt(EMID+(MR-EMID)/2, y2-9, L['ppe'], sz=7.5, bold=True, align='center')
    hline(ML, y2-12, MR)

    ergo = d.get('ergos', [])
    ppe  = d.get('ppe',  [])
    ECMID = ML + (EMID-ML)/2
    ERG_L = [L['awkward'],L['force'],L['lifting'],L['overhead']]
    ERG_R = [L['reach'],L['repetitive'],L['sharpsurf'],L['vibrating']]
    PPE_I = [L['hardhat'],L['glasses'],L['vest'],L['boots']]
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
    txt(ML+3, y2-10, L['civilWork'], sz=8, bold=True)
    txt(ML+126, y2-10, L['civilNote'], sz=6.5)
    hline(ML, y2-13, MR)
    y2 -= 13

    if civil_na:
        txt(ML+3, y2-10, L['naText'], sz=8, col=DGRAY)
        hline(ML, y2-14, MR, lw=0.3)
        y2 -= 14
    else:
        txt(ML+3, y2-10, L['soil1'], sz=7.5)
        soil = val('soilType')
        scx = ML+165
        for sv, sl in [('Type A Soil/Rock',L['typeA']),('Type B Soil/Rock',L['typeB']),('Type C Soil/Rock',L['typeC'])]:
            cb(scx, y2-13, checked=(soil==sv)); txt(scx+10, y2-10, sl, sz=7); scx+=82
        hline(ML, y2-14, MR, lw=0.3); y2 -= 14
        txt(ML+3, y2-10, val('excavDepth'), sz=8)
        hline(ML, y2-14, MR, lw=0.3); y2 -= 14

        txt(ML+3, y2-10, L['cave2'], sz=7)
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
                    (L['terrain3'],'terrain'),
                    (L['vehicle4'],'vehicleAccess'),
                    (L['elecgas5'],'elecGas'),
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

        yn_pair(        L['util6'],'utilLoc',
                        L['tx8117'],'tx811', y2)
        hline(ML, y2-RH_YN, MR, lw=0.3); y2 -= RH_YN

        yn_pair(        L['valves8'],'shutValves',
                        L['inspect9'],'excavInsp', y2)
        hline(ML, y2-RH_YN, MR, lw=0.3); y2 -= RH_YN

        txt(ML+3, y2-9, L['wx10'], sz=7)
        txt(ML+3, y2-20, val('civilWx'), sz=8)
        hline(ML, y2-26, MR, lw=0.3); y2 -= 26

    hline(ML, y2, MR, lw=1)

    # Crew Signatures
    txt(W/2, y2-10, L['crew'], sz=9, bold=True, align='center')
    hline(ML, y2-13, MR)

    N1 = ML+PW*0.38
    N2 = ML+PW*0.62
    HDR_H = 14
    rect(ML, y2-13-HDR_H, N1-ML,  HDR_H, fill=LGRAY)
    rect(N1, y2-13-HDR_H, N2-N1,  HDR_H, fill=LGRAY)
    rect(N2, y2-13-HDR_H, MR-N2,  HDR_H, fill=LGRAY)
    hdr_txt_y = y2 - 13 - HDR_H/2 - 3
    txt(ML+3, hdr_txt_y, L['printed'], sz=7.5, bold=True)
    txt(N1+3, hdr_txt_y, L['hh'], sz=7.5, bold=True)
    txt(N2+3, hdr_txt_y, L['signature'], sz=7.5, bold=True)
    hline(ML, y2-13-HDR_H, MR, lw=0.5)

    crew = d.get('crew', [])
    cy2 = y2 - 13 - HDR_H
    CRH = 22

    def crew_row(y, name='', hh='', sig_b64='', filled=False):
        if y - CRH < BOT2: return False
        txt_y = y - CRH + 7
        if filled:
            txt(ML+3,  txt_y, name, sz=8, bold=True)
            txt(N1+3,  txt_y, hh,   sz=8)
            # Draw signature image if provided
            if sig_b64 and sig_b64.startswith('data:image'):
                try:
                    import base64, io
                    from reportlab.lib.utils import ImageReader
                    # Strip data URL prefix
                    img_data = base64.b64decode(sig_b64.split(',')[1])
                    img_reader = ImageReader(io.BytesIO(img_data))
                    # Draw signature scaled to fit in signature column
                    sig_w = MR - N2 - 6
                    sig_h = CRH - 4
                    c.drawImage(img_reader, N2+3, y-CRH+2,
                                width=sig_w, height=sig_h,
                                preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print(f"Sig draw error: {e}", flush=True)
        else:
            txt(ML+3,  txt_y, L['printed'], sz=7, col=DGRAY)
            txt(N1+3,  txt_y, L['hh'], sz=7, col=DGRAY)
            txt(N2+3,  txt_y, L['signature'], sz=7, col=DGRAY)
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
        crew_row(cy2,
                 crew[i].get('name',''),
                 crew[i].get('hh',''),
                 crew[i].get('sig',''),
                 filled=True)
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
    txt(W/2, TOP3-11, f"({('AHP' if lang=='es' else 'JHA')}) {L['title1']} {L['title2']}", sz=10, bold=True, align='center')
    hline(ML, TOP3-14, MR, lw=1)

    cy3 = TOP3-14
    rect(ML, cy3-HDR_H, N1-ML,  HDR_H, fill=LGRAY)
    rect(N1, cy3-HDR_H, N2-N1,  HDR_H, fill=LGRAY)
    rect(N2, cy3-HDR_H, MR-N2,  HDR_H, fill=LGRAY)
    hdr3_y = cy3 - HDR_H/2 - 3
    txt(ML+3, hdr3_y, L['printed'], sz=7.5, bold=True)
    txt(N1+3, hdr3_y, L['hh'], sz=7.5, bold=True)
    txt(N2+3, hdr3_y, L['signature'], sz=7.5, bold=True)
    hline(ML, cy3-HDR_H, MR, lw=0.3)
    cy3 -= HDR_H

    total_p3 = len(p3_crew) + 12
    for i in range(total_p3):
        if cy3 - CRH < BOT2: break
        filled = i < len(p3_crew)
        crew_row(cy3,
                 p3_crew[i].get('name','') if filled else '',
                 p3_crew[i].get('hh','')   if filled else '',
                 p3_crew[i].get('sig','')  if filled else '',
                 filled=filled)
        cy3 -= CRH

    c.showPage()
    c.save()
    print(f"PDF saved -> {out_path}")

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
