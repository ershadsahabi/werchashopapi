from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnlyOrStaff(BasePermission):
    """
    به‌طور پیش‌فرض پروژه‌ات IsAuthenticated است.
    این اجازه می‌دهد همه کاربران ناشناس لیست/جزئیات پست‌های منتشرشده را ببینند،
    ولی ایجاد/ویرایش فقط برای استاف.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
