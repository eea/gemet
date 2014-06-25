from main import ApiTester


HOST = ApiTester().get_full_path()

ALL_TTRANSLATIONS_FOR_CONCEPT = [
    ('ar',
     u'\u0627\u0644\u0633\u0641\u0631 \u0641\u064a \u0627\u0644\u0641\u0636\u0627\u0621'),
    ('bg',
     u'\u041f\u044a\u0442\u0443\u0432\u0430\u043d\u0435 \u0432 \u043a\u043e\u0441\u043c\u043e\u0441\u0430'),
    ('ca', u'viatge espacial'),
    ('cs', u'let kosmick\xfd'),
    ('da', u'rumfart'),
    ('de', u'Raumfahrt'),
    ('el',
     u'\u03b4\u03b9\u03b1\u03c3\u03c4\u03b7\u03bc\u03b9\u03ba\u03cc \u03c4\u03b1\u03be\u03af\u03b4\u03b9'),
    ('en', u'space travel'),
    ('en-US', u'space travel'),
    ('es', u'viaje espacial'),
    ('et', u'kosmoselend'),
    ('eu', u'espazio-bidaia'),
    ('fi', u'avaruusmatka'),
    ('fr', u'astronautique (vols spatiaux)'),
    ('ga', u'sp\xe1staisteal'),
    ('hr', u'svemirsko putovanje'),
    ('hu', u'\u0171rutaz\xe1s'),
    ('it', u'viaggio spaziale'),
    ('lt', u'kosminiai skryd\u017eiai'),
    ('lv', u'kosmosa lidojums'),
    ('mt', u'vja\u0121\u0121ar fl-ispazju'),
    ('nl', u'ruimtevaart'),
    ('no', u'romferd'),
    ('pl', u'podr\xf3\u017c kosmiczna'),
    ('pt', u'viagens espaciais'),
    ('ro', u'c\u0103l\u0103torie \xeen spa\u0163iu'),
    ('ru',
     u'\u043a\u043e\u0441\u043c\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043f\u043e\u043b\u0435\u0442'),
    ('sk', u'kozmick\xfd let'),
    ('sl', u'vesoljski polet'),
    ('sv', u'rymdf\xe4rder'),
    ('tr', u'uzay yolculu\u011fu'),
    ('uk',
     u'\u043a\u043e\u0441\u043c\u0456\u0447\u043d\u0438\u0439 \u043f\u043e\u043b\u0456\u0442'),
    ('zh-CN', u'\u592a\u7a7a\u65c5\u884c')
]

TOPMOST_TERMS = [
    'accident', 'administration', 'agriculture', 'analysis',
    'animal husbandry', 'atmosphere', 'biochemical process', 'biosphere',
    'border', 'built environment', 'business', 'chemical',
    'chemical element', 'chemical process', 'chemical property',
    'climate', 'craft', 'culture (society)', 'demography', 'disaster',
    'disease', 'economy', 'education', 'effect', 'energy', 'environment',
    'environmental assessment', 'environmental awareness',
    'environmental control', 'environmental data',
    'environmental economy issue', 'environmental impact',
    'environmental management', 'environmental planning',
    'environmental policy', 'environmental problem solving',
    'environmental protection', 'equipment', 'evaluation', 'experiment',
    'finances', 'firm', 'fishery', 'forestry', 'geological process',
    'hazard', 'health', 'health-environment relationship', 'hydrosphere',
    'impact source', 'industrial process', 'industry', 'information',
    'institutional structure', 'international relations', 'justice',
    'labour', 'land', 'land setup', 'law (corpus of rules)',
    'law (individual)', 'legal form of organisations', 'legislation',
    'lithosphere', 'management', 'material', 'medicine (practice)',
    'methodology', 'military activities', 'military aspects', 'monitoring',
    'nutrition', 'organisation of the legal system', 'overburden',
    'parameter', 'pedosphere', 'physical process', 'physical property',
    'physicochemical process', 'planning', 'policy', 'politics',
    'pollutant', 'pollution', 'product', 'radiation', 'recreation',
    'research', 'resource', 'resource utilisation', 'risk', 'safety',
    'science', 'services', 'society', 'space (interplanetary)',
    'state of matter', 'statistics', 'subject', 'technical regulation',
    'technology', 'tourism', 'trade (services)', 'trade activity',
    'traffic', 'transportation', 'transportation mean', 'vibration', 'waste'
]

