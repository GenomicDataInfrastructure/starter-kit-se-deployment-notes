"""Beacon Configuration."""

#
# Beacon general info
#
beacon_id = 'org.nbis.ga4gh-approval-beacon-test' # ID of the Beacon
beacon_name = 'European Genomic Data Infrastructure Swedish Test Beacon' # Name of the Beacon service
api_version = 'v2.0.0'  # Version of the Beacon implementation
uri = 'https://beacon.gdi.nbis.se/api/'

#
# Beacon granularity
#
default_beacon_granularity = "record"
max_beacon_granularity = "record"

#
#  Organization info
#
org_id = 'NBIS'  # Id of the organization
org_name = 'National Bioinformatics Infrastructure Sweden (NBIS)'  # Full name
org_description = ('NBIS is a distributed national bioinformatics infrastructure, '
                   'supporting life sciences in Sweden.')
org_adress = ('Uppsala Biomedicine Center (BMC) '
              'Husargatan 3, '
              '751 23 Uppsala, Sweden')
org_welcome_url = 'https://gdi.nbis.se/'
org_contact_url = 'mailto:info@gdi.nbis.se'
org_logo_url = 'https://gdi.onemilliongenomes.eu/images/gdi-logo.svg'
org_info = ''

#
# Project info
#
description = r"This Beacon is based on two synthetic datasets. The first is the dataset EGAD00001003338 at EGA archive and it contains 2504 samples including genetic data based on 1K Genomes data, and 76 individual attributes and phenotypic data derived from UKBiobank. The second one, is the Heilsa synthetic data, including 14 individuals."
version = 'v2.0'
welcome_url = 'https://beacon.gdi.nbis.se'
alternative_url = 'https://beacon.gdi.nbis.se/api'
create_datetime = '2023-06-01T12:00:00.000000'
update_datetime = ''
# update_datetime will be created when initializing the beacon, using the ISO 8601 format

#
# Service
#
service_type = 'org.ga4gh:beacon:1.0.0'  # service type
service_url = 'https://beacon.ega-archive.org/api/services'
entry_point = False
is_open = True
documentation_url = 'https://github.com/EGA-archive/beacon-2.x/'  # Documentation of the service
environment = 'test'  # Environment (production, development or testing/staging deployments)

# GA4GH
ga4gh_service_type_group = 'org.ga4gh'
ga4gh_service_type_artifact = 'beacon'
ga4gh_service_type_version = '1.0'

# Beacon handovers
beacon_handovers = [
    {
        'handoverType': {
            'id': 'CUSTOM:000001',
            'label': 'Project description'
        },
        'note': 'Project description',
        'url': 'https://www.nist.gov/programs-projects/genome-bottle'
    }
]

#
# Database connection
#
database_host = 'mongo'
database_port = 27017
database_user = 'root'
database_password = 'example'
database_name = 'beacon'
database_auth_source = 'admin'
# database_schema = 'public' # comma-separated list of schemas
# database_app_name = 'beacon-appname' # Useful to track connections

#
# Web server configuration
# Note: a Unix Socket path is used when behind a server, not host:port
#
beacon_host = '0.0.0.0'
beacon_port = 5050
beacon_tls_enabled = False
beacon_tls_client = True
beacon_cert = '/shared/etc/letsencrypt/live/htsget.gdi.nbis.se/fullchain.pem'
beacon_key = '/shared/etc/letsencrypt/live/htsget.gdi.nbis.se/privkey.pem'
CA_cert = '/etc/ega/CA.cert'

#
# Permissions server configuration
#
permissions_url = 'http://beacon-permissions'

#
# IdP endpoints (OpenID Connect/Oauth2)
#
# or use Elixir AAI (see https://elixir-europe.org/services/compute/aai)
#
idp_client_id = '"<LS_AAI_CLIENT_ID>"'
idp_client_secret = '<LS_AAI_CLIENT_SECRET>'  # same as in the test IdP
idp_scope = 'openid profile email ga4gh_passport_v1'

idp_authorize = 'https://login.elixir-czech.org/oidc/authorize'
idp_access_token = 'https://login.elixir-czech.org/oidc/token'
idp_introspection = 'https://login.elixir-czech.org/oidc/introspect'
idp_user_info = 'https://login.elixir-czech.org/oidc/userinfo'
idp_logout = 'https://login.elixir-czech.org/oidc/endsession'

idp_redirect_uri = 'https://beacon.gdi.nbis.se/login'

#
# UI
#
autocomplete_limit = 16
autocomplete_ellipsis = '...'

#
# Ontologies
#
ontologies_folder = "ontologies"
