blueprints = custom_target(
    'blueprints',
    input: files(
        'gtk/window.blp',
        'gtk/ui/PairRow.blp',
        'gtk/ui/LexiconRow.blp'
    ),
    output: '.',
    command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources(
    'Lexi',
    configure_file(
        input: 'Lexi.gresource.xml.in',
        output: 'Lexi.gresource.xml',
        configuration: conf
    ),
    gresource_bundle: true,
    install: true,
    install_dir: pkgdatadir,
    dependencies: blueprints
)

desktop_file = i18n.merge_file(
    input: configure_file(
        input: 'io.github.dzheremi2.Lexi.desktop.in',
        output: app_id + '.desktop.in',
        configuration: conf
    ),
    output: app_id + '.desktop',
    type: 'desktop',
    po_dir: '../po',
    install: true,
    install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
    test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
    input: configure_file(
        input: 'io.github.dzheremi2.Lexi.metainfo.xml.in',
        output: app_id + '.metainfo.xml.in',
        configuration: conf,
    ),
    output: app_id + '.metainfo.xml',
    po_dir: '../po',
    install: true,
    install_dir: join_paths(get_option('datadir'), 'metainfo'),
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
    test(
        'Validate appstream file',
        appstreamcli,
        args: ['validate', '--no-net', '--explain', appstream_file],
        workdir: meson.current_build_dir(),
    )
endif

install_data(
  configure_file(
    input: 'io.github.dzheremi2.Lexi.gschema.xml.in',
    output: app_id + '.gschema.xml',
    configuration: conf,
  ),
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas'),
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test(
    'Validate schema file',
    compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()],
  )
endif

subdir('icons')