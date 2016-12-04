Another MongoDB ORM for Python
========================================================================


This is amorm, meaning [a]nother [m]ongo [ORM].

You can use it like this:
```python3
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

