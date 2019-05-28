import logging
from flask_restplus import Resource, abort
from legacy.rest import (ns_legacy, kommunlista_query, yrkesgrupp_query, yrkes_query,
                         legacy_query)
from legacy import repository
from legacy.rest import model


log = logging.getLogger(__name__)


@ns_legacy.route('soklista/lan')
class SoklistaLan(Resource):

    def get(self):
        return repository.lista_lan('lan')


@ns_legacy.route('soklista/lan2')
class SoklistaLan2(Resource):

    def get(self):
        return repository.lista_lan2('lan2')


@ns_legacy.route('soklista/kommuner')
class SoklistaKommuner(Resource):

    @ns_legacy.expect(kommunlista_query)
    def get(self):
        args = kommunlista_query.parse_args()
        return repository.lista_kommuner(args['lanid'])


@ns_legacy.route('soklista/yrkesomraden')
class SoklistaYrkesomraden(Resource):

    def get(self):
        return repository.lista_yrkesomraden()


@ns_legacy.route('soklista/yrkesgrupper')
class SoklistaYrkesgrupper(Resource):

    @ns_legacy.expect(yrkesgrupp_query)
    def get(self):
        args = yrkesgrupp_query.parse_args()
        return repository.lista_yrkesgrupper(args['yrkesomradeid'])


@ns_legacy.route('soklista/yrken')
class SoklistaYrken(Resource):

    @ns_legacy.expect(yrkes_query)
    def get(self):
        args = yrkes_query.parse_args()
        return repository.lista_yrken(args['yrkesgruppid'])


@ns_legacy.route('soklista/yrken/<benamning>')
class SoklistaYrkenPath(Resource):

    def get(self, benamning):
        return repository.lista_yrken_by_string(benamning)


@ns_legacy.route('matchning')
class Matchning(Resource):

    @ns_legacy.expect(legacy_query)
    @ns_legacy.marshal_with(model.matchningslista)
    def get(self):
        args = legacy_query.parse_args()
        sida = args.pop('sida')
        rader = args.pop('antalrader')
        if sida < 1:
            abort(400, "Parametern sida måste vara större än noll.")
        if not any(v is not None for v in args.values()):
            abort(400, "Minst en av sökparametrarna nyckelord, kommunid, yrkesid, "
                  "organisationsnummer, yrkesgruppid, varaktighetid, yrkesomradeid, "
                  "landid, lanid, anstallningstyp eller omradeid måste vara satta")
        results = repository.matcha(args, sida, rader)
        return results


@ns_legacy.route('<platsannonsid>')
class ShowPlatsannons(Resource):

    @ns_legacy.marshal_with(model.platsannons)
    def get(self, platsannonsid):
        return repository.fetch_platsannons(platsannonsid)