TOPMOST_GROUPS = [
    'ADMINISTRATION, MANAGEMENT, POLICY, POLITICS, INSTITUTIONS, PLANNING',
    'AGRICULTURE, FORESTRY; ANIMAL HUSBANDRY; FISHERY',
    'ANTHROPOSPHERE (built environment, human settlements, land setup)',
    'ATMOSPHERE (air, climate)', 'BIOSPHERE (organisms, ecosystems)',
    'CHEMISTRY, SUBSTANCES, PROCESSES', 'ECONOMICS, FINANCE',
    'EFFECTS, IMPACTS', 'ENERGY',
    'ENVIRONMENT (natural environment, anthropic environment)',
    'ENVIRONMENTAL POLICY', 'FUNCTIONAL TERMS', 'GENERAL TERMS',
    'HEALTH, NUTRITION', 'HYDROSPHERE (freshwater, marine water, waters)',
    'INDUSTRY, CRAFTS; TECHNOLOGY; EQUIPMENTS',
    'INFORMATION, EDUCATION, CULTURE, ENVIRONMENTAL AWARENESS',
    'LAND (landscape, geography)', 'LEGISLATION, NORMS, CONVENTIONS',
    'LITHOSPHERE (soil, geological processes)',
    'PHYSICAL ASPECTS, NOISE, VIBRATIONS, RADIATIONS', 'PRODUCTS, MATERIALS',
    'RECREATION, TOURISM', 'RESEARCH, SCIENCES',
    'RESOURCES (utilisation of resources)', 'RISKS, SAFETY', 'SOCIETY',
    'SPACE', 'TIME (chronology)', 'TRADE, SERVICES',
    'TRAFFIC, TRANSPORTATION', 'WASTES, POLLUTANTS, POLLUTION'
]

TOPMOST_THEMES = [
    'administration', 'agriculture', 'air', 'animal husbandry', 'biology',
    'building', 'chemistry', 'climate', 'disasters, accidents, risk',
    'economics', 'energy', 'environmental policy', 'fishery',
    'food, drinking water', 'forestry', 'general', 'geography',
    'human health', 'industry', 'information', 'legislation', 'materials',
    'military aspects', 'natural areas, landscape, ecosystems',
    'natural dynamics', 'noise, vibrations', 'physics', 'pollution',
    'radiations', 'research', 'resources', 'social aspects, population',
    'soil', 'space', 'tourism', 'trade, services', 'transport',
    'urban environment, urban stress', 'waste', 'water'
]

TOPMOST_INSPIRE = [
    'Addresses', 'Administrative units',
    'Agricultural and aquaculture facilities',
    'Area management/restriction/regulation zones and reporting units',
    'Atmospheric conditions', 'Bio-geographical regions', 'Buildings',
    'Cadastral parcels', 'Coordinate reference systems', 'Elevation',
    'Energy resources', 'Environmental monitoring facilities',
    'Geographical grid systems', 'Geographical names', 'Geology',
    'Habitats and biotopes', 'Human health and safety', 'Hydrography',
    'Land cover', 'Land use', 'Meteorological geographical features',
    'Mineral resources', 'Natural risk zones',
    'Oceanographic geographical features', 'Orthoimagery',
    u'Population distribution \u2014 demography',
    'Production and industrial facilities', 'Protected sites', 'Sea regions',
    'Soil', 'Species distribution', 'Statistical units', 'Transport networks',
    'Utility and governmental services'
]

