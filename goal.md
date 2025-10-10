https://www.notion.so/Scraper-Indeed-26aececfe1b180fb9f15c1898b25af5c

## **🎯 Project Goal**

Develop a Python script for the automated daily extraction of job postings from Indeed, with intelligent matching to companies in the corporate database and data preparation for processing via LLM.

## **🏢 Business Context**

Indeed is the leading aggregator of job postings from multiple sources. The pipeline involves:

1. **Daily extraction** of all available postings
2. **Processing through LLM** for categorization (out of scope of the project)
3. **Publication** on the company portal (out of scope of the project)

---

## **📋 Functional Requirements**

### **✅ Mandatory Requirements**

- **Zero budget**: Exclusive use of free APIs or web scraping. If you use APIs, make sure they are serious provider (not Chinese one)
- **Simple architecture**: Maximum 2–3 Python files (main script + optional configuration)
- **Company matching**: Automated association system with the existing company database (see **Phase 2: Company Matching System**)

### **📊 Data to Extract for Each Job Posting**

**Mandatory fields:**

- URL of the Indeed job posting (required)
- Full job description text (required)

**Optional fields:**

- Company page URL on Indeed
- Job posting publication date
- Company name

---

## **🔄 Detailed Technical Workflow**

### **Phase 1: Data Extraction from Indeed**

Implement one of the following strategies (in priority order):

1. **Free public APIs** of Indeed (if available)
2. **Web scraping**
3. **Alternative endpoints** that aggregate Indeed data

### **Phase 2: Company Matching System**

Implement a multi-level algorithm to associate each posting with companies in the database:

### **🔴 Strategy 1: URL Matching (Highest Priority)**

```
# Direct comparison between the company URL extracted from Indeed and the "url" field in the DB
indeed_company_url = "https://asgconsulting.it/"
db_company_url = company["url"]  # from company JSON

# Implement URL normalization (remove www, trailing slash, etc.)
```

### **🟡 Strategy 2: Company Name with Fuzzy Matching (Medium Priority)**

```
# Fuzzy matching between the company name from Indeed and company fields
indeed_company_name = "Asg consulting"
db_ragione_sociale = company["ragioneSociale"]  # "ASG CONSULTING S.R.L."
db_name = company["name"]  # "Asg consulting"

# Use libraries like fuzzywuzzy or similar for intelligent matching
```

### **🔵 Strategy 3: Google API + VAT Number (Low Priority, Fallback)**

```
# Only if previous strategies fail
# 1. Query Google API with the extracted company name
# 2. Extract VAT number from Google results
# 3. Match with "iva" field in the company database
```

---

## **📊 Final Output Format**

For each processed posting, generate a structured JSON record:

```
{
  "url_job_indeed": "https://it.indeed.com/viewjob?jk=abc123",
  "url_company_indeed": "https://it.indeed.com/company?jk=abc",
  "testo_offerta": "Full job description...", /*llm*/
  "companyID": "M*****0vb******Y",
  "data_estrazione": "2025-09-10",
  "url_azienda": "https://asgconsulting.it/"
}
```

**Note**: All this fields are fundamental for the success of the code. English translation:

