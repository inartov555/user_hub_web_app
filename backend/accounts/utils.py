import pandas as pd
from django.contrib.auth import get_user_model

User = get_user_model()

REQUIRED_COLUMNS = ['username', 'email', 'first_name', 'last_name']

def handle_excel_user_import(file):
    df = pd.read_excel(file)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return {'created': 0, 'updated': 0, 'errors': [f"Missing columns: {', '.join(missing)}"]}

    created = 0
    updated = 0
    errors = []
    for _, row in df.iterrows():
        username = str(row['username']).strip()
        if not username or username.lower() == 'nan':
            errors.append('Row skipped: username empty')
            continue
        defaults = {
            'email': row.get('email') or '',
            'first_name': row.get('first_name') or '',
            'last_name': row.get('last_name') or '',
        }
        obj, is_created = User.objects.update_or_create(
            username=username,
            defaults=defaults,
        )
        if is_created:
            obj.set_unusable_password()
            obj.save()
            created += 1
        else:
            updated += 1
    return {'created': created, 'updated': updated, 'errors': errors}
