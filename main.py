import PySimpleGUI as sg
import os
import re

filename = 'Untitled'
file_location = ''
saved_text = ''
version = 'v0.1.0'


def make_window(theme):
    sg.theme(theme)
    menu_def = [['File', ['New', 'Open', 'Save', 'Save as', 'Exit']],
                ['Edit', ['Undo', 'Redo']],
                ['Options', ['Theme']],
                ['Run', ['Run Python']],
                ['About', ['Info', 'Shortcuts']]]

    layout = [
        [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 10', tearoff=True)],
        [sg.Multiline(size=(150, 45), expand_x=True, expand_y=True, key='-TEXTBOX-', enable_events=True)],
        [sg.StatusBar('', size=(1, 1), key='-STATUSBAR-')]
    ]
    window = sg.Window(filename + ' - PyPad',
                       layout,
                       icon='icon.ico',
                       right_click_menu_tearoff=True,
                       resizable=True,
                       use_custom_titlebar=False,
                       finalize=True)
    window.set_min_size(window.size)

    # KEYBOARD SHORTCUTS
    window.bind("<Control_L><n>", "New")
    window.bind("<Control_L><s>", "Save")
    window.bind("<Control_L><Alt_L><s>", "Save as")
    window.bind("<Control_L><o>", "Open")
    window.bind("<Control_L><r>", "Run Python")
    return window


def update_window(window, content):
    global saved_text
    global file_location
    if saved_text == content:
        window.set_title(filename + ' - PyPad')
    else:
        window.set_title(filename + '* - PyPad')
    lines = len(content.split('\n'))
    words = len(re.findall(r'\w+', content))
    chars = len(content)
    window['-STATUSBAR-'].update(f"Lines: {lines}, Words: {words}, Characters: {chars}")


def save_as(content):
    global file_location
    global filename
    global saved_text
    file_location = sg.popup_get_file('Save as:', keep_on_top=True, save_as=True,
                                      file_types=(('Text Files(.txt)', '*.txt'), ('Python files(.py)', '*.py')))
    if file_location:
        filename = os.path.basename(file_location)
        with open(file_location, 'w') as f:
            f.write(content)
        saved_text = content


def save(content):
    global file_location
    global saved_text
    if file_location:
        with open(file_location, 'w') as f:
            f.write(content)
            saved_text = content
    else:
        save_as(content)


def open_file():
    global file_location
    global filename
    global saved_text
    file_location = sg.popup_get_file('Choose a file:', keep_on_top=True,
                                      file_types=(('Text Files(.txt)', '*.txt'), ('Python files(.py)', '*.py')))
    if file_location:
        filename = os.path.basename(file_location)
        with open(file_location, 'r') as f:
            saved_text = f.read()
            return saved_text


def new_file():
    global file_location
    global filename
    global saved_text
    filename = 'Untitled'
    file_location = ''
    saved_text = ''
    return ''


def want_save(content):
    global saved_text
    if saved_text != content:
        if sg.popup_yes_no('Do you want to save your current file?') == 'Yes':
            save(content)


def run_python(content):
    global file_location
    if file_location and file_location.endswith(".py"):
        save(content)
        os.system(f"python {file_location}")


def about(page):
    global version
    if page == 'info':
        sg.popup_no_buttons(
            '         PyPad\n'
            'Created by Tudorie Ionut\n'
            f'    Version : {version}',
            title='',
            icon='icon.ico',
            font='Courier 10'
        )
    elif page == 'shortcuts':
        sg.popup_no_buttons(
            '   Keyboard Shortcuts\n'
            'New             CTRL + N\n'
            'Save            CTRL + S\n'
            'Save as   CTRL + ALT + S\n'
            'Open            CTRL + O\n'
            'Run             CTRL + R\n',
            title='',
            icon='icon.ico',
            font='Courier 10',
        )


def update():
    global version



def main():
    global filename
    global saved_text
    window = make_window(sg.theme())
    text = ''
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # FILE CONTEXT MENU
        elif event == 'Open':
            want_save(text)
            window['-TEXTBOX-'].update(value=open_file())
        elif event == 'Save as':
            save_as(text)
        elif event == 'Save':
            save(text)
        elif event == 'New':
            want_save(text)
            window['-TEXTBOX-'].update(value=new_file())
        # EDIT CONTEXT MENU
        elif event == "Run Python":
            run_python(text)
        # ABOUT
        elif event == 'Info':
            about('info')
        elif event == 'Shortcuts':
            about('shortcuts')
        elif event == 'Update':
            update()
        text = values['-TEXTBOX-']
        update_window(window, text)
    window.close()
    exit(0)


if __name__ == '__main__':
    sg.theme('black')
    main()
