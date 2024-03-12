import random
import smtplib
import subprocess
import threading

import customtkinter as tk

# Constants
OTP_LENGTH = 6


# Functions
def generate_otp(length):
    return ''.join(random.choices('0123456789', k=length))


def send_email(receiver_email, otp):
    sender_email = "nxtgenspace.in@gmail.com"
    sender_name = "NxtGenSpace"
    password = "vmgxwmewdbgqzuog"

    subject = "Verify Your Account"
    body = f"""<html>
                <body>
                <p style="font-size:16px;">Dear User,</p>
                <p style="font-size:16px;">To ensure the security of your account, we have sent you a One Time Password (OTP) for login verification. Please enter the OTP below to complete the login process:</p>
                <br />
                <h2 style="font-size:24px;">{otp}</h2>
                <br />
                <p style="font-size:16px;">If you did not request this OTP or are experiencing any issues, please contact our support team immediately.</p>
                <br /><br />
                <p style="font-size:16px;">Best regards,</p>
                <p style="font-size:16px;">{sender_name} Team</p>
                </body>
                </html>"""

    message = f"From: {sender_name} <{sender_email}>\nMIME-Version: 1.0\nContent-type: text/html\nSubject: {subject}\n\n{body}"

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def verify_otp(entered_otp, expected_otp):
    return entered_otp == expected_otp


def generate_and_send_otp(email_entry):
    def run():
        email = email_entry.get().strip()
        if not email or "@" not in email or "." not in email:
            session_status.configure(text="Invalid email address format")
            return

        otp = generate_otp(OTP_LENGTH)
        send_email(email, otp)

        email_entry.configure(state="disabled")
        signin_button.destroy()
        session_status.configure(text="OTP has been sent to your email address")
        otp_entry.place(relx=0.5, rely=0.4, anchor="center")
        verify_button.place(relx=0.5, rely=0.5, anchor="center")
        verify_button.configure(command=lambda: verify_otp_callback(otp))

    threading.Thread(target=run).start()


def verify_otp_callback(expected_otp):
    entered_otp = otp_entry.get()
    if verify_otp(entered_otp, expected_otp):
        session_status.configure(text="You are now logged in.")
        show_camera_options_screen()
    else:
        session_status.configure(text="Incorrect OTP. Please try again.")


def show_camera_options_screen():
    email_entry.place_forget()
    otp_entry.place_forget()
    verify_button.place_forget()
    disable_button.place(relx=0.5, rely=0.5, anchor="center")
    enable_button.place(relx=0.5, rely=0.6, anchor="center")
    check_button.place(relx=0.5, rely=0.7, anchor="center")
    session_status.place(relx=0.5, rely=0.8, anchor="center")


def reset_status():
    session_status.configure(text="Camera Status: Check status to update.")
    enable_button.configure(state="disabled")
    disable_button.configure(state="disabled")


def disable_camera():
    powershell_cmd = "(Get-PnpDevice -FriendlyName *webcam* -Class Camera -Status OK) | ForEach-Object {Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false}"
    subprocess.run(["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList",
                    f"'-NoProfile -ExecutionPolicy Bypass -Command {powershell_cmd}'", "-Verb", "RunAs"],
                   creationflags=subprocess.CREATE_NO_WINDOW)
    reset_status()


def enable_camera():
    powershell_cmd = "(Get-PnpDevice -FriendlyName *webcam* -Class Camera -Status Error) | ForEach-Object {Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false}"
    subprocess.run(["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList",
                    f"'-NoProfile -ExecutionPolicy Bypass -Command {powershell_cmd}'", "-Verb", "RunAs"],
                   creationflags=subprocess.CREATE_NO_WINDOW)
    reset_status()


def check_camera_status():
    powershell_cmd = "Get-PnpDevice -FriendlyName *webcam* -Class Camera"
    result = subprocess.run(["powershell", "-Command", powershell_cmd],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if "Error" in result.stdout:
        session_status.configure(text="Camera Status: Disabled")
        enable_button.configure(state="normal")
        disable_button.configure(state="disabled")
    elif "OK" in result.stdout:
        session_status.configure(text="Camera Status: Enabled")
        enable_button.configure(state="disabled")
        disable_button.configure(state="normal")
    else:
        session_status.configure(text="Camera Status: Unknown")
        enable_button.configure(state="disabled")
        disable_button.configure(state="disabled")


# UI
app = tk.CTk()
app.title("Camera Controller")
app.geometry("750x500")

widget_width = 250


email_entry = tk.CTkEntry(app, placeholder_text="Email", width=widget_width)
email_entry.place(relx=0.5, rely=0.4, anchor="center")

signin_button = tk.CTkButton(app, text="Sign In", command=lambda: generate_and_send_otp(email_entry),
                             width=widget_width)
signin_button.place(relx=0.5, rely=0.5, anchor="center")

otp_entry = tk.CTkEntry(app, placeholder_text="OTP", width=widget_width)
verify_button = tk.CTkButton(app, text="Verify", width=widget_width)

session_status = tk.CTkLabel(app, text="", width=widget_width)
session_status.place(relx=0.5, rely=0.7, anchor="center")

disable_button = tk.CTkButton(app, text="Disable Camera", state="disabled", command=disable_camera, width=widget_width)
enable_button = tk.CTkButton(app, text="Enable Camera", state="disabled", command=enable_camera, width=widget_width)
check_button = tk.CTkButton(app, text="Check Status", command=check_camera_status, width=widget_width)

app.mainloop()
