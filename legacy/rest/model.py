from flask_restplus import fields
from legacy.rest import ns_legacy as api

base_url = "https://www.arbetsformedlingen.se/For-arbetssokande/Platsbanken/annonser"


class BaseUrl(fields.Raw):
    def format(self, value):
        return "%s/%s" % (base_url, value)


# Search results
matchningsdata = api.model('Matchningsdata', {
    'annonsid': fields.String(attribute='_source.id'),
    'annonsrubrik': fields.String(attribute='_source.headline'),
    'yrkesbenamning': fields.String(attribute='_source.occupation.label'),
    'yrkesbenamningId': fields.Integer(
        attribute='_source.occupation.legacy_ams_taxonomy_id'),
    'arbetsplatsnamn': fields.String(attribute='_source.employer.workplace'),
    'kommunnamn': fields.String(attribute='_source.workplace_address.municipality'),
    'kommunkod': fields.Integer(attribute='_source.workplace_address.municipality_code'),
    'publiceraddatum': fields.Date(attribute='_source.publication_date'),
    'sista_ansokningsdag': fields.Date(attribute='_source.application_deadline'),
    'annonsurl': BaseUrl(attribute='_source.id'),
    'relevans': fields.Integer(attribute='relevans', default=100),
    'antalPlatser': fields.String(attribute='_source.number_of_vacancies'),
    'antalPlatserVisa': fields.Integer(attribute='_source.number_of_vacancies'),
    'varaktighetId': fields.Integer(attribute='_source.duration.legacy_ams_taxonomy_id'),
    'lanid': fields.Integer(attribute='_source.workplace_address.region_code'),
    'lan': fields.String(attribute='_source.workplace_address.region'),
    'anstallningstyp': fields.String(attribute='_source.employment_type.label'),
})

resultat = api.model('Resultat', {
    'antal_platsannonser': fields.Integer(attribute='meta.total_hits'),
    'antal_platsannonser_exakta': fields.Integer(attribute='meta.total_hits'),
    'antal_platsannonser_narliggande': fields.Integer(default=0),
    'antal_platserTotal': fields.Integer(attribute='meta.number_of_positions'),
    'antal_sidor': fields.Integer(attribute='meta.number_of_pages'),
    'matchningsdata': fields.List(fields.Nested(matchningsdata), attribute='hits')
})

matchningslista = api.model('Matchningslista', {
    'matchningslista': fields.Nested(resultat, attribute='hits')
})

# Show jobad
annons = api.model('Annons', {
    'annonsid': fields.String(attribute='id'),
    'platsannonsUrl': BaseUrl(attribute='id'),
    'annonsrubrik': fields.String(attribute='headline'),
    'annonstext': fields.String(attribute='description.text'),
    'yrkesbenamning': fields.String(attribute='occupation.label'),
    'yrkesid': fields.Integer(attribute='occupation.legacy_ams_taxonomy_id'),
    'publiceraddatum': fields.DateTime(attribute='publication_date'),
    'antal_platser': fields.String(attribute='number_of_vacancies'),
    'kommunnamn': fields.String(attribute='workplace_address.municipality'),
    'kommunkod': fields.Integer(attribute='workplace_address.municipality_code'),
    'antalplatserVisa': fields.Integer(default=1),
    'anstallningstyp': fields.String(attribute='employment_type.label')
})

annonsvillkor = api.model('Villkor', {
    'varaktighet': fields.String(attribute='duration.label'),
    'arbetstid': fields.String(attribute='working_hours_type.label'),
    'arbetstidvaraktighet': fields.String('description.conditions'),
    'tilltrade': fields.String(attribute='description.conditions'),
    'lonetyp': fields.String(attribute='salary_type.label'),
})

ansokan = api.model('Ansokan', {
    'referens': fields.String(attribute='application_details.reference'),
    'webbplats': fields.String(attribute='application_details.url'),
    'epostadress': fields.String(attribute='application_details.email'),
    'sista_ansokningsdag': fields.DateTime(attribute='application_deadline'),
    'ovrigt_om_ansokan': fields.String(attribute='application_details.other')
})

arbetsplats = api.model('Arbetsplats', {
    'arbetsplatsnamn': fields.String(attribute='employer.workplace'),
    'postnummer': fields.String(attribute='workplace_address.postcode'),
    'postadress': fields.String(attribute='workplace_address.street_address'),
    'postort': fields.String(attribute='workplace_address.city'),
    'postland': fields.String(attribute='workplace_address.country'),
    'telefonnummer': fields.String(attribute='employer.phone_number'),
    'epostadress': fields.String(attribute='employer.email'),
    'hemsida': fields.String(attribute='employer.url'),
})

korkortslista = api.model('Korkortslista', {
    'korkortstyp': fields.String(attribute='label')
})

krav = api.model('Krav', {
    'egenbil': fields.Boolean(attribute='access_to_own_car'),
    'korkortslista': fields.List(fields.Nested(korkortslista),
                                 attribute='driving_license'),
})

annonsdata = api.model('Annonsdata', {
    'annons': fields.Nested(annons, attribute='_source', skip_none=True),
    'villkor': fields.Nested(annonsvillkor, attribute='_source', skip_none=True),
    'ansokan': fields.Nested(ansokan, attribute='_source', skip_none=True),
    'arbetsplats': fields.Nested(arbetsplats, attribute='_source', skip_none=True),
    'krav': fields.Nested(krav, attribute='_source', skip_none=True),
})

platsannons = api.model('Platsannons', {
    'platsannons': fields.Nested(annonsdata, attribute='elastic_result')
})
