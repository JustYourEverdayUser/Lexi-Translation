moduledir = python_dir / 'lexi'

configure_file(
  input: 'lexi.in',
  output: 'lexi',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

install_data(
  [
    'main.py',
    'window.py',
    configure_file(input: 'shared.py.in', output: 'shared.py', configuration: conf),
  ],
  install_dir: moduledir,
)