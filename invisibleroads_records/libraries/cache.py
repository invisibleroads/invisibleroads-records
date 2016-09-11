from dogpile.cache.api import NO_VALUE
from dogpile.cache.region import make_region
from dogpile.cache.util import sha1_mangle_key
from sqlalchemy.orm.interfaces import MapperOption
from sqlalchemy.orm.query import Query


SQLALCHEMY_CACHE = make_region(key_mangler=sha1_mangle_key)


class CachingQuery(Query):

    def get_value(self, make_value):
        value = SQLALCHEMY_CACHE.get_or_create(self._cache_key, make_value)
        if value is NO_VALUE:
            raise KeyError(self._cache_key)
        value = self.merge_result(value, load=False)
        return self.expunge_result(value)

    def set_value(self, value):
        SQLALCHEMY_CACHE.set(self._cache_key, value)

    def invalidate(self):
        SQLALCHEMY_CACHE.delete(self._cache_key)

    def expunge_result(self, value):
        vs = []
        for v in value:
            self.session.expunge(v)
            vs.append(v)
        return iter(vs)

    @property
    def _cache_key(self):
        if not hasattr(self, '__cache_key'):
            cache_key = self._from_cache.cache_key
            self.__cache_key = cache_key or self._make_cache_key()
        return self.__cache_key

    def _make_cache_key(self):
        compiled = self.with_labels().statement.compile()
        params = compiled.params
        return ' '.join(
            [str(compiled)] +
            [str(params[k]) for k in sorted(params)])

    def __iter__(self):
        if hasattr(self, '_from_cache'):
            return self.get_value(lambda: list(super(
                CachingQuery, self).__iter__()))
        else:
            return super(CachingQuery, self).__iter__()


class FromCache(MapperOption):

    propagate_to_loaders = False

    def __init__(self, cache_key=None):
        self.cache_key = cache_key

    def process_query(self, query):
        query._from_cache = self
