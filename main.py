import PySimpleGUI as sg
import os
import re
import requests
import json

# DEFAULT VALUES FOR GLOBAL VARIABLES
filename = 'Untitled'
saved_text = ''
file_location = ''
font = ['Courier', 10]
theme = 'Black'
isStatusBar = True
isWordWrap = False
rememberLastOpen = True
zoom = 1
recent_files = []
# FIXED VALUES
version = 'v0.3.0'
file_types = (('Text Files', '*.txt'),
              ('Python Files', '*.py'),
              ('JSON Files', '*.json'),
              ('All Files', '*.*'))


def load_config():
    global file_location, font, theme, isStatusBar, isWordWrap, zoom, recent_files, rememberLastOpen
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    else:
        config = {"file_location": "",
                  "font": ["Courier", 10],
                  "theme": "Black",
                  "isStatusBar": True,
                  "isWordWrap": False,
                  "rememberLastOpen": True,
                  "zoom": 1.0,
                  "recent_files": []
                  }
    file_location = config['file_location']
    font = config['font']
    theme = config['theme']
    isStatusBar = config['isStatusBar']
    isWordWrap = config['isWordWrap']
    rememberLastOpen = config['rememberLastOpen']
    zoom = config['zoom']
    recent_files = config['recent_files']


load_config()


def save_config():
    global file_location, font, theme, isStatusBar, isWordWrap, zoom, recent_files, rememberLastOpen
    config = {'file_location': file_location,
              'font': font,
              'theme': theme,
              'isStatusBar': isStatusBar,
              'isWordWrap': isWordWrap,
              'rememberLastOpen': rememberLastOpen,
              'zoom': zoom,
              'recent_files': recent_files
              }
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)


def reopen_last():
    global file_location, rememberLastOpen, saved_text, filename
    if rememberLastOpen and file_location:
        filename = os.path.basename(file_location)
        with open(file_location, 'r') as f:
            saved_text = f.read().strip()
            return saved_text
    else:
        return ''


def make_window():
    global font, theme, recent_files
    sg.theme(theme)
    menu_def = [['File', ['New', 'Open', 'Save', 'Save as', 'Recent', 'Exit']],
                ['Edit', ['Find', 'Replace']],
                ['About', ['Info', 'Shortcuts', 'Update']],
                ['Zoom', ['Zoom in', 'Zoom out', 'Reset']]]
    layout = [
        [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 10', pad=(0, 0),
                          bar_background_color=sg.theme_background_color(),
                          bar_text_color=sg.theme_text_color()),
         sg.Col([[sg.Button('', image_filename='./resources/run.png', border_width=0, pad=(5, 0),
                            button_color=(sg.theme_background_color(), sg.theme_background_color()), key='-RUN-',
                            tooltip='Run Python', visible=True)]], pad=(0, 0)),
         sg.Button('', image_filename='./resources/options.png', border_width=0, pad=(5, 0),
                   button_color=(sg.theme_background_color(), sg.theme_background_color()), key='-OPTIONS-',
                   tooltip='Options')],
        [sg.Multiline(expand_x=True, expand_y=True, key='-TEXTBOX-', horizontal_scroll=isWordWrap,
                      enable_events=True, autoscroll=True, sbar_width=2, sbar_arrow_width=2,
                      sbar_background_color=sg.theme_background_color(),
                      sbar_trough_color=sg.theme_slider_color(),
                      sbar_relief=sg.RELIEF_FLAT,
                      pad=(0, 3))],
        [sg.StatusBar('', size=(1, 1), key='-STATUSBAR-', font='Courier 10', relief=sg.RELIEF_SUNKEN)]
    ]
    window = sg.Window(filename + ' - PyPad',
                       layout,
                       icon='./resources/icon.ico',
                       resizable=True,
                       use_custom_titlebar=False,
                       finalize=True,
                       font=font,
                       size=(960, 540),
                       margins=(3, 3))
    window.set_min_size((480, 270))
    # KEYBOARD SHORTCUTS
    window.bind("<Control-n>", "New")
    window.bind("<Control-s>", "Save")
    window.bind("<Control-Alt-<s>", "Save as")
    window.bind("<Control-o>", "Open")
    window.bind("<Control-r>", "-RUN-")
    window.bind("<Control-f>", "Find")
    window.bind("<Control-h>", "Replace")
    window.bind("<Control-Up>", 'Zoom in')
    window.bind("<Control-Down>", "Zoom out")
    window.bind("<Control-0>", "Reset")
    window['-TEXTBOX-'].update(value=reopen_last())
    window['-TEXTBOX-'].update(font=(font[0], int(font[1] * zoom)))
    return window


