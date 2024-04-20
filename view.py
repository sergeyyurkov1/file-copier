from contextlib import contextmanager

from nicegui import app, ui


class View:
    status = ""
    source_folder = ""
    destination_folder = ""

    def __init__(self, controller):
        self.controller = controller

        app.native.window_args["resizable"] = False
        app.native.start_args["debug"] = True
        ui.colors(primary="#FFA500")

        self.main()

    @contextmanager
    def disable_ui(self):
        self.refresh_button.disable()
        self.copy_button.disable()
        self.move_button.disable()
        self.source_input.disable()
        self.destination_input.disable()
        self.swap_folders_button.disable()
        try:
            yield
        finally:
            self.refresh_button.enable()
            self.copy_button.enable()
            self.move_button.enable()
            self.source_input.enable()
            self.destination_input.enable()
            self.swap_folders_button.enable()

    @ui.refreshable
    def create_table(self, files: list) -> None:
        columns = [
            {
                "name": "file",
                "label": "Files to copy",
                "field": "file",
                "required": True,
                "align": "left",
            },
        ]
        rows = [{"file": file} for file in files]

        ui.table(columns=columns, rows=rows, row_key="name").props(
            "virtual-scroll flat dense hide-no-data hide-header card-class='bg-grey-2'"
        ).classes("w-full").style("height: 250px")

    def main(self):
        with ui.grid(columns=16).classes("w-full gap-4"):
            with ui.row().classes("col-span-full"):
                # Input
                ui.input(
                    label="Enter file extensions separated by '|' (example: 'txt | jpg')",
                ).bind_value(app.storage.general, "exts").props(
                    "outlined dense clearable"
                ).classes("w-full")
            with ui.row().classes("col-span-7"):
                # Input
                with ui.input(label="Source folder").bind_value(
                    self, "source_folder"
                ).props("outlined dense").classes("w-full") as self.source_input:
                    ui.button(
                        on_click=self.controller.choose_source_folder,
                        icon="folder_open",
                    ).props("flat dense")
            with ui.row().classes("col-span-2 justify-center content-center"):
                self.swap_folders_button = (
                    ui.button(
                        icon="autorenew",
                        on_click=self.controller.swap_folders,
                    )
                    .props("unelevated flat")
                    .tooltip("Swap source and destination folders")
                )  # .classes("w-32")
            with ui.row().classes("col-span-7"):
                # Input
                with ui.input(label="Destination folder").bind_value(
                    self, "destination_folder"
                ).props("outlined dense").classes("w-full") as self.destination_input:
                    ui.button(
                        on_click=self.controller.choose_destination_folder,
                        icon="folder_open",
                    ).props("flat dense")
            with ui.row().classes("col-span-full"):
                self.create_table([])
            with ui.row().classes("col-span-full justify-center"):
                self.refresh_button = (
                    ui.button(
                        icon="update",
                        on_click=self.controller.refresh,
                    )
                    .props("unelevated")
                    .tooltip("Refresh source folder listing")
                )  # .classes("w-32")
                self.copy_button = (
                    ui.button(
                        icon="file_copy",
                        on_click=self.controller.copy_button_handler,
                    )
                    .props("unelevated")
                    .tooltip("Copy files")
                )  # .classes("w-32")
                self.move_button = (
                    ui.button(
                        icon="drive_file_move",
                        on_click=self.controller.move_button_handler,
                    )
                    .props("unelevated")
                    .tooltip("Move files")
                )  # .classes("w-32")
            with ui.row().classes("col-span-full"):
                self.create_status(self.status)
            with ui.row().classes("col-span-full"):
                self.progressbar = (
                    ui.linear_progress(value=0, show_value=False, size="20px")
                    .props("instant-feedback stripe")
                    .classes("fixed bottom-0 left-0 right-0")
                )
                self.progressbar.visible = False

            with ui.dialog() as self.dialog, ui.card():
                ui.markdown(
                    """
                    #### File Copier 2.0

                    Author: Yurkov Sergey
                """
                )
                ui.button("Close", on_click=self.dialog.close).props("unelevated flat")

            self.about_button = (
                ui.button(
                    icon="help",
                    on_click=self.dialog.open,
                ).props("unelevated round")
            ).classes("fixed bottom-8 right-8")

    def notify(self, text):
        ui.notify(text)

    @ui.refreshable
    def create_status(self, text):
        ui.label(text).classes("font-light fixed bottom-5 left-1 right-1")

    def run(self):
        ui.run(
            title="File Copier",
            native=True,
            window_size=(800, 600),
            fullscreen=False,
            reload=False,
        )
