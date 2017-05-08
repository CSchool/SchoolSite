import datetime


def get_user_vk_info(backend, details, response, social_user, uid, user, *args, **kwargs):
    if getattr(backend, 'name', None) != 'vk':
        return
    try:
        import vk
        session = vk.Session(access_token=response.get('access_token'))
        api = vk.API(session, v='5.64', lang='ru', timeout=10)
        res = api.users.get(user_ids=response.get('user_id'), fields='bdate,nickname')
        if res:
            bdate = res.get('bdate')
            nickname = res.get('nickname')
            if bdate:
                sp = bdate.split('.')
                if len(sp) == 3:
                    user.birthday = datetime.date(int(sp[2]), int(sp[1]), int(sp[0]))
            if nickname:
                user.patronymic = nickname
            user.save()
    except:
        return