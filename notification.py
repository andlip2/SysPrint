from win10toast import ToastNotifier


def show_notification(title, message, duration):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=duration, threaded=True)
