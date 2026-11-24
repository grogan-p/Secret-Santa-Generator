# Secret Santa Generator

Randomly pairs up a group and emails each person who they're buying for. Nobody, including whoever runs it, sees the pairings.

## Setup

Requires Python 3.10 or newer.

```
pip install -r requirements.txt
```

You need a Gmail account with an [App Password](https://myaccount.google.com/apppasswords). Other email providers aren't supported. App Passwords only appear once 2-Step Verification is on. If you're playing, use a separate account, since Gmail keeps a copy of sent emails.

Optional: add the login to a `.env` file so it's filled in automatically:
```
EMAIL_USER=your.santa.account@gmail.com
EMAIL_PWD=your-app-password
```

## Usage

```
py main.py
```

Add everyone (at least 3 people), click **Test connection**, then **Send emails**.

The list saves automatically to `participants.csv`, so it's still there next time. You can also edit that file in Excel, as long as the app is closed.

**Only send once.** Each send makes new pairings.
