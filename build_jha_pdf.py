import json, sys, io, base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

W, H = letter
BLACK = colors.black
WHITE = colors.white
LGRAY = colors.HexColor('#E8E8E8')
DGRAY  = colors.HexColor('#666666')
ML, MR = 36, 576
PW = MR - ML

# ── Hazard key→display label lookup ──────────────────────────
HAZ_LABELS_PDF = {
  'en': {
    'Access / Egress':'Access/ Egress',
    'Crane':'Crane',
    'Fire Hazards':'Fire Hazards',
    'Impalement Hazards':'Impalement Hazards',
    'Material Handling':'Material Handling',
    'Access to General Public':'Access to\nGeneral Public',
    'Demolition':'Demolition',
    'Floor / Wall Openings':'Floor/Wall\nOpenings',
    'Ladders (Tied Off / Inspected)':'Ladders (Tied\nOff/Inspected)',
    'Overhead Power Lines':'Overhead Power\nLines',
    'Barricades / Signage':'Barricades/\nSignage',
    'Electrical Hazards':'Electrical Hazards',
    'Guardrails / Toeboards / Bracing':'Guardrails/\nToeboards/bracing',
    'Lifts':'Lifts',
    'Pinch Points':'Pinch Points',
    'Chemical Hazards':'Chemical\nHazards',
    'Excavation / Trench':'Excavation/Trench',
    'Hearing Protection':'Hearing Protection',
    'Lighting':'Lighting',
    'Powder Actuated Tools':'Powder Actuated\nTools',
    'Confined Spaces':'Confined Spaces',
    'Fall Hazards':'Fall Hazards',
    'Heavy Equipment':'Heavy Equipment',
    'Lockout / Tagout':'Lockout/Tagout',
    'Traffic Control':'Traffic Control',
    'Inspection Current':'Inspection\nCurrent',
    'Proper Tools for the Job':'Proper Tools for\nthe job',
    'Tools in Good Working Condition':'Tools in Good\nWorking Condition',
    'Qualification Required':'Qualification\nRequired',
    'Lift Equipment Properly Inspected by Qualified Person':'Lift Equipment\nProperly Inspected\nby Qualified person',
    'Manual Lifting Equipment':'Manual Lifting\nEquipment',
    'Proper Rigging Practices':'Proper Rigging\nPractices',
    'Manual Lifting (Using Your Legs) <50 lbs':'Manual Lifting\n(using Legs)\n<50 lbs',
    'Hole Covers':'Hole Covers',
    'Overhead Work / Other':'Overhead Work\nOther',
    'Work Crews Heavy Equipment':'Work Crews\nHeavy',
    'Underground Utilities':'Underground\nUtilities',
    'Scaffold (Properly Inspected by Competent Person)':'Scaffold\n(Inspected by\nCompetent Person)',
    'Personal Basket (Inspected and Approved)':'Personal Basket\n(Inspected and\nApproved)',
    'Aerial Lift / Certification':'Aerial Lift/\nCertification',
    'Confined Space (Entry)':'Confined Space',
    'Try Start / Stop Switch':'Try Start/ Stop\nSwitch',
    'GFCI':'GFCI',
    'Slip / Trip Potential':'Slip/ Trip\nPotential',
    'Body Position / Line of Fire':'Body Position/\nLine of Fire',
    'Crush By / Struck By / Contact With':'Crush By/Struck\nBy/ Contact With',
    'Adequate Anchorage Points':'Adequate\nAnchorage Points',
    'Sharp Objects':'Sharp Objects',
  },
  'es': {
    'Access / Egress':'Acceso/ Salida',
    'Crane':'Grua',
    'Fire Hazards':'Riesgos de\nIncendio',
    'Impalement Hazards':'Peligros de\nEmpalamiento',
    'Material Handling':'Manejo de\nMateriales',
    'Access to General Public':'Acceso al Publico\nen General',
    'Demolition':'Demolición',
    'Floor / Wall Openings':'Pisos/ Aberturas\nde Pared',
    'Ladders (Tied Off / Inspected)':'Escaleras/\nAtado/\nInspeccionado',
    'Overhead Power Lines':'Líneas de\nAlta Tensión',
    'Barricades / Signage':'Barricadas/\nSeñalización',
    'Electrical Hazards':'Peligros\nElectricos',
    'Guardrails / Toeboards / Bracing':'Barandillas\nRodariés/\nVigorizante',
    'Lifts':'Ascensores',
    'Pinch Points':'Puntos de\nPellizco',
    'Chemical Hazards':'Peligros\nQuímicos',
    'Excavation / Trench':'Excavación/\nZanja',
    'Hearing Protection':'Protección\nAuditiva',
    'Lighting':'Iluminación',
    'Powder Actuated Tools':'Herramientas\nde Pólvora',
    'Confined Spaces':'Espacio\nConfinado',
    'Fall Hazards':'Peligro\nde Caída',
    'Heavy Equipment':'Equipamiento\nPesado',
    'Lockout / Tagout':'Bloqueo/\nEtiquete',
    'Traffic Control':'Control\nde Trafico',
    'Inspection Current':'Corriente de\nInspección',
    'Proper Tools for the Job':'Herramientas\nAdecuadas\npara el Trabajo',
    'Tools in Good Working Condition':'Herramientas en\nBuenas Condiciones',
    'Qualification Required':'Calificación\nRequerida',
    'Lift Equipment Properly Inspected by Qualified Person':'Equipo Elevación\nInspeccionado por\nPers. Calificada',
    'Manual Lifting Equipment':'Levantamiento\nEquipo Manual',
    'Proper Rigging Practices':'Prácticas\nAdecuadas\nde Aparejo',
    'Manual Lifting (Using Your Legs) <50 lbs':'Levantamiento\nManual (Piernas)\n<50 lbs',
    'Hole Covers':'Tapas de\nAgujeros',
    'Overhead Work / Other':'Trabajo Encima\nde la Cabeza',
    'Work Crews Heavy Equipment':'Equipo de\nTrabajo Pesado',
    'Underground Utilities':'Servicios\nSubterráneos',
    'Scaffold (Properly Inspected by Competent Person)':'Andamio-\nInspeccionado\nPers. Competente',
    'Personal Basket (Inspected and Approved)':'Canasta Personal\n(Inspeccionado\ny Aprobado)',
    'Aerial Lift / Certification':'Ascensor Aéreo/\nCertificación',
    'Confined Space (Entry)':'Espacio\nConfinado',
    'Try Start / Stop Switch':'Intentar Empezar/\nInterruptor\nde Parada',
    'GFCI':'GFCI',
    'Slip / Trip Potential':'Deslizar/\nPotencial\nde Viaje',
    'Body Position / Line of Fire':'Posición del\nCuerpo/\nLinea de Fuego',
    'Crush By / Struck By / Contact With':'Aplastar Por/\nGolpeado Por/\nContactar Con',
    'Adequate Anchorage Points':'Puntos de\nAnclaje Adecuados',
    'Sharp Objects':'Objetos\nAfilados',
  }
}

