import PySimpleGUI as sg
import re
import requests
import json
import os
import subprocess

# DEFAULT VALUES FOR GLOBAL VARIABLES
filename = ['Untitled']
saved_text = ['']
file_location = ['']
openTabs = 1
currentTab = 0
font = ['Courier', 10]
theme = 'Black'
isStatusBar = True
isWordWrap = False
rememberLastOpen = False
zoom = 1
recent_files = []
# FIXED VALUES
version = 'v0.4.0'
file_types = (('Text Files', '*.txt'),
              ('Python Files', '*.py'),
              ('JSON Files', '*.json'),
              ('All Files', '*.*'))
# CUSTOM THEMES
sg.LOOK_AND_FEEL_TABLE['PyPadDark'] = {'BACKGROUND': '#07090f',
                                       'TEXT': '#FFFFFF',
                                       'INPUT': '#2a2b2e',
                                       'TEXT_INPUT': '#DDDDDD',
                                       'SCROLL': '#2a2b2e',
                                       'BUTTON': ('#EEEEEE', '#1e1f22'),
                                       'PROGRESS': ('#EEEEEE', '#1e1f22'),
                                       'BORDER': 0,
                                       'SLIDER_DEPTH': 1,
                                       'PROGRESS_DEPTH': 0}
sg.LOOK_AND_FEEL_TABLE['PyPadLight'] = {'BACKGROUND': '',
                                        'TEXT': '',
                                        'INPUT': '',
                                        'TEXT_INPUT': '',
                                        'SCROLL': '',
                                        'BUTTON': ('', ''),
                                        'PROGRESS': ('', ''),
                                        'BORDER': 1,
                                        'SLIDER_DEPTH': 0,
                                        'PROGRESS_DEPTH': 0}


def load_config():
    global file_location, font, theme, isStatusBar, isWordWrap, zoom, recent_files, rememberLastOpen, openTabs
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    else:
        config = {"file_location": [""],
                  "openTabs": 1,
                  "font": ["Courier", 10],
                  "theme": "Black",
                  "isStatusBar": True,
                  "isWordWrap": False,
                  "rememberLastOpen": True,
                  "zoom": 1.0,
                  "recent_files": []
                  }
    rememberLastOpen = config['rememberLastOpen']
    if rememberLastOpen:
        file_location = config['file_location']
        openTabs = config['openTabs']
    font = config['font']
    theme = config['theme']
    isStatusBar = config['isStatusBar']
    isWordWrap = config['isWordWrap']
    zoom = config['zoom']
    recent_files = config['recent_files']


