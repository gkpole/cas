from aiogram.dispatcher.filters.state import State, StatesGroup


class costing(StatesGroup):
    cost = State()


class promokods(StatesGroup):
    promo = State()

class crash(StatesGroup):
    summ = State()

class kubik_casino(StatesGroup):
    summ = State()

class rnd_numchik(StatesGroup):
    summ = State()

class ecn_add(StatesGroup):
    summ = State()


class bring(StatesGroup):
    summ = State()


class bring_requisites(StatesGroup):
    summ = State()
    requisites = State()


class setMamont(StatesGroup):
    id_mamont = State()


class setPromo(StatesGroup):
    promocode = State()


class mamont_edit_balance(StatesGroup):
    id_mamont = State()
    summ = State()


class mess_send(StatesGroup):
    id_mamont = State()
    messages = State()


class mamont_edit_dep(StatesGroup):
    id_mamont = State()
    summ = State()

class mamont_edit_pay(StatesGroup):
    id_mamont = State()
    summ = State()


class count_offer(StatesGroup):
    id_mamont = State()
    count = State()

class count_days(StatesGroup):
    id_mamont = State()
    count = State()

class mamont_mailing(StatesGroup):
    text = State()

class worker_mailing(StatesGroup):
    text = State()

class qiwi_phone(StatesGroup):
    number = State()

class qiwi_token(StatesGroup):
    token = State()

class admin_dep(StatesGroup):
    summ = State()

class admin_procent(StatesGroup):
    summ = State()








    