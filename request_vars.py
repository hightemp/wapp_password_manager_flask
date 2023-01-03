

class RequestVars:
    aGroupFields = {
        'id': {
            'name': 'id',
            'type': 'hidden',
            'field_name': 'id',
            'value': '',
        },
        'name': {
            'name': 'Название',
            'type': 'text',
            'field_name': 'name',
            'value': '',
        },
    }

    aCategoryFields = {
        'id': {
            'name': 'id',
            'type': 'hidden',
            'field_name': 'id',
            'value': '',
        },
        'name': {
            'name': 'Название',
            'type': 'text',
            'field_name': 'name',
            'value': '',
        },
        'group': {
            'name': 'Группа',
            'type': 'select',
            'field_name': 'group',
            'list': [],
            'value': '',
            'sel_value': '',
        },
    }

    aAccountFields = {
        'title': {
            'name': 'Заголовок',
            'type': 'title',
            'field_name': 'name',
            'value': '',
        },
        'id': {
            'name': 'id',
            'type': 'hidden',
            'field_name': 'id',
            'value': '',
        },
        'category': {
            'name': 'Категория',
            'type': 'select',
            'field_name': 'category',
            'list': [],
            'value': '',
            'sel_value': '',
        },
        'name': {
            'name': 'Название',
            'type': 'text',
            'field_name': 'name',
            'value': '',
        },
        'a_username': {
            'name': 'Логин',
            'type': 'text',
            'field_name': 'a_username',
            'value': '',
        },
        'a_password': {
            'name': 'Пароль',
            'type': 'text',
            'field_name': 'a_password',
            'value': '',
        },
        'a_token': {
            'name': 'Токен',
            'type': 'text',
            'field_name': 'a_token',
            'value': '',
        },
        'a_url': {
            'name': 'url',
            'type': 'url',
            'field_name': 'a_url',
            'value': '',
        },
        'a_desc': {
            'name': 'Описание',
            'type': 'textarea',
            'field_name': 'a_desc',
            'value': '',
        },
    }

    aClasses = {
        'group': 'Group',
        'category': 'Category',
        'account': 'Account',
    }

    sBaseURL = ''

    oArgs = []
    oArgsLists = []

    sSelectGroup = ''
    sSelectCategory = ''
    sSelectAccount = ''

    sGroupFilter = ''
    sCategoryFilter = ''
    sAccountFilter = ''

    aListAllGroups = []
    aListAllCategories = []

    oListAllGroups = []
    oListAllCategories = []

    aFields=[]
    aGroups=[]
    aAccounts=[]

    oAccounts=[]

    aAccountFieldsList=[]
    aOpenedCategories = []
    aCategories = []

    dFormsFieldsList=[]

    sGroupFilter = ''
    sCategoryFilter = ''
    sAccountFilter = ''
    
    aForGroupCategories = []
    aForCategoryAccounts = []

class SessionVars:
    sSelectProject = ""
    sSelectGroup = ""
    sSelectTask = ""
    sSelectFile = ""