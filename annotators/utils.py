def capitalize_form(field: str):
    field = field.split('_')
    field = ' '.join(field)
    return field.title()
