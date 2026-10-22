from core.types import StrEnum


class StatusEnum(StrEnum):
    """启用状态"""

    enable = ("enable", "启用")
    disable = ("disable", "禁用")


class PermissionTypeEnum(StrEnum):
    """权限类型"""

    api = ("api", "API")


class SystemResourceTypeEnum(StrEnum):
    """系统资源类型"""

    menu = ("menu", "菜单")
    button = ("button", "按钮")
    api = ("api", "接口")


class SystemResourceSubTypeEnum(StrEnum):
    """系统资源子类型"""

    add_tab = ("add_tab", "选项卡")
    dialog = ("dialog", "弹窗")
    ajax = ("ajax", "Ajax请求")
    link = ("link", "链接")


class TokenSceneTypeEnum(StrEnum):
    """token场景"""

    general = ("General", "通用")
    web = ("Web", "网页端")
    ios = ("Ios", "Ios")
    android = ("Android", "Android")
    wmp = ("WMP", "微信小程序")
    unknown = ("Unknown", "未知")


class SendCodeScene(StrEnum):
    """发送短信场景"""

    login = ("login", "登录")
    reset_password = ("reset_password", "重置密码")
    change_account_phone = ("change_account_phone", "修改账户手机号")
