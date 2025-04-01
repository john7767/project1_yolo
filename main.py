import flet as ft
import glob
import os

from aws_s3 import *
import yolo


root_dir = os.getcwd()
file_path = ""

image_view = ft.Column(width=600, height=600, scroll=ft.ScrollMode.ALWAYS)
image_view.controls.append(ft.Image(src="_blank.jpg", fit=ft.ImageFit.COVER))
image_view.controls.append(ft.Image(src="_blank.jpg", fit=ft.ImageFit.COVER))


class FileList(ft.Column):
    def __init__(self):
        super().__init__()
        self.width = 300
        self.height = 600
        self.scroll = ft.ScrollMode.ALWAYS

    def append(self, file_path):
        self.controls.append(FileName(file_path, self.clear_blue))
        self.update()

    def get_files(self, filedir):
        ### getting files
        # filelist = glob.glob(f"{filedir}/*")
        filelist = get_s3List(filedir)
        # get_s3Object(filedir)
        for path in filelist:
            self.controls.append(FileName(path, self.clear_blue))

    def clear_blue(self):
        # global file_list
        for filename in self.controls:
            filename.text_button.style.bgcolor = ft.Colors.WHITE
        self.update()


file_list = FileList()


class FileName(ft.Row):
    def __init__(self, file_path, clear_blue):
        super().__init__()
        self.file_path = file_path
        self.clear_blue = clear_blue
        self.file_name = os.path.basename(self.file_path)
        self.check_box = ft.Checkbox(value=True)
        self.text_button = ft.TextButton(
            text=self.file_name,
            data=self.file_name,
            on_click=self.textbutton_clicked,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE),
            expand=True,
        )
        self.controls = [self.check_box, self.text_button]

    def textbutton_clicked(self, e):
        self.clear_blue()
        self.text_button.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE)
        image_view.controls = []
        image_name = os.path.basename(self.file_path)
        image_view.controls.append(
            ft.InteractiveViewer(
                min_scale=0.1,
                max_scale=15,
                boundary_margin=ft.margin.all(20),
                # content=ft.Image(src=f"{file_path.split("/")[-1]}/{image_name}"),
                content=ft.Image(src=f"tmp/{image_name}"),
            )
        )

        image_view.controls.append(
            ft.InteractiveViewer(
                min_scale=0.1,
                max_scale=15,
                boundary_margin=ft.margin.all(20),
                content=ft.Image(
                    # src=f"{self.file_path.split("/")[0]}_done/{image_name}"
                    src=f"tmp_done/{image_name}"
                ),
            )
        )

        image_view.update()
        self.update()


def main(page: ft.Page) -> None:

    page.title = "Yolo"

    #######################################################
    files = ft.Column(width=200, height=700, scroll="always")

    img = ft.Column(width=600)
    img.controls.append(
        ft.Image(
            src="image0.jpg",
            fit=ft.ImageFit.COVER,
        )
    )
    img.controls.append(
        ft.Image(
            src="image0.jpg",
            fit=ft.ImageFit.COVER,
        )
    )
    #######################################################

    def textField_changed(e):
        global file_path
        global fileList
        file_path = e.control.value
        fileList = glob.glob(f"{file_path}/*")
        page.update()

    # tf_getDir = ft.TextField(hint_text="src/assets/imgs", label="경로", width=600)
    tf_getDir = ft.TextField(hint_text="Your Bucket Name", label="bucket", width=600)
    tf_getDir.on_change = textField_changed

    def on_start(e):
        global file_path
        file_path = tf_getDir.value
        # file_list.get_files(tf_getDir.value)
        file_list.get_files(file_path)
        page.go("/progr")
        yolo.yolo_detect(workingFolder)
        page.go("/files")

    def on_save(e):
        page.go("/saved")
        save_files = []
        for control in file_list.controls:
            if control.controls[0].value:
                save_files.append(control.controls[1].text)
        # put_s3Object(file_path, save_files)

    def on_cancer(e):
        global file_list
        file_list.controls = []
        image_view.controls = []
        tf_getDir.value = ""
        page.go("/")

    def on_goroot(e):
        on_cancer(e)

    def route_change(e: ft.RouteChangeEvent) -> None:
        page.views.clear()

        # Home
        page.views.append(view_root)

        # progressbar
        if page.route == "/progr":
            page.views.append(view_progr)

        # file & image list
        if page.route == "/files":
            page.views.append(view_files)

        # saved
        if page.route == "/saved":
            page.views.append(view_saved)

        page.update()

    #######################################################
    ### all views
    view_root = ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("Home"), bgcolor="blue"),
            # Text(value="경로를 입력 해 주세요", size=30),
            # ft.TextField(hint_text="C:\\", label="경로 설정",
            #              width=800, on_change=textbox_changed),
            tf_getDir,
            ft.ElevatedButton(text="Start", on_click=on_start),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=26,
    )

    view_progr = ft.View(
        route="/progr",
        controls=[
            ft.Text(
                "working...", style="headlineSmall"  # "Indeterminate progress bar",
            ),
            ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee"),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=26,
    )

    view_files = ft.View(
        route="/files",
        controls=[
            ft.AppBar(title=ft.Text("progr"), bgcolor="blue"),
            # ft.Text("Files & Images List", style="headlineSmall"),
            ft.Row(
                [
                    ft.ElevatedButton(text="Save", on_click=on_save),
                    ft.ElevatedButton(text="Cancer", on_click=on_cancer),
                ],
                # expand=1
            ),
            ft.Row([file_list, image_view]),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=66,
    )

    view_saved = ft.View(
        route="/saved",
        controls=[
            ft.AppBar(title=ft.Text("Saved"), bgcolor="blue"),
            ft.Text("Files Saved", style="headlineSmall"),
            ft.ElevatedButton(text="Go back", on_click=on_goroot),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=26,
    )

    #######################################################

    def view_pop(e: ft.ViewPopEvent) -> None:
        page.views.pop()
        top_view: ft.View = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
