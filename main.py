from flask import g, Flask, request, send_file, redirect, session, jsonify
import os
import re
from werkzeug.utils import secure_filename

from flask import Response
from jinja2 import Template, FunctionLoader, Environment, BaseLoader
from flask import Flask
import mimetypes
import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict
import zipfile
from flask_caching import Cache
from request_vars import *
from baselib import *
from database import *

# NOTE: Константы
UPLOAD_PATH_REL = "static/uploads"
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), UPLOAD_PATH_REL)
DATABASE = './wapp_password_manager_flask.database.db'

__DEMO__ = False
APP_NAME=__name__

# NOTE: Переменные
bFirstStart = not os.path.isfile(DATABASE)
app = Flask(__name__)
config = {
    # "DEBUG": True,          # some Flask specific configs
    # "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)

@cache.cached(timeout=500)
def fnIterCategories(iGroupID, aOpened, sCategoryFilter, aCategories=[], iLevel=0):
    if (iLevel==0):
        aQueryCategories = []

        if str(iGroupID)=="-1":
            aQueryCategories = Category.select().where(Category.name ** f"%{sCategoryFilter}%", Category.parent == None)
        else: 
            aQueryCategories = Category.select().where(Category.name ** f"%{sCategoryFilter}%", Category.parent == None, Category.group == iGroupID)

        return fnIterCategories(iGroupID, aOpened, sCategoryFilter, aQueryCategories, 1)
    else:
        aNewCategories = []
        for oCategory in aCategories:
            sID = oCategory.id

            if str(iGroupID)=="-1":
                aQueryCategories = Category.select().where(Category.name ** f"%{sCategoryFilter}%", Category.parent == sID)
            else: 
                aQueryCategories = Category.select().where(Category.name ** f"%{sCategoryFilter}%", Category.parent == sID, Category.group == iGroupID)
            
            if sCategoryFilter!='':
                aQueryCategories.where(Category.name ** f"%{sCategoryFilter}%")

            aIterCategories = []
            if (sID in aOpened) and aQueryCategories and len(aQueryCategories)>0:
                aIterCategories = fnIterCategories(iGroupID, aOpened, sCategoryFilter, aQueryCategories, iLevel+1)
            
            iCnt = Account.select().where(Account.category == sID).count()

            oNewCategory = {}
            oNewCategory['id'] = oCategory.id
            oNewCategory['name'] = oCategory.name
            oNewCategory['level'] = (iLevel - 1) * "<span class='tree-spacer'></span>" + oNewCategory['name']
            oNewCategory['cnt'] = iCnt

            aNewCategories += [oNewCategory] + aIterCategories
        
        return aNewCategories

def fnPrepareFormFields(aFields, cCls, sSelID):
    kls = globals()[cCls]
    oItem = {}
    if sSelID != "" and int(sSelID) > 0:
        try:
            oItem = kls.get_by_id(sSelID)
            oItem = model_to_dict(oItem, recurse=False, backrefs=False)
        except:
            pass

    for sK, oV in aFields.items():
        if 'sel_value' in aFields[sK]:
            aFields[sK]['value'] = aFields[sK]['sel_value']
        else:
            if sSelID==0:
                aFields[sK]['value'] = ''
            else:
                if sK in oItem and oItem[sK]:
                    aFields[sK]['value'] = oItem[oV['field_name']]
                else:
                    aFields[sK]['value'] = ''
    return aFields

@app.route("/zip/static/<path:path>", methods=['GET', 'POST'])
def zip_static(path):
    oR = Response(readfile("static/"+path), mimetype=mimetypes.guess_type(path)[0])
    oR.headers['Cache-Control'] = 'max-age=60480000, stale-if-error=8640000, must-revalidate'
    return oR

@app.route("/", methods=['GET', 'POST'])
@cache.cached()
def index():
    oR = RequestVars()
    oR.sBaseURL = request.url

    fnPrepareArgs(oR)

    oMW = ModelsWrapper(oR)
    
    # session.update('sSelGroup','sSelAccount')
    if (oR.sSelectGroup!="-1"):
        oR.aForGroupCategories = oMW.fnGetCategoryForCurrentGroup()
        if len(oR.aForGroupCategories)==0 and oR.sSelectCategory!="-1":
            oR.sSelectCategory = ''
    if (oR.sSelectCategory!="-1"):
        oR.aForCategoryAccounts = oMW.fnGetAccountForCurrentCategory()
        if len(oR.aForCategoryAccounts)==0 and oR.sSelectAccount!="-1":
            oR.sSelectAccount = ''

    # NOTE: Формы
    if f'cancel' in oR.oArgs:
        return redirect("/")
    for sName in ['group', 'category', 'account']:
        if f'search-clean-{sName}' in oR.oArgs:
            oR.oArgs[f'search-{sName}'] = ''
            setattr(oR, 's'+oR.aClasses[sName]+'Filter', '')
        if f'search-{sName}' in oR.oArgs:
            setattr(oR, 's'+oR.aClasses[sName]+'Filter', oR.oArgs[f'search-{sName}'])
        if f'accept-remove-{sName}' in oR.oArgs:
            oMW.fmDeleteByArgsList(sName)
            del oR.oArgs[f'accept-remove-{sName}']
            break
        if f'remove-{sName}' in oR.oArgs:
            return render_template(f'{sName}/alert_delete.html', aFields=oR.oArgs)        

        if f'save-{sName}' in oR.oArgs:
            print(oR.oArgs[f'save-{sName}'], sName, oR.oArgs)
            oMW.fmUpdateFromFields(sName)
            del oR.oArgs[f'save-{sName}']
            del oR.oArgs[f'edit-{sName}']
            break
        if f'clean-{sName}' in oR.oArgs:
            break
        
    # FIXME: Дубль кода
    oR.oListAllGroups = oMW.fnGetAllGroups()
    oR.oListAllCategories = oMW.fnGetAllCategories()
    oR.aListAllGroups = []
    oR.aListAllCategories = []
    for oI in oR.oListAllGroups:
        oR.aListAllGroups += [oI]
    for oI in oR.oListAllCategories:
        oR.aListAllCategories += [oI]
    
    oR.aAccountFields['category']['list'] = oMW.fnGetAllCategories()
    oR.aAccountFields['category']['sel_value'] = oR.sSelectCategory

    if ((f'edit-category' in oR.oArgs) or (f'create-category' in oR.oArgs)):
        oR.aCategoryFields['group']['list'] = oMW.fnGetAllGroups()
        oR.aCategoryFields['group']['sel_value'] = oR.sSelectGroup
    if ((f'edit-account' in oR.oArgs) or (f'create-account' in oR.oArgs)):
        if (f'edit-account' in oR.oArgs):
            oR.dFormsFieldsList = fnPrepareFormFields(oR.aAccountFields, 'Account', oR.sSelectAccount)
            # NOTE: Account - edit
            return render_template(f'account/edit.html',oR=oR)
        elif (f'create-account' in oR.oArgs):
            oR.dFormsFieldsList = fnPrepareFormFields(oR.aAccountFields, 'Account', 0)
            # NOTE: Account - create
            return render_template(f'account/create.html', oR=oR)
    if f'create-group' in oR.oArgs:
        oR.dFormsFieldsList = {}
        oR.dFormsFieldsList = fnPrepareFormFields(oR.aGroupFields, 'Group', 0)
        return render_template(f'group/create.html',oR=oR)
    if f'create-category' in oR.oArgs:
        oR.dFormsFieldsList = {}
        oR.dFormsFieldsList = fnPrepareFormFields(oR.aCategoryFields, 'Category', 0)
        # NOTE: Group, Category - create
        return render_template(f'category/create.html',oR=oR)
    if f'edit-group' in oR.oArgs:
        oR.dFormsFieldsList = {}
        oR.dFormsFieldsList = fnPrepareFormFields(oR.aGroupFields, 'Group', oR.sSelectGroup)
        return render_template(f'group/edit.html',oR=oR)            
    if f'edit-category' in oR.oArgs:
        oR.dFormsFieldsList = {}
        oR.dFormsFieldsList = fnPrepareFormFields(oR.aCategoryFields, 'Category', oR.sSelectCategory)
        # NOTE: Group, Category - edit
        return render_template(f'category/edit.html',oR=oR)

    oR.oListAllGroups = oMW.fnGetAllGroupsWithFilter()
    print(oR.oListAllGroups)
    oR.oListAllCategories = oMW.fnGetAllCategoryiesWithFilter()
    oR.aListAllGroups = []
    oR.aListAllCategories = []
    for oI in oR.oListAllGroups:
        oR.aListAllGroups += [oI]
    for oI in oR.oListAllCategories:
        oR.aListAllCategories += [oI]

    # NOTE: Группы
    oR.aGroups = [{'id':-1,'name':'Все','short':1}] + oR.aListAllGroups


    oR.aOpenedCategories = []
    if 'category' in oR.oArgsLists:
        oR.aOpenedCategories = oR.oArgsLists["category"]
    
    oR.aCategories = fnIterCategories(oR.sSelectGroup, oR.aOpenedCategories, oR.sCategoryFilter)
    oR.aCategories.insert(0, {'id':-1,'name':'Все','level':'Все','short':1})

    oR.aAccounts=[]
    oR.aAccountFieldsList = []
    if oR.sSelectCategory != '':
        oR.aAccounts = oMW.fnGetAllAccount()

        # aAccountFields['group']['list'] = oR.aListAllGroups
        oR.aAccountFields['category']['list'] = oR.aListAllCategories
        oR.aAccountFieldsList = fnPrepareFormFields(oR.aAccountFields, 'Account', oR.sSelectAccount)

    return render_template(
        'index.html', 
        oR=oR
    )

@app.route("/as_table", methods=['GET', 'POST'])
@cache.cached()
def as_table():
    oR = RequestVars()

    oR.oAccounts = Account.select().join(Category).join(Group)
    oR.oAccounts = models_col_to_list(oR.oAccounts)

    return render_template(
        'table.html', 
        oR=oR
    )

def run():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    run()