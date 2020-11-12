from django.core import serializers
import json

def capitalize_form(field: str):
    field = field.split('_')
    field = ' '.join(field)
    return field.title()

def serialize_json(arr: list, fields: tuple = ()):
    ser = ''
    if len(fields) == 0:
        ser = serializers.serialize('json', arr)
    else:
        ser = serializers.serialize('json', arr, fields=fields)

    ret = []
    for obj in json.loads(ser):
        filtered_obj = obj['fields']
        filtered_obj['id'] = obj['pk']
        ret.append(filtered_obj)

    return ret