from math import floor
from datetime import date, timedelta
from app import models

def calculate_xp(log: models.ActivityLog) -> int:
    """Calculate XP earned for a completed log."""
    xp_base = (log.time_allocated or 0) * (log.completion_percent / 100)

    # Mode bonus
    if log.mode == models.Mode.watch:
        mode_bonus = 0
    elif log.mode == models.Mode.read:
        mode_bonus = xp_base * 0.10
    elif log.mode == models.Mode.code:
        mode_bonus = xp_base * 0.20
    else:
        mode_bonus = 0

    # Outcome bonus
    if log.outcome == models.Outcome.clear:
        outcome_bonus = 10
    elif log.outcome == models.Outcome.needs_review:
        outcome_bonus = 5
    elif log.outcome == models.Outcome.breakthrough:
        outcome_bonus = 50
    else:
        outcome_bonus = 0

    return int(xp_base + mode_bonus + outcome_bonus)


def update_user_progress(user: models.User, xp_total: int):
    """Update user XP, level, and streaks."""
    user.xp += xp_total
    user.level = floor(user.xp / 1000) + 1

    today = date.today()
    if user.last_active_date:
        if today == user.last_active_date + timedelta(days=1):
            user.current_streak += 1
        elif today == user.last_active_date:
            pass  # same day, no streak change
        else:
            user.current_streak = 1
    else:
        user.current_streak = 1

    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak

    user.last_active_date = today
