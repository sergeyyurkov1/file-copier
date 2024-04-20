from multiprocessing import Manager, freeze_support

import webview
from nicegui import app, run, ui

from model import Model
from view import View


class Controller:
    TIMER = 0.5

    def __init__(self, queue):
        self.model = Model()
        self.view = View(self)

        self.queue = queue

    def swap_folders(self):
        self.view.source_folder, self.view.destination_folder = (
            self.view.destination_folder,
            self.view.source_folder,
        )

    async def copy_button_handler(self, e) -> None:
        if self.view.source_folder == "" or self.view.destination_folder == "":
            self.view.notify("No source or destination folders selected.")
            return

        if self.view.source_folder == self.view.destination_folder:
            self.view.notify("Source and destination folders cannot be the same.")
            return

        # Run copy operation and update status
        with self.view.disable_ui():
            self.view.progressbar.visible = True
            ui.timer(self.TIMER, callback=self.update_status)
            result = await run.io_bound(
                self.model.copy, self.queue, self.view.destination_folder
            )
            self.view.notify(result)
            self.view.progressbar.visible = False

    def update_status(self):
        if not self.queue.empty():
            progress, current_file = self.queue.get()

            self.view.create_status.refresh(current_file)
            self.view.progressbar.set_value(progress)
        else:
            self.view.create_status.refresh(self.view.status)
            self.view.progressbar.set_value(self.view.progressbar.value)

    async def choose_source_folder(self):
        folders: tuple[str] | None = await app.native.main_window.create_file_dialog(
            dialog_type=webview.FOLDER_DIALOG
        )
        if folders:
            self.view.source_folder = folders[0]

            await self.refresh()

    async def choose_destination_folder(self):
        folders: tuple[str] | None = await app.native.main_window.create_file_dialog(
            dialog_type=webview.FOLDER_DIALOG
        )
        if folders:
            self.view.destination_folder = folders[0]

    async def move_button_handler(self):
        if self.view.source_folder == "" or self.view.destination_folder == "":
            ui.notify("No source or destination folders selected.")
            return

        if self.view.source_folder == self.view.destination_folder:
            ui.notify("Source and destination folders cannot be the same.")
            return

        # Run copy operation and update status
        with self.view.disable_ui():
            self.view.progressbar.visible = True
            ui.timer(self.TIMER, callback=self.update_status)
            result = await run.io_bound(
                self.model.copy, self.queue, self.view.destination_folder, move=True
            )
            self.view.notify(result)
            self.view.progressbar.visible = False

        await self.refresh()

    async def refresh(self):
        self.model.files_to_copy = await self.model.find_files_to_copy(
            self.view.source_folder
        )
        self.view.create_table.refresh(self.model.files_to_copy)

    def run(self):
        self.view.run()


if __name__ == "__main__":
    freeze_support()
    queue = Manager().Queue()
    Controller(queue).run()