def save_config():
    global file_location, font, theme, isStatusBar, isWordWrap, zoom, recent_files, rememberLastOpen, openTabs
    config = {'file_location': file_location,
              'openTabs': openTabs,
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


def reopen_last(window):
    global file_location, saved_text, filename, currentTab
    filename = [''] * openTabs
    saved_text = [''] * openTabs
    window['-NEW-TAB-'].update(visible=False)
    for i in range(openTabs):
        if file_location[i]:
            filename[i] = os.path.basename(file_location[i])
            with open(file_location[i], 'r') as f:
                saved_text[i] = f.read().strip()
        else:
            filename[i] = 'Untitled'
            saved_text[i] = ''
        window[f"-TAB{i}-"].update(visible=True)
    window['-TEXTBOX-'].update(value=saved_text[currentTab])
    window['-NEW-TAB-'].update(visible=True)


def make_window():
    global font, theme, recent_files, rememberLastOpen
    sg.theme(theme)
    menu_def = [['File', ['New', 'Open', 'Save', 'Save as', 'Recent', 'Exit']],
                ['Edit', ['Find', 'Replace']],
                ['About', ['Info', 'Shortcuts', 'Update']],
                ['Zoom', ['Zoom in', 'Zoom out', 'Reset']]]
    layout = [
        [  # TAB BAR
            sg.Col([[sg.Button('', pad=(0, 0), key='-TAB0-NAME-'), sg.Button('X', pad=(0, 0), key='-CLOSE-TAB0-')]],
                   pad=(2, 0), key='-TAB0-', visible=True),
            sg.Col([[sg.Button('', pad=(0, 0), key='-TAB1-NAME-'), sg.Button('X', pad=(0, 0), key='-CLOSE-TAB1-')]],
                   pad=(2, 0), key='-TAB1-', visible=False),
            sg.Col([[sg.Button('', pad=(0, 0), key='-TAB2-NAME-'), sg.Button('X', pad=(0, 0), key='-CLOSE-TAB2-')]],
                   pad=(2, 0), key='-TAB2-', visible=False),
            sg.Col([[sg.Button('', pad=(0, 0), key='-TAB3-NAME-'), sg.Button('X', pad=(0, 0), key='-CLOSE-TAB3-')]],
                   pad=(2, 0), key='-TAB3-', visible=False),
            sg.Col([[sg.Button('', pad=(0, 0), key='-TAB4-NAME-'), sg.Button('X', pad=(0, 0), key='-CLOSE-TAB4-')]],
                   pad=(2, 0), key='-TAB4-', visible=False),
            sg.Button('+', key='-NEW-TAB-', pad=(0, 0), visible=True)
        ],
        [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 10', pad=(0, 1),
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
                      pad=(1, 0))],
        [sg.StatusBar('', size=(1, 1), key='-STATUSBAR-', font='Courier 10', relief=sg.RELIEF_SUNKEN)]
    ]
    window = sg.Window('PyPad',
                       layout,
                       icon='./resources/icon.ico',
                       resizable=True,
                       use_custom_titlebar=False,
                       finalize=True,
                       font=font,
                       size=(960, 540),
                       margins=(5, 0))
    window.set_min_size((480, 270))
    # KEYBOARD SHORTCUTS
    window.bind("<Control-n>", "New")
    window.bind("<Control-s>", "Save")
    window.bind("<Control-Alt-s>", "Save as")
    window.bind("<Control-o>", "Open")
    window.bind("<Control-r>", "-RUN-")
    window.bind("<Control-f>", "Find")
    window.bind("<Control-h>", "Replace")
    window.bind("<Control-Up>", 'Zoom in')
    window.bind("<Control-Down>", "Zoom out")
    window.bind("<Control-0>", "Reset")
    if rememberLastOpen:
        reopen_last(window)
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
    global font, theme, recent_files, saved_text, file_location, filename, currentTab
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
                file_location[currentTab] = values['-RECENT-']
                window.close()
                filename[currentTab] = os.path.basename(file_location[currentTab])
                with open(file_location[currentTab], 'r') as f:
                    saved_text[currentTab] = f.read().strip()
                    main_window['-TEXTBOX-'].update(saved_text[currentTab])
            break
    main_window.enable()
    main_window.bring_to_front()


def update_window(window, content):
    global saved_text, file_location, isStatusBar, recent_files, zoom, openTabs, currentTab, font
    for i in range(openTabs):
        if saved_text[i] == content[i]:
            window[f'-TAB{i}-NAME-'].update(filename[i])
        else:
            window[f'-TAB{i}-NAME-'].update(filename[i]+'*')
        if i == currentTab:
            window[f'-TAB{i}-NAME-'].update(disabled=True)
        else:
            window[f'-TAB{i}-NAME-'].update(disabled=False)
    if openTabs == 1:
        window['-CLOSE-TAB0-'].update(visible=False)
    else:
        window['-CLOSE-TAB0-'].update(visible=True)
    lines = len(content[currentTab].split('\n'))
    words = len(re.findall(r'\w+', content[currentTab]))
    chars = len(content[currentTab])
    if str(file_location[currentTab]).endswith('.py'):
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
    global file_location, currentTab
    if file_location[currentTab] not in recent_files:
        recent_files.insert(0, file_location[currentTab])
        if len(recent_files) > 5:
            recent_files.pop()


def save_as(content):
    global file_location, filename, saved_text, recent_files, file_types, currentTab
    old_location = file_location[currentTab]
    file_location[currentTab] = sg.popup_get_file('Save as:', keep_on_top=True, save_as=True,
                                                  file_types=file_types)
    if file_location[currentTab]:
        save_to_recent()
        filename[currentTab] = os.path.basename(file_location[currentTab])
        with open(file_location[currentTab], 'w') as f:
            f.write(content[currentTab])
        saved_text[currentTab] = content[currentTab]
    else:
        file_location[currentTab] = old_location


