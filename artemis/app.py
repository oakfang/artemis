
import json
from operator import and_, or_

from tornado.web import RequestHandler, Application
from tinydb import TinyDB, where


class ModelRequest(RequestHandler):
    def initialize(self, model):
        self.model = model

    @property
    def json(self):
        return json.loads(self.request.body)


class ModelBaseRequest(ModelRequest):
    """
    /<resource>
    """

    def get(self):
        self.write(dict(data=[model.to_primitive() for model in self.model.get_many()]))
        self.flush()

    def post(self):
        self.write(self.model.new(self.json).to_primitive())
        self.flush()


class ModelIDRequest(ModelRequest):
    """
    /<resource>/<resource_id>
    """
    SUPPORTED_METHODS = ['GET', 'PUT', 'PATCH', 'DELETE']

    def get(self, selector):
        self.write(self.model.get_one(selector).to_primitive())
        self.flush()

    def put(self, selector):
        self.write(self.model.replace(selector, self.json).to_primitive())
        self.flush()

    def patch(self, selector):
        self.write(self.model.update(selector, self.json).to_primitive())
        self.flush()

    def delete(self, selector):
        self.write(self.model.delete(selector).to_primitive())
        self.flush()


class ModelMethodRequest(ModelRequest):
    """
    /<resource>/<resource_id>/<method>
    """

    def post(self, selector, method):
        instance = self.model.get_one(selector)
        method = getattr(instance, method)
        assert method.restful is not None
        result = method(**{arg: lmd(self) for arg, lmd in method.restful.iteritems()})
        self.write(json.dumps(result))
        self.flush()


class ModelQueryRequest(ModelRequest):
    """
    /<resource>/query
    """

    def _json_to_query(self, jsn):
        ops = {'&': and_, '|': or_}
        if jsn["field"] in ops:
            return reduce(ops[jsn["field"]], map(self._json_to_query, jsn["value"]))
        return getattr(where(jsn["field"]), jsn["method"])(jsn["value"])

    def post(self):
        self.write(dict(data=[model.to_primitive()
                              for model
                              in self.model.get_many(self._json_to_query(self.json))]))
        self.flush()


class ArtemisApplication(Application):
    def __init__(self, db_file, *args, **kwargs):
        super(ArtemisApplication, self).__init__(*args, **kwargs)
        self._db = TinyDB(db_file)

    def table(self, tname):
        return self._db.table(tname)

    def model(self, model_name):
        def _outer(model_cls):
            model_cls.__table__ = self.table(model_name)

            self.add_handlers('.*', [
                (r'/{}'.format(model_name),
                 ModelBaseRequest, dict(model=model_cls)),
                (r'/{}/query'.format(model_name),
                 ModelQueryRequest, dict(model=model_cls)),
                (r'/{}/([a-zA-Z\-_0-9]+)'.format(model_name),
                 ModelIDRequest, dict(model=model_cls)),
                (r'/{}/([a-zA-Z\-_0-9]+)/([a-zA-Z\-_0-9]+)'.format(model_name),
                 ModelMethodRequest, dict(model=model_cls))
            ])

            return model_cls

        return _outer