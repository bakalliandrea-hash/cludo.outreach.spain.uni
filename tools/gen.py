import pandas as pd, re, json, urllib.parse as up

SRC = 'apollo-contacts-export.csv'
OUT = '.'

df = pd.read_csv(SRC)
g = df[df['Email Status'].str.lower().isin(['valid', 'verified'])
       & (df['Stage'] == 'Cold') & (df['Email Sent'] != True)].copy()

# ---------- organisation name + article ----------
ORG_FIX = {
    'CTO': 'Grupo CTO',
    'University of Navarra': 'Universidad de Navarra',
    'University of Valencia': 'Universitat de València',
    'Máster Marketing Digital USC': 'Universidade de Santiago de Compostela',
    'Postgrado en Odontología UCAM': 'UCAM Universidad Católica San Antonio de Murcia',
    'FSUPV Team': 'Universitat Politècnica de València',
}
FEM = r'^(Universidad|Universitat|Universidade|University|Fundaci[oó]n?|Fundacio|Escuela|Escola|Instituci[oó]n)\b'
MASC = r'^(Hospital|Institut|Instituto|Centro|Centre|Colegio|Parc|Campus|Consorci|Grupo|Club|Taller|Johan)\b'

def org_of(row):
    name = str(row['Company Name for Emails']).strip()
    name = ORG_FIX.get(name, name)
    if re.search(FEM, name, re.I):
        art = 'la'
    elif re.search(MASC, name, re.I):
        art = 'el'
    else:
        art = ''
    return name, art

def en_org(name, art):      # "en la Universidad X" / "en el Hospital X" / "en Esade"
    return f"en {art} {name}" if art else f"en {name}"

def de_org(name, art):      # "de la Universidad X" / "del Hospital X" / "de Esade"
    if art == 'la': return f"de la {name}"
    if art == 'el': return f"del {name}"
    return f"de {name}"

# ---------- title -> área ----------
ACADEMIC = re.compile(r"m[aá]ster\b|master\b|c[aá]tedra|catedr|profesor|professor|lecturer|^chair\b|chair,|research|investig|"
                      r"\binstitut(?:e|o)?\b|\btfm\b|\btfe\b|observatorio|co-director|^department of|director del? departamento|"
                      r"director de la escuela|director general of|deputy director of academic|m[eé]dico|mathematical|"
                      r"advanced vehicle|dir\. m[aá]ster|^associate professor|sede colombia|director gass|director del centro|"
                      r"financial & it|sede colombia|cto ucam", re.I)
ACADEMIC_OVERRIDE = re.compile(r"\bCTO\b(?! UCAM)|responsable tic|it manager|head of communications?|communications? manager|webmaster|"
                               r"academic director & cto|head of operations, information and technology", re.I)

RULES = [
    # (regex, phrase)
    (r"telecomunic|comunicaciones y sistemas|sistemas.*comunicaciones|infrastructure and communications|infraestructura, comunicaciones|networking, communications|technology & communications", "los sistemas y la infraestructura tecnológica"),
    (r"university press website", "la web"),
    (r"web analytics", "la analítica web"),
    (r"admissions", "las admisiones, el marketing y la comunicación"),
    (r"internal communications", "la comunicación interna"),
    (r"press|\bpr\b|media relations|protocolo", "la comunicación y las relaciones con los medios"),
    (r"digital engagement", "la comunicación digital"),
    (r"(communicat|comunica|komunikazio).*(marketing|branding|brand)|(marketing|branding|brand).*(communicat|comunica)", "la comunicación y el marketing"),
    (r"community manager|social media", "las redes sociales y la web"),
    (r"growth digital marketing|marketing digital|digital marketing", "el marketing digital"),
    (r"\bseo\b", "la web y el SEO"),
    (r"webmaster", "la web"),
    (r"contenidos? web|web content|content manager|website content|publications", "los contenidos de la web"),
    (r"web project|portales web|project manager de portales|plataforma y aplicaciones web|aplicaciones web|p[aá]ginas web", "los proyectos web"),
    (r"web develop|desarrollo web", "el desarrollo web"),
    (r"web design|diseño gráfico-web|dise[ñn]adora|visual design", "el diseño web"),
    (r"website|\bweb\b|responsable de web", "la web"),
    (r"communicat|comunica|komunikazio|outreach|\bcomms\b", "la comunicación"),
    (r"marketing", "el marketing"),
    (r"digital strategy|digital transformation|transformation|digital department|chief digital|digitalization|innovation", "la estrategia digital y la tecnología"),
    (r"\bcto\b|chief techn|technical chief|technology officer|\bctto\b|\bcta\b", "la tecnología"),
    (r"\bcio\b|it director|director de sistemas|director sistemas|director de tic|director tic|director (del )?[aá]rea tic|"
     r"director ejecutivo|director - information|director del [aá]rea de sistemas|it systems", "los sistemas de información"),
    (r"infrastructure|infraestructura", "la infraestructura tecnológica"),
    (r"security|seguridad", "la seguridad informática"),
    (r"it support|soporte|cau tic", "el soporte informático"),
    (r"it project|project manager it|project manager|it service|it business|portfolio", "los proyectos tecnológicos"),
    (r"software|developer|programador|application|aplicaciones|lms", "las aplicaciones y los sistemas"),
    (r"\bit\b|\bict\b|\btic\b|\bti\b|inform[aá]tic|sistemas|computer|technology|tecnolog|network|redes", "los sistemas informáticos"),
    (r"training", "la formación"),
]
RULES = [(re.compile(p, re.I), ph) for p, ph in RULES]

