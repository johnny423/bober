from bober.src.fe.windows.main_window import MainWindow


def launch_gui():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