def make_window_customize():
    global font, theme, isStatusBar, isWordWrap, rememberLastOpen
    sg.theme(theme)
    theme_list = sg.theme_list()
    font_list = sg.Text.fonts_installed_list()
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
        [sg.Checkbox('Remember last open file', key='-REMEMBER-', default=rememberLastOpen)],
        [sg.Checkbox('Enable Status Bar', key='-ENABLE_STATUS-', default=isStatusBar)],
        [sg.Checkbox('Enable WordWrap', key='-ENABLE_WRAP-', default=not isWordWrap)],
        [sg.HorizontalSeparator()],
        [sg.Button('Apply', key='-APPLY-'),
         sg.Button('Default', key='-DEFAULT-')],
        [sg.Button('Close', key='-CLOSE-')]
    ]
    window = sg.Window('Customization - PyPad',
                       layout,
                       icon='resources/icon.ico',
                       resizable=False,
                       finalize=True,
                       element_justification='center',
                       font=font
                       )
    window.set_min_size(window.size)
    return window


def recent(main_window):
    global font, theme, recent_files, saved_text, file_location, filename
    if not recent_files:
        sg.popup_no_buttons('No recent files!', no_titlebar=True, auto_close=True, auto_close_duration=1)
        return
    main_window.disable()
    sg.theme(theme)
    layout = [
        [sg.Text('Choose a recent file!')],
        [sg.Combo(recent_files, key='-RECENT-', readonly=True)],
        [sg.Button('Choose', key='-CHOOSE-'),
         sg.Button('Cancel', key='-CANCEL-')]
    ]

    window = sg.Window(title='',
                       layout=layout,
                       icon='./resources/icon.ico',
                       resizable=False,
                       finalize=True,
                       element_justification='center',
                       font=font)

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == '-CANCEL-':
            window.close()
            break
        elif event == '-CHOOSE-':
            if values['-RECENT-']:
                file_location = values['-RECENT-']
                window.close()
                filename = os.path.basename(file_location)
                with open(file_location, 'r') as f:
                    saved_text = f.read().strip()
                    main_window['-TEXTBOX-'].update(saved_text)

            break
    main_window.enable()
    main_window.bring_to_front()


def update_window(window, content):
    global saved_text, file_location, isStatusBar, recent_files, zoom
    if saved_text == content:
        window.set_title(filename + ' - PyPad')
    else:
        window.set_title(filename + '* - PyPad')
    lines = len(content.split('\n'))
    words = len(re.findall(r'\w+', content))
    chars = len(content)
    if str(file_location).endswith('.py'):
        window['-RUN-'].update(visible=True)
    else:
        window['-RUN-'].update(visible=False)
    if isStatusBar:
        window['-STATUSBAR-'].update(f"Lines: {lines} | Words: {words} | Characters: {chars} | Zoom: {int(zoom*100)}%",
                                     visible=True)
    else:
        window['-STATUSBAR-'].update(f"Lines: {lines} | Words: {words} | Characters: {chars} | Zoom: {int(zoom*100)}%",
                                     visible=False)


def save_to_recent():
    global file_location
    if file_location not in recent_files:
        recent_files.insert(0, file_location)
        if len(recent_files) > 5:
            recent_files.pop()


def save_as(content):
    global file_location, filename, saved_text, recent_files, file_types
    old_location = file_location
    file_location = sg.popup_get_file('Save as:', keep_on_top=True, save_as=True,
                                      file_types=file_types)
    if file_location:
        save_to_recent()
        filename = os.path.basename(file_location)
        with open(file_location, 'w') as f:
            f.write(content)
        saved_text = content
    else:
        file_location = old_location


def save(content):
    global file_location, saved_text
    if file_location:
        with open(file_location, 'w') as f:
            f.write(content)
            saved_text = content
    else:
        save_as(content)


def open_file():
    global file_location, filename, saved_text, recent_files, file_types
    old_location = file_location
    file_location = sg.popup_get_file('Choose a file:', keep_on_top=True,
                                      file_types=file_types)
    if file_location:
        save_to_recent()
        filename = os.path.basename(file_location)
        with open(file_location, 'r') as f:
            saved_text = f.read().strip()
            return saved_text
    else:
        file_location = old_location


def new_file():
    global file_location, filename, saved_text
    filename = 'Untitled'
    file_location = ''
    saved_text = ''
    return ''