TEST_PREFFIX = {
    'waste air', 'emission to air', 'respiratory air', 'soil air', 'air'
}

TEST_SUFFIX = {
    'air traffic law', 'aircraft engine emission', 'air quality monitoring',
    'air safety', 'air traffic regulation', 'airborne noise',
    'air quality management', 'air quality', 'air pollutant',
    'air conditioning', 'air transportation', 'air movement',
    'aircraft noise', 'air quality control', 'aircraft',
    'air traffic', 'air quality impact', 'air pollution',
    'air-water interaction', 'air temperature', 'air', 'airport',
    'airspace planning'
}

TEST_SUFFIX_PREFFIX = {
    'air traffic law', 'military air traffic', 'respiratory air',
    'aircraft engine emission', 'air quality monitoring',
    'ocean-air interface', 'air safety', 'waste air',
    'waste air purification (gas)', 'air traffic regulation', 'airborne noise',
    'air quality management', 'air quality', 'dairy product', 'air pollutant',
    'air conditioning', 'air transportation', 'air movement', 'aircraft noise',
    'gaseous air pollutant', 'indoor air pollution', 'air quality control',
    'hearing impairment', 'aircraft', 'civil air traffic', 'dairy farm',
    'emission to air', 'air traffic', 'air quality impact', 'soil air',
    'air pollution', 'clean air area', 'air-water interaction',
    'repair business', 'air temperature', 'air', 'clean air car', 'airport',
    'airspace planning', 'dairy industry',
}

TEST_EXACT_TERM = {'travel'}

TEST_PREFFIX_TERMS = {'travel cost', 'travel'}

TEST_SUFFIX_TERMS = {'travel', 'gravel', 'space travel'}

TEST_NO_MATCH = set([])

TEST_NO_MATCH_REGEX = set([])

TEST_NO_WILDCARD = set(['air'])

TEST_QUOTE = {
    "earth's crust", "woman's status", "Chagas' disease",
    "public prosecutor's office",
}

TEST_AVAILABLE_LANGUAGES = sorted([
    'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en', 'en-US', 'es', 'et', 'eu',
    'fi', 'fr', 'ga', 'hr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl', 'no', 'pl',
    'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'tr', 'uk', 'zh-CN'
])

TEST_SUPPORTED_LANGUAGES = [
    'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en', 'en-US', 'es', 'et', 'eu',
    'fi', 'fr', 'ga', 'hr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl', 'no', 'pl',
    'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'tr', 'uk', 'zh-CN'
]

TEST_EXTRA_LANGUAGES = ['zh']

THESAURI = [
    {
        'name': 'Concepts',
        'uri': HOST + 'concept/',
        'version': 'GEMET - Concepts, version 3.1, 2012-07-20'
    },
    {
        'name': 'Super groups',
        'uri': HOST + 'supergroup/',
        'version': 'GEMET - Super groups, version 2.4, 2010-01-13'
    },
    {
        'name': 'Groups',
        'uri': HOST + 'group/',
        'version': 'GEMET - Groups, version 2.4, 2010-01-13'
    },
    {
        'name': 'Themes',
        'uri': HOST + 'theme/',
        'version': 'GEMET - Themes, version 2.4, 2010-01-13'
    },
    {
        'name': 'Inspire Themes',
        'uri': 'http://inspire.ec.europa.eu/theme/',
        'version': 'GEMET - INSPIRE themes, version 1.0, 2008-06-01'
    }
]

