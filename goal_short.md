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
}]

Proxy
The format of the proxy is
user:password@ip:port
NEW = [
    "http://fejxdsct:e36rq2djfzwr@64.137.73.123:5211",
    "http://fejxdsct:e36rq2djfzwr@45.41.162.192:6829",
    "http://fejxdsct:e36rq2djfzwr@45.127.250.173:5782",
    "http://fejxdsct:e36rq2djfzwr@45.151.161.152:6243",
    "http://fejxdsct:e36rq2djfzwr@104.253.13.50:5482",
    "http://fejxdsct:e36rq2djfzwr@45.131.95.9:5673",
]