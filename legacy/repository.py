import logging
import certifi
import json
import io
import os
import requests
from ssl import create_default_context
from elasticsearch import Elasticsearch, exceptions
from flask import send_file
from flask_restplus import abort
from legacy import settings, querybuilder

log = logging.getLogger(__name__)
not_found_file = None

log.info("Using Elasticsearch node at %s:%s" % (settings.ES_HOST, settings.ES_PORT))
if settings.ES_USER and settings.ES_PWD:
    context = create_default_context(cafile=certifi.where())
    elastic = Elasticsearch([settings.ES_HOST], port=settings.ES_PORT,
                            use_ssl=True, scheme='https',
                            ssl_context=context,
                            http_auth=(settings.ES_USER, settings.ES_PWD))
else:
    elastic = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])


def lista_lan():
    (antal_annons, antal_plats) = _get_total_hits(
        {
            'bool': {
                'must': {
                    'term': {
                        settings.WORKPLACE_ADDRESS_COUNTRY_CODE: "199"
                    }
                }
            }
        })
    lanlista = _load_taxonomy("region", None, None,
                              settings.WORKPLACE_ADDRESS_REGION_CODE, 2)
    return _build_list("lan", antal_annons, antal_plats, lanlista)


def lista_lan2():
    (antal_annons, antal_plats) = _get_total_hits()
    lanlista = _load_taxonomy("region", None, None,
                              settings.WORKPLACE_ADDRESS_REGION_CODE, 2)
    (annons_utomlands, plats_utomlands) = _get_total_hits(
        {
            'bool': {
                'must_not': {
                    'term': {
                        settings.WORKPLACE_ADDRESS_COUNTRY_CODE: "199"
                    }
                }
            }
        }
    )
    (annons_ospec, plats_ospec) = _get_total_hits({
        'bool': {
            'must': {
                'term': {
                    settings.WORKPLACE_ADDRESS_REGION_CODE: "90"
                }
            }
        }
    })
    lanlista.append({'id': 90, 'namn': 'Ospecificed arbetsort',
                     'antal_platsannonser': annons_ospec,
                     'antal_ledigajobb': plats_ospec})
    lanlista.append({'id': 199, 'namn': 'Utomlands',
                     'antal_platsannonser': annons_utomlands,
                     'antal_ledigajobb': plats_utomlands})
    return _build_list("lan2", antal_annons, antal_plats, lanlista)


def lista_kommuner(lansid):
    (antal_annons, antal_plats) = _get_total_hits({
        'bool': {
            'must': {
                "term": {
                    settings.WORKPLACE_ADDRESS_REGION_CODE: f"{lansid:02d}"
                }
            }
        }
    })
    return _build_list("kommuner", antal_annons, antal_plats,
                       _load_taxonomy("municipality",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      lansid,
                                      settings.WORKPLACE_ADDRESS_MUNICIPALITY_CODE, 4))


def lista_yrkesomraden():
    (antal_annons, antal_plats) = _get_total_hits()
    return _build_list("yrkesomraden", antal_annons, antal_plats,
                       _load_taxonomy("occupation-field", None, None,
                                      settings.OCCUPATION_FIELD +
                                      ".legacy_ams_taxonomy_id"))


def lista_yrkesgrupper(yrkesomradeid):
    omrade_field = settings.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"
    grupp_field = settings.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"
    (antal_annons, antal_plats) = _get_total_hits(
        {
            'bool': {
                'must': {"term": {omrade_field: yrkesomradeid}}
            }
        }
    )
    return _build_list("yrkesgrupper", antal_annons, antal_plats,
                       _load_taxonomy("occupation-group",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      yrkesomradeid, grupp_field))


def lista_yrken(yrkesgruppid):
    grupp_field = settings.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"
    yrke_field = settings.OCCUPATION + ".legacy_ams_taxonomy_id"
    (antal_annons, antal_plats) = _get_total_hits(
        {
            'bool': {
                'must': {"term": {grupp_field: yrkesgruppid}}
            }
        }
    )
    return _build_list("yrken", antal_annons, antal_plats,
                       _load_taxonomy("occupation-name",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      yrkesgruppid, yrke_field))