def save(content):
    global file_location, saved_text, currentTab
    if file_location[currentTab]:
        with open(file_location[currentTab], 'w') as f:
            f.write(content[currentTab])
            saved_text[currentTab] = content[currentTab]
    else:
        save_as(content)


def open_file():
    global file_location, filename, saved_text, recent_files, file_types, currentTab
    old_location = file_location[currentTab]
    file_location[currentTab] = sg.popup_get_file('Choose a file:', keep_on_top=True,
                                                  file_types=file_types)
    if file_location[currentTab]:
        save_to_recent()
        filename[currentTab] = os.path.basename(file_location[currentTab])
        with open(file_location[currentTab], 'r') as f:
            saved_text[currentTab] = f.read().strip()
            return saved_text[currentTab]
    else:
        file_location[currentTab] = old_location


def new_file():
    global file_location, filename, saved_text, currentTab
    filename[currentTab] = 'Untitled'
    file_location[currentTab] = ''
    saved_text[currentTab] = ''
    return ''


def want_save(content):
    global saved_text
    if saved_text[currentTab] != content[currentTab] and content[currentTab] != '':
        if sg.popup_yes_no('Do you want to save your current file?', title='') == 'Yes':
            save(content)


def run_python(content):
    global file_location, currentTab
    if file_location[currentTab] and file_location[currentTab].endswith(".py"):
        save(content)
        subprocess.Popen(f'python "{file_location[currentTab]}"')


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


def new_tab(window, content):
    global currentTab, openTabs, filename, file_location, saved_text
    window['-NEW-TAB-'].update(visible=False)
    openTabs += 1
    switch_tab(window, openTabs-1, content)
    filename.append('Untitled')
    file_location.append('')
    saved_text.append('')
    window[f'-TAB{currentTab}-'].update(visible=True)
    if openTabs < 5:
        window['-NEW-TAB-'].update(visible=True)


def switch_tab(window, tab_nr, content):
    global filename, currentTab
    currentTab = int(tab_nr)
    window['-TEXTBOX-'].update(value=content[currentTab])


def close_tab(window, s_tab_nr, content):
    global currentTab, openTabs, filename, file_location, saved_text
    tab_nr = int(s_tab_nr)
    openTabs -= 1
    filename.pop(tab_nr)
    file_location.pop(tab_nr)
    saved_text.pop(tab_nr)
    if currentTab == tab_nr:
        switch_tab(window, openTabs-1, content)
    elif tab_nr < currentTab:
        currentTab -= 1
    window[f'-TAB{openTabs}-'].update(visible=False)
    window['-NEW-TAB-'].update(visible=True)


def main():
    global filename, saved_text, theme, font, isWordWrap, isStatusBar, recent_files, zoom, rememberLastOpen, openTabs, \
        currentTab
    load_config()
    window = make_window()
    text = list(saved_text)
    text.append('')
    # PRIMARY WINDOW LOOP
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # FILE MENU
        elif event == '-NEW-TAB-' and openTabs <= 5:
            new_tab(window, text)
            text.append('')
        elif (event in ['-CLOSE-TAB0-', '-CLOSE-TAB1-', '-CLOSE-TAB2-', '-CLOSE-TAB3-', '-CLOSE-TAB4-']
              and openTabs != 1):
            want_save(text)
            close_tab(window, event[-2], text)
            text.pop(int(event[-2]))
            window['-TEXTBOX-'].update(value=text[currentTab])
        elif event in ['-TAB0-NAME-', '-TAB1-NAME-', '-TAB2-NAME-', '-TAB3-NAME-', '-TAB4-NAME-']:
            switch_tab(window, event[4], text)
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
            window_c = make_window_customize()
            # OPTIONS WINDOW LOOP
            while True:
                event_c, values_c = window_c.read(timeout=100)
                if event_c == sg.WIN_CLOSED or event_c == '-CLOSE-':
                    window_c.close()
                    window = make_window()
                    window['-TEXTBOX-'].update(value=reopen_last(window))
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
        text[currentTab] = values['-TEXTBOX-']
        update_window(window, text)
    window.close()
    save_config()


if __name__ == '__main__':
    main()