THEMES_PREF_LABEL = [
    {'string': 'administration', 'language': 'en'},
    {'string': 'agriculture', 'language': 'en'},
    {'string': 'air', 'language': 'en'},
    {'string': 'animal husbandry', 'language': 'en'},
    {'string': 'biology', 'language': 'en'},
    {'string': 'building', 'language': 'en'},
    {'string': 'chemistry', 'language': 'en'},
    {'string': 'climate', 'language': 'en'},
    {'string': 'disasters, accidents, risk', 'language': 'en'},
    {'string': 'economics', 'language': 'en'},
    {'string': 'energy', 'language': 'en'},
    {'string': 'environmental policy', 'language': 'en'},
    {'string': 'fishery', 'language': 'en'},
    {'string': 'food, drinking water', 'language': 'en'},
    {'string': 'forestry', 'language': 'en'},
    {'string': 'general', 'language': 'en'},
    {'string': 'geography', 'language': 'en'},
    {'string': 'human health', 'language': 'en'},
    {'string': 'industry', 'language': 'en'},
    {'string': 'information', 'language': 'en'},
    {'string': 'legislation', 'language': 'en'},
    {'string': 'materials', 'language': 'en'},
    {'string': 'military aspects', 'language': 'en'},
    {'string': 'natural areas, landscape, ecosystems', 'language': 'en'},
    {'string': 'natural dynamics', 'language': 'en'},
    {'string': 'noise, vibrations', 'language': 'en'},
    {'string': 'physics', 'language': 'en'},
    {'string': 'pollution', 'language': 'en'},
    {'string': 'radiations', 'language': 'en'},
    {'string': 'research', 'language': 'en'},
    {'string': 'resources', 'language': 'en'},
    {'string': 'social aspects, population', 'language': 'en'},
    {'string': 'soil', 'language': 'en'},
    {'string': 'space', 'language': 'en'},
    {'string': 'tourism', 'language': 'en'},
    {'string': 'trade, services', 'language': 'en'},
    {'string': 'transport', 'language': 'en'},
    {'string': 'urban environment, urban stress', 'language': 'en'},
    {'string': 'waste', 'language': 'en'},
    {'string': 'water', 'language': 'en'}
]

THEMES_URI = [
    HOST + 'theme/1',
    HOST + 'theme/2',
    HOST + 'theme/3',
    HOST + 'theme/18',
    HOST + 'theme/4',
    HOST + 'theme/5',
    HOST + 'theme/6',
    HOST + 'theme/7',
    HOST + 'theme/32',
    HOST + 'theme/9',
    HOST + 'theme/10',
    HOST + 'theme/11',
    HOST + 'theme/12',
    HOST + 'theme/13',
    HOST + 'theme/14',
    HOST + 'theme/15',
    HOST + 'theme/16',
    HOST + 'theme/17',
    HOST + 'theme/19',
    HOST + 'theme/20',
    HOST + 'theme/21',
    HOST + 'theme/27',
    HOST + 'theme/22',
    HOST + 'theme/23',
    HOST + 'theme/8',
    HOST + 'theme/24',
    HOST + 'theme/25',
    HOST + 'theme/26',
    HOST + 'theme/28',
    HOST + 'theme/30',
    HOST + 'theme/31',
    HOST + 'theme/34',
    HOST + 'theme/35',
    HOST + 'theme/36',
    HOST + 'theme/29',
    HOST + 'theme/33',
    HOST + 'theme/37',
    HOST + 'theme/38',
    HOST + 'theme/39',
    HOST + 'theme/40'
]

THEMES_THESAURUS = 40 * [HOST + 'theme/']

