
from schematics.models import Model
from schematics.types import StringType


def restful(**kwlambdas):
    def _outer(method):
        method.restful = kwlambdas
        return method
    return _outer


class EntityNotFoundException(Exception):
    pass


class ArtemisModel(Model):
    __table__ = None
    _eid = StringType()

    @classmethod
    def get_one(cls, selector):
        """This should recieve a unique ID and return one instance."""
        json_instance = cls.__table__.get(eid=selector)
        if not json_instance:
            return
        return cls(json_instance)

    @classmethod
    def get_many(cls, search_resource=None):
        """This should return all instances, filtered by a search resource, if any."""
        if search_resource:
            return map(cls, cls.__table__.search(search_resource))
        return map(cls, cls.__table__.all())

    @classmethod
    def update(cls, selector, partial_resource):
        """This should receive a unique ID and a partial update resource."""
        json_instance = cls.__table__.get(eid=selector)
        if not json_instance:
            raise EntityNotFoundException
        instance = cls(json_instance)
        instance.import_data(partial_resource)
        instance.validate(partial=True)
        cls.__table__.update(partial_resource, eids=[json_instance.eid])
        return instance

    @classmethod
    def replace(cls, selector, resource):
        """This should receive a unique ID and a complete update resource."""
        json_instance = cls.__table__.get(eid=selector)
        if not json_instance:
            raise EntityNotFoundException
        instance = cls(resource)
        instance.validate()
        cls.__table__.update(resource, eids=[json_instance.eid])
        return instance

    @classmethod
    def delete(cls, selector):
        """This should receive a unique ID and delete that resource."""
        instance = cls.get_one(selector)
        cls.__table__.remove(eids=[selector])
        return instance

    @classmethod
    def new(cls, resource):
        """This should receive an initial resource and create it."""
        instance = cls(resource)
        instance.validate()
        eid = cls.__table__.insert(resource)
        cls.update(unicode(eid), dict(_eid=eid))
        instance.import_data(dict(_eid=eid))
        return instance