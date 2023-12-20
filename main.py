import PySimpleGUI as sg
import os
import re
import requests

# DEFAULT VALUES FOR GLOBAL VARIABLES
filename = 'Untitled'
file_location = ''
saved_text = ''
version = 'v0.2.0'
font = ['Courier', 10]
theme = 'black'
isStatusBar = True
isWordWrap = False


def make_window():
    global font, theme
    sg.theme(theme)
    menu_def = [['File', ['New', 'Open', 'Save', 'Save as', 'Exit']],
                ['Edit', ['Find', 'Replace']],
                ['Run', ['Run Python']],
                ['About', ['Info', 'Shortcuts', 'Update']]]
    layout = [
        [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 10'),
         sg.Button('', image_filename='options.png', border_width=0,
                   button_color=(sg.theme_background_color(), sg.theme_background_color()), key='-OPTIONS-')],
        [sg.Multiline(expand_x=True, expand_y=True, key='-TEXTBOX-', horizontal_scroll=isWordWrap,
                      enable_events=True, autoscroll=True, sbar_width=2, sbar_arrow_width=2,
                      sbar_background_color=sg.theme_background_color(),
                      sbar_trough_color=sg.theme_slider_color(),
                      sbar_relief=sg.RELIEF_FLAT)],
        [sg.StatusBar('', size=(1, 1), key='-STATUSBAR-', font='Courier 10', relief=sg.RELIEF_SUNKEN)]
    ]
    window = sg.Window(filename + ' - PyPad',
                       layout,
                       icon='icon.ico',
                       resizable=True,
                       use_custom_titlebar=False,
                       finalize=True,
                       font=font,
                       size=(960, 540))
    window.set_min_size((300, 200))
    # KEYBOARD SHORTCUTS
    window.bind("<Control_L><n>", "New")
    window.bind("<Control_L><s>", "Save")
    window.bind("<Control_L><Alt_L><s>", "Save as")
    window.bind("<Control_L><o>", "Open")
    window.bind("<Control_L><r>", "Run Python")
    return window


def make_window_customize():
    global font, theme, isStatusBar, isWordWrap
    sg.theme(theme)
    theme_list = sg.theme_list()
    font_list = sg.Text.fonts_installed_list()
    size_list = list(range(5, 21))
    layout = [
        [sg.Text('Options', justification='center', font=(font[0], font[1]+3, 'bold'), expand_x=True)],
        [sg.HorizontalSeparator()],
        [sg.Text('Choose a theme:', justification='center')],
        [sg.Combo(theme_list, expand_x=True, key='-THEME-', default_value=theme, readonly=True)],
        [sg.Text('Choose a font type:', justification='center')],
        [sg.Combo(font_list, expand_x=True, key='-FONT_TYPE-', default_value=font[0], readonly=True)],
        [sg.Text('Choose a font size:', justification='center')],
        [sg.Slider(range=(5, 20), orientation='horizontal', expand_x=True, key='-FONT_SIZE-', default_value=font[1],
                   relief=sg.RELIEF_FLAT, size=(0, 10))],
        [sg.Checkbox('Enable Status Bar', key='-ENABLE_STATUS-', default=isStatusBar)],
        [sg.Checkbox('Enable WordWrap', key='-ENABLE_WRAP-', default=not isWordWrap)],
        [sg.Button('Apply', key='-APPLY-'),
         sg.Button('Default', key='-DEFAULT-')]
    ]
    window = sg.Window('Customization - PyPad',
                       layout,
                       icon='icon.ico',
                       resizable=False,
                       finalize=True,
                       element_justification='center',
                       font=font
                       )
    window.set_min_size(window.size)
    return window


def update_window(window, content):
    global saved_text, file_location, isStatusBar
    if saved_text == content:
        window.set_title(filename + ' - PyPad')
    else:
        window.set_title(filename + '* - PyPad')
    lines = len(content.split('\n'))
    words = len(re.findall(r'\w+', content))
    chars = len(content)
    if isStatusBar:
        window['-STATUSBAR-'].update(f"Lines: {lines}, Words: {words}, Characters: {chars}", visible=True)
    else:
        window['-STATUSBAR-'].update(f"Lines: {lines}, Words: {words}, Characters: {chars}", visible=False)


