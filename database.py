import os
from peewee import *
import datetime
from baselib import *

UPLOAD_PATH_REL = "static/uploads"
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), UPLOAD_PATH_REL)
DATABASE = './wapp_task_manager_flask.database.db'

__DEMO__ = True

# if (__DEMO__):
#     os.unlink(DATABASE)

bFirstStart = not os.path.exists(DATABASE)
db = SqliteDatabase(DATABASE)
lClasses = []

# NOTE: Модели
class Group(Model):
    name = CharField()

    class Meta:
        database = db
lClasses.append(Group)

class Category(Model):
    name = CharField()
    group = ForeignKeyField(Group, backref='categories')
    parent = ForeignKeyField('self', backref='children', null=True)

    class Meta:
        database = db
lClasses.append(Category)

class Account(Model):
    name = CharField()
    category = ForeignKeyField(Category, backref='accounts')
    created_at = DateField(default=datetime.datetime.now)
    updated_at = DateField(default=datetime.datetime.now)
    a_username = CharField(null=True)
    a_password = CharField(null=True)
    a_token = CharField(null=True)
    a_url = CharField(null=True)
    a_desc = TextField(null=True)

    class Meta:
        database = db
lClasses.append(Account)

class ModelsWrapper():
    oR = {}

    def __init__(self, oR) -> None:
        self.oR = oR

    def fmUpdateFromFields(self, sName):
        Klass = globals()[self.oR.aClasses[sName]]
        self.oR.aFields = getattr(self.oR, 'a'+self.oR.aClasses[sName]+'Fields', '')
        oF = {}
        for sK, oV in self.oR.aFields.items():
            sFK = 'field-'+str(sName)+'-'+str(sK)
            try:
                oF[sK] = self.oR.oArgs[sFK]
            except:
                pass
        if 'id' in oF:
            sID = oF['id']
            del oF['id']
            Klass.update(oF).where(Klass.id==sID).execute()
        else:
            Klass.create(**oF).save()        

    def fmDeleteByArgsList(self, sName):
        Klass = globals()[self.oR.aClasses[sName]]
        for sID in self.oR.oArgsLists[sName]:
            Klass.delete().where(Klass.id == sID).execute()


    def fnGetAllGroup(self):
        return Group.select().where(Group.name ** f"%{self.oR.sGroupFilter}%")

    def fnGetCategoryForCurrentGroup(self):
        return Category.select().where(Category.group==self.oR.sSelectGroup,Category.id==self.oR.sSelectCategory)

    def fnGetAccountForCurrentCategory(self):
        return Account.select().where(Account.category==self.oR.sSelectCategory,Account.id==self.oR.sSelectAccount)

    def fnGetAllGroups(self):
        return Group.select()

    def fnGetAllCategories(self):
        return Category.select()

    def fnGetAllGroupsWithFilter(self):
        return Group.select().where(Group.name ** f"%{self.oR.sGroupFilter}%")

    def fnGetAllCategoryiesWithFilter(self):
        return Category.select().where(Category.name ** f"%{self.oR.sCategoryFilter}%")

    def fnGetAllAccount(self):
        return Account.select().where(Account.category==self.oR.sSelectCategory, Account.name ** f"%{self.oR.sAccountFilter}%")

db.connect()

# NOTE: DEMO
if (bFirstStart):
    db.create_tables([Group, Category, Account])

    if (__DEMO__):
        group01 = Group.create(name='Разное')
        group02 = Group.create(name='Гос сервисы')
        group03 = Group.create(name='Почта')
        group04 = Group.create(name='Интернет-магазины')

        category01 = Category.create(name="google", group=group01)

        category0101 = Category.create(name="gmail", group=group01, parent=category01.id)
        category0102 = Category.create(name="api", group=group01, parent=category01.id)

        category0103 = Category.create(name="secret 1", group=group01, parent=category0101.id)
        category0103 = Category.create(name="secret 2", group=group01, parent=category0101.id)

        category0103 = Category.create(name="secret 3", group=group01, parent=category0102.id)
        category0103 = Category.create(name="secret 4", group=group01, parent=category0102.id)

        category02 = Category.create(name="yandex", group=group03)
        category03 = Category.create(name="yandex", group=group04)

        account01 = Account.create(name="google 1", category=category01, a_username="testlogin 1",a_password="password",a_desc="TEST!")
        account02 = Account.create(name="google 2", category=category01, a_username="testlogin 2",a_password="password",a_desc="TEST!")

        account03 = Account.create(name="ya 1", category=category02, a_username="testlogin 3",a_password="password",a_desc="TEST!")
        account04 = Account.create(name="ya 2", category=category02, a_username="testlogin 4",a_password="password",a_desc="TEST!")
        account05 = Account.create(name="ya 3", category=category02, a_username="testlogin 5",a_password="password",a_desc="TEST!")
        account06 = Account.create(name="ya 4", category=category02, a_username="testlogin 6",a_password="password",a_desc="TEST!")


        