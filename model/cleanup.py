# cleanup.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from __init__ import app, db
from model.donation import Donation

def cleanup_delivered_donations():
    """Remove donations that were delivered more than 24 hours ago."""
    with app.app_context():
        cutoff = datetime.utcnow() - timedelta(hours=24)
        expired = Donation.query.filter(
            Donation.status == 'delivered',
            Donation.delivered_at <= cutoff
        ).all()
        count = len(expired)
        for d in expired:
            db.session.delete(d)
        if count > 0:
            db.session.commit()
            print(f"🗑️ Auto-cleaned {count} delivered donation(s) older than 24hrs")

def start_cleanup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=cleanup_delivered_donations,
        trigger='interval',
        minutes=30,  # Run every 30 minutes
        id='donation_cleanup',
        name='Clean up delivered donations',
        replace_existing=True
    )
    scheduler.start()
    print("APScheduler started for delivered donation cleanup.")