def want_save(content):
    global saved_text
    if saved_text != content and content != '':
        if sg.popup_yes_no('Do you want to save your current file?', title='') == 'Yes':
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
            icon='./resources/icon.ico',
            font='Courier 10'
        )
    elif page == 'shortcuts':
        sg.popup_no_buttons(
            '   Keyboard Shortcuts\n'
            'New             CTRL + N\n'
            'Save            CTRL + S\n'
            'Save as   CTRL + ALT + S\n'
            'Open            CTRL + O\n'
            'Run             CTRL + R\n'
            'Find            CTRL + F\n'
            'Replace         CTRL + H\n',
            title='',
            icon='./resources/icon.ico',
            font='Courier 10',
        )


def check_version():
    global version
    url = 'https://raw.githubusercontent.com/Domino03/PyPad/master/version.txt'
    git_version = requests.get(url).text
    print(version, git_version)
    if version.strip() == git_version.strip():
        sg.popup_no_buttons('You have the latest version!\n',
                            title='',
                            icon='./resources/icon.ico'
                            )
    else:
        sg.popup_no_buttons('PyPad is outdated!\n',
                            title='',
                            icon='./resources/icon.ico')


def restore_default():
    global font, theme, isStatusBar, isWordWrap, rememberLastOpen
    font = ['Courier', 10]
    theme = 'Black'
    isStatusBar = True
    isWordWrap = True
    rememberLastOpen = True


def find(window, replace=False, content=''):
    window['-TEXTBOX-'].update(disabled=True)
    find_text = sg.popup_get_text(title='Find - PyPad', message='Insert Text to Find', no_titlebar=True)
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
            text_widget.tag_config('highlight', background='yellow', foreground='black')
            start = f'{pos}+{len(find_text)}c'
        if found > 0:
            if not replace:
                sg.popup(f"'{find_text}' was found {found} time(s)",
                         title='',
                         icon='./resources/icon.ico')
            else:
                replace_text = sg.popup_get_text(f"{find_text}' was found {found} time(s)\n"
                                                 f"Choose word to replace it with:",
                                                 title='',
                                                 no_titlebar=True)
                if replace_text:
                    content = content.replace(find_text, replace_text)
                    window['-TEXTBOX-'].update(value=content)
            text_widget.tag_delete('highlight')
        else:
            sg.popup_no_buttons(f"File doesn't contain '{find_text}'", no_titlebar=True, auto_close=True,
                                auto_close_duration=1)
    window['-TEXTBOX-'].update(disabled=False)


def main():
    global filename, saved_text, theme, font, isWordWrap, isStatusBar, recent_files, zoom, rememberLastOpen
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
        elif event == 'Recent':
            want_save(text)
            recent(window)
        # EDIT MENU
        elif event == 'Find':
            find(window)
        elif event == 'Replace':
            find(window, replace=True, content=values['-TEXTBOX-'])
        # ABOUT MENU
        elif event == 'Info':
            about('info')
        elif event == 'Shortcuts':
            about('shortcuts')
        elif event == 'Update':
            check_version()
        # ZOOM MENU
        elif event == 'Zoom in':
            zoom += 0.25
            window['-TEXTBOX-'].update(font=(font[0], int(font[1]*zoom)))
        elif event == 'Zoom out':
            if zoom > 0.25:
                zoom -= 0.25
            window['-TEXTBOX-'].update(font=(font[0], int(font[1]*zoom)))
        elif event == 'Reset':
            zoom = 1
            window['-TEXTBOX-'].update(font=(font[0], int(font[1] * zoom)))
        # RUN BUTTON
        elif event == "-RUN-":
            run_python(text)
        # OPTIONS BUTTON
        elif event == "-OPTIONS-":
            want_save(text)
            window.close()
            save_config()
            filename = 'Untitled'
            saved_text = ''
            window_c = make_window_customize()
            # OPTIONS WINDOW LOOP
            while True:
                event_c, values_c = window_c.read(timeout=100)
                if event_c == sg.WIN_CLOSED or event_c == '-CLOSE-':
                    window_c.close()
                    load_config()
                    window = make_window()
                    break
                elif event_c == '-APPLY-':
                    theme = values_c['-THEME-']
                    font[0] = values_c['-FONT_TYPE-']
                    font[1] = int(values_c['-FONT_SIZE-'])
                    isStatusBar = values_c['-ENABLE_STATUS-']
                    isWordWrap = not values_c['-ENABLE_WRAP-']
                    rememberLastOpen = values_c['-REMEMBER-']
                    window_c.close()
                    window_c = make_window_customize()
                elif event_c == '-DEFAULT-':
                    restore_default()
                    window_c.close()
                    window_c = make_window_customize()
        text = values['-TEXTBOX-']
        update_window(window, text)
    window.close()
    save_config()


if __name__ == '__main__':
    main()
