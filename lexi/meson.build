pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'lexi'

configure_file(
  input: 'lexi.in',
  output: 'lexi',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

install_subdir('ui', install_dir: moduledir, exclude_files: [
  'widgets.pyi',
  'Preferences.pyi'
])
# install_subdir('utils', install_dir: moduledir)

install_data(
  [
    'main.py',
    'window.py',
    'enums.py',
    configure_file(input: 'shared.py.in', output: 'shared.py', configuration: conf),
  ],
  install_dir: moduledir,
)