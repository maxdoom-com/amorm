Another MongoDB ORM for Python, well better to say it's an Active Record Implementation
========================================================================

This is amorm, meaning [a]nother [m]ongo [ORM].
Being more precisely it is an active record interface for mongodb.

You can use it like this:
```py
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
    same1 = User.get( user1._id )
    print(user1)
    print(same1)

    print(User.count())

    for u in User.all():
        print(u)
        u.some='thing'
        u.save()

    if User.count()>=10:
        for u in User.all():
            u.delete()
```

Note that the User class is initialized with a 'passwd' field.
In the database the passwd field will not be stored but only the 'encoded_passwd'.

Please note further, that the _id is in contrast to mongodb a string.
You still can not search for an _id but you can .get() to select an object by it's _id.

Attention: This orm has currently no bulk insert/update or delete methods!

