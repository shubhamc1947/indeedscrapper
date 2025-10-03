# indeed_selectors_config.py

# CSS Selectors for Indeed Italy
INDEED_SELECTORS = {
    # Job Cards (Search Results)
    'job_cards': [
        'li.css-1ac2h1w > div[class*="cardOutline"]',
        'li.css-1ac2h1w',
        'div[data-jk]',
        '.jobsearch-SerpJobCard',
        '.job_seen_beacon'
    ],
    
    'job_title_link': [
        'a.jcs-JobTitle',
        'h2.jobTitle a',
        'a[data-testid="job-title"]'
    ],
    
    'job_title_text': [
        'span[id^="jobTitle-"]',
        'span[title]',
        'h2.jobTitle'
    ],
    
    # Job Details Panel
    'company_name': [
        '[data-testid="inlineHeader-companyName"]',
        'span.companyName',
        '.companyName'
    ],
    
    'company_link': [
        '[data-testid="inlineHeader-companyName"] a',
        'div[data-testid="inlineHeader-companyName"] a'
    ],
    
    'company_location': [
        '[data-testid="inlineHeader-companyLocation"]',
        'div[data-testid="jobsearch-JobInfoHeader-companyLocation"]',
        '.companyLocation'
    ],
    
    'company_rating': [
        'span.css-10jzft1',
        '.ratingNumber',
        '[data-testid*="rating"]'
    ],
    
    # Job Description
    'full_description': [
        'div#jobDescriptionText',
        'div.jobsearch-JobComponent-description',
        'div[data-testid="jobDescriptionText"]'
    ],
    
    # Job Details Section
    'job_details_section': '#jobDetailsSection',
    'job_details_groups': 'div[role="group"]',
    'job_details_items': 'li[data-testid="list-item"]',
    
    # Benefits Section
    'benefits_section': '#benefits',
    'benefits_list': '#benefits ul li',
    
    # Salary
    'salary_snippet': [
        '.salary-snippet',
        '[data-testid="salary-snippet"]'
    ],
}

