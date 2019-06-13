from datetime import datetime
from simplexml import dumps
from flask_restplus import Api, Namespace, reqparse, inputs
from flask import make_response

api = Api(version='1.0', title='Platsannonser',
          description='Arbetsförmedlingens öppna sök-API',
          default='legacy',
          default_label="Ett API för att söka jobbannonser.",
          default_mediatype='application/xml')

ns_legacy = Namespace('Legacy API', description='Feature replicated legacy API')


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    xml = dumps(data)
    # simplexml lacks ability to insert encoding and standalone,
    # so this is a hack
    xml_with_headers = "%s%s%s" % (xml[0:20],
                                   'encoding="utf-8" standalone="yes"',
                                   xml[19:])
    resp = make_response(xml_with_headers, code)
    resp.headers.extend(headers or {})
    return resp


api.add_namespace(ns_legacy, '/')
api.representations['application/xml'] = output_xml

kommunlista_query = reqparse.RequestParser()
kommunlista_query.add_argument('lanid', type=int, required=True)

yrkesgrupp_query = reqparse.RequestParser()
yrkesgrupp_query.add_argument('yrkesomradeid', type=int, required=True)

yrkes_query = reqparse.RequestParser()
yrkes_query.add_argument('yrkesgruppid', type=int, required=True)

legacy_query = reqparse.RequestParser()
legacy_query.add_argument('landid', type=int)
legacy_query.add_argument('lanid', type=int)
legacy_query.add_argument('kommunid', type=int)
legacy_query.add_argument('nyckelord')
legacy_query.add_argument('yrkesid', type=int)
legacy_query.add_argument('yrkesgruppid', type=int)
legacy_query.add_argument('yrkesomradeid', type=int)
legacy_query.add_argument('varaktighetid', type=int)
legacy_query.add_argument('anstallningstyp', type=int)
legacy_query.add_argument('organisationsnummer', type=int)
legacy_query.add_argument('sokdatum',
                          type=lambda x: datetime.strptime(x,
                                                           '%Y-%m-%d %H:%M:%S'))
legacy_query.add_argument('sida', type=int, default=1)
legacy_query.add_argument('antalrader', type=inputs.int_range(0, 10000), default=20)
