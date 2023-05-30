
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'description': 'Value example: Bearer ******************',
            'in': 'header'
        },
        'Api-Key': {
            'type': 'apiKey',
            'name': 'Authorization',
            'description': 'Value example: Api-Key l29AEBgf.a5w4OXxlVZHRTUgCN9HKNaRJMFZhERbV',
            'in': 'header'
        },
        'Language': {
            'type': 'apiKey',
            'name': 'Accept-Language',
            'in': 'header',
            'description': 'Your language code. Example: ua,ru,en',
            'default': 'en'
        },
        'Remote-User': {
            'type': 'apiKey',
            'name': 'Remote-User',
            'description': 'Value example: user_id',
            'in': 'header'
        },
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': False,
    'LOGOUT_URL': 'rest_framework:logout',
    'DEFAULT_MODEL_RENDERING': 'example',
    "DEFAULT_AUTO_SCHEMA_CLASS": "main.swagger_schemes.CustomAutoSchema"
}
