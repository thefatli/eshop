from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # request.user能获取访问的user信息 & 只有既是用户又是staff才行
        return bool(request.user and request.user.is_staff)

class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    # 查看DjangoModelPermissions，模仿给予GET权限
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

'''
設定權限的一種方法：
先到model中的meta中設定对应项(code中的，后台人看到的易于理解的语言)
再来到permissions中根据是否有权限返回True/False
再来到view中使用action进行修饰，定义函数
'''
class ViewCustomerHistoryPermissiom(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')