# Skills Keywords (Technical + Non-Technical + Italian)
SKILL_KEYWORDS = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'golang',
    'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
    'objective-c', 'dart', 'elixir', 'haskell', 'clojure', 'lua', 'groovy',
    'visual basic', 'vb.net', 'fortran', 'cobol', 'assembly', 'bash', 'shell',
    'programmazione',  # IT: programming
    
    # Web Frontend
    'html', 'css', 'sass', 'scss', 'less', 'react', 'react.js', 'vue', 'vue.js',
    'angular', 'angularjs', 'svelte', 'next.js', 'nuxt.js', 'jquery', 'bootstrap',
    'tailwind', 'material-ui', 'webpack', 'vite', 'redux', 'mobx', 'vuex',
    'sviluppo web', 'sviluppo frontend',  # IT: web development, frontend development
    
    # Backend & Frameworks
    'node.js', 'express', 'fastapi', 'django', 'flask', 'spring', 'spring boot',
    'laravel', 'symfony', 'rails', 'ruby on rails', 'asp.net', '.net', '.net core',
    'nestjs', 'fastify', 'koa', 'gin', 'echo', 'fiber', 'actix',
    'sviluppo backend',  # IT: backend development
    
    # Databases
    'sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'sql server', 'mssql',
    'mongodb', 'cassandra', 'redis', 'elasticsearch', 'dynamodb', 'couchdb',
    'neo4j', 'firebase', 'supabase', 'mariadb', 'sqlite', 'memcached',
    'database', 'basi di dati', 'gestione database',  # IT: databases
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'vercel',
    'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab ci', 'github actions',
    'terraform', 'ansible', 'puppet', 'chef', 'circleci', 'travis ci',
    'ci/cd', 'helm', 'istio', 'prometheus', 'grafana', 'datadog', 'nginx',
    'apache', 'cloudflare', 'cloudformation',
    'cloud computing', 'devops', 'automazione',  # IT: automation
    
    # Data Science & ML
    'machine learning', 'deep learning', 'ai', 'artificial intelligence',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'opencv', 'nlp', 'computer vision', 'spacy', 'hugging face', 'transformers',
    'bert', 'gpt', 'llm', 'spark', 'hadoop', 'airflow', 'kafka', 'flink',
    'tableau', 'power bi', 'looker', 'jupyter', 'dask', 'mlflow',
    'intelligenza artificiale', 'apprendimento automatico', 'analisi dati',
    'data science', 'scienza dei dati', 'big data',
    
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
    'swift', 'swiftui', 'kotlin', 'jetpack compose',
    'sviluppo mobile', 'app mobile',
    
    # Testing & Quality
    'jest', 'mocha', 'pytest', 'junit', 'selenium', 'cypress', 'playwright',
    'testng', 'cucumber', 'postman', 'jmeter', 'k6', 'testing',
    'test', 'collaudo', 'qualità', 'qa', 'quality assurance',
    
    # Version Control & Collaboration
    'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'jira',
    'confluence', 'slack', 'trello', 'asana',
    'controllo versione', 'versionamento',
    
    # Architecture & Design
    'microservices', 'rest api', 'restful', 'graphql', 'grpc', 'soap',
    'websocket', 'event-driven', 'serverless', 'lambda', 'api gateway',
    'message queue', 'rabbitmq', 'activemq', 'sqs', 'pub/sub',
    'architettura software', 'microservizi', 'api rest',
    
    # Operating Systems & Tools
    'linux', 'unix', 'ubuntu', 'centos', 'debian', 'windows server',
    'macos', 'vim', 'emacs', 'vscode', 'intellij', 'pycharm',
    'sistemi operativi',
    
    # Security
    'oauth', 'jwt', 'ssl', 'tls', 'encryption', 'penetration testing',
    'security', 'cybersecurity', 'owasp', 'sso', 'ldap', 'active directory',
    'sicurezza', 'sicurezza informatica', 'crittografia',
    
    # Business & Soft Skills (Technical)
    'agile', 'scrum', 'kanban', 'devops', 'project management',
    'gestione progetti', 'metodologie agile',
    
    # ERP & Business Software
    'sap', 'salesforce', 'oracle erp', 'microsoft dynamics', 'odoo',
    'netsuite', 'workday', 'servicenow', 'sharepoint', 'excel', 'word',
    'powerpoint', 'outlook', 'microsoft office', 'google workspace',
    'erp', 'gestionale', 'software gestionale',
    
    # Design & Creative
    'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'invision',
    'ux', 'ui', 'ux/ui', 'user experience', 'user interface', 'wireframing',
    'design', 'progettazione', 'grafica', 'design grafico',
    
    # E-commerce & CMS
    'shopify', 'magento', 'woocommerce', 'wordpress', 'drupal', 'joomla',
    'contentful', 'strapi', 'sanity',
    'e-commerce', 'commercio elettronico', 'cms',
    
    # Blockchain & Web3
    'blockchain', 'ethereum', 'solidity', 'web3', 'smart contracts', 'nft',
    'defi', 'cryptocurrency', 'bitcoin', 'criptovaluta',
    
    # Game Development
    'unity', 'unreal engine', 'godot', 'game development', 'opengl', 'directx',
    'sviluppo giochi', 'videogiochi',
    
    # Other Technologies
    'mqtt', 'iot', 'embedded systems', 'plc', 'scada', 'real-time',
    'multithreading', 'concurrent', 'distributed systems', 'edge computing',
    'sistemi embedded', 'tempo reale',
    
    # Non-Technical / Soft Skills (English + Italian)
    'leadership', 'guida', 'direzione',
    'communication', 'comunicazione',
    'teamwork', 'team work', 'lavoro di squadra', 'collaborazione',
    'problem solving', 'risoluzione problemi',
    'critical thinking', 'pensiero critico', 'analitico', 'analisi',
    'creativity', 'creatività', 'innovazione',
    'time management', 'gestione del tempo', 'organizzazione',
    'attention to detail', 'attenzione ai dettagli', 'precisione',
    'multitasking', 'gestione priorità',
    'negotiation', 'negoziazione', 'trattativa',
    'presentation', 'presentazione', 'public speaking',
    'customer service', 'servizio clienti', 'assistenza clienti',
    'sales', 'vendite', 'commerciale',
    'marketing', 'digital marketing',
    'strategic thinking', 'pensiero strategico', 'strategia',
    'decision making', 'gestione conflitti', 'mediazione',
    'emotional intelligence', 'intelligenza emotiva', 'empatia',
    'adaptability', 'flexibility', 'adattabilità', 'flessibilità',
    'self-motivation', 'initiative', 'autonomia', 'iniziativa', 'proattività',
    'mentoring', 'coaching', 'formazione', 'training',
    'delegation', 'delega', 'coordinamento',
    'stakeholder management', 'gestione stakeholder',
    'client relations', 'relazioni clienti', 'networking',
    'business development', 'sviluppo business',
    'budget management', 'gestione budget', 'controllo costi',
    'risk management', 'gestione rischio',
    'change management', 'gestione del cambiamento',
    'process improvement', 'miglioramento processi', 'ottimizzazione',
    'research', 'ricerca', 'ricerca e sviluppo', 'r&d',
    'documentation', 'documentazione', 'reporting', 'reportistica',
    'planning', 'pianificazione', 'programmazione',
    'scheduling', 'prioritization',
    'quality assurance', 'compliance', 'conformità', 'normativa',
    'legal', 'contract negotiation', 'contrattualistica',
    'vendor management', 'supply chain', 'logistica',
    'operations', 'operazioni', 'gestione operativa',
    'human resources', 'hr', 'risorse umane', 'gestione personale',
    'recruitment', 'selezione', 'recruiting', 'ricerca personale',
    'talent acquisition', 'onboarding', 'inserimento',
    'performance management', 'valutazione performance',
    'employee relations', 'compensation', 'benefits',
    'accounting', 'contabilità', 'ragioneria',
    'finance', 'finanza', 'analisi finanziaria',
    'bookkeeping', 'financial analysis', 'auditing', 'audit',
    'taxation', 'tassazione', 'fiscale', 'tributario',
    'payroll', 'paghe', 'buste paga',
    'invoicing', 'fatturazione',
    'budgeting', 'forecasting', 'previsione',
    
    # Languages
    'bilingual', 'multilingual', 'bilingue', 'multilingue',
    'english', 'inglese', 'italian', 'italiano',
    'spanish', 'spagnolo', 'french', 'francese',
    'german', 'tedesco', 'mandarin', 'cinese',
    'translation', 'traduzione', 'interpretation', 'interpretariato',
    'lingue straniere',
]