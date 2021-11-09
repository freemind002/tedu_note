from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from .models import User
import hashlib

def reg_view(request):
    # 註冊
    if request.method == 'GET':
        # GET 返回頁面
        return render(request, 'user/register.html')
    elif request.method == 'POST':
        # POST 處理提交數據
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
        # 1.兩個密碼要保持一致
        if password_1 != password_2:
            return HttpResponse('兩次密碼輸入不一致')

        # 哈希算法-給定明文，計算出一段定長的，不可逆的值;md5,sha-256
        # 特點：
              # 1.定長輸出：不管明文輸入長度為多少，哈希值都是定長的，比如md5：32位16進制
              # 2.不可逆：無法反向計算出對應的明文
              # 3.雪崩效應：輸入只要改變，輸出必然改變
        # 場景：1.密碼處理。2.文件完整性校驗。
        # 如何使用
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()

        # 2.當前用戶名是否可用
        old_users = User.objects.filter(username=username)
        if old_users:
            return HttpResponse('用戶名己註冊')
        # 3.插入數據[明文處理密碼]
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            # 有可能 報錯 - 重複插入[唯一索引注意並發寫入問題]
            print('--create user error %s' % (e))
            return HttpResponse('用戶名已註冊')

        # 免登錄一天
        request.session['username'] = username
        request.session['uid'] = user.id
        # TODO 修改session存儲時間為1天

        return HttpResponseRedirect('/index')


def login_view(request):
    if request.method == 'GET':
        # 獲取登錄頁面
        # 檢查登錄狀態，如果登錄了，顯示'已登錄'
        if request.session.get('username') and request.session.get('uid'):
            # return HttpResponse('已登錄')
            return HttpResponseRedirect('/index')
        # 檢查cookies
        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            # 回寫session
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            # return HttpResponse('已登錄')
            return HttpResponseRedirect('/index')
        return render(request, 'user/login.html')
    elif request.method == 'POST':
        # 處理數據
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print('--login user error %s' % (e))
            return HttpResponse('用戶名或密碼錯誤')

        # 比對密碼
        m = hashlib.md5()
        m.update(password.encode())

        if m.hexdigest() != user.password:
            return HttpResponse('用戶名或密碼錯誤')
        
        # 記錄會話狀態
        request.session['username'] = username
        request.session['uid'] = user.id

        resp = HttpResponseRedirect('/index')
        # 判斷用戶是否點選了'記住用戶名'
        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600*24*3)
            resp.set_cookie('uid', user.id, 3600*24*3)
        # 點選了 -> Cookie 存儲 username,uid 時間3天
        return resp

def logout_view(request):
    # 刪除session值
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']

    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.COOKIES:
        resp.delete_cookie('uid')
    return resp