GROUPS_PREF_LABEL = [
    {'string':
        'ADMINISTRATION, MANAGEMENT, POLICY, POLITICS, INSTITUTIONS, PLANNING',
        'language': 'en'},
    {'string': 'AGRICULTURE, FORESTRY; ANIMAL HUSBANDRY; FISHERY',
        'language': 'en'},
    {'string':
         'ANTHROPOSPHERE (built environment, human settlements, land setup)',
         'language': 'en'},
    {'string': 'ATMOSPHERE (air, climate)', 'language': 'en'},
    {'string': 'BIOSPHERE (organisms, ecosystems)',
     'language': 'en'},
    {'string': 'CHEMISTRY, SUBSTANCES, PROCESSES',
     'language': 'en'},
    {'string': 'ECONOMICS, FINANCE', 'language': 'en'},
    {'string': 'EFFECTS, IMPACTS', 'language': 'en'},
    {'string': 'ENERGY', 'language': 'en'},
    {
        'string': 'ENVIRONMENT (natural environment, anthropic environment)',
        'language': 'en'},
    {'string': 'ENVIRONMENTAL POLICY', 'language': 'en'},
    {'string': 'FUNCTIONAL TERMS', 'language': 'en'},
    {'string': 'GENERAL TERMS', 'language': 'en'},
    {'string': 'HEALTH, NUTRITION', 'language': 'en'},
    {'string': 'HYDROSPHERE (freshwater, marine water, waters)',
        'language': 'en'},
    {'string': 'INDUSTRY, CRAFTS; TECHNOLOGY; EQUIPMENTS',
     'language': 'en'},
    {'string': 'INFORMATION, EDUCATION, CULTURE, ENVIRONMENTAL AWARENESS',
        'language': 'en'},
    {'string': 'LAND (landscape, geography)',
     'language': 'en'},
    {'string': 'LEGISLATION, NORMS, CONVENTIONS',
     'language': 'en'},
    {'string': 'LITHOSPHERE (soil, geological processes)',
     'language': 'en'},
    {'string': 'PHYSICAL ASPECTS, NOISE, VIBRATIONS, RADIATIONS',
        'language': 'en'},
    {'string': 'PRODUCTS, MATERIALS', 'language': 'en'},
    {'string': 'RECREATION, TOURISM', 'language': 'en'},
    {'string': 'RESEARCH, SCIENCES', 'language': 'en'},
    {'string': 'RESOURCES (utilisation of resources)',
     'language': 'en'},
    {'string': 'RISKS, SAFETY', 'language': 'en'},
    {'string': 'SOCIETY', 'language': 'en'},
    {'string': 'SPACE', 'language': 'en'},
    {'string': 'TIME (chronology)', 'language': 'en'},
    {'string': 'TRADE, SERVICES', 'language': 'en'},
    {'string': 'TRAFFIC, TRANSPORTATION', 'language': 'en'},
    {'string': 'WASTES, POLLUTANTS, POLLUTION',
     'language': 'en'}
]

GROUPS_URI = [
    HOST + 'group/96',
    HOST + 'group/234',
    HOST + 'group/1062',
    HOST + 'group/618',
    HOST + 'group/893',
    HOST + 'group/1349',
    HOST + 'group/2504',
    HOST + 'group/10114',
    HOST + 'group/2711',
    HOST + 'group/10111',
    HOST + 'group/13109',
    HOST + 'group/14980',
    HOST + 'group/10117',
    HOST + 'group/3875',
    HOST + 'group/4125',
    HOST + 'group/4281',
    HOST + 'group/1922',
    HOST + 'group/4630',
    HOST + 'group/4750',
    HOST + 'group/4856',
    HOST + 'group/6237',
    HOST + 'group/10112',
    HOST + 'group/7007',
    HOST + 'group/7136',
    HOST + 'group/10118',
    HOST + 'group/7243',
    HOST + 'group/7779',
    HOST + 'group/7956',
    HOST + 'group/14979',
    HOST + 'group/8575',
    HOST + 'group/8603',
    HOST + 'group/9117'
]

GROUPS_THESAURUS = 32 * [HOST + 'group/']

SUPERGROUP_RELATIVES = [
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/10112',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/10114',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/10118',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/1349',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/234',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/2711',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/4281',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/6237',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/7007',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/8575',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/8603',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'group/9117'
]

CONCEPT_RELATIVES = [
    HOST + '2004/06/gemet-schema.rdf#group ' + HOST + 'group/96',
    HOST + '2004/06/gemet-schema.rdf#theme ' + HOST + 'theme/1',
    'http://www.w3.org/2004/02/skos/core#broader ' + HOST + 'concept/13292',
    'http://www.w3.org/2004/02/skos/core#narrower ' + HOST + 'concept/661'
]
