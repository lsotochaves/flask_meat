from website import create_app
from website.cart import check_cart_reservation
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()

def scheduled_task():
    with app.app_context():
        check_cart_reservation()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_task, trigger='interval', seconds=10)
    scheduler.start()
    app.run(debug=True)
