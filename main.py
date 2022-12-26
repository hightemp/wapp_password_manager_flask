from flask import g, Flask, render_template, request, send_file, redirect, session, jsonify
import os
import re
import sqlite3
import glob
import re
import base64
import html
import requests
import uuid
from werkzeug.utils import secure_filename

from flask import Response
import importlib.resources
import jinja2
from jinja2 import Template, FunctionLoader, Environment, BaseLoader
from flask import Flask
import mimetypes
import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict
import zipfile

# NOTE: Константы
UPLOAD_PATH_REL = "static/uploads"
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), UPLOAD_PATH_REL)
DATABASE = './database.db'

# NOTE: Переменные
bFirstStart = not os.path.isfile(DATABASE)
app = Flask(__name__)
db = SqliteDatabase(DATABASE)

# NOTE: Модели
class Group(Model):
    name = CharField()

    class Meta:
        database = db

class Category(Model):
    name = CharField()
    group = ForeignKeyField(Group, backref='categories')
    parent = ForeignKeyField('self', backref='children', null=True)

    class Meta:
        database = db

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

db.connect()

if (bFirstStart):
    db.create_tables([Group, Category, Account])

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

    account01 = Account.create(
        name="google", 
        category=category01, 
        a_username="testlogin 1",
        a_password="password",
        a_desc="TEST!"
    )
    account02 = Account.create(
        name="google", 
        category=category01, 
        a_username="testlogin 2",
        a_password="password",
        a_desc="TEST!"
    )


# NOTE: Хелперы
def parse_get(args):
    data = {}

    for u, v in args.lists():
        if hasattr(v, "__len__"):
            for k in v:
                data[u] = k
                if k == '':
                    del data[u]
        else:
            data[u] = v
            if v == '':
                del data[u]

    return data

def parse_multi_form(form):
    data = {}
    for url_k, v in form.lists():
        if ('' in v):
            continue
        v = v[0]

        ks = []
        while url_k:
            if '[' in url_k:
                k, r = url_k.split('[', 1)
                ks.append(k)
                if r[0] == ']':
                    ks.append('')
                url_k = r.replace(']', '', 1)
            else:
                ks.append(url_k)
                break
        sub_data = data
        for i, k in enumerate(ks):
            if k.isdigit():
                k = int(k)
            if i+1 < len(ks):
                if not isinstance(sub_data, dict):
                    break
                if k in sub_data:
                    sub_data = sub_data[k]
                else:
                    sub_data[k] = {}
                    sub_data = sub_data[k]
            else:
                if isinstance(sub_data, dict):
                    sub_data[k] = v

    return data

def fnIterCategories(iGroupID, aOpened, aCategories=[], iLevel=0):
    if (iLevel==0):
        aQueryCategories = Category.select().where(Category.parent == None, Category.group == iGroupID)
        return fnIterCategories(iGroupID, aOpened, aQueryCategories, 1)
    else:
        aNewCategories = []
        for oCategory in aCategories:
            sID = oCategory.id
            aQueryCategories = Category.select().where(Category.parent == sID, Category.group == iGroupID)
            print(aQueryCategories)
            
            aIterCategories = []
            if (sID in aOpened) and aQueryCategories and len(aQueryCategories)>0:
                aIterCategories = fnIterCategories(iGroupID, aOpened, aQueryCategories, iLevel+1)
            
            iCnt = Account.select().where(Account.category == sID).count()
            # oNewCategory = model_to_dict(oCategory, recurse=False, backrefs=False, exclude=['group','parent'])

            oNewCategory = {}
            oNewCategory['id'] = oCategory.id
            oNewCategory['name'] = oCategory.name
            oNewCategory['level'] = (iLevel - 1) * "<span class='tree-spacer'></span>" + oNewCategory['name']
            oNewCategory['cnt'] = iCnt

            aNewCategories += [oNewCategory] + aIterCategories
        
        print(">>", aNewCategories)
        return aNewCategories

def readfile(sFilePath):
    with zipfile.ZipFile(os.path.dirname(__file__)) as z:
        # print(z.namelist())
        with z.open(sFilePath) as f:
            print("[!] "+f.name)
            # print("[!] "+f.read().decode("utf-8"))
            return f.read()
    return "ERROR"

@app.route("/zip/static/<path:path>", methods=['GET', 'POST'])
def zip_static(path):
    oR = Response(readfile("static/"+path), mimetype=mimetypes.guess_type(path)[0])
    oR.headers['Cache-Control'] = 'max-age=60480000, stale-if-error=8640000, must-revalidate'
    return oR

@app.route("/", methods=['GET', 'POST'])
def index():
    sBaseURL = request.url

    oArgs = parse_get(request.args)
    oArgsLists = parse_multi_form(request.args)
    
    sSelGroup = ''
    sSelCategory = ''
    sSelAccount = ''

    if 'select-group' in oArgs:
        sSelGroup = oArgs['select-group']
    if 'select-category' in oArgs:
        sSelCategory = oArgs['select-category']
    if 'select-account' in oArgs:
        sSelAccount = oArgs['select-account']
    
    aOpenedCategories = []
    if 'category' in oArgsLists:
        aOpenedCategories = oArgsLists["category"]
    
    # oGroup = Group.get_by_id(sSelGroup)
    aGroups = Group.select()
    aCategories = fnIterCategories(sSelGroup, aOpenedCategories)

    return render_template('index.html', 
        sBaseURL=sBaseURL,
        sSelGroup=sSelGroup,
        sSelCategory=sSelCategory,
        aGroups=aGroups,
        aCategories=aCategories,
        aOpenedCategories=aOpenedCategories
    )