def save_as(content):
    global file_location, filename, saved_text
    file_location = sg.popup_get_file('Save as:', keep_on_top=True, save_as=True,
                                      file_types=(('Text Files(.txt)', '*.txt'), ('Python files(.py)', '*.py')))
    if file_location:
        filename = os.path.basename(file_location)
        with open(file_location, 'w') as f:
            f.write(content)
        saved_text = content


def save(content):
    global file_location, saved_text
    if file_location:
        with open(file_location, 'w') as f:
            f.write(content)
            saved_text = content
    else:
        save_as(content)


def open_file():
    global file_location, filename, saved_text
    file_location = sg.popup_get_file('Choose a file:', keep_on_top=True,
                                      file_types=(('Text Files(.txt)', '*.txt'), ('Python files(.py)', '*.py')))
    if file_location:
        filename = os.path.basename(file_location)
        with open(file_location, 'r') as f:
            saved_text = f.read().strip()
            return saved_text


def new_file():
    global file_location, filename, saved_text
    filename = 'Untitled'
    file_location = ''
    saved_text = ''
    return ''


def want_save(content):
    global saved_text
    if saved_text != content and saved_text != '':
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


def check_version():
    global version
    url = 'https://raw.githubusercontent.com/Domino03/PyPad/master/version.txt'
    git_version = requests.get(url).text
    print(version, git_version)
    if version.strip() == git_version.strip():
        sg.popup_no_buttons('You have the latest version!\n',
                            title=''
                            )
    else:
        sg.popup_no_buttons('PyPad is outdated!\n', title='')


def restore_default():
    global font, theme, isStatusBar, isWordWrap
    font = ['Courier', 10]
    theme = 'black'
    isStatusBar = True
    isWordWrap = True


def find(window, replace=False):
    find_text = sg.popup_get_text(title='Find - PyPad', message='Insert Text to Find')
    if find_text:
        text_widget = window['-TEXTBOX-'].Widget
        start = '1.0'
        found = 0
        while True:
            pos = text_widget.search(find_text, start, stopindex='end')
            if not pos:
                break
            found += 1
            end = f'{pos}+{len(find_text)}c'
            text_widget.tag_add('highlight', pos, end)
            text_widget.tag_config('highlight', background='yellow')
            start = f'{pos}+1c'
        if found > 0:
            sg.popup(f"'{find_text}' was found {found} time(s)", title='')
            text_widget.tag_delete('highlight')
        else:
            sg.popup(f"File doesn't contain '{find_text}'", title='')


def main():
    global filename, saved_text, theme, font, isWordWrap, isStatusBar
    window = make_window()
    text = ''
    # PRIMARY WINDOW LOOP
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # FILE MENU
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
        # EDIT MENU
        elif event == 'Find':
            find(window)
        # RUN MENU
        elif event == "Run Python":
            run_python(text)
        # ABOUT MENU
        elif event == 'Info':
            about('info')
        elif event == 'Shortcuts':
            about('shortcuts')
        elif event == 'Update':
            check_version()
        # OPTIONS MENU
        elif event == "-OPTIONS-":
            want_save(text)
            window.close()
            filename = 'Untitled'
            saved_text = ''
            window_c = make_window_customize()
            # OPTIONS WINDOW LOOP
            while True:
                event_c, values_c = window_c.read(timeout=100)
                if event_c == sg.WIN_CLOSED or event_c == 'Exit':
                    window = make_window()
                    break
                elif event_c == '-APPLY-':
                    theme = values_c['-THEME-']
                    font[0] = values_c['-FONT_TYPE-']
                    font[1] = int(values_c['-FONT_SIZE-'])
                    isStatusBar = values_c['-ENABLE_STATUS-']
                    isWordWrap = not values_c['-ENABLE_WRAP-']
                    window_c.close()
                    window_c = make_window_customize()
                elif event_c == '-DEFAULT-':
                    restore_default()
                    window_c.close()
                    window_c = make_window_customize()
        text = values['-TEXTBOX-']
        update_window(window, text)
    window.close()
    exit(0)


if __name__ == '__main__':
    main()