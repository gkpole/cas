from peewee import *
db = SqliteDatabase('database.db')


class default_setting(Model):
    id = IntegerField(primary_key=True)
    qiwi_fake = CharField(null=True)
    btc_fake = CharField(null=True)
    card_fake = CharField(null=True)
    default_procent = IntegerField(default=80)
    pay_status = IntegerField(default=0)
    pay_up_summ = IntegerField(default=500)
    class Meta:
        database = db


class all_users(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField(null=True)
    balance = IntegerField(default=0)
    fart = IntegerField(default=1)
    days = IntegerField(default=0)
    offer = IntegerField(default=0)
    worker = IntegerField(null=True)
    verif = IntegerField(default=0)
    worker_ref = IntegerField(null=True)
    freez = IntegerField(default=0)
    id_mamont = IntegerField(null=True)
    min_pay_up = IntegerField(default=default_setting.get(default_setting.id == 1).pay_up_summ)

    class Meta:
        database = db

class Pay(Model):
    id = IntegerField(primary_key=True)
    qiwi_number=CharField(null=True)
    qiwi_token = CharField(null=True)

    class Meta:
        database = db

class workers(Model):
    user_id = IntegerField(primary_key=True)
    procent = IntegerField(default=default_setting.get(default_setting.id == 1).default_procent)

    class Meta:
        database = db

class promo(Model):
    user_id = IntegerField(null=False)
    promok = CharField(null=False)
    summ =IntegerField(null=False)

    class Meta:
        primary_key=False
        database = db


class root(Model):
    admin = IntegerField(primary_key=True)

    class Meta:
        database = db

if __name__ == '__main__':
    db.connect()