import os
import smtplib
import tkinter as tk
from collections.abc import Callable
from contextlib import AbstractContextManager
from tkinter import messagebox, ttk

from core.matcher import assign
from core.messages import build_message
from core.models import Participant
from senders import Sender
from storage import load_participants, save_participants

# Takes (sending email, password) and returns a context manager that yields a Sender.
Connect = Callable[[str, str], AbstractContextManager[Sender]]

BOLD = ("Segoe UI", 10, "bold")


class SecretSantaApp(tk.Tk):
    def __init__(self, connect: Connect) -> None:
        super().__init__()
        self.connect = connect
        self.title("Secret Santa")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=12)
        frame.grid()

        # --- Participants ---
        ttk.Label(frame, text="Participants", font=BOLD).grid(row=0, column=0, columnspan=4, sticky="w")
        self.tree = ttk.Treeview(frame, columns=("name", "email"), show="headings", height=8, selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.column("name", width=140)
        self.tree.column("email", width=280)
        self.tree.grid(row=1, column=0, columnspan=4, pady=(4, 8))
        for p in load_participants():
            self.tree.insert("", "end", values=(p.name, p.email))

        ttk.Label(frame, text="Name").grid(row=2, column=0, sticky="w")
        self.name_entry = ttk.Entry(frame, width=18)
        self.name_entry.grid(row=2, column=1, sticky="w")
        ttk.Label(frame, text="Email").grid(row=2, column=2, sticky="w", padx=(8, 4))
        self.email_entry = ttk.Entry(frame, width=30)
        self.email_entry.grid(row=2, column=3, sticky="w")
        self.email_entry.bind("<Return>", lambda _: self.on_add())

        people_buttons = ttk.Frame(frame)
        people_buttons.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 14))
        ttk.Button(people_buttons, text="Add", command=self.on_add).pack(side="left")
        ttk.Button(people_buttons, text="Remove selected", command=self.on_remove).pack(side="left", padx=6)

        # --- Sending account ---
        ttk.Label(frame, text="Send from", font=BOLD).grid(row=4, column=0, columnspan=4, sticky="w")
        ttk.Label(frame, text="Email").grid(row=5, column=0, sticky="w", pady=2)
        self.sender_entry = ttk.Entry(frame, width=40)
        self.sender_entry.insert(0, os.getenv("EMAIL_USER", ""))
        self.sender_entry.grid(row=5, column=1, columnspan=3, sticky="w")
        ttk.Label(frame, text="App password").grid(row=6, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(frame, width=40, show="•")
        self.password_entry.insert(0, os.getenv("EMAIL_PWD", ""))
        self.password_entry.grid(row=6, column=1, columnspan=3, sticky="w")

        # --- Actions ---
        actions = ttk.Frame(frame)
        actions.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(14, 4))
        ttk.Button(actions, text="Test connection", command=self.on_test).pack(side="left")
        ttk.Button(actions, text="Send emails", command=self.on_send).pack(side="right")

        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status).grid(row=8, column=0, columnspan=4, sticky="w")

        self.update_status()
        self.name_entry.focus()

    # --- Reading from the window (the table is the source of truth; the CSV is a copy of it) ---

    def people(self) -> list[Participant]:
        return [Participant(*self.tree.item(row, "values")) for row in self.tree.get_children()]

    def credentials(self) -> tuple[str, str] | None:
        sender = self.sender_entry.get().strip()
        password = self.password_entry.get().strip()
        if not sender or not password:
            messagebox.showerror("Missing details", "Fill in the sending email and app password.")
            return None
        return sender, password

    def update_status(self) -> None:
        n = len(self.tree.get_children())
        self.status.set(f"{n} participants" + ("  (need at least 3)" if n < 3 else " ready"))

    # --- Event handlers ---

    def on_add(self) -> None:
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if not name or "@" not in email:
            messagebox.showerror("Can't add", "Enter a name and a valid email.")
            return
        for p in self.people():
            if p.email.lower() == email.lower():
                messagebox.showerror("Can't add", f"{email} is already on the list.")
                return
            if p.name.lower() == name.lower():
                messagebox.showerror("Can't add", f"There's already someone named {name}.")
                return
        self.tree.insert("", "end", values=(name, email))
        save_participants(self.people())
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.name_entry.focus()
        self.update_status()

    def on_remove(self) -> None:
        for row in self.tree.selection():
            self.tree.delete(row)
        save_participants(self.people())
        self.update_status()

    def on_test(self) -> None:
        creds = self.credentials()
        if creds is None:
            return
        self.status.set("Connecting...")
        self.update_idletasks()
        try:
            with self.connect(*creds):
                pass
        except Exception as e:
            self.show_error(e)
            return
        self.update_status()
        messagebox.showinfo("Connection works", "Logged in successfully. No emails were sent.")

    def on_send(self) -> None:
        creds = self.credentials()
        if creds is None:
            return
        try:
            pairings = assign(self.people())  # checks count/duplicates before connecting
        except ValueError as e:
            messagebox.showerror("Can't make pairings", str(e))
            return

        n = len(pairings)
        if not messagebox.askyesno(
            "Send emails?",
            f"Send Secret Santa emails to {n} people from {creds[0]}?\n\nThis can't be undone.",
        ):
            return

        self.status.set("Sending...")
        self.update_idletasks()
        sent = 0
        try:
            with self.connect(*creds) as send:
                for pairing in pairings:
                    send(pairing.giver, build_message(pairing))
                    sent += 1
        except Exception as e:
            if sent == 0:
                self.show_error(e)
            else:
                self.status.set(f"Stopped after {sent} of {n} emails")
                messagebox.showerror(
                    "Sending stopped",
                    f"Sent {sent} of {n} emails before an error:\n{e}\n\n"
                    "Don't just press Send again: it makes new pairings, so people who "
                    "already got an email would get a different assignment.",
                )
            return

        self.status.set(f"Sent {n} emails ✓")
        print(f"Sent {n} Secret Santa messages successfully!")
        messagebox.showinfo("Done", f"Sent {n} Secret Santa emails ✓")

    def show_error(self, e: Exception) -> None:
        self.update_status()
        if isinstance(e, (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected)):
            message = (
                "Couldn't log in. Check the email, and that the password is a Gmail "
                "App Password (not your normal password)."
            )
        elif isinstance(e, smtplib.SMTPException):
            message = str(e)
        elif isinstance(e, OSError):
            message = "Couldn't reach the mail server. Check your internet connection."
        else:
            message = str(e)
        messagebox.showerror("Email error", message)
