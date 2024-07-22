from bober.src.fe.windows.main_window import MainWindow


def launch_gui(session):
    app = MainWindow(session)
    app.mainloop()


if __name__ == "__main__":
    launch_gui(None)  # can raise an error downstream
