from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch or not current_app.elasticsearch.ping():
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch or not current_app.elasticsearch.ping():
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query):
    if not current_app.elasticsearch or not current_app.elasticsearch.ping():
        return [], 0
    search = Search(using=current_app.elasticsearch, index=index).query(
        MultiMatch(query=query, fuzziness='auto'))[:current_app.config['POSTS_PER_PAGE']]
    response = search.execute()
    ids = list(map(lambda hit: hit.meta.id, response))
    return ids, response.hits.total
