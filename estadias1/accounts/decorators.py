from django.shortcuts import redirect
from functools import wraps


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')  # Redirige a la página de inicio de sesión si no está autenticado
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    @login_required  
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('privilegio', False):
            return redirect('ventas') 
        return view_func(request, *args, **kwargs)
    return _wrapped_view
