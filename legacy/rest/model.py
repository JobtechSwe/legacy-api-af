from flask_restplus import fields
from legacy.rest import ns_legacy as api


class BaseUrl(fields.Raw):
    def format(self, value):
        return "https://www.arbetsformedlingen.se/Tjanster/lArbetssokande/Platsbanken/annonser/%s" % value


annons = api.model('matchnindsdata', {
    'annonsid': fields.String(attribute='_source.id'),
    'annonsrubrik': fields.String(attribute='_source.headline'),
    'yrkesbenamnning': fields.String(attribute='_source.occupation.label'),
    'yrkesbenamnningId': fields.Integer(
        attribute='_source.occupation.legacy_ams_taxonomy_id'),
    'arbetsplatsnamn': fields.String(attribute='_source.employer.workplace'),
    'kommunnamn': fields.String(attribute='_source.workplace_address.municipality'),
    'kommunkod': fields.Integer(attribute='_source.workplace_address.municipality_code'),
    'publiceraddatum': fields.Date(attribute='_source.publication_date'),
    'sista_ansokningsdag': fields.Date(attribute='_source.application_deadline'),
    'annonsurl': BaseUrl(attribute='_source.id'),
    'relevans': fields.Integer(default=100),
    'antalPlatser': fields.Integer(attribute='_source.number_of_vacancies'),
    'antalPlatserVisa': fields.Integer(attribute='_source.number_of_vacancies'),
    'varaktighetId': fields.Integer(attribute='_source.duration.legacy_ams_taxonomy_id'),
    'lanid': fields.Integer(attribute='_source.workplace_address.region_code'),
    'lan': fields.String(attribute='_source.workplace_address.region'),
    'anstallningstyp': fields.String(attribute='_source.employment_type.label'),
})

annonslista = api.model('resultat', {
    'antal_platsannonser': fields.Integer(attribute='total.value'),
    'antal_platsannonser_exakta': fields.Integer(attribute='total.value'),
    'antal_platsannonser_narliggande': fields.Integer(default=0),
    'antal_platserTotal': fields.Integer(attribute='meta.number_of_positions'),
    'antal_sidor': fields.Integer(attribute='meta.number_of_pages'),
    'matchningsdata': fields.List(fields.Nested(annons), attribute='hits')
})

annonsresultat = api.model('matchningslista', {
    'matchningslista': fields.Nested(annonslista, attribute='hits')
})
