import unittest
import requests
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status


class Testcase(unittest.TestCase):
    def setUp(self):
        data = {
            "username": "test123",
            "password": "test123456",
            "email": "3242354133@qq.com"
        }
        self.url = "http://127.0.0.1:8000/api/user_about/register"
        response = requests.post(self.url, json=data)
        self.url = "http://127.0.0.1:8000/api/user_about/login"

    def test_login_success(self):
        data = {
            "username": "test123",
            "password": "test123456",
        }
        response = requests.post(self.url, json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["errno"], 0)
        self.assertEqual(response.json()["errmsg"], "登录成功")

    def test_login_username_fail(self):
        data = {
            "username": None,
            "password": "test123456",
        }
        response = requests.post(self.url, json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["errno"], 1002)
        self.assertEqual(response.json()["errmsg"], "用户名或邮箱不存在")

    def test_login_password_fail(self):
        data = {
            "username": "test123",
            "password": "test123465",
        }
        response = requests.post(self.url, json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["errno"], 1003)
        self.assertEqual(response.json()["errmsg"], "密码错误")