- Testo-offerta: job offers full text
- data_estrazione: when you have found (date) this job offers. Note: the date of found must be the same date of publication, it means that you need to crawl jobs the same date of publication.
- url_azienda: company’s URL of home page (e.g.: [https://vocations.io](https://vocations.io/))

## **🏢 Example Reference Company Database Entry**

```
{
  "_id": {"$oid": "******2a02********"},
  "companyID": "M*****0vb******Y",
  "ragioneSociale": "ASG CONSULTING S.R.L.",
  "employees": 603,
  "vat": "IT09372750969",
  "iva": "09372750969",
  "address": "VIA SANDRO PERTINI 107-109 - 50019 - SESTO FIORENTINO (FI)",
  "city": "SESTO FIORENTINO",
  "province": "Firenze",
  "region": "Toscana",
  "rea": "668187",
  "formaGiuridica": "SR",
  "dataIscrizione": 1454281200,
  "ateco": "Logistics services related to goods distribution",
  "atecoCod": "522922",
  "cameraCommercio": "FI",
  "codiceDestinatario": "M5UXCR1",
  "capitaleSociale": 50000,
  "utile": 96403,
  "fatturato": 20903987,
  "name": "Asg consulting",
  "file": "asgconsultingit.webp",
  "url": "https://asgconsulting.it/",
  "sectors": ["Logistics"],
  "pages": [],
  "details": "https://www.ufficiocamerale.it/6156/asg-consulting-srl",
  "genSector": "Logistics consulting and outsourcing",
  "updatedData": 1751045234,
  "toCheck": "",
  "newGenSector": "Consulting and outsourcing for logistics",
  "newSectors": ["Logistics"],
  "meta_description": "ASG Consulting is a Tuscan company offering consulting, management, and outsourcing services to businesses in the logistics sector."
}
```

---

## **🔍 Allowed Resources and Sources**

- **GitHub repositories**: Analyze and adapt existing Indeed scraping projects
- **API documentation**: Explore official or alternative APIs
- **Online resources**

---

## **🚀 Final Deliverables**

### **📁 Code**

- **Main Python script** working and tested
- **Requirements.txt** with dependencies

### **📖 Documentation**

- **README.md** with installation and usage instructions
- **Inline comments** in the code for maintainability

### **🧪 Validation**

- **Test dataset** with at least 10 processed postings
- **Sample logs** of correct execution


Some data
ACCENTURE S.P.A.
TOD'S S.P.A.
LFOUNDRY S.R.L.
COMOLI, FERRARI E C. - S.P.A
​
More data
ACCENTURE S.P.A.
TOD'S S.P.A.
LFOUNDRY S.R.L.
COMOLI, FERRARI E C. - S.P.A
FPT INDUSTRIAL S.P.A. O, PER ESTESO, FIAT POWERTRAIN TECHNOLOGIES INDUSTRIAL S.P.A.
GESCO SOCIETA' COOPERATIVA AGRICOLA IN BREVE GESCO S.C.A.
COMMERCIANTI INDIPENDENTI ASSOCIATI - SOCIETA' COOPERATIVA
ABB S.P.A.
ENEL PRODUZIONE S.P.A.
HERA COMM S.P.A.
NUOVO PIGNONE INTERNATIONAL S.R.L.
SONATRACH RAFFINERIA ITALIANA S.R.L.
WIND TRE S.P.A.
A2A ENERGIA S.P.A.
AGRICOLA TRE VALLI - SOCIETA' COOPERATIVA
A.I.A. - AGRICOLA ITALIANA ALIMENTARE - S.P.A.
ARVAL SERVICE LEASE ITALIA S.P.A.
ASPIAG SERVICE S.R.L.
AUTOSTRADE PER L'ITALIA S.P.A.
AUTOTORINO S.P.A.
BASF ITALIA S.P.A.
CALZEDONIA S.P.A.
MARCEGAGLIA CARBON STEEL S.P.A.
CNH INDUSTRIAL ITALIA S.P.A.
COOP ALLEANZA 3.0 SOCIETA' COOPERATIVA
COSTA CROCIERE S.P.A.
ESPRINET S.P.A.
EDENRED ITALIA S.R.L.
ENGIE ITALIA SPA
ESSELUNGA SPA
LUXOTTICA GROUP SPA
FINCANTIERI S.P.A.
A2A S.P.A.
IREN MERCATO S.P.A.
TELECOM ITALIA SPA O TIM S.P.A.
GESTORE DEI SERVIZI ENERGETICI - GSE S.P.A.
HITACHI RAIL STS S.P.A.
UNICOOP FIRENZE SOCIETA' COOPERATIVA IN SIGLA UNICOOP FIRENZE SC
IKEA ITALIA RETAIL S.R.L.
STMICROELECTRONICS S.R.L.
ITALIA TRASPORTO AEREO S.P.A.
LIDL ITALIA S.R.L.
MAXI DI S.R.L.
COMIFAR DISTRIBUZIONE S.P.A.
PIRELLI TYRE SPA
POSTE ITALIANE - SOCIETA' PER AZIONI
PRADA S.P.A.
PRYSMIAN POWERLINK S.R.L.
KUWAIT PETROLEUM ITALIA S.P.A.
RETE FERROVIARIA ITALIANA - SOCIETA' PER AZIONI IN SIGLA RFI S .P.A.
SAIPEM S.P.A.
SAMSUNG ELECTRONICS ITALIA S.P.A.
SERVIZIO ELETTRICO NAZIONALE S.P.A.
MEDIAMARKET SPA
ANAS - SOCIETA' PER AZIONI
TECNIMONT S.P.A.
TRENITALIA S.P.A.
VERSALIS S.P.A.
VODAFONE ITALIA S.P.A.
VOLKSWAGEN GROUP ITALIA SOCIETA PER AZIONI (OPPURE - IN FORMA ABBREVIATA - VOLKSWAGEN GROUP ITALIA S.P.A.)
WEBUILD S.P.A.
BARILLA G. E R. FRATELLI - SOCIETA' PER AZIONI
CONAD NORD OVEST SOCIETA' COOPERATIVA
ENI S.P.A.
GRIMALDI EUROMED S.P.A.
IREN ENERGIA S.P.A.
LEONARDO -  SOCIETA' PER AZIONI
LUIGI LAVAZZA - SOCIETA' PER AZIONI ABBREVIABILE ANCHE NELLA SIGLA: LAVAZZA S.P.A.
NUOVO PIGNONE S.R.L.
PAC 2000 A SOCIETA' COOPERATIVA
PHILIP MORRIS ITALIA S.R.L.
SPESA INTELLIGENTE S.P.A.
TERNA - RETE ELETTRICA NAZIONALE SOCIETA' PER AZIONI (IN FORMA ABBREVIATA TERNA S.P.A.)
ACEA ENERGIA S.P.A.
AXPO ITALIA S.P.A.
BMW ITALIA SPA
CONAD - CONSORZIO NAZIONALE DETTAGLIANTI - SOCIETA' COOPERATIVA IN SIGLA CONAD
DUFERCO ENERGIA S.P.A.
E.ON ENERGIA S.P.A.
EDISON ENERGIA S.P.A.
ENEL GLOBAL TRADING S.P.A.
LOGISTA ITALIA S.P.A.
RENAULT ITALIA S.P.A.
SARAS S.P.A. O IN FORMA ESTESA SARAS S.P.A. - RAFFINERIE SARDE
SORGENIA S.P.A.
TOYOTA MOTOR ITALIA S.P.A.
CHIMET - S.P.A.-
EG ITALIA S.P.A.
ESSO ITALIANA S.R.L.
FORD ITALIA S.P.A.
GESTORE DEI MERCATI ENERGETICI S.P.A.
GROUPE PSA ITALIA S.P.A.
REPOWER ITALIA S.P.A.
T.C.A. - TRATTAMENTI CENERI AUROARGENTIFERE - S.P.A.
ENI TRADE & BIOFUELS S.P.A.
FIBERCOP S.P.A.
ITALPREZIOSI S.P.A.
HERA TRADING S.R.L.
SERVIZI ENERGIA ITALIA S.P.A.
FERRARI-SOCIETA'PER AZIONI ESERCIZIO FABBRICHE AUTOMOBILI E CORSE O SEMPLICEMENTE: FERRARI S.P.A.
ACCIAI SPECIALI TERNI S.P.A.
ENI TRADING & SHIPPING S.P.A. - IN LIQUIDAZIONE
UNICOMM - S.R.L.
ENEL ENERGIA S.P.A.
Q8 QUASER S.R.L.
UNIEURO  S.P.A.
IVECO S.P.A.
SKY ITALIA - S.R.L.
SOCIETA' EUROPEA VEICOLI LEGGERI-SEVEL-SPA
MD S.P.A.
ACCIAIERIE D'ITALIA S.P.A.
FASTWEB SPA
ACCIAIERIA ARVEDI S.P.A.
TAMOIL ITALIA S.P.A.
ENIMOOV S.P.A.
AUTOMOBILI LAMBORGHINI S.P.A.
ITALIANA PETROLI S.P.A.
STELLANTIS &YOU ITALIA S.P.A.
SNAM RETE GAS S.P.A. O, IN FORMA ABBREVIATA SNAM RG S.P.A.
GUCCIO GUCCI S.P.A.
EDISON S.P.A.
ENI PLENITUDE S.P.A. SOCIETA' BENEFIT
MERCEDES-BENZ ITALIA S.P.A.
COOP CONSORZIO NORD OVEST SOC. CONSORTILE A R.L.
ESE S.R.L.
LUDOIL ENERGIA S.R.L.
A2A TRADING S.R.L.
BEKO EUROPE MANAGEMENT S.R.L.
ISAB S.R.L.
CENTRALE ADRIATICA SOCIETA' COOPERATIVA
ENILIVE S.P.A.
ACCENTURE S.P.A.
STELLANTIS EUROPE S.P.A.
GS SPA
E-DISTRIBUZIONE S.P.A.
ITX ITALIA S.R.L.
RAI - RADIOTELEVISIONE ITALIANA S.P.A.
ADECCO ITALIA SPA
RANDSTAD ITALIA S.P.A.
WIZZ AIR HUNGARY LTD ITALIAN BRANCH
AMAZON EU S.A R.L.
SONY EUROPE B.V.
AMAZON WEB SERVICES EMEA SARL
NIKE RETAIL B.V.
BRIDGESTONE EUROPE NV/SA
NINTENDO OF EUROPE SE
BASELL SALES & MARKETING COMPANY B.V.
CELANESE SALES GERMANY GMBH


Db data
[{
  "companyID": "Cq0*********b",
  "ragioneSociale": "ENEL PRODUZIONE S.P.A.",
  "vat": "IT05617841001",
  "iva": "05617841001",
  "name": "Enel",
  "url": "https://www.enel.com"
},
{
  "companyID": "yC-*********LN",
  "ragioneSociale": "TOD'S S.P.A.",
  "vat": "IT01113570442",
  "iva": "01113570442",
  "name": "Tod's",
  "url": "http://www.todsgroup.com/"
},
{
  "companyID": "j************Ec",
  "ragioneSociale": "GESCO SOCIETA' COOPERATIVA AGRICOLA IN BREVE GESCO S.C.A.",
  "vat": "IT02522130406",
  "iva": "02522130406",
  "name": "Amadori",
  "url": "http://www.amadori.it/"
},
{
  "companyID": "9*********UX",
  "ragioneSociale": "LFOUNDRY S.R.L.",
  "vat": "IT01465930665",
  "iva": "01465930665",
  "name": "Lfoundry",
  "url": "http://www.lfoundry.com/"
},
{
  "companyID": "g*********u",
  "ragioneSociale": "ABB S.P.A.",
  "vat": "IT11988960156",
  "iva": "11988960156",
  "name": "Abb",
  "url": "https://global.abb/"
},
{
  "companyID": "W*********",
  "ragioneSociale": "ASPIAG SERVICE S.R.L.",
  "vat": "IT00882800212",
  "iva": "00882800212",
  "name": "Despar",
  "url": "https://www.despar.it/it/"
},
{
  "companyID": "p9*********",
  "ragioneSociale": "AGRICOLA TRE VALLI - SOCIETA' COOPERATIVA",
  "vat": "IT02447620234",
  "iva": "02447620234",
  "name": "Agrícola tre valli",
  "url": "https://www.agricolatrevalli.it/"
},
{
  "companyID": "oK*********",
  "ragioneSociale": "ARVAL SERVICE LEASE ITALIA S.P.A.",
  "vat": "IT04911190488",
  "iva": "04911190488",
  "name": "Arval",
  "url": "https://www.arval.it/"
},
{
  "companyID": "qgE*********",
  "ragioneSociale": "A2A ENERGIA S.P.A.",
  "vat": "IT12883420155",
  "iva": "12883420155",
  "name": "A2a",
  "url": "https://www.a2a.it/"
},
{
  "companyID": "Wc*********R",
  "ragioneSociale": "AUTOSTRADE PER L'ITALIA S.P.A.",
  "vat": "IT07516911000",
  "iva": "07516911000",
  "name": "Autostrade",
  "url": "https://www.autostrade.it/"
},
{
  "companyID": "ro*********r",
  "ragioneSociale": "SONATRACH RAFFINERIA ITALIANA S.R.L.",
  "vat": "IT10410680960",
  "iva": "10410680960",
  "name": "Sonatrach italia",
  "url": "https://sonatrachitalia.it/"
},
{
  "companyID": "U6*********M",
  "ragioneSociale": "CALZEDONIA S.P.A.",
  "vat": "IT02253210237",
  "iva": "02253210237",
  "name": "Calzedonia",
  "url": "https://www.calzedonia.com/"
},
{
  "companyID": "jb*********T",
  "ragioneSociale": "MARCEGAGLIA CARBON STEEL S.P.A.",
  "vat": "IT02466220205",
  "iva": "02466220205",
  "name": "Marcegaglia carbon steel",
  "url": "https://www.carbonsteel.marcegaglia.com/"
},
{
  "companyID": "xti*********t",
  "ragioneSociale": "BASF ITALIA S.P.A.",
  "vat": "IT00688460963",
  "iva": "00688460963",
  "name": "Basf",
  "url": "https://www.basf.com/"
},
{
  "companyID": "4gY*********2",
  "ragioneSociale": "A.I.A. - AGRICOLA ITALIANA ALIMENTARE - S.P.A.",
  "vat": "IT00233470236",
  "iva": "00233470236",
  "name": "Aia",
  "url": "https://www.aiafood.com/"
},
{
  "companyID": "ai*********C",
  "ragioneSociale": "AUTOTORINO S.P.A.",
  "vat": "IT10024610155",
  "iva": "10024610155",
  "name": "Autotorino",
  "url": "https://www.autotorino.it/"
},
{
  "companyID": "i*********c",
  "ragioneSociale": "WIND TRE S.P.A.",
  "vat": "IT13378520152",
  "iva": "13378520152",
  "name": "Wind tre",
  "url": "https://windtregroup.it/"
},
{
  "companyID": "5r*********K",
  "ragioneSociale": "LUXOTTICA GROUP SPA",
  "vat": "IT10182640150",
  "iva": "10182640150",
  "name": "Luxottica",
  "url": "https://www.essilorluxottica.com/it/"
},
{
  "companyID": "W2*********1",
  "ragioneSociale": "ESSELUNGA SPA",
  "vat": "IT04916380159",
  "iva": "04916380159",
  "name": "Esselunga",
  "url": "https://www.esselunga.it/"
},
{
  "companyID": "sb2*********",
  "ragioneSociale": "FINCANTIERI S.P.A.",
  "vat": "IT00629440322",
  "iva": "00629440322",
  "name": "Fincantieri",
  "url": "https://www.fincantieri.com/"
},
{
  "companyID": "RRG*********",
  "ragioneSociale": "CNH INDUSTRIAL ITALIA S.P.A.",
  "vat": "IT00370290363",
  "iva": "00370290363",
  "name": "Cnh",
  "url": "https://www.cnh.com/"
},
{
  "companyID": "YVi*********",
  "ragioneSociale": "COSTA CROCIERE S.P.A.",
  "vat": "IT02545900108",
  "iva": "02545900108",
  "name": "Costa cruises",
  "url": "https://www.costacruises.com/"
},
{
  "companyID": "bsT*********",
  "ragioneSociale": "ESPRINET S.P.A.",
  "vat": "IT02999990969",
  "iva": "02999990969",
  "name": "Esprinet",
  "url": "https://www.esprinet.com/it/"
},
{
  "companyID": "X*********CR",
  "ragioneSociale": "COMOLI, FERRARI E C. - S.P.A",
  "vat": "IT00123060030",
  "iva": "00123060030",
  "name": "Comoli ferrari",
  "url": "https://www.comoliferrari.it/"
},
{
  "companyID": "yY*********",
  "ragioneSociale": "COOP ALLEANZA 3.0 SOCIETA' COOPERATIVA",
  "vat": "IT03503411203",
  "iva": "03503411203",
  "name": "Coop alleanza 3.0",
  "url": "https://www.coopalleanza3-0.it/"
},
{
  "companyID": "0y*********",
  "ragioneSociale": "EDENRED ITALIA S.R.L.",
  "vat": "IT09429840151",
  "iva": "09429840151",
  "name": "Edenred",
  "url": "https://www.edenred.it/"
},
{
  "companyID": "Nj*********B",
  "ragioneSociale": "ENGIE ITALIA SPA",
  "vat": "IT06289781004",
  "iva": "06289781004",
  "name": "Engie",
  "url": "https://www.engie.it/"
},
{
  "companyID": "9-*********",
  "ragioneSociale": "IKEA ITALIA RETAIL S.R.L.",
  "vat": "IT02992760963",
  "iva": "02992760963",
  "name": "Ikea",
  "url": "https://www.ikea.com/"
},
{
  "companyID": "WH7*********i",
  "ragioneSociale": "HITACHI RAIL STS S.P.A.",
  "vat": "IT01371160662",
  "iva": "01371160662",
  "name": "Hitachi rail",
  "url": "https://www.hitachirail.com/"
},
{
  "companyID": "Kp*********n",
  "ragioneSociale": "A2A S.P.A.",
  "vat": "IT11957540153",
  "iva": "11957540153",
  "name": "A2a",
  "url": "https://www.gruppoa2a.it/"
},
{
  "companyID": "VF*********Br",
  "ragioneSociale": "STMICROELECTRONICS S.R.L.",
  "vat": "IT00951900968",
  "iva": "00951900968",
  "name": "Stmicroelectronics",
  "url": "http://www.st.com/"
},
{
  "companyID": "xTh*********",
  "ragioneSociale": "GESTORE DEI SERVIZI ENERGETICI - GSE S.P.A.",
  "vat": "IT05754381001",
  "iva": "05754381001",
  "name": "Gse",
  "url": "https://www.gse.it/"
},
{
  "companyID": "ig*********_",
  "ragioneSociale": "TELECOM ITALIA SPA O TIM S.P.A.",
  "vat": "IT00488410010",
  "iva": "00488410010",
  "name": "Tim",
  "url": "https://www.gruppotim.it/"
},
{
  "companyID": "Wd*********j",
  "ragioneSociale": "UNICOOP FIRENZE SOCIETA' COOPERATIVA IN SIGLA UNICOOP FIRENZE SC",
  "vat": "IT00407780485",
  "iva": "00407780485",
  "name": "Coop firenze",
  "url": "https://www.coopfirenze.it/"
},
{
  "companyID": "Zy*********",
  "ragioneSociale": "PRADA S.P.A.",
  "vat": "IT10115350158",
  "iva": "10115350158",
  "name": "Prada",
  "url": "https://www.pradagroup.com/"
},
{
  "companyID": "kC*********",
  "ragioneSociale": "MAXI DI S.R.L.",
  "vat": "IT00542090238",
  "iva": "00542090238",
  "name": "Maxi di",
  "url": "https://www.maxidi.it/"
},
{
  "companyID": "6*********i",
  "ragioneSociale": "LIDL ITALIA S.R.L.",
  "vat": "IT02275030233",
  "iva": "02275030233",
  "name": "Lidl",
  "url": "https://www.lidl.it/"
},
{
  "companyID": "lb*********6",
  "ragioneSociale": "POSTE ITALIANE - SOCIETA' PER AZIONI",
  "vat": "IT01114601006",
  "iva": "01114601006",
  "name": "Poste italiane",
  "url": "https://www.poste.it/"
},
{
  "companyID": "vt*********J7",
  "ragioneSociale": "KUWAIT PETROLEUM ITALIA S.P.A.",
  "vat": "IT00891951006",
  "iva": "00891951006",
  "name": "Q8",
  "url": "https://www.q8.com/"
},
{
  "companyID": "KO-*********H",
  "ragioneSociale": "RETE FERROVIARIA ITALIANA - SOCIETA' PER AZIONI IN SIGLA RFI S .P.A.",
  "vat": "IT01008081000",
  "iva": "01008081000",
  "name": "Rfi",
  "url": "https://www.rfi.it/"
},
{
  "companyID": "V2*********RC",
  "ragioneSociale": "PRYSMIAN POWERLINK S.R.L.",
  "vat": "IT05931070964",
  "iva": "05931070964",
  "name": "Prysmian",
  "url": "https://www.prysmian.com/"
},
{
  "companyID": "T*********JC",
  "ragioneSociale": "VERSALIS S.P.A.",
  "vat": "IT01768800748",
  "iva": "01768800748",
  "name": "Versalis",
  "url": ""
},
{
  "companyID": "yJi*********Z",
  "ragioneSociale": "BARILLA G. E R. FRATELLI - SOCIETA' PER AZIONI",
  "vat": "IT01654010345",
  "iva": "01654010345",
  "name": "Barilla",
  "url": "https://www.barillagroup.com/"
},
{
  "companyID": "Qu3P*********-c",
  "ragioneSociale": "SAIPEM S.P.A.",
  "vat": "IT00825790157",
  "iva": "00825790157",
  "name": "Saipem",
  "url": "https://www.saipem.com/"
},
{
  "companyID": "5g*********Z",
  "ragioneSociale": "VODAFONE ITALIA S.P.A.",
  "vat": "IT08539010010",
  "iva": "08539010010",
  "name": "Vodafone",
  "url": "https://www.vodafone.it/"
},
{
  "companyID": "Bv2*********f",
  "ragioneSociale": "VOLKSWAGEN GROUP ITALIA SOCIETA PER AZIONI (OPPURE - IN FORMA ABBREVIATA - VOLKSWAGEN GROUP ITALIA S.P.A.)",
  "vat": "IT01779120235",
  "iva": "01779120235",
  "name": "Volkswagen group italia",
  "url": "https://www.volkswagengroup.it/"
},
{
  "companyID": "JpF*********Y",
  "ragioneSociale": "MEDIAMARKET SPA",
  "vat": "IT02630120166",
  "iva": "02630120166",
  "name": "MediaMarkt",
  "url": ""
},
{
  "companyID": "VDn*********KL",
  "ragioneSociale": "TRENITALIA S.P.A.",
  "vat": "IT05403151003",
  "iva": "05403151003",
  "name": "Trenitalia",
  "url": "https://www.trenitalia.com/"
},
{
  "companyID": "lT*********yv",
  "ragioneSociale": "WEBUILD S.P.A.",
  "vat": "IT02895590962",
  "iva": "02895590962",
  "name": "Webuild",
  "url": "https://www.webuildgroup.com/"
},
{
  "companyID": "Nt*********B0",
  "ragioneSociale": "SAMSUNG ELECTRONICS ITALIA S.P.A.",
  "vat": "IT11325690151",
  "iva": "11325690151",
  "name": "Samsung",
  "url": "https://www.samsung.com/"
},
{
  "companyID": "p-*********",
  "ragioneSociale": "ANAS - SOCIETA' PER AZIONI",
  "vat": "IT02133681003",
  "iva": "02133681003",
  "name": "Anas",
  "url": "https://www.stradeanas.it/"
},
{
  "companyID": "W9*********F",
  "ragioneSociale": "TECNIMONT S.P.A.",
  "vat": "IT01628410159",
  "iva": "01628410159",
  "name": "Tecnimont",
  "url": "https://www.tecnimont.com/"
},
{
  "companyID": "lg*********_j",
  "ragioneSociale": "PHILIP MORRIS ITALIA S.R.L.",
  "vat": "IT06657521008",
  "iva": "06657521008",
  "name": "Pmi",
  "url": "https://www.pmi.com/"
},
{
  "companyID": "bu*********C",
  "ragioneSociale": "ACEA ENERGIA S.P.A.",
  "vat": "IT07305361003",
  "iva": "07305361003",
  "name": "Acea",
  "url": "https://www.acea.it/"
},
{
  "companyID": "9u*********WmFa7",
  "ragioneSociale": "LUIGI LAVAZZA - SOCIETA' PER AZIONI ABBREVIABILE ANCHE NELLA SIGLA: LAVAZZA S.P.A.",
  "vat": "IT00470550013",
  "iva": "00470550013",
  "name": "Lavazza",
  "url": "https://www.lavazzagroup.com/"
},
{
  "companyID": "sm*********c",
  "ragioneSociale": "LEONARDO -  SOCIETA' PER AZIONI",
  "vat": "IT00881841001",
  "iva": "00881841001",
  "name": "Leonardo",
  "url": "https://www.leonardo.com/"
},
{
  "companyID": "ci*********g_",
  "ragioneSociale": "CONAD NORD OVEST SOCIETA' COOPERATIVA",
  "vat": "IT01977130473",
  "iva": "01977130473",
  "name": "Conad Nord Ovest",
  "url": ""
},
{
  "companyID": "W7*********r",
  "ragioneSociale": "ENI S.P.A.",
  "vat": "IT00905811006",
  "iva": "00905811006",
  "name": "Eni",
  "url": "https://www.eni.com/"
},
{
  "companyID": "i1*********K",
  "ragioneSociale": "GRIMALDI EUROMED S.P.A.",
  "vat": "IT00278730825",
  "iva": "00278730825",
  "name": "Grimaldi Euromed",
  "url": ""
},
{
  "companyID": "CR*********ew",
  "ragioneSociale": "TERNA - RETE ELETTRICA NAZIONALE SOCIETA' PER AZIONI (IN FORMA ABBREVIATA TERNA S.P.A.)",
  "vat": "IT05779661007",
  "iva": "05779661007",
  "name": "Terna",
  "url": "https://www.terna.it/"
},
{
  "companyID": "SvT*********w",
  "ragioneSociale": "IREN ENERGIA S.P.A.",
  "vat": "IT09357630012",
  "iva": "09357630012",
  "name": "IREN",
  "url": ""
},
{
  "companyID": "F2*********E",
  "ragioneSociale": "NUOVO PIGNONE S.R.L.",
  "vat": "IT06176750484",
  "iva": "06176750484",
  "name": "Baker hughes",
  "url": "https://www.bakerhughes.com/"
},
{
  "companyID": "k3Z*********R7",
  "ragioneSociale": "SPESA INTELLIGENTE S.P.A.",
  "vat": "IT02416840235",
  "iva": "02416840235",
  "name": "Rospin",
  "url": "https://www.eu/rospin.it/"
},
{
  "companyID": "P*********1y",
  "ragioneSociale": "AXPO ITALIA S.P.A.",
  "vat": "IT01141160992",
  "iva": "01141160992",
  "name": "Axpo",
  "url": "https://www.axpo.com/"
},
{
  "companyID": "8t_*********HL",
  "ragioneSociale": "BMW ITALIA SPA",
  "vat": "IT12532500159",
  "iva": "12532500159",
  "name": "Bmw",
  "url": "https://www.bmw.it/it/home.html"
},
{
  "companyID": "N2*********Wq",
  "ragioneSociale": "CONAD - CONSORZIO NAZIONALE DETTAGLIANTI - SOCIETA' COOPERATIVA IN SIGLA CONAD",
  "vat": "IT03320960374",
  "iva": "03320960374",
  "name": "Conad",
  "url": ""
},
{
  "companyID": "ra*********1",
  "ragioneSociale": "E.ON ENERGIA S.P.A.",
  "vat": "IT03429130234",
  "iva": "03429130234",
  "name": "E.on",
  "url": "https://www.eon-energia.com/"
},
{
  "companyID": "nms*********X",
  "ragioneSociale": "ENEL GLOBAL TRADING S.P.A.",
  "vat": "IT05918271007",
  "iva": "05918271007",
  "name": "Enel",
  "url": ""
},
{
  "companyID": "hzA8*********A",
  "ragioneSociale": "DUFERCO ENERGIA S.P.A.",
  "vat": "IT01016870329",
  "iva": "01016870329",
  "name": "Duferco energia",
  "url": "https://dufercoenergia.com/"
},
{
  "companyID": "u*********8P",
  "ragioneSociale": "EDISON ENERGIA S.P.A.",
  "vat": "IT08526440154",
  "iva": "08526440154",
  "name": "Edison energia",
  "url": "https://www.edisonenergia.it/"
},
{
  "companyID": "0a*********FCf",
  "ragioneSociale": "LOGISTA ITALIA S.P.A.",
  "vat": "IT06741351008",
  "iva": "06741351008",
  "name": "Logista",
  "url": "https://www.logista.it/"
},
{
  "companyID": "YcW*********KqE",
  "ragioneSociale": "RENAULT ITALIA S.P.A.",
  "vat": "IT05811161008",
  "iva": "05811161008",
  "name": "Renault",
  "url": ""
},
{
  "companyID": "3VgP*********bYW",
  "ragioneSociale": "SORGENIA S.P.A.",
  "vat": "IT12874490159",
  "iva": "12874490159",
  "name": "Sorgenia",
  "url": "https://www.sorgenia.it/"
},
{
  "companyID": "KC*********b",
  "ragioneSociale": "TOYOTA MOTOR ITALIA S.P.A.",
  "vat": "IT03926291000",
  "iva": "03926291000",
  "name": "Toyota",
  "url": "https://www.toyota.it/"
},
{
  "companyID": "7bj*********E",
  "ragioneSociale": "EG ITALIA S.P.A.",
  "vat": "IT09964350962",
  "iva": "09964350962",
  "name": "Eg",
  "url": "https://www.eg.group/"
},
{
  "companyID": "OH*********97",
  "ragioneSociale": "ESSO ITALIANA S.R.L.",
  "vat": "IT00902231000",
  "iva": "00902231000",
  "name": "Esso",
  "url": "https://www.exxonmobil.it/"
},
{
  "companyID": "BV*********8NV",
  "ragioneSociale": "FORD ITALIA S.P.A.",
  "vat": "IT00894451004",
  "iva": "00894451004",
  "name": "Ford",
  "url": "https://www.ford.it/#"
},
{
  "companyID": "H*********DJ",
  "ragioneSociale": "GESTORE DEI MERCATI ENERGETICI S.P.A.",
  "vat": "IT06208031002",
  "iva": "06208031002",
  "name": "Gme",
  "url": "https://www.mercatoelettrico.org/"
},
{
  "companyID": "SRi*********fl",
  "ragioneSociale": "GROUPE PSA ITALIA S.P.A.",
  "vat": "IT00882090152",
  "iva": "00882090152",
  "name": "Groupe PSA Italia",
  "url": ""
},
{
  "companyID": "m*********H",
  "ragioneSociale": "REPOWER ITALIA S.P.A.",
  "vat": "IT00789540143",
  "iva": "00789540143",
  "name": "Repower",
  "url": "https://www.repower.com/"
},
{
  "companyID": "WT*********4",
  "ragioneSociale": "T.C.A. - TRATTAMENTI CENERI AUROARGENTIFERE - S.P.A.",
  "vat": "IT00279290514",
  "iva": "00279290514",
  "name": "Tcaspa",
  "url": "https://www.tcaspa.com/"
},
{
  "companyID": "iQW*********Mp",
  "ragioneSociale": "FIBERCOP S.P.A.",
  "vat": "IT11459900962",
  "iva": "11459900962",
  "name": "Fibercop",
  "url": "https://www.fibercop.it/"
},
{
  "companyID": "12h*********",
  "ragioneSociale": "ITALPREZIOSI S.P.A.",
  "vat": "IT01111420517",
  "iva": "01111420517",
  "name": "Italpreziosi",
  "url": "https://www.italpreziosi.it/"
},
{
  "companyID": "0_*********N",
  "ragioneSociale": "HERA TRADING S.R.L.",
  "vat": "IT02060500390",
  "iva": "02060500390",
  "name": "HERA TRADING",
  "url": ""
},
{
  "companyID": "a_*********t",
  "ragioneSociale": "SERVIZI ENERGIA ITALIA S.P.A.",
  "vat": "IT03843480272",
  "iva": "03843480272",
  "name": "Servizi Energia Italia",
  "url": ""
},
{
  "companyID": "t*********0",
  "ragioneSociale": "FERRARI-SOCIETA'PER AZIONI ESERCIZIO FABBRICHE AUTOMOBILI E CORSE O SEMPLICEMENTE: FERRARI S.P.A.",
  "vat": "IT00159560366",
  "iva": "00159560366",
  "name": "Ferrari",
  "url": "https://www.ferrari.com/"
},
{
  "companyID": "bP*********Rn",
  "ragioneSociale": "ACCIAI SPECIALI TERNI S.P.A.",
  "vat": "IT00715760559",
  "iva": "00715760559",
  "name": "Arvedi ast",
  "url": "https://www.acciaiterni.it/"
},
{
  "companyID": "u*********9bM",
  "ragioneSociale": "ENEL ENERGIA S.P.A.",
  "vat": "IT06655971007",
  "iva": "06655971007",
  "name": "Enel energia",
  "url": "https://www.enel.it"
},
{
  "companyID": "Hh*********n5",
  "ragioneSociale": "UNIEURO  S.P.A.",
  "vat": "IT00876320409",
  "iva": "00876320409",
  "name": "Unieuro",
  "url": "https://unieurospa.com/"
},
{
  "companyID": "cn*********DJ",
  "ragioneSociale": "MD S.P.A.",
  "vat": "IT03185210618",
  "iva": "03185210618",
  "name": "Md",
  "url": "https://www.mdspa.it/"
},
{
  "companyID": "rx*********_",
  "ragioneSociale": "SOCIETA' EUROPEA VEICOLI LEGGERI-SEVEL-SPA",
  "vat": "IT00297220691",
  "iva": "00297220691",
  "name": "SEVEL",
  "url": ""
},
{
  "companyID": "Uj*********o",
  "ragioneSociale": "SKY ITALIA - S.R.L.",
  "vat": "IT04619241005",
  "iva": "04619241005",
  "name": "Sky",
  "url": "https://www.sky.it/"
},
{
  "companyID": "J*********Q",
  "ragioneSociale": "TAMOIL ITALIA S.P.A.",
  "vat": "IT00698550159",
  "iva": "00698550159",
  "name": "Tamoil italia",
  "url": "https://www.tamoil.it/"
},
{
  "companyID": "H*********hv8",
  "ragioneSociale": "FASTWEB SPA",
  "vat": "IT12878470157",
  "iva": "12878470157",
  "name": "Fastweb",
  "url": "https://www.fastweb.it/"
},
{
  "companyID": "S*********KeM",
  "ragioneSociale": "AUTOMOBILI LAMBORGHINI S.P.A.",
  "vat": "IT00591801204",
  "iva": "00591801204",
  "name": "Lamborghini",
  "url": "https://www.lamborghini.com/"
},
{
  "companyID": "aM*********9",
  "ragioneSociale": "ACCIAIERIE D'ITALIA S.P.A.",
  "vat": "IT10354890963",
  "iva": "10354890963",
  "name": "Acciaierie d'italia",
  "url": "https://www.acciaierieditalia.com/"
},
{
  "companyID": "3P*********",
  "ragioneSociale": "ENI PLENITUDE S.P.A. SOCIETA' BENEFIT",
  "vat": "IT12300020158",
  "iva": "12300020158",
  "name": "Plenitude",
  "url": "https://corporate.eniplenitude.com/"
},
{
  "companyID": "_Jz*********u",
  "ragioneSociale": "COOP CONSORZIO NORD OVEST SOC. CONSORTILE A R.L.",
  "vat": "IT04117520967",
  "iva": "04117520967",
  "name": "Coop Nord Ovest",
  "url": ""
},
{
  "companyID": "9H*********Iw",
  "ragioneSociale": "GUCCIO GUCCI S.P.A.",
  "vat": "IT04294710480",
  "iva": "04294710480",
  "name": "Gucci",
  "url": "https://www.gucci.com/"
},
{
  "companyID": "Z*********d4",
  "ragioneSociale": "EDISON S.P.A.",
  "vat": "IT08263330014",
  "iva": "08263330014",
  "name": "Edison",
  "url": "https://www.edison.it/"
},
{
  "companyID": "0i*********cy",
  "ragioneSociale": "ISAB S.R.L.",
  "vat": "IT01629050897",
  "iva": "01629050897",
  "name": "Isab",
  "url": "https://www.isab.com/"
},
{
  "companyID": "f1G*********Uc",
  "ragioneSociale": "CENTRALE ADRIATICA SOCIETA' COOPERATIVA",
  "vat": "IT02795150362",
  "iva": "02795150362",
  "name": "Centrale Adriatica",
  "url": ""
},
{
  "companyID": "OJL*********CgD",
  "ragioneSociale": "ENILIVE S.P.A.",
  "vat": "IT11403240960",
  "iva": "11403240960",
  "name": "Enilive",
  "url": ""
},
{
  "companyID": "je*********",
  "ragioneSociale": "ACCENTURE S.P.A.",
  "vat": "IT13454210157",
  "iva": "13454210157",
  "name": "Accenture",
  "url": "https://www.accenture.com/"
},
{
  "companyID": "ytZ*********-",
  "ragioneSociale": "STELLANTIS EUROPE S.P.A.",
  "vat": "IT07973780013",
  "iva": "07973780013",
  "name": "Stellantis",
  "url": "https://www.stellantis.com/"
},
{
  "companyID": "Hl*********5D",
  "ragioneSociale": "ITX ITALIA S.R.L.",
  "vat": "IT11209550158",
  "iva": "11209550158",
  "name": "Inditex",
  "url": "https://www.inditex.com/itxcomweb/it/en/home"
},
{
  "companyID": "7t*********O",
  "ragioneSociale": "GS SPA",
  "vat": "IT12683790153",
  "iva": "12683790153",
  "name": "Carrefour",
  "url": "https://www.carrefour.it/"
},
{
  "companyID": "rn*********cNQ",
  "ragioneSociale": "RAI - RADIOTELEVISIONE ITALIANA S.P.A.",
  "vat": "IT06382641006",
  "iva": "06382641006",
  "name": "Rai",
  "url": "https://www.rai.it/"
},
{
  "companyID": "Nm*********sl",
  "ragioneSociale": "RANDSTAD ITALIA S.P.A.",
  "vat": "IT12730090151",
  "iva": "12730090151",
  "name": "Randstad",
  "url": "https://www.randstad.it/"
},
{
  "companyID": "ZY*********DN1t",
  "ragioneSociale": "AMAZON EU S.A R.L.",
  "vat": "IT08973230967",
  "iva": "08973230967",
  "name": "Amazon",
  "url": "https://sellercentral-europe.amazon.com/"
},
{
  "companyID": "xa6*********Z4",
  "ragioneSociale": "NIKE RETAIL B.V.",
  "vat": "IT02573160047",
  "iva": "02573160047",
  "name": "Nike",
  "url": "https://www.nike.com/"
},
{
  "companyID": "I*********LjSOp0",
  "ragioneSociale": "WIZZ AIR HUNGARY LTD ITALIAN BRANCH",
  "vat": "IT11291000963",
  "iva": "11291000963",
  "name": "Wizz air",
  "url": "https://www.wizzair.com/"
},
{
  "companyID": "_RI*********c",
  "ragioneSociale": "AMAZON WEB SERVICES EMEA SARL",
  "vat": "IT10119840964",
  "iva": "10119840964",
  "name": "Aws",
  "url": "https://aws.amazon.com/"
},
{
  "companyID": "2M3*********O2i",
  "ragioneSociale": "SONY EUROPE B.V.",
  "vat": "IT10496660969",
  "iva": "10496660969",
  "name": "Sony",
  "url": "https://www.sony-europe.com/"
},
{
  "companyID": "rw*********Jjb",
  "ragioneSociale": "BRIDGESTONE EUROPE NV/SA",
  "vat": "IT09712150961",
  "iva": "09712150961",
  "name": "Bridgestone",
  "url": "https://www.bridgestone-emea.com/"
},
{
  "companyID": "KlR*********fBTg",
  "ragioneSociale": "NINTENDO OF EUROPE SE",
  "vat": "IT03359860966",
  "iva": "03359860966",
  "name": "Nintendo",
  "url": "https://www.nintendo.com/"
},
{
  "companyID": "cM*********A74",
  "ragioneSociale": "CELANESE SALES GERMANY GMBH",
  "vat": "IT12156070968",
  "iva": "12156070968",
  "name": "Celanese",
  "url": ""
},
{
  "companyID": "eRs8*********cZ",
  "ragioneSociale": "A2A TRADING S.R.L.",
  "vat": "IT13390450156",
  "iva": "13390450156",
  "name": "A2A Trading",
  "url": ""
},
{
  "companyID": "2Y*********LnCbn",
  "ragioneSociale": "ACCIAIERIA ARVEDI S.P.A.",
  "vat": "IT11852670154",
  "iva": "11852670154",
  "name": "Arvedi",
  "url": ""
},
{
  "companyID": "Q*********VS1P9On",
  "ragioneSociale": "ADECCO ITALIA SPA",
  "vat": "IT13366030156",
  "iva": "13366030156",
  "name": "Adecco",
  "url": "https://www.adecco.it"
},
{
  "companyID": "Gpy*********P",
  "ragioneSociale": "BASELL SALES & MARKETING COMPANY B.V.",
  "vat": "IT10886640969",
  "iva": "10886640969",
  "name": "Basell",
  "url": "https://www.lyondellbasell.com/"
},
{
  "companyID": "KP*********Yg",
  "ragioneSociale": "BEKO EUROPE MANAGEMENT S.R.L.",
  "vat": "IT10895280963",
  "iva": "10895280963",
  "name": "Beko europe management",
  "url": "https://www.bekoeurope.com/"
},
{
  "companyID": "Em*********YO38S",
  "ragioneSociale": "CHIMET - S.P.A.-",
  "vat": "IT00155440514",
  "iva": "00155440514",
  "name": "Chimet",
  "url": "https://www.chimet.com/"
},
{
  "companyID": "dVm*********OB",
  "ragioneSociale": "COMIFAR DISTRIBUZIONE S.P.A.",
  "vat": "IT10406510155",
  "iva": "10406510155",
  "name": "COMIFAR",
  "url": ""
},
{
  "companyID": "73d*********0c",
  "ragioneSociale": "COMMERCIANTI INDIPENDENTI ASSOCIATI - SOCIETA' COOPERATIVA",
  "vat": "IT00138950407",
  "iva": "00138950407",
  "name": "CIA - Commercianti Indipendenti Associati",
  "url": ""
},
{
  "companyID": "zyuM*********H",
  "ragioneSociale": "E-DISTRIBUZIONE S.P.A.",
  "vat": "IT05779711000",
  "iva": "05779711000",
  "name": "E-distribuzione",
  "url": "https://www.e-distribuzione.it/"
},
{
  "companyID": "Kk*********ycDg",
  "ragioneSociale": "ENI TRADE & BIOFUELS S.P.A.",
  "vat": "IT10133500966",
  "iva": "10133500966",
  "name": "ENI",
  "url": ""
},
{
  "companyID": "DTc*********FMp5",
  "ragioneSociale": "ENI TRADING & SHIPPING S.P.A. - IN LIQUIDAZIONE",
  "vat": "IT09598861004",
  "iva": "09598861004",
  "name": "ENI Trading & Shipping",
  "url": ""
},
{
  "companyID": "IxK*********rzI",
  "ragioneSociale": "ENIMOOV S.P.A.",
  "vat": "IT02701740108",
  "iva": "02701740108",
  "name": "ENIMOOV",
  "url": ""
},
{
  "companyID": "U-U*********X-X",
  "ragioneSociale": "ESE S.R.L.",
  "vat": "IT17112421007",
  "iva": "17112421007",
  "name": "ESE",
  "url": ""
},
{
  "companyID": "mAo*********Nu6P",
  "ragioneSociale": "FPT INDUSTRIAL S.P.A. O, PER ESTESO, FIAT POWERTRAIN TECHNOLOGIES INDUSTRIAL S.P.A.",
  "vat": "IT09397710014",
  "iva": "09397710014",
  "name": "Fpt industrial",
  "url": "http://fptindustrial.com/"
},
{
  "companyID": "KB__*********hB1N",
  "ragioneSociale": "HERA COMM S.P.A.",
  "vat": "IT02221101203",
  "iva": "02221101203",
  "name": "Heracomm",
  "url": "https://heracomm.gruppohera.it/"
},
{
  "companyID": "ZC*********0SYl",
  "ragioneSociale": "IREN MERCATO S.P.A.",
  "vat": "IT01178580997",
  "iva": "01178580997",
  "name": "Iren",
  "url": ""
},
{
  "companyID": "ya*********yBwJ04",
  "ragioneSociale": "ISAB S.R.L.",
  "vat": "IT13118070153",
  "iva": "13118070153",
  "name": "ISAB",
  "url": ""
},
{
  "companyID": "Nkd*********CARIm",
  "ragioneSociale": "ITALIA TRASPORTO AEREO S.P.A.",
  "vat": "IT15907661001",
  "iva": "15907661001",
  "name": "Ita airways",
  "url": "https://www.ita-airways.com/"
},
{
  "companyID": "ED*********-V",
  "ragioneSociale": "ITALIANA PETROLI S.P.A.",
  "vat": "IT00051570893",
  "iva": "00051570893",
  "name": "Italiana petroli",
  "url": "https://ip.gruppoapi.com/"
},
{
  "companyID": "6g*********_UUB8",
  "ragioneSociale": "IVECO S.P.A.",
  "vat": "IT09709770011",
  "iva": "09709770011",
  "name": "Iveco group",
  "url": "https://www.ivecogroup.com/"
},
{
  "companyID": "NTU*********6m7",
  "ragioneSociale": "LUDOIL ENERGIA S.R.L.",
  "vat": "IT07047491217",
  "iva": "07047491217",
  "name": "Ludoil energia",
  "url": "https://stationfinder.eni.com/"
},
{
  "companyID": "Dt*********waau",
  "ragioneSociale": "MD S.P.A.",
  "vat": "IT12980970151",
  "iva": "12980970151",
  "name": "Md wellness",
  "url": "https://md-wellness.com/"
},
{
  "companyID": "SWb*********mnPR",
  "ragioneSociale": "MERCEDES-BENZ ITALIA S.P.A.",
  "vat": "IT06325761002",
  "iva": "06325761002",
  "name": "Mercedes-benz italia",
  "url": "https://group.mercedes-benz.com/"
},
{
  "companyID": "oO*********nUE",
  "ragioneSociale": "NUOVO PIGNONE INTERNATIONAL S.R.L.",
  "vat": "IT04880930484",
  "iva": "04880930484",
  "name": "Nuovo pignone",
  "url": "https://nuovoparts.com/"
},
{
  "companyID": "0LS*********Gd",
  "ragioneSociale": "PAC 2000 A SOCIETA' COOPERATIVA",
  "vat": "IT00163040546",
  "iva": "00163040546",
  "name": "PAC 2000A",
  "url": ""
},
{
  "companyID": "dsK*********BwI",
  "ragioneSociale": "PIRELLI TYRE SPA",
  "vat": "IT07211330159",
  "iva": "07211330159",
  "name": "Pirelli",
  "url": ""
},
{
  "companyID": "ob*********E3RYp",
  "ragioneSociale": "Q8 QUASER S.R.L.",
  "vat": "IT06543251000",
  "iva": "06543251000",
  "name": "Q8 Quaser",
  "url": ""
},
{
  "companyID": "R6i*********Axc",
  "ragioneSociale": "SARAS S.P.A. O IN FORMA ESTESA SARAS S.P.A. - RAFFINERIE SARDE",
  "vat": "IT00136440922",
  "iva": "00136440922",
  "name": "Saras",
  "url": "https://www.saras.it/"
},
{
  "companyID": "gvGZd*********p",
  "ragioneSociale": "SERVIZIO ELETTRICO NAZIONALE S.P.A.",
  "vat": "IT09633951000",
  "iva": "09633951000",
  "name": "Servizio elettrico nazionale",
  "url": "https://www.servizioelettriconazionale.it/"
},
{
  "companyID": "v0H-*********kT5",
  "ragioneSociale": "SKY ITALIA - S.R.L.",
  "vat": "IT01373511003",
  "iva": "01373511003",
  "name": "SKY",
  "url": ""
},
{
  "companyID": "9E4*********iz9V2",
  "ragioneSociale": "SNAM RETE GAS S.P.A. O, IN FORMA ABBREVIATA SNAM RG S.P.A.",
  "vat": "IT10238291008",
  "iva": "10238291008",
  "name": "SNAM",
  "url": ""
},
{
  "companyID": "dPh*********lhHAiG",
  "ragioneSociale": "STELLANTIS &YOU ITALIA S.P.A.",
  "vat": "IT07016530011",
  "iva": "07016530011",
  "name": "Stellantis &you italia",
  "url": "https://www.stellantisandyou.com/"
},
{
  "companyID": "Nsm*********0",
  "ragioneSociale": "UNICOMM - S.R.L.",
  "vat": "IT01274580248",
  "iva": "01274580248",
  "name": "UNICOMM",
  "url": ""
}]


Proxy
The format of the proxy is
user:password@ip:port
NEW = [
    "http://fejxdsct:e36rq2djfzwr@104.239.73.111:6654",
    "http://fejxdsct:e36rq2djfzwr@142.147.129.156:5765",
    "http://fejxdsct:e36rq2djfzwr@103.99.33.128:6123",
    "http://fejxdsct:e36rq2djfzwr@103.37.180.144:6538",
    "http://fejxdsct:e36rq2djfzwr@193.161.2.155:6578",
    "http://fejxdsct:e36rq2djfzwr@92.249.34.110:5792",
    "http://fejxdsct:e36rq2djfzwr@93.118.38.246:6390",
    "http://fejxdsct:e36rq2djfzwr@31.57.82.127:6708",
    "http://fejxdsct:e36rq2djfzwr@64.137.104.93:5703",
    "http://fejxdsct:e36rq2djfzwr@104.239.92.205:6845",
    "http://fejxdsct:e36rq2djfzwr@148.135.188.184:7216",
    "http://fejxdsct:e36rq2djfzwr@192.210.191.123:6109",
    "http://fejxdsct:e36rq2djfzwr@209.35.5.40:6731",
    "http://fejxdsct:e36rq2djfzwr@104.143.224.162:6023",
    "http://fejxdsct:e36rq2djfzwr@156.243.179.134:6622",
    "http://fejxdsct:e36rq2djfzwr@104.143.229.197:6125",
    "http://fejxdsct:e36rq2djfzwr@137.59.7.88:5632",
    "http://fejxdsct:e36rq2djfzwr@185.216.106.239:6316",
    "http://fejxdsct:e36rq2djfzwr@45.81.149.236:6668",
    "http://fejxdsct:e36rq2djfzwr@45.250.64.3:5640",
    "http://fejxdsct:e36rq2djfzwr@84.33.62.225:5761",
    "http://fejxdsct:e36rq2djfzwr@46.202.248.65:5559",
    "http://fejxdsct:e36rq2djfzwr@85.198.41.112:6038",
    "http://fejxdsct:e36rq2djfzwr@31.58.23.16:5589",
    "http://fejxdsct:e36rq2djfzwr@45.151.162.189:6591",
    "http://fejxdsct:e36rq2djfzwr@50.114.98.116:5600",
    "http://fejxdsct:e36rq2djfzwr@64.137.104.108:5718",
    "http://fejxdsct:e36rq2djfzwr@179.61.166.171:6594",
    "http://fejxdsct:e36rq2djfzwr@23.27.93.120:5699",
    "http://fejxdsct:e36rq2djfzwr@67.227.42.17:5994",
    "http://fejxdsct:e36rq2djfzwr@174.140.254.157:6748",
    "http://fejxdsct:e36rq2djfzwr@148.135.177.190:5724",
    "http://fejxdsct:e36rq2djfzwr@166.88.58.3:5728",
    "http://fejxdsct:e36rq2djfzwr@184.174.126.31:6323",
    "http://fejxdsct:e36rq2djfzwr@104.239.0.11:5712",
    "http://fejxdsct:e36rq2djfzwr@185.135.10.16:5530",
    "http://fejxdsct:e36rq2djfzwr@46.203.52.178:5701",
    "http://fejxdsct:e36rq2djfzwr@31.58.30.171:6753",
    "http://fejxdsct:e36rq2djfzwr@23.27.93.217:5796",
    "http://fejxdsct:e36rq2djfzwr@89.249.195.229:6984",
    "http://fejxdsct:e36rq2djfzwr@104.239.91.44:5768",
    "http://fejxdsct:e36rq2djfzwr@198.89.123.129:6671",
    "http://fejxdsct:e36rq2djfzwr@23.26.94.180:6162",
    "http://fejxdsct:e36rq2djfzwr@45.39.31.146:5573",
    "http://fejxdsct:e36rq2djfzwr@50.114.98.37:5521",
    "http://fejxdsct:e36rq2djfzwr@45.43.71.62:6660",
    "http://fejxdsct:e36rq2djfzwr@45.43.185.190:6196",
    "http://fejxdsct:e36rq2djfzwr@45.43.83.231:6514",
    "http://fejxdsct:e36rq2djfzwr@23.95.250.85:6358",
    "http://fejxdsct:e36rq2djfzwr@38.225.11.127:5408",
    "http://fejxdsct:e36rq2djfzwr@92.113.7.149:6875",
    "http://fejxdsct:e36rq2djfzwr@104.239.40.86:6705",
    "http://fejxdsct:e36rq2djfzwr@45.41.169.194:6855",
    "http://fejxdsct:e36rq2djfzwr@45.87.69.42:6047",
    "http://fejxdsct:e36rq2djfzwr@92.113.7.135:6861",
    "http://fejxdsct:e36rq2djfzwr@92.113.236.223:6808",
    "http://fejxdsct:e36rq2djfzwr@64.137.37.168:6758",
    "http://fejxdsct:e36rq2djfzwr@193.42.224.60:6261",
    "http://fejxdsct:e36rq2djfzwr@64.137.73.123:5211",
    "http://fejxdsct:e36rq2djfzwr@45.41.162.192:6829",
    "http://fejxdsct:e36rq2djfzwr@45.127.250.173:5782",
    "http://fejxdsct:e36rq2djfzwr@45.151.161.152:6243",
    "http://fejxdsct:e36rq2djfzwr@104.253.13.50:5482",
    "http://fejxdsct:e36rq2djfzwr@45.131.95.9:5673",
]