def area_of(title):
    t = str(title)
    if 'grupo cto' in t.lower() and not re.search(r'\bCTO\b(?! UCAM)(?!\s*$)', t):
        t = re.sub(r'grupo cto', '', t, flags=re.I)
    if ACADEMIC.search(t) and not ACADEMIC_OVERRIDE.search(t):
        return "la parte académica", True
    for rx, ph in RULES:
        if rx.search(t):
            return ph, False
    return "la web", True

# ---------- template ----------
SENDER = 'andrea.bakalli@cludo.com'

TEMPLATE = """Hola {nombre},

He visto que te ocupas de {area} {en_org} y te escribo en relación con el buscador de vuestra web.

Cuando los estudiantes y el personal no encuentran información que ya está publicada en la web, acaban acudiendo a la secretaría o al CAU. Un buscador más eficaz les ayuda a resolver sus dudas de forma autónoma y reduce las consultas repetitivas que llegan a estos servicios.

En Cludo trabajamos con varias universidades europeas, entre ellas King's College London, Stockholm University y Copenhagen University, para mejorar la búsqueda en sus webs.

En los últimos meses hemos desarrollado una herramienta que analiza el buscador de vuestra web desde el punto de vista de los usuarios. El informe muestra, con ejemplos concretos, qué búsquedas llevan a la información correcta, cuáles presentan problemas y qué podéis mejorar, incluso por vuestra cuenta y sin depender de nosotros.

¿Te interesaría una breve presentación de nuestra solución, tomando como referencia cómo otras universidades han mejorado la búsqueda en su web? El análisis es totalmente gratuito y sin ningún compromiso.

Si no eres tú la persona que lleva este tema, ¿me podrías indicar a quién dirigirme?"""

NAME_FIX = {'M?': 'Mª Ángeles'}
def clean_name(n):
    n = str(n).strip()
    n = NAME_FIX.get(n, n)
    return n.title() if n.isupper() or n.islower() else n

def q(s):  # RFC3986 encoding, safe for mailto and Outlook deeplink
    return up.quote(s, safe='')

rows = []
for _, r in g.iterrows():
    name, art = org_of(r)
    area, flag = area_of(r['Title'])
    first = clean_name(r['First Name'])
    body = TEMPLATE.format(nombre=first, area=area, en_org=en_org(name, art)).replace('de el ', 'del ')
    subject = f"Experiencia de búsqueda en la web {de_org(name, art)}"
    email = r['Email'].strip()
    mailto = f"mailto:{email}?subject={q(subject)}&body={q(body)}"
    owa = f"https://outlook.office.com/mail/deeplink/compose?to={q(email)}&subject={q(subject)}&body={q(body)}&login_hint={q(SENDER)}"
    rows.append(dict(
        first_name=first, last_name=str(r['Last Name']).strip(), title=r['Title'], area=area,
        organisation=name, email=email, website=r['Website'], city=r['City'] if pd.notna(r['City']) else '',
        subject=subject, body=body, mailto=mailto, outlook_web=owa,
        review='yes' if flag else '', linkedin=r['Person Linkedin Url'] if pd.notna(r['Person Linkedin Url']) else '',
        apollo_contact_id=r['Apollo Contact Id'], salesforce_id=r['Salesforce ID'] if pd.notna(r['Salesforce ID']) else ''))

out = pd.DataFrame(rows).sort_values(['organisation', 'last_name'])
out.to_csv(f'{OUT}/cludo_spain_outreach.csv', index=False)
with open(f'{OUT}/contacts.json', 'w') as f:
    json.dump([{k: v for k, v in d.items() if k not in ('mailto', 'outlook_web')} for d in out.to_dict('records')], f, ensure_ascii=False)
print(len(out), 'rows;', (out.review == 'yes').sum(), 'flagged')
print(out.area.value_counts().to_string())
print(out[out.review == 'yes'][['title', 'organisation', 'area']].to_string())