def lista_yrken_by_string(benamning):
    yrke_field = settings.OCCUPATION + ".label"
    (antal_annons, antal_plats) = _get_total_hits(
        {
            'bool': {
                'must': {"prefix": {yrke_field: benamning}}
            }
        }
    )
    return _build_list("yrken", antal_annons, antal_plats,
                       _load_taxonomy("occupation-name",
                                      None,
                                      None,
                                      settings.OCCUPATION + ".legacy_ams_taxonomy_id",
                                      0,
                                      benamning))


def _calculate_pages(args, size):
    pages = querybuilder.build_query(args, 0, 0)
    response = elastic.search(index=settings.ES_INDEX, body=pages)

    total_hits = response.get('hits', {}).get('total', {}).get('value', 0)
    number_of_pages = (total_hits // size + (total_hits % size > 0)
                       if size else 0)
    positions = response['aggregations']['positions']['value']
    return total_hits, number_of_pages, positions


def _find_highest_id(query_args, offset, size):
    next_offset = offset
    last_id = None
    while next_offset > 10000:
        catchup = querybuilder.build_query(query_args, 9999, 1, last_id, True)
        response = elastic.search(index=settings.ES_INDEX, body=catchup)
        hits = response.get('hits', {}).get('hits', [])
        if hits:
            last_id = hits[0]['_id']
            log.debug("Updating last id for pagination: %s" % last_id)
        next_offset = next_offset - 10000

    next_offset = next_offset if next_offset > 0 else 0

    while next_offset+size > 10000:
        next_offset = next_offset - size if next_offset > size else 0
        catchup = querybuilder.build_query(query_args, next_offset, 1, last_id, True)
        response = elastic.search(index=settings.ES_INDEX, body=catchup)
        hits = response.get('hits', {}).get('hits', [])
        if hits:
            last_id = hits[0]['_id']
            log.debug("Updating last id for pagination: %s" % last_id)
            log.debug("Pagination: Filter from %s with new offset: %d" % (last_id, next_offset))
    return last_id, next_offset


def matcha(query_args, sida=1, size=20):
    sort_by_id = False
    offset = _calculate_offset(sida, size)
    (total_hits, number_of_pages, positions) = _calculate_pages(query_args, size)
    if total_hits > 10000:
        # Must sort by ID for this query
        sort_by_id = True
    if sida <= number_of_pages:
        (last_id, new_offset) = _find_highest_id(query_args, offset, size)
        dsl = querybuilder.build_query(query_args, new_offset, size, last_id, sort_by_id)
        response = elastic.search(index=settings.ES_INDEX, body=dsl)
        max_score = response['hits']['max_score']
        if not sort_by_id and max_score > 0:
            # If using relevance, calculate score for each hit
            for hit in response.get('hits', {}).get('hits', []):
                doc_score = hit['_score']
                hit['relevans'] = int((doc_score / max_score)*100)
    else:
        response = dict()
        response['hits'] = {'hits': []}
    response['hits']['meta'] = {
        'total_hits': total_hits,
        'number_of_positions': positions,
        'number_of_pages': number_of_pages,
    }
    return response


def fetch_platsannons(ad_id):
    try:
        query_result = elastic.get(index=settings.ES_INDEX, id=ad_id, ignore=404)
        if query_result and '_source' in query_result:
            return {"elastic_result": query_result}
        else:
            ext_id_query = {
                'query': {
                    'term': {
                        'external_id': ad_id
                    }
                }
            }
            query_result = elastic.search(index=settings.ES_INDEX, body=ext_id_query)
            hits = query_result.get('hits', {}).get('hits', [])
            if hits:
                return {"elastic_result": hits[0]}

        log.info("Job ad %s not found, returning 404 message" % ad_id)
        abort(404, 'Platsannons saknas')
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return
    return elastic.get()


