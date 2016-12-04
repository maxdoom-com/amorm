"""This is amorm, meaning [a]nother [m]ongo [ORM].

You can use it like this:
```
    from amorm import Model, orm

    class User(Model):
        @property
        def passwd(self):
            return '******'
        
        @passwd.setter
        def passwd(self, value):
            self.encoded_passwd = '123:%s' % value
    
    orm.connect('mongodb://localhost:27017/', 'test-database')

    user1 = User.create({ 'email':'me@somewhe.re', 'passwd':'yes-i-have-a-password' })
    user1.save()

    print(User.count())

    for u in User.all():
        print(u)
        u.some='thing'
        u.save()

    if User.count()>=10:
        for u in User.all():
            u.delete()
```

Attention: This orm has currently no bulk insert/update or delete methods!
"""

__author__ = "Nico Hoffmann"
__copyright__ = "Copyright (C) 2016 Nico Hoffmann"
__license__ = "BSD"

from bson import ObjectId

class orm:
    """Sets up and holds the connection to the database.
    """
    __client = None
    __db = None
    
    @staticmethod
    def connect(uri, dbname):
        from pymongo import MongoClient
        orm.__client = MongoClient(uri)
        orm.__db = orm.__client[dbname]
    
    @staticmethod
    def collection(name):
        """Get a handle on the collection(name).
        """
        return orm.__db[name]
    
class MetaModel(type):
    """Some meta programming to inherit the name of the collection from the class name.
    """
    def __new__(cls, name, bases, args):
        if name in globals():
            return globals()[name]
        else:
            Type = type.__new__(cls, name, bases, args)
            
            if not '__collection__' in Type.__dict__:
                Type.__collection__ = name
            
            return Type

class Object(object):
    """A shim object that will hol the data.
    """
    pass

class Model(Object, metaclass=MetaModel):
    """Base class of all models. Just subclass them and you're fine.
    """
    def __setattr__(self, key, value):
        """Will write all attributes into the parent (Object).
        """
        super(Object, self).__setattr__(key, value)

    def __repr__(self):
        """Prints this objects content.
        """
        return '; '.join( [ '%s=%s' % ( k, self.__dict__[k] ) for k in self.__dict__ ] )
    
    @property
    def __has_id__(self):
        """To check, if this object already has an _id. THIS ORM ASSUMES, THAT EVERY COLLECTION HAS _id AS IT'S ID.
        """
        return '_id' in self.__dict__
    
    @property
    def __data__(self):
        """Returns a dict of the data.
        """
        return { k: self.__dict__[k]   for k in self.__dict__ if not k.startswith('__') }

    @classmethod
    def create(cls, data={}):
        """Creates an instance with the data provided in the dict data.
        """
        if data is not None:
            return cls(data)
        else:
            return None

    def __init__(self, data={}):
        """Creates a new instance of this model.
        """
        if data is not None:
            for k in list(data.keys()):
                setattr(self, k, data[k])
    
    def save(self):
        """Inserts or replaces this data set.
        """
        if not self.__has_id__:
            self._id = orm.collection(self.__collection__).insert( self.__data__ )
        else:
            orm.collection(self.__collection__).replace_one( {'_id': ObjectId(self._id)}, self.__data__ )
    
    @property
    def _id(self):
        return self.__id

    @_id.setter
    def _id(self, value):
        self.__id = str(value)

    @classmethod
    def get(cls, _id):
        """Get one entry by it's ID.
        """
        return cls.create( orm.collection(cls.__collection__).find_one({ '_id': ObjectId(_id) }) )
    
    @classmethod
    def one(cls, conditions={}):
        """Get one entry matching the conditions.
        """
        return cls.create( orm.collection(cls.__collection__).find_one(conditions) )
    
    @classmethod
    def all(cls, conditions={}, limit=None, skip=None, order_by=None):
        """Get all entries matching the conditions.
        You may choose to limit the query and skip some results.
        You may as well set the order.
        Order ist set as string with an optional minus in front to sort descending.
        Default sorting is ascending.

        An exmple:
        users = User.all({}, limit=10, skip=20, order_by='-last_name')
        ... this will list 10 users, skipping the first 20, sorting by last_name, descending,
            with no further filtering conditions at all.
        """
        query = orm.collection(cls.__collection__).find(conditions)
        if limit is not None:
            query = query.limit(limit)
        if skip is not None:
            query = query.skip(skip)
        if order_by is not None:
            fieldname = '_id'
            direction = pymongo.ASCENDING
            if order_by.startswith('-'):
                direction = pymongo.DESCENDING
                fieldname = order_by[1:]
            elif order_by.startswith('+'):
                direction = pymongo.ASCENDING
                fieldname = order_by[1:]
            else:
                fieldname = order_by
            query = query.order_by((fieldname, direction))
        for result in query:
            yield cls.create( result )
    
    @classmethod
    def count(cls, conditions={}):
        """Returns the count of objects matching your query.
        """
        return orm.collection(cls.__collection__).find(conditions).count()
    
    def delete(self):
        """Deletes one entry.
        """
        orm.collection(self.__collection__).delete_one( {'_id': ObjectId(self._id)} )

