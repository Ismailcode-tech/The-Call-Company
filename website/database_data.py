from website import create_app
from website import db
from .models import NetworkProvider, Plan

app = create_app()

with app.app_context():


    fone = NetworkProvider(name='Fone')
    gap = NetworkProvider(name='Gap')
    flipper = NetworkProvider(name='Flipper')
    db.session.add_all([fone, gap, flipper])
    db.session.commit()


    fone_plans = [
        Plan(provider_id=fone.id, name='Super Saver', data_gb=0.5, unlimited_data=False, calls='500',texts='500', phone_included=None, monthly_price=8),
        Plan(provider_id=fone.id, name='Saver', data_gb=1, unlimited_data=False, calls='750', texts='750', phone_included=None, monthly_price=11),
        Plan(provider_id=fone.id, name='Average', data_gb=4, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=16),
        Plan(provider_id=fone.id, name='Regular', data_gb=8, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=19),
        Plan(provider_id=fone.id, name='Spender', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=29),
        Plan(provider_id=fone.id, name='All-in', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included='iPhone 14 Pro', monthly_price=75),
        Plan(provider_id=fone.id, name='All-in', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included='iPhone 14', monthly_price=60),
        Plan(provider_id=fone.id, name='All-in', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included='iPhone 13', monthly_price=55),
        Plan(provider_id=fone.id, name='All-in', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included='Samsung S22', monthly_price=75),
        Plan(provider_id=fone.id, name='All-in', data_gb=100, unlimited_data=False, calls='unl', texts='unl', phone_included='Samsung S21', monthly_price=52),
        Plan(provider_id=fone.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14 Pro', monthly_price=55),
        Plan(provider_id=fone.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14', monthly_price=40),
        Plan(provider_id=fone.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 13', monthly_price=35),
        Plan(provider_id=fone.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S22', monthly_price=55),
        Plan(provider_id=fone.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S21', monthly_price=32),
    ]
    db.session.add_all(fone_plans)


    gap_plans = [
        Plan(provider_id=gap.id, name='Super Saver', data_gb=1,unlimited_data=False, calls='unl',  texts='unl',  phone_included=None, monthly_price=10),
        Plan(provider_id=gap.id, name='Saver', data_gb=2, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=14),
        Plan(provider_id=gap.id, name='Average', data_gb=5, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=19),
        Plan(provider_id=gap.id, name='Regular', data_gb=10, unlimited_data=False, calls='unl', texts='unl', phone_included=None, monthly_price=25),
        Plan(provider_id=gap.id, name='Spender', data_gb=None, unlimited_data=True,  calls='unl',  texts='unl', phone_included=None, monthly_price=32),
        Plan(provider_id=gap.id, name='All-in', data_gb=None, unlimited_data=True, calls='unl', texts='unl', phone_included='iPhone 14 Pro', monthly_price=79),
        Plan(provider_id=gap.id, name='All-in', data_gb=None, unlimited_data=True, calls='unl', texts='unl', phone_included='iPhone 14', monthly_price=55),
        Plan(provider_id=gap.id, name='All-in', data_gb=None, unlimited_data=True, calls='unl', texts='unl', phone_included='iPhone 13', monthly_price=50),
        Plan(provider_id=gap.id, name='All-in', data_gb=None, unlimited_data=True, calls='unl', texts='unl', phone_included='Samsung S22', monthly_price=72),
        Plan(provider_id=gap.id, name='All-in', data_gb=None, unlimited_data=True, calls='unl', texts='unl', phone_included='Samsung S21', monthly_price=50),
        Plan(provider_id=gap.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14 Pro', monthly_price=59),
        Plan(provider_id=gap.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14', monthly_price=42),
        Plan(provider_id=gap.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 13', monthly_price=37),
        Plan(provider_id=gap.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S22', monthly_price=57),
        Plan(provider_id=gap.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S21', monthly_price=30),
    ]
    db.session.add_all(gap_plans)

    flipper_plans = [
        Plan(provider_id=flipper.id, name='Super Saver', data_gb=1, unlimited_data=False, calls='500', texts='500', phone_included=None, monthly_price=6),
        Plan(provider_id=flipper.id, name='Saver', data_gb=2, unlimited_data=False, calls='750', texts='750', phone_included=None, monthly_price=8),
        Plan(provider_id=flipper.id, name='Average', data_gb=3, unlimited_data=False, calls='unl', texts='unl',  phone_included=None, monthly_price=10),
        Plan(provider_id=flipper.id, name='Regular', data_gb=6, unlimited_data=False, calls='unl', texts='unl',  phone_included=None, monthly_price=15),
        Plan(provider_id=flipper.id, name='Spender', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included=None, monthly_price=22),
        Plan(provider_id=flipper.id, name='All-in', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included='iPhone 14 Pro', monthly_price=70),
        Plan(provider_id=flipper.id, name='All-in', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included='iPhone 14', monthly_price=58),
        Plan(provider_id=flipper.id, name='All-in', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included='iPhone 13', monthly_price=49),
        Plan(provider_id=flipper.id, name='All-in', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included='Samsung S22', monthly_price=70),
        Plan(provider_id=flipper.id, name='All-in', data_gb=35, unlimited_data=False, calls='unl', texts='unl',  phone_included='Samsung S21', monthly_price=48),
        Plan(provider_id=flipper.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14 Pro', monthly_price=60),
        Plan(provider_id=flipper.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 14', monthly_price=39),
        Plan(provider_id=flipper.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='iPhone 13', monthly_price=29),
        Plan(provider_id=flipper.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S22', monthly_price=50),
        Plan(provider_id=flipper.id, name='Just Phone', data_gb=None, unlimited_data=False, calls=None, texts=None, phone_included='Samsung S21', monthly_price=35),
    ]
    db.session.add_all(flipper_plans)

    db.session.commit()
    print('Database seeded successfully!')