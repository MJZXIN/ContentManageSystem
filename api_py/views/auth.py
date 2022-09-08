import datetime

from flask import Blueprint, request, jsonify

from utils import Result, JwtImpl, db
from views.user import TblUser

auth = Blueprint("auth", __name__)

routes_list = [
    {
        "path": "/",
        "name": "home",
        "root": True,
        "meta": {
            "title": "首页",
            "icon": "",
            "roles": [
                "ADMIN",
                "SYSTEM",
                "USER"
            ]
        },
        "component": "../views/layout/layout.vue",
        "children": [{
            "path": "",
            "name": "dashboard",
            "root": False,
            "meta": {
                "title": "看板",
                "icon": "",
                "roles": [
                    "ADMIN",
                    "SYSTEM",
                    "USER"
                ]
            },
            "component": "../views/home/dashboard.vue",
            "children": []
        }]
    },
    {
        "path": "/product",
        "name": "product",
        "root": True,
        "meta": {
            "title": "产品管理",
            "icon": "",
            "roles": [
                "ADMIN",
                "SYSTEM",
                "USER"
            ]
        },
        "component": "../views/layout/layout.vue",
        "children": [
            {
                "path": "",
                "name": "产品管理",
                "root": False,
                "meta": {
                    "title": "产品管理",
                    "icon": "",
                    "roles": [
                        "ADMIN",
                        "SYSTEM",
                        "USER"
                    ]
                },
                "component": "../views/product/product.vue",
                "children": []
            },
            {
                "path": "cost",
                "name": "成本管理",
                "root": False,
                "meta": {
                    "title": "成本管理",
                    "icon": "",
                    "roles": [
                        "ADMIN",
                        "SYSTEM",
                    ]
                },
                "component": "../views/product/cost.vue",
                "children": []
            },
            {
                "path": "bom",
                "name": "BOM管理",
                "root": False,
                "meta": {
                    "title": "BOM管理",
                    "icon": "",
                    "roles": [
                        "ADMIN",
                        "SYSTEM",
                    ]
                },
                "component": "../views/product/bom.vue",
                "children": []
            }
        ]
    },
    {
        "path": "/:catchAll(.*)",
        "name": "404",
        "root": True,
        "meta": {
            "title": "404",
            "icon": "",
            "roles": [
                "ADMIN",
                "SYSTEM",
                "USER"
            ]
        },
        "component": "../views/error/404.vue",
        "children": []
    }
]


@auth.route("/login", methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    obj = TblUser.query.filter(TblUser.username == username).first()
    if obj:
        # 校验密码
        if obj.chek_password(raw_password=password):
            token = JwtImpl.create_token(obj.username, obj.userrole)
            obj.login_date = datetime.datetime.now()
            obj.login_ip = request.remote_addr
            db.session.flush()
            userinfo = {"username": obj.username, "userrole": obj.userrole}
            return Result.SUCCESS(data={"token": token, "userinfo": userinfo, "routes": routes_list}, msg="登录成功")
        else:
            return Result.ERROR(msg="账号或密码错误")
    else:
        return Result.ERROR(msg="账号或密码错误")


@auth.route("/reg", methods=['POST'])
def reg():
    username = request.json.get("username")
    password = request.json.get("password")
    obj = TblUser.query.filter(TblUser.username == username).first()
    if obj:
        return Result.ERROR(msg="用户名已存在")
    obj = TblUser(username=username, password=password, userrole='USER')
    db.session.add(obj)
    db.session.flush()
    return Result.SUCCESS(msg="注册成功")


@auth.route("/auth")
def getInfo():
    token = request.headers['Authorization']
    if token.startswith('Bearer '):
        payload = JwtImpl.verify_jwt(token[7:])
    else:
        payload = JwtImpl.verify_jwt(token)

    return Result.SUCCESS(data={
        "username": payload.get("username"),
        "userrole": payload.get("userrole")
    }, msg="已登录")
