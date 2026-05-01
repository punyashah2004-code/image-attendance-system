import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3


def get_users_from_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def generate_logs():
    users = get_users_from_db()

    if not users:
        users = ['NoUser']  # fallback

    actions = ['Login', 'Download File', 'Upload File']

    data = []

    for _ in range(100):
        user = np.random.choice(users)
        action = np.random.choice(actions)

        hour = np.random.randint(9, 18)

        if np.random.rand() < 0.1:
            hour = np.random.randint(0, 5)

        date = datetime.now() - timedelta(days=np.random.randint(0, 5))

        data.append([
            user,
            action,
            date.strftime("%Y-%m-%d"),
            f"{hour}:00"
        ])

    df = pd.DataFrame(data, columns=['user', 'action', 'date', 'time'])
    return df