# hryuton_builder.py
"""
HRYUTON.EXE — Final corrected HRYUTON EXE Builder (single-file Python script)
AUTHOR: HRYUSHKA 63 yt

Изменения в этой версии:
- Добавлен селектор языка (RU/EN) — кнопка/выпадающий список русификатора.
- UI-элементы используют строки из STRINGS и обновляются при смене языка.
- Сохранение выбранного языка в конфиг.
- Несколько строк и messagebox'ов локализованы.
- Мелкие правки для стабильности.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
import os
import json
from pathlib import Path
import shutil
import queue
import time
import tempfile
import venv
import platform
import webbrowser

# --- Constants & Config ---
CONFIG_PATH = Path.home() / ".hryuton_config.json"
PROJECT_SAVE_EXT = ".hryproj.json"
DEFAULT_OUTPUT_NAME = "HRYUTON"
AUTHOR = "BY HRYUSHKA 63"

# Localization (RU/EN) - добавлены недостающие ключи
STRINGS = {
    'en': {
        'title': 'HRYUTON EXE Builder',
        'select_script': 'Python script (.py):',
        'browse': 'Browse',
        'output_name': 'Output name:',
        'icon': 'Icon (.ico, optional):',
        'onefile': 'One-file package (--onefile)',
        'windowed': 'Windowed (no console) (--noconsole)',
        'add_files': 'Additional files/folders to include:',
        'add': 'Add',
        'remove': 'Remove',
        'requirements': 'requirements.txt (optional):',
        'check_pyinstaller': 'Check PyInstaller',
        'install_pyinstaller': 'Auto-install PyInstaller',
        'open_dist': 'Open Dist Folder',
        'build': 'Build EXE',
        'cancel_build': 'Cancel Build',
        'build_log': 'Build log',
        'status_ready': 'Ready',
        'use_venv': 'Use isolated venv for build',
        'upx_path': 'UPX path (optional):',
        'hidden_imports': 'Hidden imports (comma-separated):',
        'create_nsis': 'Create NSIS installer after build',
        'language': 'Language',
        'nsis_missing': 'NSIS (makensis) not found. Installer will not be created.',
        'build_started': 'Starting build...',
        'build_success': 'Build finished successfully. Check the dist folder.',
        'build_errors': 'Build finished with errors. See log.',
        'confirm_cancel': 'Are you sure you want to cancel the build?',
        'installing_requirements': 'Installing requirements...',
        'venv_creating': 'Creating virtual environment...',
        'venv_cleanup': 'Cleaning temporary virtual environment...',
        'upx_running': 'Running UPX...',
        'nsis_running': 'Running NSIS to create installer...',
        'theme': 'Theme',
        'light': 'Light',
        'dark': 'Dark',
        'help_nsis': 'Open NSIS download page',
        'help_upx': 'Open UPX download page',
        'save_project': 'Save project',
        'load_project': 'Load project',
        'export_settings': 'Export settings',
        'import_settings': 'Import settings',
        'installer_template': 'Installer template',
        'template_basic': 'Basic',
        'template_license': 'With License page',
        'template_admin': 'Require Admin',
        # added keys
        'options': 'Options',
        'find_upx': 'Find UPX',
        'find_nsis': 'Find NSIS',
        'makensis_label': 'makensis:',
        'license_file': 'License file (for installer):',
        'author': 'Author:',
        'save_project_msg': 'Project saved.',
        'load_project_msg': 'Project loaded.',
        'export_settings_msg': 'Settings exported.',
        'import_settings_msg': 'Settings imported. Restart app to apply.',
        'install_requirements_prompt': "Run 'pip install -r requirements.txt' into the current Python environment before building?",
        'upx_not_found': 'UPX not found in PATH.',
        'nsis_not_found': 'makensis not found in PATH.',
        'select_data': 'Select files or folders to include',
        'upx_title': 'UPX',
        'nsis_title': 'NSIS',
        'save_title': 'Save project',
        'load_title': 'Load project',
        'export_title': 'Export',
        'import_title': 'Import',
        'error': 'Error',
    },
    'ru': {
        'title': 'HRYUTON EXE Builder',
        'select_script': 'Python-скрипт (.py):',
        'browse': 'Обзор',
        'output_name': 'Имя результата:',
        'icon': 'Иконка (.ico, опц.):',
        'onefile': 'В один файл (--onefile)',
        'windowed': 'Без консоли (--noconsole)',
        'add_files': 'Доп. файлы/папки для включения:',
        'add': 'Добавить',
        'remove': 'Удалить',
        'requirements': 'requirements.txt (опц.):',
        'check_pyinstaller': 'Проверить PyInstaller',
        'install_pyinstaller': 'Установить PyInstaller',
        'open_dist': 'Открыть папку dist',
        'build': 'Собрать EXE',
        'cancel_build': 'Отменить сборку',
        'build_log': 'Лог сборки',
        'status_ready': 'Готово',
        'use_venv': 'Собирать в изолированном venv',
        'upx_path': 'Путь к UPX (опц.):',
        'hidden_imports': 'Скрытые импорты (через запятую):',
        'create_nsis': 'Создать NSIS-инсталлятор после сборки',
        'language': 'Язык',
        'nsis_missing': 'NSIS (makensis) не найден. Инсталлятор не будет создан.',
        'build_started': 'Начинаю сборку...',
        'build_success': 'Сборка завершена успешно. Проверьте папку dist.',
        'build_errors': 'Сборка завершена с ошибками. Смотрите лог.',
        'confirm_cancel': 'Вы уверены, что хотите отменить сборку?',
        'installing_requirements': 'Установка зависимостей...',
        'venv_creating': 'Создаю виртуальное окружение...',
        'venv_cleanup': 'Очищаю временный venv...',
        'upx_running': 'Запускаю UPX...',
        'nsis_running': 'Запускаю NSIS для создания инсталлятора...',
        'theme': 'Тема',
        'light': 'Светлая',
        'dark': 'Тёмная',
        'help_nsis': 'Открыть страницу загрузки NSIS',
        'help_upx': 'Открыть страницу загрузки UPX',
        'save_project': 'Сохранить проект',
        'load_project': 'Загрузить проект',
        'export_settings': 'Экспорт настроек',
        'import_settings': 'Импорт настроек',
        'installer_template': 'Шаблон инсталлятора',
        'template_basic': 'Базовый',
        'template_license': 'С лицензией',
        'template_admin': 'Требует права администратора',
        # added keys
        'options': 'Опции',
        'find_upx': 'Найти UPX',
        'find_nsis': 'Найти NSIS',
        'makensis_label': 'makensis:',
        'license_file': 'Файл лицензии (для инсталлятора):',
        'author': 'Автор:',
        'save_project_msg': 'Проект сохранён.',
        'load_project_msg': 'Проект загружен.',
        'export_settings_msg': 'Настройки экспортированы.',
        'import_settings_msg': 'Настройки импортированы. Перезапустите приложение для применения.',
        'install_requirements_prompt': "Выполнить 'pip install -r requirements.txt' в текущем Python окружении перед сборкой?",
        'upx_not_found': 'UPX не найден в PATH.',
        'nsis_not_found': 'makensis не найден в PATH.',
        'select_data': 'Выберите файлы или папки для включения',
        'upx_title': 'UPX',
        'nsis_title': 'NSIS',
        'save_title': 'Сохранить проект',
        'load_title': 'Загрузить проект',
        'export_title': 'Экспорт',
        'import_title': 'Импорт',
        'error': 'Ошибка',
    }
}

# NSIS download and UPX pages (for help)
NSIS_URL = 'https://nsis.sourceforge.io/Download'
UPX_URL = 'https://upx.github.io/'

# --- Helper functions ---
def load_app_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

def save_app_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass

# --- Main App ---
class HryutonBuilderApp:
    def __init__(self, root):
        self.root = root
        self.app_cfg = load_app_config()
        self.lang = self.app_cfg.get('lang', 'ru')
        if self.lang not in STRINGS:
            self.lang = 'ru'
        self.strings = STRINGS.get(self.lang, STRINGS['ru'])
        self.root.title(f"{self.strings['title']} — {AUTHOR}")
        self.root.geometry('1024x760')

        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.build_thread = None

        # Auto-detect makensis and upx
        self.makensis_path = shutil.which('makensis') or self.app_cfg.get('makensis')
        self.upx_path = shutil.which('upx') or self.app_cfg.get('upx')

        # Keep references to widgets that need text updates
        self._widgets = {}
        self.create_ui()
        self.poll_queue()

    def create_ui(self):
        # ttk style
        style = ttk.Style(self.root)
        try:
            if sys.platform.startswith('win'):
                style.theme_use('vista')
            else:
                style.theme_use('clam')
        except Exception:
            pass

        # Top frame: source and options
        top = ttk.Frame(self.root)
        top.pack(fill='x', padx=10, pady=8)

        # Language selector
        ttk.Label(top, text=self.strings['language']).grid(column=0, row=0, sticky='w')
        lang_names = {'ru': 'Русский', 'en': 'English'}
        self.lang_var = tk.StringVar(value=lang_names.get(self.lang, 'Русский'))
        self.lang_combo = ttk.Combobox(top, values=[lang_names['ru'], lang_names['en']], state='readonly', width=10, textvariable=self.lang_var)
        self.lang_combo.grid(column=1, row=0, sticky='w', padx=6)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_lang_change)
        # put spacer
        top.columnconfigure(2, weight=1)

        # Row 1: script selection
        self.lbl_select_script = ttk.Label(top, text=self.strings['select_script'])
        self.lbl_select_script.grid(column=0, row=1, sticky='w', pady=(8,0))
        self.src_entry = ttk.Entry(top)
        self.src_entry.grid(column=1, row=1, sticky='ew', padx=6, pady=(8,0))
        self.btn_browse_source = ttk.Button(top, text=self.strings['browse'], command=self.browse_source)
        self.btn_browse_source.grid(column=2, row=1, padx=(6,0), pady=(8,0))
        top.columnconfigure(1, weight=1)

        # Row 2: output name
        self.lbl_output_name = ttk.Label(top, text=self.strings['output_name'])
        self.lbl_output_name.grid(column=0, row=2, sticky='w', pady=6)
        self.name_entry = ttk.Entry(top)
        self.name_entry.insert(0, DEFAULT_OUTPUT_NAME)
        self.name_entry.grid(column=1, row=2, sticky='ew')

        # Row 3: icon
        self.lbl_icon = ttk.Label(top, text=self.strings['icon'])
        self.lbl_icon.grid(column=0, row=3, sticky='w')
        self.icon_entry = ttk.Entry(top)
        self.icon_entry.grid(column=1, row=3, sticky='ew')
        self.btn_browse_icon = ttk.Button(top, text=self.strings['browse'], command=self.browse_icon)
        self.btn_browse_icon.grid(column=2, row=3)

        # Options frame
        opts = ttk.LabelFrame(self.root, text=self.strings['options'])
        opts.pack(fill='x', padx=10, pady=6)
        self.opts_frame = opts

        self.onefile_var = tk.BooleanVar(value=True)
        self.windowed_var = tk.BooleanVar(value=False)
        self.venv_var = tk.BooleanVar(value=False)
        self.nsis_var = tk.BooleanVar(value=False)

        self.chk_onefile = ttk.Checkbutton(opts, text=self.strings['onefile'], variable=self.onefile_var)
        self.chk_onefile.grid(column=0, row=0, sticky='w', padx=6, pady=4)
        self.chk_windowed = ttk.Checkbutton(opts, text=self.strings['windowed'], variable=self.windowed_var)
        self.chk_windowed.grid(column=1, row=0, sticky='w', padx=6)
        self.chk_venv = ttk.Checkbutton(opts, text=self.strings['use_venv'], variable=self.venv_var)
        self.chk_venv.grid(column=2, row=0, sticky='w', padx=6)
        self.chk_nsis = ttk.Checkbutton(opts, text=self.strings['create_nsis'], variable=self.nsis_var)
        self.chk_nsis.grid(column=3, row=0, sticky='w', padx=6)

        self.lbl_hidden = ttk.Label(opts, text=self.strings['hidden_imports'])
        self.lbl_hidden.grid(column=0, row=1, sticky='w', padx=6, pady=4)
        self.hidden_entry = ttk.Entry(opts)
        self.hidden_entry.grid(column=1, row=1, columnspan=3, sticky='ew', padx=6)
        opts.columnconfigure(1, weight=1)

        self.lbl_upx = ttk.Label(opts, text=self.strings['upx_path'])
        self.lbl_upx.grid(column=0, row=2, sticky='w', padx=6, pady=4)
        self.upx_entry = ttk.Entry(opts)
        if self.upx_path:
            self.upx_entry.insert(0, str(self.upx_path))
        self.upx_entry.grid(column=1, row=2, sticky='ew', padx=6)
        self.btn_find_upx = ttk.Button(opts, text=self.strings['find_upx'], command=self.find_upx)
        self.btn_find_upx.grid(column=2, row=2)
        self.btn_help_upx = ttk.Button(opts, text=self.strings['help_upx'], command=lambda: webbrowser.open(UPX_URL))
        self.btn_help_upx.grid(column=3, row=2)

        self.lbl_makensis = ttk.Label(opts, text=self.strings['makensis_label'])
        self.lbl_makensis.grid(column=0, row=3, sticky='w', padx=6, pady=4)
        self.nsis_entry = ttk.Entry(opts)
        if self.makensis_path:
            self.nsis_entry.insert(0, str(self.makensis_path))
        self.nsis_entry.grid(column=1, row=3, sticky='ew', padx=6)
        self.btn_find_nsis = ttk.Button(opts, text=self.strings['find_nsis'], command=self.find_nsis)
        self.btn_find_nsis.grid(column=2, row=3)
        self.btn_help_nsis = ttk.Button(opts, text=self.strings['help_nsis'], command=lambda: webbrowser.open(NSIS_URL))
        self.btn_help_nsis.grid(column=3, row=3)

        # Data files
        data_frame = ttk.LabelFrame(self.root, text=self.strings['add_files'])
        data_frame.pack(fill='both', padx=10, pady=6)
        self.data_frame = data_frame
        self.data_listbox = tk.Listbox(data_frame, height=5)
        self.data_listbox.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        data_btn_frame = ttk.Frame(data_frame)
        data_btn_frame.pack(side='right', padx=6)
        self.btn_add_data = ttk.Button(data_btn_frame, text=self.strings['add'], command=self.add_data)
        self.btn_add_data.pack(fill='x', pady=4)
        self.btn_remove_data = ttk.Button(data_btn_frame, text=self.strings['remove'], command=self.remove_data)
        self.btn_remove_data.pack(fill='x', pady=4)

        # requirements and license
        misc = ttk.Frame(self.root)
        misc.pack(fill='x', padx=10, pady=6)
        self.lbl_requirements = ttk.Label(misc, text=self.strings['requirements'])
        self.lbl_requirements.grid(column=0, row=0, sticky='w')
        self.req_entry = ttk.Entry(misc)
        self.req_entry.grid(column=1, row=0, sticky='ew', padx=6)
        self.btn_browse_req = ttk.Button(misc, text=self.strings['browse'], command=self.browse_requirements)
        self.btn_browse_req.grid(column=2, row=0)

        self.lbl_license = ttk.Label(misc, text=self.strings['license_file'])
        self.lbl_license.grid(column=0, row=1, sticky='w', pady=6)
        self.lic_entry = ttk.Entry(misc)
        self.lic_entry.grid(column=1, row=1, sticky='ew', padx=6)
        self.btn_browse_license = ttk.Button(misc, text=self.strings['browse'], command=self.browse_license)
        self.btn_browse_license.grid(column=2, row=1)
        misc.columnconfigure(1, weight=1)

        # NSIS template
        tmpl = ttk.Frame(self.root)
        tmpl.pack(fill='x', padx=10, pady=4)
        self.lbl_template = ttk.Label(tmpl, text=self.strings['installer_template'])
        self.lbl_template.grid(column=0, row=0, sticky='w')
        self.template_var = tk.StringVar(value='basic')
        self.rb_template_basic = ttk.Radiobutton(tmpl, text=self.strings['template_basic'], variable=self.template_var, value='basic')
        self.rb_template_basic.grid(column=1, row=0)
        self.rb_template_license = ttk.Radiobutton(tmpl, text=self.strings['template_license'], variable=self.template_var, value='license')
        self.rb_template_license.grid(column=2, row=0)
        self.rb_template_admin = ttk.Radiobutton(tmpl, text=self.strings['template_admin'], variable=self.template_var, value='admin')
        self.rb_template_admin.grid(column=3, row=0)

        # Project buttons
        proj = ttk.Frame(self.root)
        proj.pack(fill='x', padx=10, pady=6)
        self.btn_save_proj = ttk.Button(proj, text=self.strings['save_project'], command=self.save_project)
        self.btn_save_proj.pack(side='left', padx=6)
        self.btn_load_proj = ttk.Button(proj, text=self.strings['load_project'], command=self.load_project)
        self.btn_load_proj.pack(side='left', padx=6)
        self.btn_export = ttk.Button(proj, text=self.strings['export_settings'], command=self.export_settings)
        self.btn_export.pack(side='left', padx=6)
        self.btn_import = ttk.Button(proj, text=self.strings['import_settings'], command=self.import_settings)
        self.btn_import.pack(side='left', padx=6)

        # Build controls
        build = ttk.Frame(self.root)
        build.pack(fill='x', padx=10, pady=6)
        self.build_btn = ttk.Button(build, text=self.strings['build'], command=self.start_build)
        self.build_btn.pack(side='left')
        self.cancel_btn = ttk.Button(build, text=self.strings['cancel_build'], command=self.cancel_build, state='disabled')
        self.cancel_btn.pack(side='left', padx=6)

        # Progress and log
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(fill='both', expand=True, padx=10, pady=6)
        self.progress = ttk.Progressbar(prog_frame, mode='indeterminate')
        self.progress.pack(fill='x')
        log_frame = ttk.LabelFrame(prog_frame, text=self.strings['build_log'])
        log_frame.pack(fill='both', expand=True, pady=6)
        self.log_frame = log_frame
        self.log_text = tk.Text(log_frame, wrap='none')
        self.log_text.pack(fill='both', expand=True)

        # Status & author
        bottom = ttk.Frame(self.root)
        bottom.pack(fill='x', padx=10, pady=6)
        self.status = ttk.Label(bottom, text=self.strings['status_ready'])
        self.status.pack(side='left')
        self.author_label = ttk.Label(bottom, text=f"{self.strings['author']} {AUTHOR}")
        self.author_label.pack(side='right')

        # store widgets mapping for easy update
        self._widgets.update({
            'lbl_select_script': self.lbl_select_script,
            'btn_browse_source': self.btn_browse_source,
            'lbl_output_name': self.lbl_output_name,
            'lbl_icon': self.lbl_icon,
            'btn_browse_icon': self.btn_browse_icon,
            'opts_frame': self.opts_frame,
            'chk_onefile': self.chk_onefile,
            'chk_windowed': self.chk_windowed,
            'chk_venv': self.chk_venv,
            'chk_nsis': self.chk_nsis,
            'lbl_hidden': self.lbl_hidden,
            'lbl_upx': self.lbl_upx,
            'btn_find_upx': self.btn_find_upx,
            'btn_help_upx': self.btn_help_upx,
            'lbl_makensis': self.lbl_makensis,
            'btn_find_nsis': self.btn_find_nsis,
            'btn_help_nsis': self.btn_help_nsis,
            'data_frame': self.data_frame,
            'btn_add_data': self.btn_add_data,
            'btn_remove_data': self.btn_remove_data,
            'lbl_requirements': self.lbl_requirements,
            'btn_browse_req': self.btn_browse_req,
            'lbl_license': self.lbl_license,
            'btn_browse_license': self.btn_browse_license,
            'lbl_template': self.lbl_template,
            'rb_template_basic': self.rb_template_basic,
            'rb_template_license': self.rb_template_license,
            'rb_template_admin': self.rb_template_admin,
            'btn_save_proj': self.btn_save_proj,
            'btn_load_proj': self.btn_load_proj,
            'btn_export': self.btn_export,
            'btn_import': self.btn_import,
            'build_btn': self.build_btn,
            'cancel_btn': self.cancel_btn,
            'log_frame': self.log_frame,
            'status': self.status,
            'author_label': self.author_label,
            'lbl_language': None,  # label for language sits at top static
        })

    # --- UI update / language switching ---
    def on_lang_change(self, event=None):
        val = self.lang_var.get()
        # map displayed name back to code
        mapping = {'Русский': 'ru', 'English': 'en'}
        new_lang = mapping.get(val, 'ru')
        if new_lang == self.lang:
            return
        self.lang = new_lang
        self.strings = STRINGS.get(self.lang, STRINGS['ru'])
        # save preference
        self.app_cfg['lang'] = self.lang
        save_app_config(self.app_cfg)
        # update window title
        try:
            self.root.title(f"{self.strings['title']} — {AUTHOR}")
        except Exception:
            pass
        self.update_ui_texts()

    def update_ui_texts(self):
        s = self.strings
        # update texts for stored widgets
        try:
            self._widgets['lbl_select_script'].config(text=s['select_script'])
            self._widgets['btn_browse_source'].config(text=s['browse'])
            self._widgets['lbl_output_name'].config(text=s['output_name'])
            self._widgets['lbl_icon'].config(text=s['icon'])
            self._widgets['btn_browse_icon'].config(text=s['browse'])
            self._widgets['opts_frame'].config(text=s['options'])
            self._widgets['chk_onefile'].config(text=s['onefile'])
            self._widgets['chk_windowed'].config(text=s['windowed'])
            self._widgets['chk_venv'].config(text=s['use_venv'])
            self._widgets['chk_nsis'].config(text=s['create_nsis'])
            self._widgets['lbl_hidden'].config(text=s['hidden_imports'])
            self._widgets['lbl_upx'].config(text=s['upx_path'])
            self._widgets['btn_find_upx'].config(text=s['find_upx'])
            self._widgets['btn_help_upx'].config(text=s['help_upx'])
            self._widgets['lbl_makensis'].config(text=s['makensis_label'])
            self._widgets['btn_find_nsis'].config(text=s['find_nsis'])
            self._widgets['btn_help_nsis'].config(text=s['help_nsis'])
            self._widgets['data_frame'].config(text=s['add_files'])
            self._widgets['btn_add_data'].config(text=s['add'])
            self._widgets['btn_remove_data'].config(text=s['remove'])
            self._widgets['lbl_requirements'].config(text=s['requirements'])
            self._widgets['btn_browse_req'].config(text=s['browse'])
            self._widgets['lbl_license'].config(text=s['license_file'])
            self._widgets['btn_browse_license'].config(text=s['browse'])
            self._widgets['lbl_template'].config(text=s['installer_template'])
            self._widgets['rb_template_basic'].config(text=s['template_basic'])
            self._widgets['rb_template_license'].config(text=s['template_license'])
            self._widgets['rb_template_admin'].config(text=s['template_admin'])
            self._widgets['btn_save_proj'].config(text=s['save_project'])
            self._widgets['btn_load_proj'].config(text=s['load_project'])
            self._widgets['btn_export'].config(text=s['export_settings'])
            self._widgets['btn_import'].config(text=s['import_settings'])
            self._widgets['build_btn'].config(text=s['build'])
            self._widgets['cancel_btn'].config(text=s['cancel_build'])
            self._widgets['log_frame'].config(text=s['build_log'])
            self._widgets['status'].config(text=s['status_ready'])
            self._widgets['author_label'].config(text=f"{s['author']} {AUTHOR}")
        except Exception:
            # ignore any missing widget updates
            pass

    # --- UI helpers ---
    def browse_source(self):
        p = filedialog.askopenfilename(filetypes=[('Python files', '*.py')])
        if p:
            self.src_entry.delete(0, tk.END)
            self.src_entry.insert(0, p)

    def browse_icon(self):
        p = filedialog.askopenfilename(filetypes=[('ICO files', '*.ico'), ('All files', '*')])
        if p:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, p)

    def add_data(self):
        title = self.strings.get('select_data', 'Select files or folders to include')
        p = filedialog.askopenfilenames(title=title)
        for f in p:
            self.data_listbox.insert(tk.END, f)

    def remove_data(self):
        sel = list(self.data_listbox.curselection())
        for i in reversed(sel):
            self.data_listbox.delete(i)

    def browse_requirements(self):
        p = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All files', '*')])
        if p:
            self.req_entry.delete(0, tk.END)
            self.req_entry.insert(0, p)

    def browse_license(self):
        p = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All files', '*')])
        if p:
            self.lic_entry.delete(0, tk.END)
            self.lic_entry.insert(0, p)

    def find_upx(self):
        path = shutil.which('upx')
        if path:
            self.upx_entry.delete(0, tk.END)
            self.upx_entry.insert(0, path)
            messagebox.showinfo(self.strings.get('upx_title', 'UPX'), f'Found UPX: {path}')
        else:
            messagebox.showwarning(self.strings.get('upx_title', 'UPX'), self.strings.get('upx_not_found', 'UPX not found in PATH.'))

    def find_nsis(self):
        path = shutil.which('makensis')
        if path:
            self.nsis_entry.delete(0, tk.END)
            self.nsis_entry.insert(0, path)
            messagebox.showinfo(self.strings.get('nsis_title', 'NSIS'), f'Found makensis: {path}')
        else:
            messagebox.showwarning(self.strings.get('nsis_title', 'NSIS'), self.strings.get('nsis_not_found', 'makensis not found in PATH.'))

    # --- Project / settings ---
    def save_project(self):
        p = filedialog.asksaveasfilename(defaultextension=PROJECT_SAVE_EXT, filetypes=[('HRYUTON project', PROJECT_SAVE_EXT)])
        if not p:
            return
        proj = self.collect_options()
        Path(p).write_text(json.dumps(proj, ensure_ascii=False, indent=2), encoding='utf-8')
        messagebox.showinfo(self.strings.get('save_title', 'Save project'), self.strings.get('save_project_msg', 'Project saved.'))

    def load_project(self):
        p = filedialog.askopenfilename(filetypes=[('HRYUTON project', PROJECT_SAVE_EXT)])
        if not p:
            return
        try:
            proj = json.loads(Path(p).read_text(encoding='utf-8'))
            self.apply_options(proj)
            messagebox.showinfo(self.strings.get('load_title', 'Load project'), self.strings.get('load_project_msg', 'Project loaded.'))
        except Exception as e:
            messagebox.showerror(self.strings.get('error', 'Error'), str(e))

    def export_settings(self):
        p = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '.json')])
        if not p:
            return
        save_app_config(self.app_cfg)
        try:
            shutil.copy(CONFIG_PATH, p)
            messagebox.showinfo(self.strings.get('export_title', 'Export'), self.strings.get('export_settings_msg', 'Settings exported.'))
        except Exception as e:
            messagebox.showerror(self.strings.get('error', 'Error'), str(e))

    def import_settings(self):
        p = filedialog.askopenfilename(filetypes=[('JSON', '.json')])
        if not p:
            return
        try:
            cfg = json.loads(Path(p).read_text(encoding='utf-8'))
            self.app_cfg.update(cfg)
            save_app_config(self.app_cfg)
            messagebox.showinfo(self.strings.get('import_title', 'Import'), self.strings.get('import_settings_msg', 'Settings imported. Restart app to apply.'))
        except Exception as e:
            messagebox.showerror(self.strings.get('error', 'Error'), str(e))

    def collect_options(self):
        return {
            'src': self.src_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'icon': self.icon_entry.get().strip(),
            'data': list(self.data_listbox.get(0, tk.END)),
            'onefile': self.onefile_var.get(),
            'windowed': self.windowed_var.get(),
            'venv': self.venv_var.get(),
            'nsis': self.nsis_var.get(),
            'hidden': self.hidden_entry.get().strip(),
            'upx': self.upx_entry.get().strip(),
            'makensis': self.nsis_entry.get().strip(),
            'req': self.req_entry.get().strip(),
            'license': self.lic_entry.get().strip(),
            'template': self.template_var.get(),
        }

    def apply_options(self, proj):
        if not proj:
            return
        self.src_entry.delete(0, tk.END); self.src_entry.insert(0, proj.get('src',''))
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, proj.get('name',''))
        self.icon_entry.delete(0, tk.END); self.icon_entry.insert(0, proj.get('icon',''))
        self.data_listbox.delete(0, tk.END)
        for d in proj.get('data',[]): self.data_listbox.insert(tk.END, d)
        self.onefile_var.set(proj.get('onefile', True))
        self.windowed_var.set(proj.get('windowed', False))
        self.venv_var.set(proj.get('venv', False))
        self.nsis_var.set(proj.get('nsis', False))
        self.hidden_entry.delete(0, tk.END); self.hidden_entry.insert(0, proj.get('hidden',''))
        self.upx_entry.delete(0, tk.END); self.upx_entry.insert(0, proj.get('upx',''))
        self.nsis_entry.delete(0, tk.END); self.nsis_entry.insert(0, proj.get('makensis',''))
        self.req_entry.delete(0, tk.END); self.req_entry.insert(0, proj.get('req',''))
        self.lic_entry.delete(0, tk.END); self.lic_entry.insert(0, proj.get('license',''))
        self.template_var.set(proj.get('template','basic'))

    # --- Build logic ---
    def start_build(self):
        opts = self.collect_options()
        src = opts['src']
        if not src or not Path(src).exists():
            messagebox.showerror(self.strings.get('error', 'Error'), self.strings.get('select_script', 'Please choose a valid Python source file (.py).'))
            return
        self.build_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.progress.start(10)
        self.log_text.delete('1.0', tk.END)
        self.stop_event.clear()
        self.append_log(self.strings['build_started'])
        self.build_thread = threading.Thread(target=self.run_build, args=(opts,))
        self.build_thread.start()

    def cancel_build(self):
        if messagebox.askyesno(self.strings.get('cancel_build', 'Cancel'), self.strings['confirm_cancel']):
            self.stop_event.set()
            self.append_log('Cancel requested')

    def run_build(self, opts):
        try:
            src = Path(opts['src']).resolve()
            name = opts['name'] or DEFAULT_OUTPUT_NAME
            icon = opts['icon'] or None
            data = opts['data']
            onefile = opts['onefile']
            windowed = opts['windowed']
            req = opts['req']
            use_venv = opts['venv']
            upx_path = opts['upx']
            hidden = opts['hidden']
            makensis_cfg = opts['makensis']
            create_nsis = opts['nsis']
            license_file = opts['license']
            template = opts.get('template', 'basic')

            workdir = Path.cwd()
            distdir = workdir / 'dist'

            # Clean previous
            try:
                spec_file = workdir / f"{name}.spec"
                if spec_file.exists(): spec_file.unlink()
                old_dist_file = distdir / (name + ('.exe' if sys.platform.startswith('win') else ''))
                old_dist_folder = distdir / name
                if old_dist_file.exists(): old_dist_file.unlink()
                if old_dist_folder.exists(): shutil.rmtree(old_dist_folder, ignore_errors=True)
            except Exception as e:
                self.append_log(f'Warning cleaning: {e}')

            def build_using(python_exe):
                cmd = [python_exe, '-m', 'PyInstaller']
                if onefile: cmd.append('--onefile')
                if windowed: cmd.append('--noconsole')
                if hidden:
                    for hi in [h.strip() for h in hidden.split(',') if h.strip()]:
                        cmd += ['--hidden-import', hi]
                cmd += ['--name', name]
                if icon:
                    cmd += ['--icon', str(icon)]
                for item in data:
                    src_item = Path(item)
                    if not src_item.exists():
                        self.append_log(f'Warning: data not found: {item}')
                        continue
                    sep = os.pathsep
                    add_arg = f"{str(src_item)}{sep}{src_item.name}"
                    cmd += ['--add-data', add_arg]
                cmd.append(str(src))
                # Log only a short summary of the command to keep readability
                self.append_log('PyInstaller command: ' + ' '.join(cmd[:6]) + ' ...')
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                while True:
                    if self.stop_event.is_set():
                        try:
                            proc.terminate()
                            self.append_log('Terminated PyInstaller')
                        except Exception:
                            pass
                        return 1
                    line = proc.stdout.readline()
                    if not line:
                        if proc.poll() is not None:
                            break
                        time.sleep(0.1)
                        continue
                    self.append_log(line.rstrip())
                return proc.poll()

            # venv path
            if use_venv:
                self.append_log(self.strings['venv_creating'])
                tmpdir = Path(tempfile.mkdtemp(prefix='hryuton_venv_'))
                venv_dir = tmpdir / 'venv'
                venv.EnvBuilder(with_pip=True).create(str(venv_dir))
                py_bin = venv_dir / ('Scripts' if os.name == 'nt' else 'bin') / ('python.exe' if os.name == 'nt' else 'python')
                py_exe = str(py_bin)
                try:
                    subprocess.run([py_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], capture_output=True, text=True)
                    subprocess.run([py_exe, '-m', 'pip', 'install', 'pyinstaller'], capture_output=True, text=True)
                    if req and Path(req).exists():
                        self.append_log(self.strings['installing_requirements'])
                        subprocess.run([py_exe, '-m', 'pip', 'install', '-r', req], capture_output=True, text=True)
                    ret = build_using(py_exe)
                finally:
                    try:
                        self.append_log(self.strings['venv_cleanup'])
                        shutil.rmtree(tmpdir, ignore_errors=True)
                    except Exception as e:
                        self.append_log(f'Failed cleanup venv: {e}')
            else:
                if req and Path(req).exists():
                    if messagebox.askyesno(self.strings.get('installing_requirements', 'Install'), self.strings.get('install_requirements_prompt', "")):
                        self.append_log(self.strings['installing_requirements'])
                        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req], capture_output=True, text=True)
                ret = build_using(sys.executable)

            if ret == 0:
                self.append_log(self.strings['build_success'])
                # UPX
                final_upx = upx_path or shutil.which('upx')
                if final_upx:
                    exe_path = None
                    onefile_exe = distdir / (name + ('.exe' if sys.platform.startswith('win') else ''))
                    if onefile_exe.exists():
                        exe_path = onefile_exe
                    else:
                        alt = distdir / name / (name + ('.exe' if sys.platform.startswith('win') else ''))
                        if alt.exists():
                            exe_path = alt
                    if exe_path:
                        self.append_log(self.strings['upx_running'])
                        try:
                            subprocess.run([final_upx, str(exe_path)], capture_output=True, text=True)
                        except Exception as e:
                            self.append_log(f'UPX error: {e}')

                # NSIS
                if create_nsis:
                    makensis_exe = makensis_cfg or shutil.which('makensis')
                    if not makensis_exe:
                        self.append_log(self.strings['nsis_missing'])
                    else:
                        try:
                            self.append_log(self.strings['nsis_running'])
                            installer = self.create_nsis_installer(name, makensis_exe, template, license_file)
                            self.append_log(f'Installer created: {installer}')
                        except Exception as e:
                            self.append_log(f'NSIS error: {e}')

                # notify on main thread via queue
                self.append_log(self.strings['build_success'])
            else:
                self.append_log(self.strings['build_errors'])

        except Exception as e:
            self.append_log(f'Error: {e}')
        finally:
            # UI updates must happen on main thread
            def finish():
                self.progress.stop()
                self.build_btn.config(state='normal')
                self.cancel_btn.config(state='disabled')
            try:
                self.root.after(0, finish)
            except Exception:
                finish()

    def create_nsis_installer(self, app_name, makensis_exe, template, license_file):
        dist = Path.cwd() / 'dist'
        exe_name = app_name + '.exe'
        exe_path = dist / exe_name
        if not exe_path.exists():
            alt = dist / app_name / exe_name
            if alt.exists():
                exe_path = alt
            else:
                raise FileNotFoundError('Built exe not found for NSIS packaging')

        # Build NSIS script using f-strings; escape backslashes where needed
        if template == 'basic':
            nsis = f'''OutFile "{app_name}_installer.exe"
InstallDir "$PROGRAMFILES\\{app_name}"
Page directory
Page instfiles
Section "Install"
  SetOutPath "$INSTDIR"
  File "{exe_path}"
  CreateShortCut "$DESKTOP\\{app_name}.lnk" "$INSTDIR\\{exe_name}"
SectionEnd
'''
        elif template == 'license':
            lic = license_file or ''
            nsis = f'''OutFile "{app_name}_installer.exe"
InstallDir "$PROGRAMFILES\\{app_name}"
!insertmacro MUI_PAGE_LICENSE "{lic}"
Page directory
Page instfiles
Section "Install"
  SetOutPath "$INSTDIR"
  File "{exe_path}"
  CreateShortCut "$DESKTOP\\{app_name}.lnk" "$INSTDIR\\{exe_name}"
SectionEnd
'''
        elif template == 'admin':
            nsis = f'''OutFile "{app_name}_installer.exe"
RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\{app_name}"
Page directory
Page instfiles
Section "Install"
  SetOutPath "$INSTDIR"
  File "{exe_path}"
  CreateShortCut "$DESKTOP\\{app_name}.lnk" "$INSTDIR\\{exe_name}"
SectionEnd
'''
        else:
            nsis = ''

        header = f'; Generated by HRYUTON ({AUTHOR})\n'
        nsis = header + nsis

        tmp = Path(tempfile.mkdtemp(prefix='hryuton_nsis_'))
        script_path = tmp / 'installer.nsi'
        script_path.write_text(nsis, encoding='utf-8')
        proc = subprocess.run([makensis_exe, str(script_path)], capture_output=True, text=True, cwd=tmp)
        self.append_log((proc.stdout or '') + (proc.stderr or ''))
        # Find resulting exe
        installer = None
        for f in tmp.iterdir():
            if f.suffix.lower() == '.exe':
                installer = f
                break
        if not installer:
            raise FileNotFoundError('NSIS did not produce installer')
        dest = Path.cwd() / 'dist'
        dest.mkdir(exist_ok=True)
        final = dest / installer.name
        shutil.move(str(installer), str(final))
        # cleanup
        try:
            script_path.unlink()
        except Exception:
            pass
        return final

    # --- Logging / UI update ---
    def append_log(self, text):
        # Put log messages into the GUI queue from background threads
        try:
            self.queue.put(str(text))
        except Exception:
            pass

    def poll_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                # Insert with explicit newline
                self.log_text.insert(tk.END, str(item) + '\n')
                self.log_text.see(tk.END)
                self.status.config(text=str(item)[:80])
        except queue.Empty:
            pass
        # Schedule the next poll
        self.root.after(200, self.poll_queue)

# --- Run ---
if __name__ == '__main__':
    root = tk.Tk()
    # Apply a ttk theme where available
    try:
        style = ttk.Style(root)
        if sys.platform.startswith('win'):
            style.theme_use('vista')
        else:
            style.theme_use('clam')
    except Exception:
        pass
    app = HryutonBuilderApp(root)
    # Ensure UI reflects chosen language on start
    app.update_ui_texts()
    root.mainloop()
