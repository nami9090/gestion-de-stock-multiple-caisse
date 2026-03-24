
def redirect_user_by_role(user):
    if user.groups.filter(name='Admin').exists():
        return 'dashboard:admin_dashboard'

    if user.groups.filter(name='Caisse').exists():
        return 'dashboard:admin_dashboard'

    if user.groups.filter(name='Gestionnaire_stock').exists():
        return 'dashboard:admin_dashboard'

    return 'access_denied'
