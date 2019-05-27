import logging
import json
from legacy import settings

log = logging.getLogger(__name__)


def build_query(args, offset, size, start_from=None):
    dsl = {"query": {"bool": {"must": []}}, "track_total_hits": True,
           "from": offset, "size": size, "sort": {"id": "ASC"}}
    dsl['aggs'] = {
        "positions": {
            "sum": {"field": settings.NUMBER_OF_VACANCIES}
        }
    }
    dsl['query']['bool']['filter'] = [
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
    if start_from:
        dsl['query']['bool']['filter'].append({"range": {"id": {"gt": start_from}}})

    for qp in [('landid', settings.WORKPLACE_ADDRESS_COUNTRY_CODE, 0),
               ('lanid', settings.WORKPLACE_ADDRESS_REGION_CODE, 2),
               ('kommunid', settings.WORKPLACE_ADDRESS_MUNICIPALITY_CODE, 4),
               ('yrkesid', settings.OCCUPATION + ".legacy_ams_taxonomy_id", 0),
               ('yrkesgruppid', settings.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id", 0),
               ('yrkesomradeid',
                settings.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id", 0),
               ('varaktighetid', settings.DURATION + ".legacy_ams_taxonomy_id", 0),
               ('anstallningstyp',
                settings.EMPLOYMENT_TYPE + ".legacy_ams_taxonomy_id", 0),
               ('organisationsnummer', settings.EMPLOYER_ORGANIZATION_NUMBER, 0),
               ]:
        if args[qp[0]]:
            dsl['query']['bool']['must'].append(
                {"term": {
                    qp[1]: str(args[qp[0]]).zfill(qp[2])
                }}
            )

    log.debug("QUERY: %s" % json.dumps(dsl, indent=2))
    return dsl
