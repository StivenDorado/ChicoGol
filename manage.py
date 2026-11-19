#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # Algunas terminales administradas bloquean la lectura de HKCU\Console.
    # Django solo usa esta consulta para decidir si colorea la salida.
    from django.core.management import color
    color.vt_codes_enabled_in_windows_registry = lambda: False
    color.supports_color = lambda *args, **kwargs: False
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