def _get_correct_logo_url(ad_id):
    result = fetch_platsannons(ad_id)

    ad = result.get('elastic_result', {}).get('_source', {})

    logo_url = None
    if ad and 'employer' in ad:
        if 'organization_number' in ad['employer'] and ad['employer']['organization_number']:
            org_number = ad['employer']['organization_number']
            eventual_logo_url = '%sorganisation/%s/logotyper/logo.png' % (settings.COMPANY_LOGO_BASE_URL, org_number)
            r = requests.head(eventual_logo_url, timeout=15)
            if r.status_code == 200:
                logo_url = eventual_logo_url
    return logo_url


def _get_not_found_logo_file():
    global not_found_file
    currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'
    if not_found_file is None:
        not_found_filepath = currentdir + "resources/1x1-00000000.png"
        log.debug('Opening global file %s' % not_found_filepath)
        not_found_file = open(not_found_filepath, 'rb')
        not_found_file = not_found_file.read()
    return not_found_file


def fetch_platsannons_logo(ad_id):
    logo_url = _get_correct_logo_url(ad_id)

    attachment_filename = 'logo.png'
    mimetype = 'image/png'

    if logo_url is None:
        return send_file(
            io.BytesIO(_get_not_found_logo_file()),
            attachment_filename=attachment_filename,
            mimetype=mimetype
        )
    else:
        r = requests.get(logo_url, stream=True)
        return send_file(
            io.BytesIO(r.raw.read(decode_content=False)),
            attachment_filename=attachment_filename,
            mimetype=mimetype
        )


def _calculate_offset(pagenumber, rows):
    if pagenumber == 1:
        return 0
    return (pagenumber - 1) * rows


def _build_list(listnamn, antal_annons, antal_plats, sokdata):
    return {
        'soklista': {
            "listnamn": listnamn,
            "totalt_antal_platsannonser": antal_annons,
            "totalt_antal_ledigajobb": antal_plats,
            "sokdata": sokdata
        }
    }


def _load_taxonomy(taxtype, key, value, jobad_field, zero_fill=0, label_string=None):
    dsl = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"type": taxtype}},
                ]
            }
        },
        "size": 500
    }
    if key and value:
        dsl['query']['bool']['must'].append({"term": {key: value}})
    if label_string:
        dsl['query']['bool']['must'].append({"prefix": {"label": label_string}})

    log.debug("TAXONOMY DSL: %s" % json.dumps(dsl))
    result = elastic.search(index=settings.ES_TAX_INDEX, body=dsl)
    taxonomy_list = [{'id': hit['_source']['legacy_ams_taxonomy_num_id'],
                      'namn': hit['_source']['label']}
                     for hit in result.get('hits', {}).get('hits', [])]

    for entry in taxonomy_list:
        (a, p) = _get_total_hits(
            {
                'bool': {
                    'must': {
                        'term': {
                            jobad_field: str(entry['id']).zfill(zero_fill)
                        }
                    }
                }
            }
        )
        entry['antal_platsannonser'] = a
        entry['antal_ledigajobb'] = p

    return taxonomy_list


def _get_total_hits(query={"bool": {"must": []}}):
    query['bool']['filter'] = [
                    {
                        'range': {
                            settings.PUBLICATION_DATE: {
                                'lte': 'now/m'
                            }
                        }
                    },
                    {
                        'range': {
                            settings.LAST_PUBLICATION_DATE: {
                                'gte': 'now/m'
                            }
                        }
                    },
                    {
                        'term': {
                            settings.REMOVED: False
                        }
                    },
                ]
    dsl = {
        "query": query,
        "size": 0,
        "track_total_hits": True,
        "aggs": {
            "positions": {
                "sum": {"field": settings.NUMBER_OF_VACANCIES}
            }
        }
    }
    log.debug("TOTAL HITS DSL: %s" % json.dumps(dsl))
    result = elastic.search(index=settings.ES_INDEX, body=dsl)
    return (result.get('hits', {}).get('total', {}).get('value', 0),
            int(result.get('aggregations', {}).get('positions', {}).get('value', 0)))
