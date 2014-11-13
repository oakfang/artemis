Artemis - Async Restful TinyDB Models
======================================

A usage example:

```python

from artemis import ArtemisApplication, ArtemisModel
from artemis import types


app = ArtemisApplication('db.json')


@app.model('foos')
class Foo(ArtemisModel):
    name = types.StringType(required=True)
    age = type.FloatType(default=5)

```