def build(data_path, out_path):
    with open(data_path) as f:
        d = json.load(f)

    lang = d.get('lang', 'en')
    HL = HAZ_LABELS_PDF.get(lang, HAZ_LABELS_PDF['en'])

    if lang == 'es':
        L = {
            'title1':'Análisis de Peligros','title2':'del Trabajo (JHA)',
            'reviewer':'Crítico:','company':'Empresa:','name':'Nombre:',
            'date':'Fecha:','weather':'Clima','location':'Localización:',
            'scope':'Alcance:','temp':'La Temperature','wind':'Viento','notes':'Notas:',
            'clear':'Claro','sunny':'Soleado','rain':'Lluvia','overcast':'Cubierto',
            'drizzle':'Llovizna','foggy':'Nebuloso','other':'Otro',
            'vlight':'Muy Claro','windy':'Ventoso','vwindy':'Muy Ventoso',
            'emerg':'Procedimientos de Emergencia',
            'notifyQ':'Es consciente de notificar a D Wilson en caso de accidente?',
            'injuredQ':'Te lesionaste hoy?',
            'firstAid':'Ubicación del Botiquín de Primeros Auxilios – Oficina DWCC',
            'stretcher':'Ubicaciones de la Camilla/ el Cesto/ Rescate de Gran Altura – N/A',
            'msds':'Ubicaciones de S.D.S – Oficina DWCC',
            'evacuation':'Puntos de Evacuación – Estacionamiento',
            'fireExt':'Ubicaciones de Extintores – Espacios Renovados / Baños',
            'clinicName':'Nombre de la Clínica:','clinicLoc':'Ubicación de la Clínica:',
            'clinicProto':'Protocolos de la Clínica:','yes':'Si','no':'No',
            'hospName':'Nombre del Hospital Más Cercano:',
            'hospLoc':'Ubicación del Hospital Más Cercano:',
            'steps':'Pasos Involucrados:',
            'hazards':'Lista de Verificación de Peligros Potenciales',
            'prevMeasures':'Medidas Preventivas para Cada Peligro',
            'ergo':'Factores de Riesgo Ergonómico Identificados',
            'ppe':'Requiere PPE',
            'civilWork':'Completa para Obra Civil',
            'civilNote':"(Tenga en cuenta: Se requiere un plan de excavación aprobado por un ingeniero para zanjas >5')",
            'soil1':'1. Describir el tipo y la profundidad de las excavaciones:',
            'typeA':'Tierra Tipo A','typeB':'Tierra Tipo B','typeC':'Tierra Tipo C',
            'cave2':'2. Derrumbe/ medidas de control de inmersión si la excavación será mayor de 5 pies:',
            'terrain3':'3. Describir la elevación/ terreno del sitio/ preocupaciones ambientales/ peligros:',
            'vehicle4':'4. Describir los peligros con el sitio/ acceso de vehículos (mucho tráfico, transporte pesado, grúa, HAZMAT):',
            'elecgas5':'5. Describir el tipo de problemas eléctricos o de gas (e.g. eléctrico, gas, línea de fibra óptica):',
            'util6':'6. Se han perforado los servicios públicos existentes/ válvulas',
            'tx8117':'7. Se ha contactado la línea directa de Texas 811:',
            'valves8':'8. Se han ubicado las válvulas de cierre de los servicios públicos',
            'inspect9':'9. Una persona capacitada ha inspeccionado la excavación',
            'wx10':'10. Condiciones climáticas? (mojado, lodo, peligros de excavación, seco, grietas):',
            'crew':'Firma del Miembro de la Tripulación (Incluidos los Subcontratistas)',
            'printed':'Imprimir:','hh':'Número de Casco:','signature':'Firma:',
            'naText':'N/A — Obra civil no aplica para el alcance de hoy.',
            'awkward':'Posicionamiento Incómodo','reach':'Llegar/ Claro Acceso',
            'force':'Fuerza Excesiva','repetitive':'Movimientos Repetitivos',
            'lifting':'Levantamiento','sharpsurf':'Superficies de Trabajo Afiladas',
            'overhead':'Trabajo por Encima de la Cabeza','vibrating':'Herramientas Vibrantes/ Equipo',
            'hardhat':'Casco de Seguridad','glasses':'Lentes de Seguridad',
            'vest':'Chaleco de Seguridad','boots':'Botas de Trabajo',
        }
    else:
        L = {
            'title1':'Job Hazard','title2':'Analysis (JHA)',
            'reviewer':'Reviewer:','company':'Company:','name':'Name:',
            'date':'Date:','weather':'Weather','location':'Location:',
            'scope':'Scope:','temp':'Temperature','wind':'Wind','notes':'Notes:',
            'clear':'Clear','sunny':'Sunny','rain':'Rain','overcast':'Overcast',
            'drizzle':'Drizzle','foggy':'Foggy','other':'Other',
            'vlight':'Very Light','windy':'Windy','vwindy':'Very Windy',
            'emerg':'Emergency Procedures',
            'notifyQ':'Are you aware to notify D. Wilson in case of accident?',
            'injuredQ':'Were you injured today?',
            'firstAid':'First Aid Kit Location',
            'stretcher':'Stretcher Location/ Basket/ High-Rise Rescue',
            'msds':'M.S.D.S Location/ S.D.S Location',
            'evacuation':'Evacuation Points',
            'fireExt':'Fire Extinguisher Location(s)',
            'clinicName':'Clinic Name:','clinicLoc':'Clinic Location:',
            'clinicProto':'Clinic Protocols:','yes':'Yes','no':'No',
            'hospName':'Nearest Hospital Name:',
            'hospLoc':'Nearest Hospital Location:',
            'steps':'Steps Involved:',
            'hazards':'Potential Hazards Check List',
            'prevMeasures':'Preventive Measures for Each Hazard',
            'ergo':'Ergonomic Risk Factors Identified',
            'ppe':'PPE Required',
            'civilWork':'Complete for Civil Work',
            'civilNote':"(Please Note: Engineer Approved Trenching Plan Required for Trenches >5')",
            'soil1':'1. Describe type and depth of excavations:',
            'typeA':'Type A Soil/Rock','typeB':'Type B Soil/Rock','typeC':'Type C Soil/Rock',
            'cave2':'2. Cave-in/Engulfment control measures if excavation greater than 5 feet:',
            'terrain3':'3. Describe elevation/site terrain/environmental concerns/hazards:',
            'vehicle4':'4. Describe hazards with site/vehicle access (High Traffic, Heavy Haul, Boom Cranes, HAZMAT):',
            'elecgas5':'5. Describe type of electrical or gas concerns (e.g. Electrical/Gas/Fiber Optic):',
            'util6':'6. Have existing utilities been potholed/located?',
            'tx8117':'7. Has Texas 811 hot-line been contacted:',
            'valves8':'8. Have Utility shut valves been located?',
            'inspect9':'9. Have excavations been inspected by a trained competent person?',
            'wx10':'10. Weather Conditions? (Wet, Mud, Excavation Hazards, Dry, Cracks):',
            'crew':'Crew Member Signature (Including Subcontractors)',
            'printed':'Printed:','hh':'Hard Hat Number:','signature':'Signature:',
            'naText':"N/A — Civil work not applicable for today's scope.",
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
        if align=='center': c.drawCentredString(x, y, s)
        elif align=='right': c.drawRightString(x, y, s)
        else: c.drawString(x, y, s)

    def txt_lv(x, y, label, value, sz=7.5):
        """Draw bold label then value, auto-spaced by label width."""
        c.setFont('Helvetica-Bold', sz); c.setFillColor(BLACK)
        c.drawString(x, y, label)
        lw = stringWidth(label, 'Helvetica-Bold', sz)
        c.setFont('Helvetica', sz)
        c.drawString(x + lw + 3, y, str(value) if value else '')

    def rect(x, y, w, h, fill=None, lw=0.5):
        c.setLineWidth(lw); c.setStrokeColor(BLACK)
        c.setFillColor(fill if fill else WHITE)
        c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1)

    def hline(x1, y, x2, lw=0.5):
        c.setLineWidth(lw); c.setStrokeColor(BLACK); c.line(x1,y,x2,y)

    def vline(x, y1, y2, lw=0.5):
        c.setLineWidth(lw); c.setStrokeColor(BLACK); c.line(x,y1,x,y2)

    def cb(x, y, sz=7, checked=False):
        c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
        c.rect(x, y, sz, sz, fill=1, stroke=1)
        if checked:
            c.setFillColor(BLACK); c.setFont('Helvetica-Bold', sz)
            c.drawString(x+1, y+0.8, 'X')

    def val(k, default=''):
        v = d.get(k, default)
        return str(v).strip() if v and str(v).strip() and str(v).strip()!='—' else default

    def split_lines(text, max_w=74, sz=6.5):
        """Word-wrap text to fit max_w pts."""
        if '\n' in text:
            result = []
            for part in text.split('\n'):
                result.extend(split_lines(part, max_w, sz))
            return result
        words = text.split(); lines = []; line = ''
        for w in words:
            test = (line+' '+w).strip()
            if stringWidth(test,'Helvetica',sz) <= max_w: line = test
            else:
                if line: lines.append(line)
                line = w
        if line: lines.append(line)
        return lines or [text]

    def draw_haz_row(y_top, row_keys, haz_set):
        """Draw one row of the hazard grid. Returns row height used."""
        COL_W = PW/5; CB_SZ = 8
        # Calculate height needed
        max_lines = 1
        for k in row_keys:
            if k: max_lines = max(max_lines, len(split_lines(HL.get(k,k))))
        rh = max(14, max_lines*8+6)
        mid_y = y_top - rh/2
        for ci, key in enumerate(row_keys):
            cx = ML + ci*COL_W
            checked = (key in haz_set) if key else False
            cb_y = mid_y - CB_SZ/2
            c.setLineWidth(0.6); c.setStrokeColor(BLACK); c.setFillColor(WHITE)
            c.rect(cx+2, cb_y, CB_SZ, CB_SZ, fill=1, stroke=1)
            if checked:
                c.setFillColor(BLACK); c.setFont('Helvetica-Bold', CB_SZ)
                c.drawString(cx+3, cb_y+1, 'X')
            if key:
                lines = split_lines(HL.get(key,key))
                tx = cx + CB_SZ + 5
                total_h = len(lines)*8
                ty = mid_y + total_h/2 - 2
                for ln in lines:
                    txt(tx, ty, ln, sz=6.5); ty -= 8
            if ci>0: vline(cx, y_top-rh, y_top, lw=0.3)
        hline(ML, y_top-rh, MR, lw=0.3)
        return rh

    # ══════════════════════════════════════════
    # PAGE 1
    # ══════════════════════════════════════════
    TOP=700; BOT=60
    txt(W/2, 738, L['title1'], sz=18, bold=True, align='center')
    txt(W/2, 718, L['title2'], sz=18, bold=True, align='center')
    txt(380, 704, L['reviewer'], sz=9, bold=True)
    txt(424, 704, val('reviewer'), sz=9)
    hline(421, 702, MR)
    rect(ML, BOT, PW, TOP-BOT, lw=1)
    y = TOP

    # Company / Name
    hline(ML, y, MR, lw=1)
    txt(ML+3, y-10, L['company'], sz=8, bold=True)
    txt(ML+3+stringWidth(L['company'],'Helvetica-Bold',8)+3, y-10, val('company'), sz=8)
    hline(ML, y-14, MR)
    txt(ML+3, y-25, L['name'], sz=8, bold=True)
    txt(ML+3+stringWidth(L['name'],'Helvetica-Bold',8)+3, y-25, val('name'), sz=8)
    hline(ML, y-28, MR)

    SPLIT = ML + PW*0.49
    # Date + Weather
    txt(ML+3, y-39, L['date'], sz=8, bold=True)
    txt(ML+3+stringWidth(L['date'],'Helvetica-Bold',8)+3, y-39, val('date'), sz=8)
    txt(SPLIT+4, y-39, L['weather'], sz=8, bold=True)
    wx = val('weather')
    for i,(lbl,key) in enumerate([(L['clear'],'Clear'),(L['rain'],'Rain'),(L['overcast'],'Overcast')]):
        cx=SPLIT+46+i*46; cb(cx,y-42,checked=(wx==key)); txt(cx+9,y-39,lbl,sz=7)
    hline(ML,y-43,SPLIT); hline(ML,y-43,MR)

    # Location + Weather row 2
    txt(ML+3, y-54, L['location'], sz=8, bold=True)
    txt(ML+3+stringWidth(L['location'],'Helvetica-Bold',8)+3, y-54, val('location'), sz=8)
    for i,(lbl,key) in enumerate([(L['sunny'],'Sunny'),(L['drizzle'],'Drizzle'),(L['foggy'],'Foggy')]):
        cx=SPLIT+46+i*46; cb(cx,y-57,checked=(wx==key)); txt(cx+9,y-54,lbl,sz=7)
    hline(ML,y-60,MR)
    cb(SPLIT+46,y-72,checked=(wx=='Other')); txt(SPLIT+56,y-69,L['other'],sz=7)
    hline(ML,y-74,MR)

    # Scope + Temp/Wind/Notes
    txt(ML+3, y-85, L['scope'], sz=8, bold=True)
    scope=val('scope'); words=scope.split(); lines=[]; line=''
    for w in words:
        if len(line)+len(w)+1<=42: line=(line+' '+w).strip()
        else:
            if line: lines.append(line)
            line=w
    if line: lines.append(line)
    sy=y-97
    for ln in lines[:4]:
        txt(ML+3, sy, ln, sz=8); sy-=10

    txt(SPLIT+4, y-85, L['temp'], sz=8, bold=True)
    txt(SPLIT+4+stringWidth(L['temp'],'Helvetica-Bold',8)+4, y-85, val('temp'), sz=8)
    wind=val('wind')
    txt(SPLIT+4, y-100, L['wind'], sz=8, bold=True)
    for i,(lbl,key) in enumerate([(L['vlight'],'Very Light'),(L['windy'],'Windy'),(L['vwindy'],'Very Windy')]):
        cx=SPLIT+34+i*50; cb(cx,y-103,checked=(wind==key)); txt(cx+9,y-100,lbl,sz=7)
    txt(SPLIT+4, y-115, L['notes'], sz=8, bold=True)
    txt(SPLIT+4+stringWidth(L['notes'],'Helvetica-Bold',8)+4, y-115, val('wxNotes'), sz=8)
    hline(ML,y-120,MR,lw=1); vline(SPLIT,y-43,y-120); y-=120

    # Emergency Procedures
    txt(ML+3, y-11, L['emerg'], sz=9, bold=True)
    hline(ML,y-14,MR)
    notw=val('notifyW')
    txt(ML+3, y-24, L['notifyQ'], sz=7.5)
    nqw=stringWidth(L['notifyQ'],'Helvetica',7.5)
    cb(ML+3+nqw+5,y-27,checked=(notw=='Yes')); txt(ML+3+nqw+15,y-24,L['yes'],sz=8)
    cb(ML+3+nqw+30,y-27,checked=(notw=='No')); txt(ML+3+nqw+40,y-24,L['no'],sz=8)
    inj=val('injured')
    txt(ML+3, y-36, L['injuredQ'], sz=8)
    iqw=stringWidth(L['injuredQ'],'Helvetica',8)
    cb(ML+3+iqw+5,y-39,checked=(inj=='Yes')); txt(ML+3+iqw+15,y-36,L['yes'],sz=8)
    cb(ML+3+iqw+30,y-39,checked=(inj=='No')); txt(ML+3+iqw+40,y-36,L['no'],sz=8)
  

    emerg=d.get('emergChecks',[])
    EMERG_MAP=[('firstAid',L['firstAid']),('stretcher',L['stretcher']),('msds',L['msds']),
               ('evacuation',L['evacuation']),('fireExt',L['fireExt'])]
    ey=y
    for key,lbl in EMERG_MAP:
        cb(ML+3,ey-12,checked=(key in emerg))
        txt(ML+13,ey-9,lbl,sz=7.5); ey-=13

    # Clinic / Hospital — auto-spaced
    RCOL=SPLIT-32
    txt_lv(RCOL, y-9,  L['clinicName'], val('clinicName'))
    txt_lv(RCOL, y-22, L['clinicLoc'],  val('clinicLoc'))
    proto=val('clinicProto')
    txt(RCOL, y-35, L['clinicProto'], sz=7.5, bold=True)
    pw2=stringWidth(L['clinicProto'],'Helvetica-Bold',7.5)+5
    cb(RCOL+pw2,y-38,checked=(proto=='Yes')); txt(RCOL+pw2+9,y-35,L['yes'],sz=7.5)
    cb(RCOL+pw2+24,y-38,checked=(proto=='No')); txt(RCOL+pw2+33,y-35,L['no'],sz=7.5)
    txt_lv(RCOL, y-48, L['hospName'], val('hospName'))
    txt_lv(RCOL, y-61, L['hospLoc'],  val('hospLoc'))
    vline(SPLIT,ey,y); hline(ML,ey,MR,lw=1); y=ey

    # Steps
    txt(ML+3,y-11,L['steps'],sz=9,bold=True); hline(ML,y-14,MR)
    steps=d.get('steps',[])
    for i in range(5):
        ry=y-14-(i*13)
        txt(ML+3,ry-10,f'{i+1}.',sz=8,bold=True)
        txt(ML+16,ry-10,steps[i] if i<len(steps) else '',sz=8)
        hline(ML,ry-13,MR)
    y=y-14-(5*13)

    # Potential Hazards
    txt(W/2,y-10,L['hazards'],sz=9,bold=True,align='center')
    hline(ML,y-13,MR); y-=13
    haz_set=set(d.get('hazards',[]))

    HAZ_ROWS=[
      ['Access / Egress','Crane','Fire Hazards','Impalement Hazards','Material Handling'],
      ['Access to General Public','Demolition','Floor / Wall Openings','Ladders (Tied Off / Inspected)','Overhead Power Lines'],
      ['Barricades / Signage','Electrical Hazards','Guardrails / Toeboards / Bracing','Lifts','Pinch Points'],
      ['Chemical Hazards','Excavation / Trench','Hearing Protection','Lighting','Powder Actuated Tools'],
      ['Confined Spaces','Fall Hazards','Heavy Equipment','Lockout / Tagout','Traffic Control'],
      ['Inspection Current','Proper Tools for the Job','Tools in Good Working Condition','Qualification Required','Lift Equipment Properly Inspected by Qualified Person'],
      ['Manual Lifting Equipment','Proper Rigging Practices','Manual Lifting (Using Your Legs) <50 lbs','Hole Covers','Overhead Work / Other'],
      ['Work Crews Heavy Equipment','Underground Utilities','Scaffold (Properly Inspected by Competent Person)','Personal Basket (Inspected and Approved)',None],
    ]
    for row in HAZ_ROWS:
        rh=draw_haz_row(y,row,haz_set); y-=rh

    c.showPage()

    # ══════════════════════════════════════════
    # PAGE 2
    # ══════════════════════════════════════════
    TOP2=756; BOT2=60
    rect(ML,BOT2,PW,TOP2-BOT2,lw=1); y2=TOP2

    P2_ROWS=[
      ['Aerial Lift / Certification','Confined Space (Entry)','Try Start / Stop Switch','GFCI','Slip / Trip Potential'],
      ['Body Position / Line of Fire','Crush By / Struck By / Contact With','Adequate Anchorage Points','Sharp Objects',None],
    ]
    other_haz=val('otherHaz')
    for ri,row in enumerate(P2_ROWS):
        if ri==1:
            # last col is "Other"
            max_lines=1
            for k in row:
                if k: max_lines=max(max_lines,len(split_lines(HL.get(k,k))))
            rh=max(18,max_lines*8+6); mid_y=y2-rh/2
            for ci,key in enumerate(row):
                cx=ML+ci*PW/5
                if key is None:
                    cb_y=mid_y-4
                    c.setLineWidth(0.6);c.setStrokeColor(BLACK);c.setFillColor(WHITE)
                    c.rect(cx+2,cb_y,8,8,fill=1,stroke=1)
                    if other_haz:
                        c.setFillColor(BLACK);c.setFont('Helvetica-Bold',8);c.drawString(cx+3,cb_y+1,'X')
                    txt(cx+14,mid_y+1,'Other:',sz=6.5)
                    txt(cx+14,mid_y-8,other_haz[:18],sz=6.5)
                else:
                    lines=split_lines(HL.get(key,key))
                    checked=key in haz_set
                    cb_y=mid_y-4
                    c.setLineWidth(0.6);c.setStrokeColor(BLACK);c.setFillColor(WHITE)
                    c.rect(cx+2,cb_y,8,8,fill=1,stroke=1)
                    if checked:
                        c.setFillColor(BLACK);c.setFont('Helvetica-Bold',8);c.drawString(cx+3,cb_y+1,'X')
                    tx=cx+14; total_h=len(lines)*8; ty=mid_y+total_h/2-2
                    for ln in lines: txt(tx,ty,ln,sz=6.5); ty-=8
                if ci>0: vline(cx,y2-rh,y2,lw=0.3)
            hline(ML,y2-rh,MR,lw=0.3); y2-=rh
        else:
            rh=draw_haz_row(y2,row,haz_set); y2-=rh

    # Preventive Measures
    txt(W/2,y2-10,L['prevMeasures'],sz=9,bold=True,align='center')
    hline(ML,y2-13,MR)
    pm=d.get('preventive',[]); PMID=ML+PW/2
    for i in range(4):
        ry=y2-13-(i*13)
        txt(ML+3,ry-10,f'{i+1}.',sz=8,bold=True); txt(ML+16,ry-10,pm[i] if i<len(pm) else '',sz=8)
        txt(PMID+3,ry-10,f'{i+5}.',sz=8,bold=True); txt(PMID+16,ry-10,pm[i+4] if i+4<len(pm) else '',sz=8)
        hline(ML,ry-13,MR,lw=0.3)
    vline(PMID,y2-13,y2-13-(4*13),lw=0.3); y2-=(13+4*13)

    # Ergonomics + PPE
    EMID=ML+PW/2
    rect(ML,y2-12,EMID-ML,12,fill=LGRAY); rect(EMID,y2-12,MR-EMID,12,fill=LGRAY)
    txt(ML+(EMID-ML)/2,y2-9,L['ergo'],sz=7.5,bold=True,align='center')
    txt(EMID+(MR-EMID)/2,y2-9,L['ppe'],sz=7.5,bold=True,align='center')
    hline(ML,y2-12,MR)
    ergo=d.get('ergos',[]); ppe=d.get('ppe',[])
    ECMID=ML+(EMID-ML)/2
    EL=[L['awkward'],L['force'],L['lifting'],L['overhead']]
    ER=[L['reach'],L['repetitive'],L['sharpsurf'],L['vibrating']]
    PI=[L['hardhat'],L['glasses'],L['vest'],L['boots']]
    EK_EN=[['Awkward Positioning','Excessive Force','Lifting','Overhead Work'],
           ['Reach/Clear Access','Repetitive Movements','Sharp Work Surfaces','Vibrating Tools/Equipment'],
           ['Hard Hat','Safety Glasses','Safety Vest','Work Boots']]
    RHE=11
    for i in range(4):
        ry=y2-12-(i*RHE)
        cb(ML+3,ry-RHE+3,checked=(EK_EN[0][i] in ergo)); txt(ML+13,ry-RHE+5,EL[i],sz=7)
        cb(ECMID+3,ry-RHE+3,checked=(EK_EN[1][i] in ergo)); txt(ECMID+13,ry-RHE+5,ER[i],sz=7)
        cb(EMID+3,ry-RHE+3,checked=(EK_EN[2][i] in ppe)); txt(EMID+13,ry-RHE+5,PI[i],sz=7)
        vline(ECMID,ry-RHE,ry,lw=0.3); hline(ML,ry-RHE,MR,lw=0.3)
    y2-=(12+4*RHE)
    other_ppe=val('otherPPE')
    if other_ppe:
        txt(EMID+3,y2-9,f'+ {other_ppe}',sz=7); hline(ML,y2-12,MR,lw=0.3); y2-=12
    hline(ML,y2,MR,lw=1)

    # Civil Work
    civil_na = not val('soilType') and not val('excavDepth')
    txt(ML+3,y2-10,L['civilWork'],sz=8,bold=True)
    txt(ML+3+stringWidth(L['civilWork'],'Helvetica-Bold',8)+4,y2-10,L['civilNote'],sz=6)
    hline(ML,y2-13,MR); y2-=13

    if civil_na:
        txt(ML+3,y2-10,L['naText'],sz=8,col=DGRAY)
        hline(ML,y2-14,MR,lw=0.3); y2-=14
    else:
        # Q1 soil type
        txt(ML+3,y2-10,L['soil1'],sz=7)
        soil=val('soilType')
        scx=ML+3+stringWidth(L['soil1'],'Helvetica',7)-31
        for sv,sl in [('Type A Soil/Rock',L['typeA']),('Type B Soil/Rock',L['typeB']),('Type C Soil/Rock',L['typeC'])]:
            cb(scx,y2-13,checked=(soil==sv)); txt(scx+10,y2-10,sl,sz=6.5); scx+=82
        hline(ML,y2-14,MR,lw=0.3); y2-=14
        txt(ML+3,y2-10,val('excavDepth'),sz=8)
        hline(ML,y2-14,MR,lw=0.3); y2-=14

        # Q2 cave-in — check if enough space, else new page
        cave_h=38
        if y2-cave_h < BOT2:
            c.showPage(); rect(ML,BOT2,PW,TOP2-BOT2,lw=1); y2=TOP2

        txt(ML+3,y2-10,L['cave2'],sz=7)
        hline(ML,y2-13,MR,lw=0.3); y2-=13
        ci_list=d.get('civilControls',[])
        ci_opts=[('Sloping','Sloping'),('Benching','Benching'),('Trenching','Trenching'),
                 ('Shoring','Shoring'),('Shield / Box','Shield/box'),
                 ("Ladder in Trench >5 ft and Every 25'","Ladder >5ft/25'"),
                 ('Sump Pump','Sump Pump'),('LOTO','LOTO')]
        ccx=ML+3
        for ck2,cl in ci_opts:
            cb(ccx,y2-12,checked=(ck2 in ci_list)); txt(ccx+10,y2-9,cl,sz=6.5); ccx+=68
        hline(ML,y2-14,MR,lw=0.3); y2-=14
        loto_y=y2-12
        cb(ML+3,loto_y,checked=('LOTO' in ci_list))
        hline(ML,y2-14,MR,lw=0.3); y2-=14

        # Q3-5 text rows
        for lbl,key in [(L['terrain3'],'terrain'),(L['vehicle4'],'vehicleAccess'),(L['elecgas5'],'elecGas')]:
            if y2-26 < BOT2:
                c.showPage(); rect(ML,BOT2,PW,TOP2-BOT2,lw=1); y2=TOP2
            txt(ML+3,y2-9,lbl,sz=7); txt(ML+3,y2-20,val(key),sz=8)
            hline(ML,y2-24,MR,lw=0.3); y2-=24

        # Q6-9 yes/no rows
        def yn_row(lbl_l,k_l,lbl_r,k_r,y):
            RH=36 if lang=='es' else 18; mid=y-RH/2; cb_y=mid-3.5; ty=mid+2
            txt(ML+3,ty,lbl_l,sz=6.5)
            vl=d.get(k_l,'')
            cb(ML+195,cb_y,checked=(vl=='Yes')); txt(ML+205,ty,L['yes'],sz=7)
            cb(ML+218,cb_y,checked=(vl=='No'));  txt(ML+228,ty,L['no'],sz=7)
            vline(PMID,y-RH,y,lw=0.3)
            txt(PMID+3,ty,lbl_r,sz=6.5)
            vr=d.get(k_r,'')
            cb(MR-55,cb_y,checked=(vr=='Yes')); txt(MR-46,ty,L['yes'],sz=7)
            cb(MR-38,cb_y,checked=(vr=='No'));  txt(MR-29,ty,L['no'],sz=7)
            return RH

        rh=yn_row(L['util6'],'utilLoc',L['tx8117'],'tx811',y2)
        hline(ML,y2-rh,MR,lw=0.3); y2-=rh
        rh=yn_row(L['valves8'],'shutValves',L['inspect9'],'excavInsp',y2)
        hline(ML,y2-rh,MR,lw=0.3); y2-=rh
        txt(ML+3,y2-9,L['wx10'],sz=7); txt(ML+3,y2-20,val('civilWx'),sz=8)
        hline(ML,y2-24,MR,lw=0.3); y2-=24

    hline(ML,y2,MR,lw=1)

    # Crew Signatures
    txt(W/2,y2-10,L['crew'],sz=9,bold=True,align='center')
    hline(ML,y2-13,MR)
    N1=ML+PW*0.38; N2=ML+PW*0.62; HDR_H=14
    rect(ML,y2-13-HDR_H,N1-ML,HDR_H,fill=LGRAY)
    rect(N1,y2-13-HDR_H,N2-N1,HDR_H,fill=LGRAY)
    rect(N2,y2-13-HDR_H,MR-N2,HDR_H,fill=LGRAY)
    hy=y2-13-HDR_H/2-3
    txt(ML+3,hy,L['printed'],sz=7.5,bold=True)
    txt(N1+3,hy,L['hh'],sz=7.5,bold=True)
    txt(N2+3,hy,L['signature'],sz=7.5,bold=True)
    hline(ML,y2-13-HDR_H,MR,lw=0.5)

    crew=d.get('crew',[]); cy2=y2-13-HDR_H; CRH=22
    p2_crew=[]; p3_crew=[]

    def crew_row(y,name='',hh='',sig_b64='',filled=False):
        if y-CRH<BOT2: return False
        ty=y-CRH+7
        if filled:
            txt(ML+3,ty,name,sz=8,bold=True); txt(N1+3,ty,hh,sz=8)
            if sig_b64 and sig_b64.startswith('data:image'):
                try:
                    from reportlab.lib.utils import ImageReader
                    img_data=base64.b64decode(sig_b64.split(',')[1])
                    ir=ImageReader(io.BytesIO(img_data))
                    c.drawImage(ir,N2+3,y-CRH+2,width=MR-N2-6,height=CRH-4,
                                preserveAspectRatio=True,mask='auto')
                except: pass
        else:
            txt(ML+3,ty,L['printed'],sz=7,col=DGRAY)
            txt(N1+3,ty,L['hh'],sz=7,col=DGRAY)
            txt(N2+3,ty,L['signature'],sz=7,col=DGRAY)
        vline(N1,y-CRH,y,lw=0.3); vline(N2,y-CRH,y,lw=0.3)
        hline(ML,y-CRH,MR,lw=0.3)
        return True

    for i in range(len(crew)):
        if cy2-CRH<BOT2: p3_crew=crew[i:]; break
        crew_row(cy2,crew[i].get('name',''),crew[i].get('hh',''),crew[i].get('sig',''),filled=True)
        p2_crew.append(crew[i]); cy2-=CRH
    for _ in range(12):
        if cy2-CRH<BOT2: break
        crew_row(cy2,filled=False); cy2-=CRH

    c.showPage()

    # ══════════════════════════════════════════
    # PAGE 3 — overflow crew
    # ══════════════════════════════════════════
    rect(ML,BOT2,PW,TOP2-BOT2,lw=1)
    txt(W/2,TOP2-11,f'(JHA) {L["title1"]} {L["title2"]}',sz=10,bold=True,align='center')
    hline(ML,TOP2-14,MR,lw=1)
    cy3=TOP2-14
    rect(ML,cy3-HDR_H,N1-ML,HDR_H,fill=LGRAY)
    rect(N1,cy3-HDR_H,N2-N1,HDR_H,fill=LGRAY)
    rect(N2,cy3-HDR_H,MR-N2,HDR_H,fill=LGRAY)
    hy3=cy3-HDR_H/2-3
    txt(ML+3,hy3,L['printed'],sz=7.5,bold=True)
    txt(N1+3,hy3,L['hh'],sz=7.5,bold=True)
    txt(N2+3,hy3,L['signature'],sz=7.5,bold=True)
    hline(ML,cy3-HDR_H,MR,lw=0.3); cy3-=HDR_H
    for i in range(len(p3_crew)+12):
        if cy3-CRH<BOT2: break
        filled=i<len(p3_crew)
        crew_row(cy3,p3_crew[i].get('name','') if filled else '',
                 p3_crew[i].get('hh','') if filled else '',
                 p3_crew[i].get('sig','') if filled else '',filled=filled)
        cy3-=CRH

    c.showPage(); c.save()
    print(f"PDF saved -> {out_path}")

if __name__=='__main__':
    build(sys.argv[1], sys.argv[2])
