moduledir = python_dir / 'lexi'

configure_file(
  input: 'lexi.in',
  output: 'lexi',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
)

# install_data(
#   [
#     'application_delegate.py',
#     'main.py',
#     'window.py',
#     'preferences.py',
#     'details_dialog.py',
#     'game.py',
#     'game_cover.py',
#     configure_file(input: 'shared.py.in', output: 'shared.py', configuration: conf),
#   ],
#   install_dir: moduledir,
# )