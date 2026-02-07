# Procedure Suite — gitingest (curated)

Generated: `2026-02-06T18:22:21-08:00`
Git: `updates_2_5_26` @ `0b55a13`

## What this file is
- A **token-budget friendly** snapshot of the repo **structure** + a curated set of **important files**.
- Intended for LLM/context ingestion; excludes large artifacts (models, datasets, caches).

## Exclusions (high level)
- Directories: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, __pycache__, build, coverage, data, dist, distilled, node_modules, proc_suite.egg-info, reports, validation_results, venv`
- File types: `.bin`, `.db`, `.gif`, `.jpeg`, `.jpg`, `.map`, `.onnx`, `.parquet`, `.pdf`, `.pickle`, `.pkl`, `.png`, `.pt`, `.pth`, `.pyc`, `.pyo`, `.tar.gz`, `.webp`, `.xls`, `.xlsx`, `.zip`

## Repo tree (pruned)
```
- Procedure_suite/
  - .claude/
    - .claude/commands/
      - .claude/commands/phi-redactor.md
      - .claude/commands/registry-data-prep.md
    - .claude/.DS_Store
    - .claude/settings.local.json
  - .cursor/
  - .github/
    - .github/workflows/
      - .github/workflows/ci.yml
  - .venv_pdf/
    - .venv_pdf/bin/
      - .venv_pdf/bin/activate
      - .venv_pdf/bin/activate.csh
      - .venv_pdf/bin/activate.fish
      - .venv_pdf/bin/Activate.ps1
      - .venv_pdf/bin/pip
      - .venv_pdf/bin/pip3
      - .venv_pdf/bin/pip3.12
      - .venv_pdf/bin/python
      - .venv_pdf/bin/python3
      - .venv_pdf/bin/python3.12
    - .venv_pdf/include/
      - .venv_pdf/include/python3.12/
    - .venv_pdf/lib/
      - .venv_pdf/lib/python3.12/
        - .venv_pdf/lib/python3.12/site-packages/
          - .venv_pdf/lib/python3.12/site-packages/pip/
            - .venv_pdf/lib/python3.12/site-packages/pip/_internal/
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/autocompletion.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/base_command.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/cmdoptions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/command_context.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/main.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/main_parser.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/parser.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/progress_bars.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/req_command.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/spinners.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cli/status_codes.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/cache.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/check.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/completion.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/configuration.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/debug.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/download.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/freeze.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/hash.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/help.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/index.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/inspect.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/install.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/list.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/search.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/show.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/uninstall.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/commands/wheel.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/base.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/installed.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/sdist.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/distributions/wheel.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/index/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/index/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/index/collector.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/index/package_finder.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/index/sources.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/locations/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/locations/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/locations/_distutils.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/locations/_sysconfig.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/locations/base.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/importlib/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/importlib/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_compat.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_dists.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_envs.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/_json.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/base.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/metadata/pkg_resources.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/candidate.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/direct_url.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/format_control.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/index.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/installation_report.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/link.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/scheme.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/search_scope.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/selection_prefs.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/target_python.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/models/wheel.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/auth.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/cache.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/download.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/lazy_wheel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/session.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/utils.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/network/xmlrpc.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/install/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/install/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/install/editable_legacy.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/install/wheel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/check.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/freeze.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/operations/prepare.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/constructors.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/req_file.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/req_install.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/req_set.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/req/req_uninstall.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/legacy/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/legacy/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/legacy/resolver.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/base.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/candidates.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/factory.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/provider.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/reporter.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/requirements.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/resolver.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/resolution/base.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/_jaraco_text.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/_log.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/appdirs.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/compat.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/compatibility_tags.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/datetime.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/deprecation.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/direct_url_helpers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/egg_link.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/encoding.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/entrypoints.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/filesystem.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/filetypes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/glibc.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/hashes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/logging.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/misc.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/models.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/packaging.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/setuptools_build.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/subprocess.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/temp_dir.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/unpacking.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/urls.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/virtualenv.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/utils/wheel.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/bazaar.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/git.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/mercurial.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/subversion.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_internal/vcs/versioncontrol.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/__init__.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/build_env.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/cache.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/configuration.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/exceptions.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/main.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/pyproject.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/self_outdated_check.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_internal/wheel_builder.py
            - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/file_cache.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/redis_cache.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/_cmd.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/adapter.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/cache.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/controller.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/filewrapper.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/heuristics.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/serialize.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/cachecontrol/wrapper.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/__main__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/cacert.pem
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/core.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/certifi/py.typed
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/cli/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/cli/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/cli/chardetect.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/metadata/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/metadata/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/metadata/languages.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/big5freq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/big5prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/chardistribution.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/charsetgroupprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/charsetprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/codingstatemachine.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/codingstatemachinedict.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/cp949prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/enums.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/escprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/escsm.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/eucjpprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/euckrfreq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/euckrprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/euctwfreq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/euctwprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/gb2312freq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/gb2312prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/hebrewprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/jisfreq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/johabfreq.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/johabprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/jpcntx.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langbulgarianmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langgreekmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langhebrewmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langhungarianmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langrussianmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langthaimodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/langturkishmodel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/latin1prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/macromanprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/mbcharsetprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/mbcsgroupprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/mbcssm.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/resultdict.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/sbcharsetprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/sbcsgroupprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/sjisprober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/universaldetector.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/utf1632prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/utf8prober.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/chardet/version.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/ansi_test.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/ansitowin32_test.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/initialise_test.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/isatty_test.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/utils.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/tests/winterm_test.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/ansi.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/ansitowin32.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/initialise.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/win32.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/colorama/winterm.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/compat.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/database.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/index.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/locators.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/manifest.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/markers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/metadata.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/resources.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/scripts.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/t32.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/t64-arm.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/t64.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/util.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/version.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/w32.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/w64-arm.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/w64.exe
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distlib/wheel.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distro/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distro/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distro/__main__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distro/distro.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/distro/py.typed
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/codec.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/compat.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/core.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/idnadata.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/intranges.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/package_data.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/idna/uts46data.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/msgpack/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/msgpack/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/msgpack/exceptions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/msgpack/ext.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/__about__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/_manylinux.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/_musllinux.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/_structures.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/markers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/requirements.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/specifiers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/tags.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/utils.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/packaging/version.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pkg_resources/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/__main__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/android.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/api.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/macos.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/unix.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/version.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/platformdirs/windows.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/filters/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/filters/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/_mapping.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/bbcode.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/groff.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/html.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/img.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/irc.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/latex.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/other.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/pangomarkup.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/rtf.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/svg.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/terminal.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/terminal256.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/_mapping.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/python.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/styles/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/styles/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/__main__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/cmdline.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/console.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/filter.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/formatter.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/lexer.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/modeline.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/plugin.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/regexopt.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/scanner.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/sphinxext.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/style.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/token.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/unistring.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pygments/util.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/diagram/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/diagram/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/actions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/common.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/core.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/exceptions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/helpers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/results.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/testing.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/unicode.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyparsing/util.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_compat.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_impl.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/__version__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/_internal_utils.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/adapters.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/api.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/auth.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/certs.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/compat.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/cookies.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/exceptions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/help.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/hooks.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/models.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/packages.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/sessions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/status_codes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/structures.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/requests/utils.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/compat/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/compat/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/compat/collections_abc.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/providers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/reporters.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/resolvers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/resolvelib/structs.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/__main__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_cell_widths.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_emoji_codes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_emoji_replace.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_export_format.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_extension.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_fileno.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_inspect.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_log_render.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_loop.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_null_file.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_palettes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_pick.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_ratio.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_spinners.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_stack.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_timer.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_win32_console.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_windows.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_windows_renderer.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/_wrap.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/abc.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/align.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/ansi.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/bar.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/box.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/cells.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/color.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/color_triplet.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/columns.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/console.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/constrain.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/containers.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/control.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/default_styles.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/diagnose.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/emoji.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/errors.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/file_proxy.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/filesize.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/highlighter.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/json.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/jupyter.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/layout.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/live.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/live_render.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/logging.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/markup.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/measure.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/padding.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/pager.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/palette.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/panel.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/pretty.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/progress.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/progress_bar.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/prompt.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/protocol.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/region.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/repr.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/rule.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/scope.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/screen.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/segment.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/spinner.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/status.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/style.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/styled.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/syntax.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/table.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/terminal_theme.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/text.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/theme.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/themes.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/traceback.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/rich/tree.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/_asyncio.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/_utils.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/after.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/before.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/before_sleep.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/nap.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/py.typed
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/retry.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/stop.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/tornadoweb.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tenacity/wait.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/_parser.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/_re.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/_types.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/tomli/py.typed
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/_api.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/_macos.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/_openssl.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/_ssl_constants.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/_windows.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/truststore/py.typed
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/__init__.py
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/bindings.py
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/low_level.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_appengine_environ.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/appengine.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/ntlmpool.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/pyopenssl.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/securetransport.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/socks.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/__init__.py
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/makefile.py
                    - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/weakref_finalize.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/six.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/__init__.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/connection.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/proxy.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/queue.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/request.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/response.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssl_.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssl_match_hostname.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssltransport.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/timeout.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/url.py
                  - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/util/wait.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/_collections.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/_version.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/connection.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/connectionpool.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/exceptions.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/fields.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/filepost.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/poolmanager.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/request.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/urllib3/response.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/__init__.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/labels.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/mklabels.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/tests.py
                - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/webencodings/x_user_defined.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/__init__.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/six.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/typing_extensions.py
              - .venv_pdf/lib/python3.12/site-packages/pip/_vendor/vendor.txt
            - .venv_pdf/lib/python3.12/site-packages/pip/__init__.py
            - .venv_pdf/lib/python3.12/site-packages/pip/__main__.py
            - .venv_pdf/lib/python3.12/site-packages/pip/__pip-runner__.py
            - .venv_pdf/lib/python3.12/site-packages/pip/py.typed
          - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/AUTHORS.txt
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/entry_points.txt
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/INSTALLER
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/LICENSE.txt
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/METADATA
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/RECORD
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/REQUESTED
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/top_level.txt
            - .venv_pdf/lib/python3.12/site-packages/pip-24.0.dist-info/WHEEL
    - .venv_pdf/pyvenv.cfg
  - .vscode/
    - .vscode/settings.json
  - alembic/
    - alembic/versions/
      - alembic/versions/a1b2c3d4e5f6_add_phi_vault_tables.py
      - alembic/versions/b4c5d6e7f8a9_add_review_status_and_feedback_fields.py
      - alembic/versions/c1d2e3f4a5b6_add_registry_runs_table.py
    - alembic/env.py
  - artifacts/
    - artifacts/granular_ner_model/
      - artifacts/granular_ner_model/checkpoint-1500/
        - artifacts/granular_ner_model/checkpoint-1500/config.json
        - artifacts/granular_ner_model/checkpoint-1500/model.safetensors
        - artifacts/granular_ner_model/checkpoint-1500/special_tokens_map.json
        - artifacts/granular_ner_model/checkpoint-1500/tokenizer.json
        - artifacts/granular_ner_model/checkpoint-1500/tokenizer_config.json
        - artifacts/granular_ner_model/checkpoint-1500/trainer_state.json
        - artifacts/granular_ner_model/checkpoint-1500/vocab.txt
      - artifacts/granular_ner_model/checkpoint-1880/
        - artifacts/granular_ner_model/checkpoint-1880/config.json
        - artifacts/granular_ner_model/checkpoint-1880/model.safetensors
        - artifacts/granular_ner_model/checkpoint-1880/special_tokens_map.json
        - artifacts/granular_ner_model/checkpoint-1880/tokenizer_config.json
        - artifacts/granular_ner_model/checkpoint-1880/vocab.txt
      - artifacts/granular_ner_model/config.json
      - artifacts/granular_ner_model/eval_metrics.json
      - artifacts/granular_ner_model/label_map.json
      - artifacts/granular_ner_model/model.safetensors
      - artifacts/granular_ner_model/special_tokens_map.json
      - artifacts/granular_ner_model/tokenizer_config.json
      - artifacts/granular_ner_model/vocab.txt
    - artifacts/phi_distilbert_ner/
      - artifacts/phi_distilbert_ner/checkpoint-1090/
        - artifacts/phi_distilbert_ner/checkpoint-1090/config.json
        - artifacts/phi_distilbert_ner/checkpoint-1090/model.safetensors
        - artifacts/phi_distilbert_ner/checkpoint-1090/special_tokens_map.json
        - artifacts/phi_distilbert_ner/checkpoint-1090/tokenizer.json
        - artifacts/phi_distilbert_ner/checkpoint-1090/tokenizer_config.json
        - artifacts/phi_distilbert_ner/checkpoint-1090/trainer_state.json
        - artifacts/phi_distilbert_ner/checkpoint-1090/vocab.txt
      - artifacts/phi_distilbert_ner/checkpoint-200/
        - artifacts/phi_distilbert_ner/checkpoint-200/config.json
        - artifacts/phi_distilbert_ner/checkpoint-200/model.safetensors
        - artifacts/phi_distilbert_ner/checkpoint-200/special_tokens_map.json
        - artifacts/phi_distilbert_ner/checkpoint-200/tokenizer.json
        - artifacts/phi_distilbert_ner/checkpoint-200/tokenizer_config.json
        - artifacts/phi_distilbert_ner/checkpoint-200/trainer_state.json
        - artifacts/phi_distilbert_ner/checkpoint-200/vocab.txt
      - artifacts/phi_distilbert_ner/audit_gold_report.json
      - artifacts/phi_distilbert_ner/audit_report.json
      - artifacts/phi_distilbert_ner/config.json
      - artifacts/phi_distilbert_ner/eval_metrics.json
      - artifacts/phi_distilbert_ner/label_map.json
      - artifacts/phi_distilbert_ner/model.safetensors
      - artifacts/phi_distilbert_ner/special_tokens_map.json
      - artifacts/phi_distilbert_ner/tokenizer.json
      - artifacts/phi_distilbert_ner/tokenizer_config.json
      - artifacts/phi_distilbert_ner/vocab.txt
    - artifacts/phi_distilbert_ner_mps/
      - artifacts/phi_distilbert_ner_mps/label_map.json
    - artifacts/registry_biomedbert_ner/
      - artifacts/registry_biomedbert_ner/label_map.json
    - artifacts/registry_biomedbert_ner_v2/
      - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/config.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/model.safetensors
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/special_tokens_map.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/tokenizer.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/tokenizer_config.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/trainer_state.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1500/vocab.txt
      - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/config.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/model.safetensors
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/special_tokens_map.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/tokenizer_config.json
        - artifacts/registry_biomedbert_ner_v2/checkpoint-1880/vocab.txt
      - artifacts/registry_biomedbert_ner_v2/config.json
      - artifacts/registry_biomedbert_ner_v2/eval_metrics.json
      - artifacts/registry_biomedbert_ner_v2/label_map.json
      - artifacts/registry_biomedbert_ner_v2/model.safetensors
      - artifacts/registry_biomedbert_ner_v2/special_tokens_map.json
      - artifacts/registry_biomedbert_ner_v2/tokenizer_config.json
      - artifacts/registry_biomedbert_ner_v2/vocab.txt
    - artifacts/registry_roberta_large_ner_onnx_quantized/
      - artifacts/registry_roberta_large_ner_onnx_quantized/added_tokens.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/config.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/merges.txt
      - artifacts/registry_roberta_large_ner_onnx_quantized/ort_config.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/special_tokens_map.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/tokenizer.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/tokenizer_config.json
      - artifacts/registry_roberta_large_ner_onnx_quantized/vocab.json
    - artifacts/.DS_Store
    - artifacts/redactions.jsonl
  - cms_rvu_tools/
    - cms_rvu_tools/cms_rvus_2025_ip.csv
    - cms_rvu_tools/IP_Registry_Enhanced_v2.json
    - cms_rvu_tools/local_rvu_updater.py
    - cms_rvu_tools/README.md
    - cms_rvu_tools/rvu_fetcher.py
  - config/
    - config/__init__.py
    - config/settings.py
  - configs/
    - configs/coding/
      - configs/coding/__init__.py
      - configs/coding/ip_cpt_map.yaml
      - configs/coding/ncci_edits.yaml
      - configs/coding/payer_overrides.yaml
    - configs/lex/
      - configs/lex/__init__.py
      - configs/lex/airway.topology.yaml
      - configs/lex/devices.lex.yaml
      - configs/lex/procedures.lex.yaml
    - configs/prompts/
      - configs/prompts/phase1_coder_prompt.txt
    - configs/report_templates/
      - configs/report_templates/awake_foi.j2
      - configs/report_templates/awake_foi.yaml
      - configs/report_templates/bal.j2
      - configs/report_templates/bal.json
      - configs/report_templates/bal_variant.j2
      - configs/report_templates/bal_variant.yaml
      - configs/report_templates/blvr_discharge_instructions.j2
      - configs/report_templates/blvr_discharge_instructions.yaml
      - configs/report_templates/blvr_post_procedure_protocol.j2
      - configs/report_templates/blvr_post_procedure_protocol.yaml
      - configs/report_templates/blvr_valve_placement.j2
      - configs/report_templates/blvr_valve_placement.yaml
      - configs/report_templates/blvr_valve_removal_exchange.j2
      - configs/report_templates/blvr_valve_removal_exchange.yaml
      - configs/report_templates/bpf_endobronchial_sealant.j2
      - configs/report_templates/bpf_endobronchial_sealant.yaml
      - configs/report_templates/bpf_localization_occlusion.j2
      - configs/report_templates/bpf_localization_occlusion.yaml
      - configs/report_templates/bpf_valve_air_leak.j2
      - configs/report_templates/bpf_valve_air_leak.yaml
      - configs/report_templates/bronchial_brushings.j2
      - configs/report_templates/bronchial_brushings.yaml
      - configs/report_templates/bronchial_washing.j2
      - configs/report_templates/bronchial_washing.yaml
      - configs/report_templates/cbct_augmented_bronchoscopy.j2
      - configs/report_templates/cbct_augmented_bronchoscopy.yaml
      - configs/report_templates/cbct_cact_fusion.j2
      - configs/report_templates/cbct_cact_fusion.yaml
      - configs/report_templates/chest_tube.j2
      - configs/report_templates/chest_tube.yaml
      - configs/report_templates/chest_tube_discharge.j2
      - configs/report_templates/chest_tube_discharge.yaml
      - configs/report_templates/cryo_extraction_mucus.j2
      - configs/report_templates/cryo_extraction_mucus.yaml
      - configs/report_templates/dlt_placement.j2
      - configs/report_templates/dlt_placement.yaml
      - configs/report_templates/dye_marker_placement.j2
      - configs/report_templates/dye_marker_placement.yaml
      - configs/report_templates/ebus_19g_fnb.j2
      - configs/report_templates/ebus_19g_fnb.yaml
      - configs/report_templates/ebus_ifb.j2
      - configs/report_templates/ebus_ifb.yaml
      - configs/report_templates/ebus_tbna.j2
      - configs/report_templates/ebus_tbna.yaml
      - configs/report_templates/emn_bronchoscopy.j2
      - configs/report_templates/emn_bronchoscopy.yaml
      - configs/report_templates/endobronchial_biopsy.j2
      - configs/report_templates/endobronchial_biopsy.yaml
      - configs/report_templates/endobronchial_blocker.j2
      - configs/report_templates/endobronchial_blocker.yaml
      - configs/report_templates/endobronchial_cryoablation.j2
      - configs/report_templates/endobronchial_cryoablation.yaml
      - configs/report_templates/endobronchial_hemostasis.j2
      - configs/report_templates/endobronchial_hemostasis.yaml
      - configs/report_templates/eusb.j2
      - configs/report_templates/eusb.yaml
      - configs/report_templates/fiducial_marker_placement.j2
      - configs/report_templates/fiducial_marker_placement.yaml
      - configs/report_templates/foreign_body_removal.j2
      - configs/report_templates/foreign_body_removal.yaml
      - configs/report_templates/ion_registration_complete.j2
      - configs/report_templates/ion_registration_complete.yaml
      - configs/report_templates/ion_registration_drift.j2
      - configs/report_templates/ion_registration_drift.yaml
      - configs/report_templates/ion_registration_partial.j2
      - configs/report_templates/ion_registration_partial.yaml
      - configs/report_templates/ip_general_bronchoscopy_shell.j2
      - configs/report_templates/ip_general_bronchoscopy_shell.json
      - configs/report_templates/ip_or_main_oper_report_shell.j2
      - configs/report_templates/ip_or_main_oper_report_shell.json
      - configs/report_templates/ip_pre_anesthesia_assessment.j2
      - configs/report_templates/ip_pre_anesthesia_assessment.json
      - configs/report_templates/paracentesis.j2
      - configs/report_templates/paracentesis.yaml
      - configs/report_templates/pdt_debridement.j2
      - configs/report_templates/pdt_debridement.yaml
      - configs/report_templates/pdt_light.j2
      - configs/report_templates/pdt_light.yaml
      - configs/report_templates/peg_discharge.j2
      - configs/report_templates/peg_discharge.yaml
      - configs/report_templates/peg_exchange.j2
      - configs/report_templates/peg_exchange.yaml
      - configs/report_templates/peg_placement.j2
      - configs/report_templates/peg_placement.yaml
      - configs/report_templates/peripheral_ablation.j2
      - configs/report_templates/peripheral_ablation.yaml
      - configs/report_templates/pigtail_catheter.j2
      - configs/report_templates/pigtail_catheter.yaml
      - configs/report_templates/pleurx_instructions.j2
      - configs/report_templates/pleurx_instructions.yaml
      - configs/report_templates/procedure_order.json
      - configs/report_templates/radial_ebus_sampling.j2
      - configs/report_templates/radial_ebus_sampling.yaml
      - configs/report_templates/radial_ebus_survey.j2
      - configs/report_templates/radial_ebus_survey.yaml
      - configs/report_templates/rigid_bronchoscopy.j2
      - configs/report_templates/rigid_bronchoscopy.yaml
      - configs/report_templates/robotic_ion_bronchoscopy.j2
      - configs/report_templates/robotic_ion_bronchoscopy.yaml
      - configs/report_templates/robotic_monarch_bronchoscopy.j2
      - configs/report_templates/robotic_monarch_bronchoscopy.yaml
      - configs/report_templates/robotic_navigation.j2
      - configs/report_templates/robotic_navigation.yaml
      - configs/report_templates/stent_surveillance.j2
      - configs/report_templates/stent_surveillance.yaml
      - configs/report_templates/therapeutic_aspiration.j2
      - configs/report_templates/therapeutic_aspiration.yaml
      - configs/report_templates/thoracentesis.j2
      - configs/report_templates/thoracentesis.json
      - configs/report_templates/thoracentesis_detailed.j2
      - configs/report_templates/thoracentesis_detailed.yaml
      - configs/report_templates/thoracentesis_manometry.j2
      - configs/report_templates/thoracentesis_manometry.yaml
      - configs/report_templates/tool_in_lesion_confirmation.j2
      - configs/report_templates/tool_in_lesion_confirmation.yaml
      - configs/report_templates/transbronchial_biopsy.j2
      - configs/report_templates/transbronchial_biopsy.yaml
      - configs/report_templates/transbronchial_cryobiopsy.j2
      - configs/report_templates/transbronchial_cryobiopsy.yaml
      - configs/report_templates/transbronchial_lung_biopsy.j2
      - configs/report_templates/transbronchial_lung_biopsy.yaml
      - configs/report_templates/transbronchial_needle_aspiration.j2
      - configs/report_templates/transbronchial_needle_aspiration.yaml
      - configs/report_templates/transthoracic_needle_biopsy.j2
      - configs/report_templates/transthoracic_needle_biopsy.yaml
      - configs/report_templates/tunneled_pleural_catheter_insert.j2
      - configs/report_templates/tunneled_pleural_catheter_insert.yaml
      - configs/report_templates/tunneled_pleural_catheter_remove.j2
      - configs/report_templates/tunneled_pleural_catheter_remove.yaml
      - configs/report_templates/whole_lung_lavage.j2
      - configs/report_templates/whole_lung_lavage.yaml
    - configs/__init__.py
  - docs/
    - docs/Multi_agent_collaboration/
      - docs/Multi_agent_collaboration/Architect Priming Script.md
      - docs/Multi_agent_collaboration/Codex Priming Script.md
      - docs/Multi_agent_collaboration/Codex “Repo Surgeon” Persona.md
      - docs/Multi_agent_collaboration/External_Review_Action_Plan.md
      - docs/Multi_agent_collaboration/Multi‑Agent Architecture.md
      - docs/Multi_agent_collaboration/Session Startup Template.md
      - docs/Multi_agent_collaboration/V8_MIGRATION_PLAN_UPDATED.md
    - docs/phi_review_system/
      - docs/phi_review_system/backend/
        - docs/phi_review_system/backend/dependencies.py
        - docs/phi_review_system/backend/endpoints.py
        - docs/phi_review_system/backend/main.py
        - docs/phi_review_system/backend/models.py
        - docs/phi_review_system/backend/schemas.py
      - docs/phi_review_system/frontend/
        - docs/phi_review_system/frontend/PHIReviewDemo.jsx
        - docs/phi_review_system/frontend/PHIReviewEditor.jsx
      - docs/phi_review_system/README.md
    - docs/"Diamond" Improvement Plan 1_18_26.txt
    - docs/.DS_Store
    - docs/AGENTS.md
    - docs/ARCHITECTURE.md
    - docs/CODEX_PRODUCTION_PLAN.md
    - docs/CODEX_REGISTRY_DIAMOND_LOOP.md
    - docs/DEPLOY_ARCH.md
    - docs/DEPLOY_RAILWAY.md
    - docs/DEPLOYMENT.md
    - docs/DEVELOPMENT.md
    - docs/GRAFANA_DASHBOARDS.md
    - docs/GRANULAR_NER_UPDATE_WORKFLOW.md
    - docs/INSTALLATION.md
    - docs/IPregistry_update_plan.md
    - docs/KNOWLEDGE_INVENTORY.md
    - docs/KNOWLEDGE_RELEASE_CHECKLIST.md
    - docs/MAKEFILE_COMMANDS.md
    - docs/ml_first_hybrid_policy.md
    - docs/model_release_runbook.md
    - docs/optimization_12_16_25.md
    - docs/PHI Redactor Fix Plan (v2)
    - docs/PHI_IDENTIFIERS.md
    - docs/Procedure_suite.code-workspace
    - docs/Production_Readiness_Review.md
    - docs/README.md
    - docs/REFERENCES.md
    - docs/Registry_API.md
    - docs/Registry_ML_summary.md
    - docs/REGISTRY_PRODIGY_WORKFLOW.md
    - docs/REGISTRY_RUNS.md
    - docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md
    - docs/REPO_GUIDE.md
    - docs/REPO_INDEX.md
    - docs/REPORTER_STYLE_GUIDE.md
    - docs/STRUCTURED_REPORTER.md
    - docs/unified_extraction_plan_2_5_26.md
    - docs/USER_GUIDE.md
  - extraction tests/
    - extraction tests/Integrated_iu_test.txt
    - extraction tests/pipeline_test.txt
    - extraction tests/smoke_test.txt
  - frontend/
    - frontend/registry_grid/
      - frontend/registry_grid/src/
        - frontend/registry_grid/src/__tests__/
          - frontend/registry_grid/src/__tests__/buildEvidenceIndex.test.ts
          - frontend/registry_grid/src/__tests__/flattenRegistryToRows.test.ts
          - frontend/registry_grid/src/__tests__/patchStoreCore.test.ts
        - frontend/registry_grid/src/components/
          - frontend/registry_grid/src/components/RegistryGrid.tsx
        - frontend/registry_grid/src/edits/
          - frontend/registry_grid/src/edits/patchStoreCore.ts
          - frontend/registry_grid/src/edits/types.ts
          - frontend/registry_grid/src/edits/usePatchStore.ts
        - frontend/registry_grid/src/evidence/
          - frontend/registry_grid/src/evidence/buildEvidenceIndex.ts
        - frontend/registry_grid/src/flatten/
          - frontend/registry_grid/src/flatten/flattenRegistryToRows.ts
          - frontend/registry_grid/src/flatten/jsonPointer.ts
        - frontend/registry_grid/src/monaco/
          - frontend/registry_grid/src/monaco/monacoBridge.ts
        - frontend/registry_grid/src/index.tsx
        - frontend/registry_grid/src/RegistryGridApp.tsx
        - frontend/registry_grid/src/styles.css
        - frontend/registry_grid/src/types.ts
        - frontend/registry_grid/src/vite-env.d.ts
      - frontend/registry_grid/package-lock.json
      - frontend/registry_grid/package.json
      - frontend/registry_grid/tsconfig.json
      - frontend/registry_grid/vite.config.ts
  - infra/
    - infra/prometheus/
      - infra/prometheus/prometheus.yml
  - legacy_files/
    - legacy_files/reactor.txt
    - legacy_files/veto.txt
  - models/
    - models/roberta-large-pm-m3-voc/
      - models/roberta-large-pm-m3-voc/RoBERTa-large-PM-M3-Voc-hf/
        - models/roberta-large-pm-m3-voc/RoBERTa-large-PM-M3-Voc-hf/config.json
        - models/roberta-large-pm-m3-voc/RoBERTa-large-PM-M3-Voc-hf/merges.txt
        - models/roberta-large-pm-m3-voc/RoBERTa-large-PM-M3-Voc-hf/vocab.json
  - modules/
    - modules/agents/
      - modules/agents/parser/
        - modules/agents/parser/__init__.py
        - modules/agents/parser/parser_agent.py
      - modules/agents/structurer/
        - modules/agents/structurer/__init__.py
        - modules/agents/structurer/structurer_agent.py
      - modules/agents/summarizer/
        - modules/agents/summarizer/__init__.py
        - modules/agents/summarizer/summarizer_agent.py
      - modules/agents/__init__.py
      - modules/agents/contracts.py
      - modules/agents/run_pipeline.py
    - modules/api/
      - modules/api/adapters/
        - modules/api/adapters/__init__.py
        - modules/api/adapters/response_adapter.py
      - modules/api/routes/
        - modules/api/routes/__init__.py
        - modules/api/routes/metrics.py
        - modules/api/routes/phi.py
        - modules/api/routes/phi_demo_cases.py
        - modules/api/routes/procedure_codes.py
        - modules/api/routes/registry_runs.py
        - modules/api/routes/unified_process.py
      - modules/api/schemas/
        - modules/api/schemas/__init__.py
        - modules/api/schemas/base.py
        - modules/api/schemas/qa.py
      - modules/api/services/
        - modules/api/services/__init__.py
        - modules/api/services/financials.py
        - modules/api/services/qa_pipeline.py
        - modules/api/services/unified_pipeline.py
      - modules/api/static/
        - modules/api/static/phi_redactor/
          - modules/api/static/phi_redactor/registry_grid/
            - modules/api/static/phi_redactor/registry_grid/registry_grid.css
            - modules/api/static/phi_redactor/registry_grid/registry_grid.iife.js
          - modules/api/static/phi_redactor/vendor/
            - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/onnx/
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/.DS_Store
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/config.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/label_map.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/special_tokens_map.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/tokenizer.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/tokenizer_config.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner/vocab.txt
            - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/onnx/
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/.bootstrap_state.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/config.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/manifest.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/ort_config.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/protected_terms.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/special_tokens_map.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/tokenizer.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/tokenizer_config.json
              - modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/vocab.txt
            - modules/api/static/phi_redactor/vendor/.DS_Store
            - modules/api/static/phi_redactor/vendor/.gitkeep
          - modules/api/static/phi_redactor/.DS_Store
          - modules/api/static/phi_redactor/allowlist_trie.json
          - modules/api/static/phi_redactor/app.js
          - modules/api/static/phi_redactor/index.html
          - modules/api/static/phi_redactor/protectedVeto.js
          - modules/api/static/phi_redactor/protectedVeto.legacy.js
          - modules/api/static/phi_redactor/redactor.worker.js
          - modules/api/static/phi_redactor/redactor.worker.legacy.js
          - modules/api/static/phi_redactor/reporter_builder.html
          - modules/api/static/phi_redactor/reporter_builder.js
          - modules/api/static/phi_redactor/styles.css
          - modules/api/static/phi_redactor/sw.js
          - modules/api/static/phi_redactor/transformers.legacy.js
          - modules/api/static/phi_redactor/transformers.min.js
          - modules/api/static/phi_redactor/workflow.html
        - modules/api/static/.DS_Store
        - modules/api/static/app.js
        - modules/api/static/index.html
        - modules/api/static/phi_demo.html
        - modules/api/static/phi_demo.js
        - modules/api/static/styles.css
      - modules/api/.DS_Store
      - modules/api/__init__.py
      - modules/api/coder_adapter.py
      - modules/api/dependencies.py
      - modules/api/fastapi_app.py
      - modules/api/gemini_client.py
      - modules/api/guards.py
      - modules/api/ml_advisor_router.py
      - modules/api/normalization.py
      - modules/api/phi_demo_store.py
      - modules/api/phi_dependencies.py
      - modules/api/phi_redaction.py
      - modules/api/readiness.py
      - modules/api/routes_registry.py
    - modules/autocode/
      - modules/autocode/ip_kb/
        - modules/autocode/ip_kb/canonical_rules.py
        - modules/autocode/ip_kb/ip_kb.py
      - modules/autocode/rvu/
    - modules/coder/
      - modules/coder/adapters/
        - modules/coder/adapters/llm/
          - modules/coder/adapters/llm/__init__.py
          - modules/coder/adapters/llm/gemini_advisor.py
          - modules/coder/adapters/llm/noop_advisor.py
          - modules/coder/adapters/llm/openai_compat_advisor.py
        - modules/coder/adapters/nlp/
          - modules/coder/adapters/nlp/__init__.py
          - modules/coder/adapters/nlp/keyword_mapping_loader.py
          - modules/coder/adapters/nlp/simple_negation_detector.py
        - modules/coder/adapters/persistence/
          - modules/coder/adapters/persistence/__init__.py
          - modules/coder/adapters/persistence/csv_kb_adapter.py
          - modules/coder/adapters/persistence/inmemory_procedure_store.py
          - modules/coder/adapters/persistence/supabase_procedure_store.py
        - modules/coder/adapters/__init__.py
        - modules/coder/adapters/ml_ranker.py
        - modules/coder/adapters/registry_coder.py
      - modules/coder/application/
        - modules/coder/application/__init__.py
        - modules/coder/application/candidate_expansion.py
        - modules/coder/application/coding_service.py
        - modules/coder/application/procedure_type_detector.py
        - modules/coder/application/smart_hybrid_policy.py
      - modules/coder/domain_rules/
        - modules/coder/domain_rules/registry_to_cpt/
          - modules/coder/domain_rules/registry_to_cpt/__init__.py
          - modules/coder/domain_rules/registry_to_cpt/coding_rules.py
          - modules/coder/domain_rules/registry_to_cpt/engine.py
          - modules/coder/domain_rules/registry_to_cpt/types.py
        - modules/coder/domain_rules/__init__.py
      - modules/coder/parallel_pathway/
        - modules/coder/parallel_pathway/__init__.py
        - modules/coder/parallel_pathway/confidence_combiner.py
        - modules/coder/parallel_pathway/orchestrator.py
        - modules/coder/parallel_pathway/reconciler.py
      - modules/coder/reconciliation/
        - modules/coder/reconciliation/__init__.py
        - modules/coder/reconciliation/pipeline.py
        - modules/coder/reconciliation/reconciler.py
      - modules/coder/.DS_Store
      - modules/coder/__init__.py
      - modules/coder/cli.py
      - modules/coder/code_families.py
      - modules/coder/constants.py
      - modules/coder/dictionary.py
      - modules/coder/ebus_extractor.py
      - modules/coder/ebus_rules.py
      - modules/coder/ncci.py
      - modules/coder/peripheral_extractor.py
      - modules/coder/peripheral_rules.py
      - modules/coder/phi_gating.py
      - modules/coder/posthoc.py
      - modules/coder/rules.py
      - modules/coder/rules_engine.py
      - modules/coder/schema.py
      - modules/coder/sectionizer.py
      - modules/coder/types.py
    - modules/common/
      - modules/common/rules_engine/
        - modules/common/rules_engine/__init__.py
        - modules/common/rules_engine/dsl.py
        - modules/common/rules_engine/mer.py
        - modules/common/rules_engine/ncci.py
      - modules/common/__init__.py
      - modules/common/exceptions.py
      - modules/common/knowledge.py
      - modules/common/knowledge_cli.py
      - modules/common/knowledge_schema.py
      - modules/common/llm.py
      - modules/common/logger.py
      - modules/common/model_capabilities.py
      - modules/common/openai_responses.py
      - modules/common/rvu_calc.py
      - modules/common/sectionizer.py
      - modules/common/spans.py
      - modules/common/text_cleaning.py
      - modules/common/text_io.py
      - modules/common/umls_linking.py
    - modules/domain/
      - modules/domain/coding_rules/
        - modules/domain/coding_rules/__init__.py
        - modules/domain/coding_rules/coding_rules_engine.py
        - modules/domain/coding_rules/evidence_context.py
        - modules/domain/coding_rules/json_rules_evaluator.py
        - modules/domain/coding_rules/mer.py
        - modules/domain/coding_rules/ncci.py
        - modules/domain/coding_rules/rule_engine.py
      - modules/domain/knowledge_base/
        - modules/domain/knowledge_base/__init__.py
        - modules/domain/knowledge_base/models.py
        - modules/domain/knowledge_base/repository.py
        - modules/domain/knowledge_base/validator.py
      - modules/domain/procedure_store/
        - modules/domain/procedure_store/__init__.py
        - modules/domain/procedure_store/repository.py
      - modules/domain/reasoning/
        - modules/domain/reasoning/__init__.py
        - modules/domain/reasoning/models.py
      - modules/domain/rvu/
        - modules/domain/rvu/__init__.py
        - modules/domain/rvu/calculator.py
      - modules/domain/text/
        - modules/domain/text/__init__.py
        - modules/domain/text/negation.py
      - modules/domain/__init__.py
    - modules/extraction/
      - modules/extraction/postprocessing/
        - modules/extraction/postprocessing/__init__.py
        - modules/extraction/postprocessing/clinical_guardrails.py
      - modules/extraction/__init__.py
    - modules/infra/
      - modules/infra/__init__.py
      - modules/infra/cache.py
      - modules/infra/executors.py
      - modules/infra/llm_control.py
      - modules/infra/nlp_warmup.py
      - modules/infra/perf.py
      - modules/infra/safe_logging.py
      - modules/infra/settings.py
    - modules/llm/
      - modules/llm/__init__.py
      - modules/llm/client.py
    - modules/ml_coder/
      - modules/ml_coder/__init__.py
      - modules/ml_coder/data_prep.py
      - modules/ml_coder/distillation_io.py
      - modules/ml_coder/label_hydrator.py
      - modules/ml_coder/predictor.py
      - modules/ml_coder/preprocessing.py
      - modules/ml_coder/registry_data_prep.py
      - modules/ml_coder/registry_label_constraints.py
      - modules/ml_coder/registry_label_schema.py
      - modules/ml_coder/registry_predictor.py
      - modules/ml_coder/registry_training.py
      - modules/ml_coder/self_correction.py
      - modules/ml_coder/thresholds.py
      - modules/ml_coder/training.py
      - modules/ml_coder/training_losses.py
      - modules/ml_coder/utils.py
      - modules/ml_coder/valid_ip_codes.py
    - modules/ner/
      - modules/ner/__init__.py
      - modules/ner/entity_types.py
      - modules/ner/inference.py
    - modules/phi/
      - modules/phi/adapters/
        - modules/phi/adapters/__init__.py
        - modules/phi/adapters/audit_logger_db.py
        - modules/phi/adapters/encryption_insecure_demo.py
        - modules/phi/adapters/fernet_encryption.py
        - modules/phi/adapters/phi_redactor_hybrid.py
        - modules/phi/adapters/presidio_scrubber.py
        - modules/phi/adapters/redaction-service.js
        - modules/phi/adapters/scrubber_stub.py
      - modules/phi/safety/
        - modules/phi/safety/__init__.py
        - modules/phi/safety/protected_terms.py
        - modules/phi/safety/veto.py
      - modules/phi/.DS_Store
      - modules/phi/__init__.py
      - modules/phi/db.py
      - modules/phi/models.py
      - modules/phi/ports.py
      - modules/phi/README.md
      - modules/phi/service.py
    - modules/proc_ml_advisor/
      - modules/proc_ml_advisor/__init__.py
      - modules/proc_ml_advisor/schemas.py
    - modules/registry/
      - modules/registry/adapters/
        - modules/registry/adapters/__init__.py
        - modules/registry/adapters/schema_registry.py
        - modules/registry/adapters/v3_to_v2.py
      - modules/registry/application/
        - modules/registry/application/__init__.py
        - modules/registry/application/coding_support_builder.py
        - modules/registry/application/cpt_registry_mapping.py
        - modules/registry/application/pathology_extraction.py
        - modules/registry/application/registry_builder.py
        - modules/registry/application/registry_service.py
      - modules/registry/audit/
        - modules/registry/audit/__init__.py
        - modules/registry/audit/audit_types.py
        - modules/registry/audit/compare.py
        - modules/registry/audit/raw_ml_auditor.py
      - modules/registry/deterministic/
        - modules/registry/deterministic/__init__.py
        - modules/registry/deterministic/anatomy.py
      - modules/registry/evidence/
        - modules/registry/evidence/__init__.py
        - modules/registry/evidence/verifier.py
      - modules/registry/extraction/
        - modules/registry/extraction/__init__.py
        - modules/registry/extraction/focus.py
        - modules/registry/extraction/structurer.py
      - modules/registry/extractors/
        - modules/registry/extractors/__init__.py
        - modules/registry/extractors/disease_burden.py
        - modules/registry/extractors/llm_detailed.py
        - modules/registry/extractors/noop.py
        - modules/registry/extractors/v3_extractor.py
      - modules/registry/legacy/
        - modules/registry/legacy/adapters/
          - modules/registry/legacy/adapters/__init__.py
          - modules/registry/legacy/adapters/airway.py
          - modules/registry/legacy/adapters/base.py
          - modules/registry/legacy/adapters/pleural.py
        - modules/registry/legacy/__init__.py
        - modules/registry/legacy/adapter.py
        - modules/registry/legacy/supabase_sink.py
      - modules/registry/ml/
        - modules/registry/ml/__init__.py
        - modules/registry/ml/action_predictor.py
        - modules/registry/ml/evaluate.py
        - modules/registry/ml/models.py
      - modules/registry/ner_mapping/
        - modules/registry/ner_mapping/__init__.py
        - modules/registry/ner_mapping/entity_to_registry.py
        - modules/registry/ner_mapping/procedure_extractor.py
        - modules/registry/ner_mapping/station_extractor.py
      - modules/registry/pipelines/
        - modules/registry/pipelines/__init__.py
        - modules/registry/pipelines/v3_pipeline.py
      - modules/registry/postprocess/
        - modules/registry/postprocess/__init__.py
        - modules/registry/postprocess/complications_reconcile.py
        - modules/registry/postprocess/template_checkbox_negation.py
      - modules/registry/processing/
        - modules/registry/processing/__init__.py
        - modules/registry/processing/cao_interventions_detail.py
        - modules/registry/processing/disease_burden.py
        - modules/registry/processing/focus.py
        - modules/registry/processing/linear_ebus_stations_detail.py
        - modules/registry/processing/masking.py
        - modules/registry/processing/navigation_fiducials.py
        - modules/registry/processing/navigation_targets.py
      - modules/registry/schema/
        - modules/registry/schema/adapters/
          - modules/registry/schema/adapters/v3_to_v2.py
        - modules/registry/schema/ebus_events.py
        - modules/registry/schema/granular_logic.py
        - modules/registry/schema/granular_models.py
        - modules/registry/schema/ip_v3.py
        - modules/registry/schema/ip_v3_extraction.py
        - modules/registry/schema/v2_dynamic.py
      - modules/registry/self_correction/
        - modules/registry/self_correction/__init__.py
        - modules/registry/self_correction/apply.py
        - modules/registry/self_correction/judge.py
        - modules/registry/self_correction/keyword_guard.py
        - modules/registry/self_correction/prompt_improvement.py
        - modules/registry/self_correction/types.py
        - modules/registry/self_correction/validation.py
      - modules/registry/slots/
        - modules/registry/slots/__init__.py
        - modules/registry/slots/base.py
        - modules/registry/slots/blvr.py
        - modules/registry/slots/complications.py
        - modules/registry/slots/dilation.py
        - modules/registry/slots/disposition.py
        - modules/registry/slots/ebus.py
        - modules/registry/slots/imaging.py
        - modules/registry/slots/indication.py
        - modules/registry/slots/pleura.py
        - modules/registry/slots/sedation.py
        - modules/registry/slots/stent.py
        - modules/registry/slots/tblb.py
        - modules/registry/slots/therapeutics.py
      - modules/registry/.DS_Store
      - modules/registry/__init__.py
      - modules/registry/cli.py
      - modules/registry/deterministic_extractors.py
      - modules/registry/ebus_config.py
      - modules/registry/engine.py
      - modules/registry/inference_onnx.py
      - modules/registry/inference_pytorch.py
      - modules/registry/ip_registry_improvements.md
      - modules/registry/ip_registry_schema_additions.json
      - modules/registry/label_fields.py
      - modules/registry/model_bootstrap.py
      - modules/registry/model_runtime.py
      - modules/registry/normalization.py
      - modules/registry/prompts.py
      - modules/registry/registry_system_prompt.txt
      - modules/registry/schema.py
      - modules/registry/schema_filter.py
      - modules/registry/schema_granular.py
      - modules/registry/summarize.py
      - modules/registry/tags.py
      - modules/registry/transform.py
      - modules/registry/v2_booleans.py
    - modules/registry_cleaning/
      - modules/registry_cleaning/__init__.py
      - modules/registry_cleaning/clinical_qc.py
      - modules/registry_cleaning/consistency_utils.py
      - modules/registry_cleaning/cpt_utils.py
      - modules/registry_cleaning/logging_utils.py
      - modules/registry_cleaning/schema_utils.py
    - modules/registry_store/
      - modules/registry_store/__init__.py
      - modules/registry_store/dependencies.py
      - modules/registry_store/models.py
      - modules/registry_store/phi_gate.py
    - modules/reporter/
      - modules/reporter/templates/
        - modules/reporter/templates/blvr_synoptic.md.jinja
        - modules/reporter/templates/bronchoscopy_synoptic.md.jinja
        - modules/reporter/templates/pleural_synoptic.md.jinja
      - modules/reporter/.DS_Store
      - modules/reporter/__init__.py
      - modules/reporter/cli.py
      - modules/reporter/engine.py
      - modules/reporter/prompts.py
      - modules/reporter/schema.py
    - modules/reporting/
      - modules/reporting/second_pass/
        - modules/reporting/second_pass/.keep
        - modules/reporting/second_pass/__init__.py
        - modules/reporting/second_pass/counts_backfill.py
        - modules/reporting/second_pass/laterality_guard.py
        - modules/reporting/second_pass/station_consistency.py
      - modules/reporting/templates/
        - modules/reporting/templates/addons/
          - modules/reporting/templates/addons/__init__.py
          - modules/reporting/templates/addons/airway_stent_placement.jinja
          - modules/reporting/templates/addons/airway_stent_removal_revision.jinja
          - modules/reporting/templates/addons/airway_stent_surveillance_bronchoscopy.jinja
          - modules/reporting/templates/addons/awake_fiberoptic_intubation_foi.jinja
          - modules/reporting/templates/addons/balloon_dilation.jinja
          - modules/reporting/templates/addons/blvr_discharge.jinja
          - modules/reporting/templates/addons/bronchial_brushings.jinja
          - modules/reporting/templates/addons/bronchial_washing.jinja
          - modules/reporting/templates/addons/bronchoalveolar_lavage.jinja
          - modules/reporting/templates/addons/bronchopleural_fistula_bpf_localization_and_occlusion_test.jinja
          - modules/reporting/templates/addons/bronchoscopy_guided_double_lumen_tube_dlt_placement_confirmation.jinja
          - modules/reporting/templates/addons/chemical_cauterization_of_granulation_tissue.jinja
          - modules/reporting/templates/addons/chemical_pleurodesis_via_chest_tube_talc_slurry_or_doxycycline.jinja
          - modules/reporting/templates/addons/chemical_pleurodesis_via_tunneled_pleural_catheter_ipc.jinja
          - modules/reporting/templates/addons/chest_tube_exchange_upsizing_over_guidewire.jinja
          - modules/reporting/templates/addons/chest_tube_pleurx_catheter_discharge.jinja
          - modules/reporting/templates/addons/chest_tube_removal.jinja
          - modules/reporting/templates/addons/cone_beam_ct_cbct_augmented_fluoroscopy_assisted_bronchoscopy.jinja
          - modules/reporting/templates/addons/control_of_minor_tracheostomy_bleeding_electrocautery.jinja
          - modules/reporting/templates/addons/cryo_extraction_of_mucus_casts_secretions.jinja
          - modules/reporting/templates/addons/ebus_guided_19_gauge_core_fine_needle_biopsy_fnb.jinja
          - modules/reporting/templates/addons/ebus_guided_intranodal_forceps_biopsy_ifb.jinja
          - modules/reporting/templates/addons/ebus_tbna.jinja
          - modules/reporting/templates/addons/electromagnetic_navigation_bronchoscopy.jinja
          - modules/reporting/templates/addons/endobronchial_biopsy.jinja
          - modules/reporting/templates/addons/endobronchial_blocker_placement_isolation_hemorrhage_control.jinja
          - modules/reporting/templates/addons/endobronchial_cryoablation.jinja
          - modules/reporting/templates/addons/endobronchial_hemostasis_hemoptysis_control.jinja
          - modules/reporting/templates/addons/endobronchial_sealant_application_for_bronchopleural_fistula_bpf.jinja
          - modules/reporting/templates/addons/endobronchial_tumor_destruction.jinja
          - modules/reporting/templates/addons/endobronchial_tumor_excision.jinja
          - modules/reporting/templates/addons/endobronchial_valve_placement.jinja
          - modules/reporting/templates/addons/endobronchial_valve_placement_for_persistent_air_leak_bpf.jinja
          - modules/reporting/templates/addons/endobronchial_valve_removal_exchange.jinja
          - modules/reporting/templates/addons/eus_b.jinja
          - modules/reporting/templates/addons/fiducial_marker_placement.jinja
          - modules/reporting/templates/addons/flexible_fiberoptic_laryngoscopy.jinja
          - modules/reporting/templates/addons/focused_thoracic_ultrasound_pleura_lung.jinja
          - modules/reporting/templates/addons/foreign_body_removal_flexible_rigid.jinja
          - modules/reporting/templates/addons/general_bronchoscopy_note.jinja
          - modules/reporting/templates/addons/image_guided_chest_tube.jinja
          - modules/reporting/templates/addons/indwelling_pleural_catheter_ipc_exchange.jinja
          - modules/reporting/templates/addons/indwelling_tunneled_pleural_catheter_placement.jinja
          - modules/reporting/templates/addons/interventional_pulmonology_operative_report.jinja
          - modules/reporting/templates/addons/intra_procedural_cbct_cact_fusion_registration_correction_e_g_navilink_3d.jinja
          - modules/reporting/templates/addons/intrapleural_fibrinolysis.jinja
          - modules/reporting/templates/addons/ion_registration_complete.jinja
          - modules/reporting/templates/addons/ion_registration_partial_efficiency_strategy_ssrab.jinja
          - modules/reporting/templates/addons/ion_registration_registration_drift_mismatch.jinja
          - modules/reporting/templates/addons/medical_thoracoscopy.jinja
          - modules/reporting/templates/addons/paracentesis.jinja
          - modules/reporting/templates/addons/peg_discharge.jinja
          - modules/reporting/templates/addons/peg_placement.jinja
          - modules/reporting/templates/addons/peg_removal_exchange.jinja
          - modules/reporting/templates/addons/percutaneous_tracheostomy_revision.jinja
          - modules/reporting/templates/addons/photodynamic_therapy_debridement_48_96_hours_post_light.jinja
          - modules/reporting/templates/addons/photodynamic_therapy_pdt_light_application.jinja
          - modules/reporting/templates/addons/pigtail_catheter_placement.jinja
          - modules/reporting/templates/addons/post_blvr_management_protocol.jinja
          - modules/reporting/templates/addons/pre_anesthesia_assessment_for_moderate_sedation.jinja
          - modules/reporting/templates/addons/radial_ebus_guided_sampling_with_guide_sheath.jinja
          - modules/reporting/templates/addons/radial_ebus_survey.jinja
          - modules/reporting/templates/addons/rigid_bronchoscopy_diagnostic_therapeutic.jinja
          - modules/reporting/templates/addons/robotic_navigational_bronchoscopy_ion.jinja
          - modules/reporting/templates/addons/robotic_navigational_bronchoscopy_monarch_auris.jinja
          - modules/reporting/templates/addons/stoma_or_tracheal_granulation_mechanical_debridement.jinja
          - modules/reporting/templates/addons/therapeutic_aspiration.jinja
          - modules/reporting/templates/addons/thoracentesis.jinja
          - modules/reporting/templates/addons/thoracentesis_with_pleural_manometry.jinja
          - modules/reporting/templates/addons/thoravent_placement.jinja
          - modules/reporting/templates/addons/tool_in_lesion_confirmation.jinja
          - modules/reporting/templates/addons/tracheobronchoscopy_via_tracheostomy.jinja
          - modules/reporting/templates/addons/tracheostomy_decannulation_bedside.jinja
          - modules/reporting/templates/addons/tracheostomy_downsizing_fenestrated_tube_placement.jinja
          - modules/reporting/templates/addons/tracheostomy_planned_percutaneous_bronchoscopic_assistance.jinja
          - modules/reporting/templates/addons/tracheostomy_tube_change.jinja
          - modules/reporting/templates/addons/transbronchial_cryobiopsy.jinja
          - modules/reporting/templates/addons/transbronchial_dye_marker_placement_for_surgical_localization.jinja
          - modules/reporting/templates/addons/transbronchial_lung_biopsy.jinja
          - modules/reporting/templates/addons/transbronchial_needle_aspiration.jinja
          - modules/reporting/templates/addons/transthoracic_needle_biopsy.jinja
          - modules/reporting/templates/addons/tunneled_pleural_catheter_instructions.jinja
          - modules/reporting/templates/addons/tunneled_pleural_catheter_removal.jinja
          - modules/reporting/templates/addons/ultrasound_guided_pleural_biopsy_closed_core.jinja
          - modules/reporting/templates/addons/whole_lung_lavage.jinja
        - modules/reporting/templates/macros/
          - modules/reporting/templates/macros/01_minor_trach_laryngoscopy.j2
          - modules/reporting/templates/macros/02_core_bronchoscopy.j2
          - modules/reporting/templates/macros/03_navigation_robotic_ebus.j2
          - modules/reporting/templates/macros/04_blvr_cryo.j2
          - modules/reporting/templates/macros/05_pleural.j2
          - modules/reporting/templates/macros/06_other_interventions.j2
          - modules/reporting/templates/macros/07_clinical_assessment.j2
          - modules/reporting/templates/macros/base.j2
          - modules/reporting/templates/macros/main.j2
          - modules/reporting/templates/macros/template_schema.json
        - modules/reporting/templates/.keep
        - modules/reporting/templates/bronchoscopy.jinja
        - modules/reporting/templates/cryobiopsy.jinja
        - modules/reporting/templates/ebus_tbna.jinja
        - modules/reporting/templates/ipc.jinja
        - modules/reporting/templates/pleuroscopy.jinja
        - modules/reporting/templates/stent.jinja
        - modules/reporting/templates/thoracentesis.jinja
      - modules/reporting/__init__.py
      - modules/reporting/coder_view.py
      - modules/reporting/engine.py
      - modules/reporting/EXTRACTION_RULES.md
      - modules/reporting/inference.py
      - modules/reporting/ip_addons.py
      - modules/reporting/json_patch.py
      - modules/reporting/macro_engine.py
      - modules/reporting/metadata.py
      - modules/reporting/partial_schemas.py
      - modules/reporting/questions.py
      - modules/reporting/validation.py
    - modules/.DS_Store
    - modules/__init__.py
  - observability/
    - observability/__init__.py
    - observability/coding_metrics.py
    - observability/logging_config.py
    - observability/metrics.py
    - observability/timing.py
  - output/
    - output/pdf/
    - output/.DS_Store
  - proc_kb/
    - proc_kb/ebus_config.yaml
  - proc_nlp/
    - proc_nlp/__init__.py
    - proc_nlp/normalize_proc.py
    - proc_nlp/umls_linker.py
  - proc_schemas/
    - proc_schemas/clinical/
      - proc_schemas/clinical/__init__.py
      - proc_schemas/clinical/airway.py
      - proc_schemas/clinical/common.py
      - proc_schemas/clinical/pleural.py
    - proc_schemas/registry/
      - proc_schemas/registry/__init__.py
      - proc_schemas/registry/ip_v2.py
      - proc_schemas/registry/ip_v3.py
    - proc_schemas/shared/
      - proc_schemas/shared/__init__.py
      - proc_schemas/shared/ebus_events.py
    - proc_schemas/.DS_Store
    - proc_schemas/__init__.py
    - proc_schemas/billing.py
    - proc_schemas/coding.py
    - proc_schemas/envelope_models.py
    - proc_schemas/procedure_report.py
    - proc_schemas/reasoning.py
  - processed_data/
    - processed_data/test.csv
    - processed_data/train.csv
  - Registry-First ML Data Preparation/
    - Registry-First ML Data Preparation/golden_to_csv.py
    - Registry-First ML Data Preparation/INTEGRATION_GUIDE.md
    - Registry-First ML Data Preparation/makefile_snippet.mk
    - Registry-First ML Data Preparation/registry_data_prep.py
    - Registry-First ML Data Preparation/test_registry_data_prep.py
  - registry_granular_data/
    - registry_granular_data/granular_csv_files/
      - registry_granular_data/granular_csv_files/event_log.csv
      - registry_granular_data/granular_csv_files/Label_guide.csv
      - registry_granular_data/granular_csv_files/note_index.csv
      - registry_granular_data/granular_csv_files/span_annotations.csv
      - registry_granular_data/granular_csv_files/span_hydrated.csv
      - registry_granular_data/granular_csv_files/V3_Procedure_events.csv
    - registry_granular_data/notes_text/
      - registry_granular_data/notes_text/note_001.txt
      - registry_granular_data/notes_text/note_002.txt
      - registry_granular_data/notes_text/note_003.txt
      - registry_granular_data/notes_text/note_004.txt
      - registry_granular_data/notes_text/note_005.txt
      - registry_granular_data/notes_text/note_006.txt
      - registry_granular_data/notes_text/note_007.txt
      - registry_granular_data/notes_text/note_008.txt
      - registry_granular_data/notes_text/note_009.txt
      - registry_granular_data/notes_text/note_010.txt
      - registry_granular_data/notes_text/note_011.txt
      - registry_granular_data/notes_text/note_012.txt
      - registry_granular_data/notes_text/note_013.txt
      - registry_granular_data/notes_text/note_014.txt
      - registry_granular_data/notes_text/note_015.txt
      - registry_granular_data/notes_text/note_016.txt
      - registry_granular_data/notes_text/note_017.txt
      - registry_granular_data/notes_text/note_018.txt
      - registry_granular_data/notes_text/note_019.txt
      - registry_granular_data/notes_text/note_020.txt
      - registry_granular_data/notes_text/note_021.txt
      - registry_granular_data/notes_text/note_022.txt
      - registry_granular_data/notes_text/note_023.txt
      - registry_granular_data/notes_text/note_024.txt
      - registry_granular_data/notes_text/note_025.txt
      - registry_granular_data/notes_text/note_026.txt
      - registry_granular_data/notes_text/note_027.txt
      - registry_granular_data/notes_text/note_028.txt
      - registry_granular_data/notes_text/note_029.txt
      - registry_granular_data/notes_text/note_030.txt
      - registry_granular_data/notes_text/note_031.txt
      - registry_granular_data/notes_text/note_032.txt
      - registry_granular_data/notes_text/note_033.txt
      - registry_granular_data/notes_text/note_034.txt
      - registry_granular_data/notes_text/note_035.txt
      - registry_granular_data/notes_text/note_036.txt
      - registry_granular_data/notes_text/note_037.txt
      - registry_granular_data/notes_text/note_038.txt
      - registry_granular_data/notes_text/note_039.txt
      - registry_granular_data/notes_text/note_040.txt
      - registry_granular_data/notes_text/note_041.txt
      - registry_granular_data/notes_text/note_042.txt
      - registry_granular_data/notes_text/note_043.txt
      - registry_granular_data/notes_text/note_044.txt
      - registry_granular_data/notes_text/note_045.txt
      - registry_granular_data/notes_text/note_046.txt
      - registry_granular_data/notes_text/note_047.txt
      - registry_granular_data/notes_text/note_048.txt
      - registry_granular_data/notes_text/note_049.txt
      - registry_granular_data/notes_text/note_050.txt
      - registry_granular_data/notes_text/note_051.txt
      - registry_granular_data/notes_text/note_052.txt
      - registry_granular_data/notes_text/note_053.txt
      - registry_granular_data/notes_text/note_054.txt
      - registry_granular_data/notes_text/note_055.txt
      - registry_granular_data/notes_text/note_056.txt
      - registry_granular_data/notes_text/note_057.txt
      - registry_granular_data/notes_text/note_058.txt
      - registry_granular_data/notes_text/note_059.txt
      - registry_granular_data/notes_text/note_060.txt
      - registry_granular_data/notes_text/note_061.txt
      - registry_granular_data/notes_text/note_062.txt
      - registry_granular_data/notes_text/note_063.txt
      - registry_granular_data/notes_text/note_064.txt
      - registry_granular_data/notes_text/note_065.txt
      - registry_granular_data/notes_text/note_066.txt
      - registry_granular_data/notes_text/note_067.txt
      - registry_granular_data/notes_text/note_068.txt
      - registry_granular_data/notes_text/note_069.txt
      - registry_granular_data/notes_text/note_070.txt
      - registry_granular_data/notes_text/note_071.txt
      - registry_granular_data/notes_text/note_072.txt
      - registry_granular_data/notes_text/note_073.txt
      - registry_granular_data/notes_text/note_074.txt
      - registry_granular_data/notes_text/note_075.txt
      - registry_granular_data/notes_text/note_076.txt
      - registry_granular_data/notes_text/note_077.txt
      - registry_granular_data/notes_text/note_078.txt
      - registry_granular_data/notes_text/note_079.txt
      - registry_granular_data/notes_text/note_080.txt
      - registry_granular_data/notes_text/note_081.txt
      - registry_granular_data/notes_text/note_082.txt
      - registry_granular_data/notes_text/note_083.txt
      - registry_granular_data/notes_text/note_084.txt
      - registry_granular_data/notes_text/note_085.txt
      - registry_granular_data/notes_text/note_086.txt
      - registry_granular_data/notes_text/note_087.txt
      - registry_granular_data/notes_text/note_088.txt
      - registry_granular_data/notes_text/note_089.txt
      - registry_granular_data/notes_text/note_090.txt
      - registry_granular_data/notes_text/note_091.txt
      - registry_granular_data/notes_text/note_092.txt
      - registry_granular_data/notes_text/note_093.txt
      - registry_granular_data/notes_text/note_094.txt
      - registry_granular_data/notes_text/note_095.txt
      - registry_granular_data/notes_text/note_096.txt
      - registry_granular_data/notes_text/note_097.txt
      - registry_granular_data/notes_text/note_098.txt
      - registry_granular_data/notes_text/note_099.txt
      - registry_granular_data/notes_text/note_100.txt
      - registry_granular_data/notes_text/note_101.txt
      - registry_granular_data/notes_text/note_102.txt
      - registry_granular_data/notes_text/note_103.txt
      - registry_granular_data/notes_text/note_104.txt
      - registry_granular_data/notes_text/note_105.txt
      - registry_granular_data/notes_text/note_106.txt
      - registry_granular_data/notes_text/note_107.txt
      - registry_granular_data/notes_text/note_108.txt
      - registry_granular_data/notes_text/note_109.txt
      - registry_granular_data/notes_text/note_110.txt
      - registry_granular_data/notes_text/note_111.txt
      - registry_granular_data/notes_text/note_112.txt
      - registry_granular_data/notes_text/note_113.txt
      - registry_granular_data/notes_text/note_114.txt
      - registry_granular_data/notes_text/note_115.txt
      - registry_granular_data/notes_text/note_116.txt
      - registry_granular_data/notes_text/note_117.txt
      - registry_granular_data/notes_text/note_118.txt
      - registry_granular_data/notes_text/note_119.txt
      - registry_granular_data/notes_text/note_120.txt
      - registry_granular_data/notes_text/note_121.txt
      - registry_granular_data/notes_text/note_122.txt
      - registry_granular_data/notes_text/note_123.txt
      - registry_granular_data/notes_text/note_124.txt
      - registry_granular_data/notes_text/note_125.txt
      - registry_granular_data/notes_text/note_126.txt
      - registry_granular_data/notes_text/note_127.txt
      - registry_granular_data/notes_text/note_128.txt
  - schemas/
    - schemas/IP_Registry.json
  - scripts/
    - scripts/phi_test_node/
      - scripts/phi_test_node/package-lock.json
      - scripts/phi_test_node/package.json
      - scripts/phi_test_node/results.txt
      - scripts/phi_test_node/test_phi_redaction.mjs
      - scripts/phi_test_node/test_union_mode.mjs
    - scripts/add_training_case.py
    - scripts/align_synthetic_names.py
    - scripts/apply_immediate_logic_fixes.py
    - scripts/apply_platinum_redactions.py
    - scripts/audit_model_fp.py
    - scripts/bootstrap_granular_attributes.py
    - scripts/bootstrap_granular_ner_bundle.py
    - scripts/bootstrap_phi_redactor_vendor_bundle.py
    - scripts/build_hard_negative_patch.py
    - scripts/build_model_agnostic_phi_spans.py
    - scripts/build_phi_allowlist_trie.py
    - scripts/build_registry_bundle.py
    - scripts/check_onnx_inputs.py
    - scripts/check_pydantic_models.py
    - scripts/clean_distilled_phi_labels.py
    - scripts/clean_ner.py
    - scripts/clear_unannotated_prodigy_batch.py
    - scripts/code_validation.py
    - scripts/convert_spans_to_bio.py
    - scripts/cpt_check.py
    - scripts/create_blank_update_scripts_from_patient_note_texts.py
    - scripts/create_slim_branch.py
    - scripts/dedupe_granular_ner.py
    - scripts/dev_pull_model.sh
    - scripts/devserver.sh
    - scripts/diagnose_codex.sh
    - scripts/diamond_loop_cloud_sync.py
    - scripts/discover_aws_region.sh
    - scripts/distill_phi_labels.py
    - scripts/eval_hybrid_pipeline.py
    - scripts/eval_registry_granular.py
    - scripts/evaluate_coder.py
    - scripts/evaluate_cpt.py
    - scripts/export_patient_note_texts.py
    - scripts/export_phi_gold_standard.py
    - scripts/export_phi_model_for_transformersjs.py
    - scripts/extract_ner_from_excel.py
    - scripts/find_critical_failures.py
    - scripts/find_phi_failures.py
    - scripts/fit_thresholds_from_eval.py
    - scripts/fix_alignment.py
    - scripts/fix_registry_hallucinations.py
    - scripts/force_merge_human_labels.py
    - scripts/generate_addon_templates.py
    - scripts/generate_blank_granular_note_scripts.py
    - scripts/generate_cpt_keywords.py
    - scripts/generate_gitingest.py
    - scripts/generate_procedure_suite_one_pager_pdf.py
    - scripts/generate_synthetic_phi_data.py
    - scripts/generate_teacher_logits.py
    - scripts/golden_to_csv.py
    - scripts/index_repo.py
    - scripts/ingest_phase0_data.py
    - scripts/knowledge_diff_report.py
    - scripts/label_neg_stent.py
    - scripts/merge_granular_attribute_spans.py
    - scripts/merge_registry.py
    - scripts/merge_registry_human_labels.py
    - scripts/merge_registry_prodigy.py
    - scripts/normalize_phi_labels.py
    - scripts/parse_golden_reporter_examples.py
    - scripts/patch.py
    - scripts/phi_audit.py
    - scripts/preflight.py
    - scripts/prepare_data.py
    - scripts/prodigy_cloud_sync.py
    - scripts/prodigy_export_corrections.py
    - scripts/prodigy_export_registry.py
    - scripts/prodigy_prepare_phi_batch.py
    - scripts/prodigy_prepare_registry.py
    - scripts/prodigy_prepare_registry_batch.py
    - scripts/prodigy_prepare_registry_relabel_batch.py
    - scripts/quantize_to_onnx.py
    - scripts/railway_start.sh
    - scripts/railway_start_gunicorn.sh
    - scripts/refine_ner_labels.py
    - scripts/regenerate_granular_ner_stats.py
    - scripts/registry_label_overlap_report.py
    - scripts/registry_pipeline_smoke.py
    - scripts/registry_pipeline_smoke_batch.py
    - scripts/render_report.py
    - scripts/review_llm_fallback_errors.py
    - scripts/run_coder_hybrid.py
    - scripts/run_granular_annotations.sh
    - scripts/run_python_update_scripts.py
    - scripts/sanitize_dataset.py
    - scripts/sanitize_platinum_spans.py
    - scripts/scrub_golden_jsons.py
    - scripts/self_correct_registry.py
    - scripts/smoke_run.sh
    - scripts/split_phi_gold.py
    - scripts/test_debulk.py
    - scripts/test_phi_redaction_sample.py
    - scripts/train_distilbert_ner.py
    - scripts/train_registry_ner.py
    - scripts/train_registry_sklearn.py
    - scripts/train_roberta.py
    - scripts/train_roberta_pm3.py
    - scripts/training.py
    - scripts/unified_pipeline_batch.py
    - scripts/update_nodejs_conda.sh
    - scripts/upload_registry_bundle.sh
    - scripts/validate_golden_extractions.py
    - scripts/validate_jsonschema.py
    - scripts/validate_knowledge_release.py
    - scripts/validate_ner_alignment.py
    - scripts/verify_phi_redactor_vendor_assets.py
    - scripts/verify_registry_human_data.py
    - scripts/verify_registry_runtime_bundle.py
    - scripts/warm_models.py
  - tests/
    - tests/api/
      - tests/api/conftest.py
      - tests/api/test_coding_phi_gating.py
      - tests/api/test_fastapi.py
      - tests/api/test_phi_demo_cases.py
      - tests/api/test_phi_endpoints.py
      - tests/api/test_phi_redaction.py
      - tests/api/test_phi_redactor_ui.py
      - tests/api/test_qa_run_fallback_control.py
      - tests/api/test_registry_extract_endpoint.py
      - tests/api/test_registry_runs.py
      - tests/api/test_ui.py
      - tests/api/test_unified_process.py
    - tests/coder/
      - tests/coder/test_candidate_expansion.py
      - tests/coder/test_coding_rules_phase7.py
      - tests/coder/test_hierarchy_bundling_fixes.py
      - tests/coder/test_kb_professional_descriptions.py
      - tests/coder/test_kitchen_sink_ml_first_fastpath_completeness.py
      - tests/coder/test_llm_provider_openai_compat.py
      - tests/coder/test_ncci_bundling_excludes_financials.py
      - tests/coder/test_ncci_ptp_indicator.py
      - tests/coder/test_parallel_confidence_combiner.py
      - tests/coder/test_parallel_pathway_orchestrator_path_b.py
      - tests/coder/test_reconciliation.py
      - tests/coder/test_registry_coder.py
      - tests/coder/test_registry_to_cpt_rules_pure_registry.py
      - tests/coder/test_rules_engine.py
      - tests/coder/test_smart_hybrid_policy.py
    - tests/coding/
      - tests/coding/test_ebus_rules.py
      - tests/coding/test_hierarchy_normalization.py
      - tests/coding/test_json_rules_parity.py
      - tests/coding/test_peripheral_rules.py
      - tests/coding/test_phi_gating.py
      - tests/coding/test_rules_engine_phase1.py
      - tests/coding/test_rules_validation.py
      - tests/coding/test_sectionizer.py
      - tests/coding/test_sectionizer_integration.py
    - tests/contracts/
      - tests/contracts/.gitkeep
    - tests/e2e/
      - tests/e2e/test_registry_e2e.py
    - tests/fixtures/
      - tests/fixtures/notes/
        - tests/fixtures/notes/kitchen_sink_ion_nav_ebus_fiducial_dilation.txt
        - tests/fixtures/notes/note_274.txt
        - tests/fixtures/notes/note_275.txt
        - tests/fixtures/notes/note_281.txt
        - tests/fixtures/notes/note_289.txt
        - tests/fixtures/notes/note_315.txt
        - tests/fixtures/notes/phi_example_note.txt
      - tests/fixtures/regression_suite/
        - tests/fixtures/regression_suite/README.md
      - tests/fixtures/.gitkeep
      - tests/fixtures/blvr_two_lobes.txt
      - tests/fixtures/complex_tracheal_stenosis.txt
      - tests/fixtures/ebus_staging_4R_7_11R.txt
      - tests/fixtures/ppl_nav_radial_tblb.txt
      - tests/fixtures/reporter_golden_dataset.json
      - tests/fixtures/stent_rmb_and_dilation_lul.txt
      - tests/fixtures/therapeutic_aspiration_repeat_stay.txt
      - tests/fixtures/thora_bilateral.txt
    - tests/helpers/
      - tests/helpers/__init__.py
      - tests/helpers/phi_asserts.py
    - tests/integration/
      - tests/integration/api/
        - tests/integration/api/__init__.py
        - tests/integration/api/test_coder_run_endpoint.py
        - tests/integration/api/test_health_endpoint.py
        - tests/integration/api/test_metrics_endpoint.py
        - tests/integration/api/test_procedure_codes_endpoints.py
        - tests/integration/api/test_registry_endpoints.py
        - tests/integration/api/test_startup_warmup.py
      - tests/integration/coder/
        - tests/integration/coder/__init__.py
        - tests/integration/coder/test_coding_service.py
        - tests/integration/coder/test_hybrid_policy.py
      - tests/integration/persistence/
        - tests/integration/persistence/__init__.py
        - tests/integration/persistence/test_supabase_procedure_store.py
      - tests/integration/.gitkeep
      - tests/integration/test_phi_workflow_end_to_end.py
      - tests/integration/test_pipeline_integrity.py
      - tests/integration/test_placeholder.py
    - tests/ml_advisor/
      - tests/ml_advisor/__init__.py
      - tests/ml_advisor/conftest.py
      - tests/ml_advisor/test_router.py
      - tests/ml_advisor/test_schemas.py
    - tests/ml_coder/
      - tests/ml_coder/__init__.py
      - tests/ml_coder/test_case_difficulty.py
      - tests/ml_coder/test_data_prep.py
      - tests/ml_coder/test_distillation_io.py
      - tests/ml_coder/test_label_hydrator.py
      - tests/ml_coder/test_registry_data_prep.py
      - tests/ml_coder/test_registry_first_data_prep.py
      - tests/ml_coder/test_registry_label_constraints.py
      - tests/ml_coder/test_registry_label_schema.py
      - tests/ml_coder/test_registry_predictor.py
      - tests/ml_coder/test_training_pipeline.py
    - tests/phi/
      - tests/phi/__init__.py
      - tests/phi/test_fernet_encryption_adapter.py
      - tests/phi/test_manual_scrub.py
      - tests/phi/test_models.py
      - tests/phi/test_presidio_nlp_backend_smoke.py
      - tests/phi/test_presidio_scrubber_adapter.py
      - tests/phi/test_service.py
      - tests/phi/test_veto_regression.py
    - tests/registry/
      - tests/registry/regression_cases.jsonl
      - tests/registry/test_action_predictor.py
      - tests/registry/test_airway_stent_vascular_plug_revision.py
      - tests/registry/test_audit_compare_report.py
      - tests/registry/test_auditor_raw_ml_only.py
      - tests/registry/test_cao_extraction.py
      - tests/registry/test_cao_interventions_detail.py
      - tests/registry/test_clinical_guardrails_checkbox_negative.py
      - tests/registry/test_clinical_guardrails_endobronchial_biopsy.py
      - tests/registry/test_clinical_guardrails_radial_linear.py
      - tests/registry/test_clinical_guardrails_stent_inspection.py
      - tests/registry/test_clinical_guardrails_tbna_peripheral_context.py
      - tests/registry/test_derive_procedures_from_granular_consistency.py
      - tests/registry/test_deterministic_extractors_outcomes.py
      - tests/registry/test_deterministic_extractors_phase6.py
      - tests/registry/test_disease_burden_extractor.py
      - tests/registry/test_disease_burden_overrides.py
      - tests/registry/test_ebus_config_station_count.py
      - tests/registry/test_ebus_deterministic.py
      - tests/registry/test_ebus_postprocess_enrichment.py
      - tests/registry/test_ebus_postprocess_fallback.py
      - tests/registry/test_ebus_site_block_reconcile.py
      - tests/registry/test_ebus_specimen_override.py
      - tests/registry/test_evidence_required_policy.py
      - tests/registry/test_extraction_first_flow.py
      - tests/registry/test_extraction_quality.py
      - tests/registry/test_extraction_quality_fixpack_jan2026.py
      - tests/registry/test_fixpack_batch2.py
      - tests/registry/test_fixpack_device_action_regressions.py
      - tests/registry/test_fixpack_trach_stent_elastography_normalization.py
      - tests/registry/test_focusing_audit_guardrail.py
      - tests/registry/test_granular_registry_models.py
      - tests/registry/test_header_scan.py
      - tests/registry/test_keyword_guard_coverage.py
      - tests/registry/test_keyword_guard_generated_keywords.py
      - tests/registry/test_keyword_guard_high_conf_bypass.py
      - tests/registry/test_keyword_guard_keywords.py
      - tests/registry/test_keyword_guard_omissions.py
      - tests/registry/test_keyword_guard_overrides.py
      - tests/registry/test_kitchen_sink_extraction_first.py
      - tests/registry/test_linear_ebus_stations_detail.py
      - tests/registry/test_llm_timeout_fallback.py
      - tests/registry/test_masking.py
      - tests/registry/test_navigation_fiducials.py
      - tests/registry/test_navigation_targets_inline_target.py
      - tests/registry/test_navigation_targets_numbered_targets.py
      - tests/registry/test_ner_procedure_extractor.py
      - tests/registry/test_ner_to_registry_mapper.py
      - tests/registry/test_new_extractors.py
      - tests/registry/test_normalization.py
      - tests/registry/test_note_002_regression.py
      - tests/registry/test_note_047_regression.py
      - tests/registry/test_note_164_disease_burden_and_cao_regression.py
      - tests/registry/test_note_240_cao_regression.py
      - tests/registry/test_note_279_regression.py
      - tests/registry/test_note_281_elastography_regression.py
      - tests/registry/test_note_281_granularity_regression.py
      - tests/registry/test_note_300_multilobe_navigation_regression.py
      - tests/registry/test_openai_model_structurer_override.py
      - tests/registry/test_outcomes_success_status.py
      - tests/registry/test_parallel_ner_uplift_evidence.py
      - tests/registry/test_pathology_extraction.py
      - tests/registry/test_phase5_regression_harness.py
      - tests/registry/test_pleural_extraction.py
      - tests/registry/test_post_fix_regressions.py
      - tests/registry/test_provider_name_sanitization.py
      - tests/registry/test_registry_engine_merge_llm_and_seed.py
      - tests/registry/test_registry_engine_sanitization.py
      - tests/registry/test_registry_extraction_ebus.py
      - tests/registry/test_registry_guardrails.py
      - tests/registry/test_registry_qa_regressions.py
      - tests/registry/test_registry_service_hybrid_flow.py
      - tests/registry/test_registry_to_cpt_airway_stent_assessment_only.py
      - tests/registry/test_registry_to_cpt_blvr_chartis_sedation.py
      - tests/registry/test_registry_to_cpt_diagnostic_bronchoscopy.py
      - tests/registry/test_registry_to_cpt_fibrinolytic_therapy.py
      - tests/registry/test_registry_to_cpt_mechanical_debulking.py
      - tests/registry/test_registry_to_cpt_thoracoscopy_biopsy.py
      - tests/registry/test_regression_pack.py
      - tests/registry/test_schema_filter.py
      - tests/registry/test_schema_refactor_smoke.py
      - tests/registry/test_sedation_blvr.py
      - tests/registry/test_self_correction_loop.py
      - tests/registry/test_self_correction_validation.py
      - tests/registry/test_slots_ebus_tblb.py
      - tests/registry/test_structurer_fallback.py
      - tests/registry/test_table_row_masking_regressions.py
      - tests/registry/test_template_checkbox_negation.py
      - tests/registry/test_tracheostomy_route.py
      - tests/registry/test_v3_note_281_narrative_first_and_anchors.py
    - tests/reporter/
      - tests/reporter/test_golden_examples.py
      - tests/reporter/test_ip_addons.py
      - tests/reporter/test_macro_engine_features.py
      - tests/reporter/test_questions_builder.py
    - tests/scripts/
      - tests/scripts/test_audit_model_fp_cli.py
      - tests/scripts/test_audit_model_fp_logic.py
      - tests/scripts/test_bootstrap_granular_attributes.py
      - tests/scripts/test_export_patient_note_texts.py
      - tests/scripts/test_merge_granular_attribute_spans.py
      - tests/scripts/test_prodigy_export_registry.py
      - tests/scripts/test_prodigy_export_registry_file_mode.py
      - tests/scripts/test_prodigy_prepare_registry.py
      - tests/scripts/test_train_distilbert_ner_cli.py
      - tests/scripts/test_train_registry_ner_allowlist.py
      - tests/scripts/test_train_roberta_cli.py
    - tests/unit/
      - tests/unit/.gitkeep
      - tests/unit/__init__.py
      - tests/unit/test_cpt_cleaning.py
      - tests/unit/test_dsl.py
      - tests/unit/test_extraction_adapters.py
      - tests/unit/test_inference_engine.py
      - tests/unit/test_inmemory_procedure_store.py
      - tests/unit/test_knowledge.py
      - tests/unit/test_no_legacy_imports.py
      - tests/unit/test_normalize_phi_labels.py
      - tests/unit/test_openai_payload_compat.py
      - tests/unit/test_openai_responses_primary.py
      - tests/unit/test_openai_timeouts.py
      - tests/unit/test_phi_distillation.py
      - tests/unit/test_phi_distillation_refinery.py
      - tests/unit/test_phi_platinum_filters.py
      - tests/unit/test_procedure_type_detector.py
      - tests/unit/test_protected_veto.py
      - tests/unit/test_qa_pipeline_serialization.py
      - tests/unit/test_sanitize_dataset.py
      - tests/unit/test_schemas.py
      - tests/unit/test_structured_reporter.py
      - tests/unit/test_template_cache.py
      - tests/unit/test_template_coverage.py
      - tests/unit/test_templates.py
      - tests/unit/test_validation_engine.py
    - tests/utils/
      - tests/utils/__init__.py
      - tests/utils/case_filter.py
    - tests/.DS_Store
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_clean_ip_registry.py
    - tests/test_ip_registry_schema_guardrails.py
    - tests/test_openai_responses_parse.py
    - tests/test_phi_redaction_contract.py
    - tests/test_registry_normalization.py
  - tmp/
    - tmp/pdfs/
  - updated IU componenets/
    - updated IU componenets/app.js
    - updated IU componenets/fastapi_app.py
    - updated IU componenets/index.html
    - updated IU componenets/styles.css
  - .DS_Store
  - .env
  - .env.backup
  - .env.example
  - .gitattributes
  - .gitignore
  - .pre-commit-config.yaml
  - .setup.stamp
  - add_case_3786812.py
  - AGENTS.md
  - alembic.ini
  - alignment_warnings.log
  - batch_extraction_review.txt
  - CLAUDE.md
  - debug_ner.py
  - gitingest.md
  - gitingest_details.md
  - institutions.jsonl
  - ip_golden_knowledge_v2_2.json
  - Makefile
  - my_results.txt
  - my_results2.txt
  - new_results.txt
  - NOTES_SCHEMA_REFACTOR.md
  - Output_examples.txt
  - prioritized_annotation_list.txt
  - prodigy_annotations_export.cleaned.jsonl
  - pyproject.toml
  - README.md
  - registry_examples_1_17_26.txt
  - reporter examples.txt
  - requirements-train.txt
  - requirements.txt
  - runtime.txt
  - smoketest.txt
  - stats.json
  - test_output_20260119_110530.txt
  - test_output_20260119_111551.txt
  - test_redact.txt
  - training_log.txt
```

## Important directories (not inlined)
- `modules/`
- `proc_report/`
- `proc_autocode/`
- `proc_nlp/`
- `proc_registry/`
- `proc_schemas/`
- `schemas/`
- `configs/`
- `scripts/`
- `tests/`

## Important files (inlined)

---
### `README.md`
```
# Procedure Suite

**Automated CPT Coding, Registry Extraction, and Synoptic Reporting for Interventional Pulmonology.**

This toolkit enables:
1.  **Predict CPT Codes**: Analyze procedure notes using ML + LLM hybrid pipeline to generate billing codes with RVU calculations.
2.  **Extract Registry Data**: Use deterministic extractors and LLMs to extract structured clinical data (EBUS stations, complications, demographics) into a validated schema.
3.  **Generate Reports**: Create standardized, human-readable procedure reports from structured data.

## Documentation

- **[Docs Home](docs/README.md)**: Start here — reading order and documentation map.
- **[Repo Guide](docs/REPO_GUIDE.md)**: End-to-end explanation of how the repo functions.
- **[Installation & Setup](docs/INSTALLATION.md)**: Setup guide for Python, spaCy models, and API keys.
- **[Repo Index](docs/REPO_INDEX.md)**: One-page map of the repo (entrypoints, key folders, knowledge assets).
- **[User Guide](docs/USER_GUIDE.md)**: How to use the CLI tools and API endpoints.
- **[Registry Prodigy Workflow](docs/REGISTRY_PRODIGY_WORKFLOW.md)**: Human-in-the-loop “Diamond Loop” for the registry procedure classifier.
- **[Development Guide](docs/DEVELOPMENT.md)**: **CRITICAL** for contributors and AI Agents. Defines the system architecture and coding standards.
- **[Architecture](docs/ARCHITECTURE.md)**: System design, module breakdown, and data flow.
- **[Agents](docs/AGENTS.md)**: Multi-agent pipeline documentation for Parser, Summarizer, and Structurer.
- **[Registry API](docs/Registry_API.md)**: Registry extraction service API documentation.
- **[CPT Reference](docs/REFERENCES.md)**: List of supported codes.

## Quick Start

1.  **Install**:
    ```bash
    micromamba activate medparse-py311
    make install
    make preflight
    ```

2.  **Configure**:
    Create `.env` with your `GEMINI_API_KEY`.

3.  **Run**:
    ```bash
    # Start the API/Dev Server
    ./scripts/devserver.sh
    ```

    Then open:
    - UI (Clinical Dashboard / PHI Redactor): `http://localhost:8000/ui/`
    - Workflow overview: `http://localhost:8000/ui/workflow.html`

    The UI flow is: paste note -> run PHI detection -> apply redactions -> submit scrubbed note -> review results.
    Optional: edit values in **Flattened Tables (Editable)** (generates **Edited JSON (Training)**) and export JSON/tables.

## Recent Updates (2026-01-25)

- **Schema refactor:** shared EBUS node-event types now live in `proc_schemas/shared/ebus_events.py` and are re-exported via `modules/registry/schema/ebus_events.py`.
- **Granular split:** models moved to `modules/registry/schema/granular_models.py` and logic to `modules/registry/schema/granular_logic.py`; `modules/registry/schema_granular.py` is a compat shim.
- **V2 dynamic builder:** moved to `modules/registry/schema/v2_dynamic.py`; `modules/registry/schema.py` is now a thin entrypoint preserving the `__path__` hack.
- **V3 extraction schema:** renamed to `modules/registry/schema/ip_v3_extraction.py` with a compatibility re-export at `modules/registry/schema/ip_v3.py`; the rich registry entry schema remains at `proc_schemas/registry/ip_v3.py`.
- **V3→V2 adapter:** now in `modules/registry/schema/adapters/v3_to_v2.py` with a compat shim at `modules/registry/adapters/v3_to_v2.py`.
- **Refactor notes/tests:** see `NOTES_SCHEMA_REFACTOR.md` and `tests/registry/test_schema_refactor_smoke.py`.

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement uses `31647` (initial lobe) + `31651` (each additional lobe); valve removal uses `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## Key Modules

| Module | Description |
|--------|-------------|
| **`modules/api/fastapi_app.py`** | Main FastAPI backend |
| **`modules/coder/`** | CPT coding engine with CodingService (8-step pipeline) |
| **`modules/ml_coder/`** | ML-based code predictor and training pipeline |
| **`modules/registry/`** | Registry extraction with RegistryService and RegistryEngine |
| **`modules/agents/`** | 3-agent pipeline: Parser → Summarizer → Structurer |
| **`modules/reporter/`** | Template-based synoptic report generator |
| **`modules/api/static/phi_redactor/`** | Main UI (served at `/ui/`): client-side PHI scrubbing + clinical dashboard |

## System Architecture

> **Note (Current as of 2026-01):** The server enforces `PROCSUITE_PIPELINE_MODE=extraction_first`
> at startup. The **authoritative production endpoint** is `POST /api/v1/process`, and its
> primary pipeline is **Extraction‑First**: **Registry extraction → deterministic Registry→CPT rules**.
> The older **CPT-first (ML-first) hybrid** flows still exist in code for legacy endpoints and
> tooling, but are expected to be gated/disabled in production.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Procedure Note                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Layer (modules/api/)                      │
│  • /api/v1/process - Unified extraction-first endpoint (prod)       │
│  • /v1/coder/run - Legacy CPT coding endpoint (gated)               │
│  • /v1/registry/run - Legacy registry extraction endpoint (gated)   │
│  • /v1/report/render - Report generation endpoint                   │
└─────────────────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│ RegistryService │    │    Reporter     │
│ (Extraction-    │    │ (Jinja temps)   │
│  First)         │    └─────────────────┘
└─────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ RegistryRecord (V3-shaped)   │
└──────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Deterministic Registry→CPT   │
│ (no note parsing)            │
└──────────────────────────────┘
```

### Extraction-First Pipeline (Current: `/api/v1/process`)

The production pipeline (as exercised by the UI at `/ui/` and `POST /api/v1/process`) is:

1. **(Optional) PHI redaction** (skipped when `already_scrubbed=true`)
2. **Registry extraction** from note text (engine selected by `REGISTRY_EXTRACTION_ENGINE`, production requires `parallel_ner`)
3. **Deterministic Registry→CPT derivation** from the extracted `RegistryRecord` (no raw note parsing)
4. **RAW-ML auditing** (and optional self-correction) to detect omissions/mismatches
5. **UI-ready response** with evidence spans + review flags

### Legacy CPT-First / Hybrid-First Flows (kept for tooling, gated in prod)

Some older endpoints and internal tools still use a CPT-first hybrid approach:

1. **CPT Coding** → Get codes from SmartHybridOrchestrator
2. **CPT Mapping** → Map CPT codes to registry boolean flags
3. **LLM Extraction** → Extract additional fields via RegistryEngine
4. **Reconciliation** → Merge CPT-derived and LLM-extracted fields
5. **Validation** → Validate against IP_Registry.json schema

## Data & Schemas

| File | Purpose |
|------|---------|
| `data/knowledge/ip_coding_billing_v3_0.json` | CPT codes, RVUs, bundling rules |
| `data/knowledge/IP_Registry.json` | Registry schema definition |
| `data/knowledge/golden_extractions/` | Training data for ML models |
| `schemas/IP_Registry.json` | JSON Schema for validation |

## Testing

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/coder/ -v          # Coder tests
pytest tests/registry/ -v       # Registry tests
pytest tests/ml_coder/ -v       # ML coder tests

# Validate registry extraction
make validate-registry

# Run preflight checks
make preflight
```

## Note for AI Assistants

**Please read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) before making changes.**

- Always edit `modules/api/fastapi_app.py` (not `api/app.py` - deprecated)
- Use `CodingService` from `modules/coder/application/coding_service.py`
- Use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing_v3_0.json`
- Run `make test` before committing

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM backend: `gemini` or `openai_compat` | `gemini` |
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM features |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `OPENAI_API_KEY` | API key for OpenAI-protocol backend (openai_compat) | Required unless `OPENAI_OFFLINE=1` |
| `OPENAI_BASE_URL` | Base URL for OpenAI-protocol backend (no `/v1`) | `https://api.openai.com` |
| `OPENAI_MODEL` | Default model name for openai_compat | Required unless `OPENAI_OFFLINE=1` |
| `OPENAI_MODEL_SUMMARIZER` | Model override for summarizer/focusing tasks (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_MODEL_STRUCTURER` | Model override for structurer tasks (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_MODEL_JUDGE` | Model override for self-correction judge (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_OFFLINE` | Disable openai_compat network calls (use stubs) | `0` |
| `OPENAI_PRIMARY_API` | Primary API: `responses` or `chat` | `responses` |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat Completions on 404 | `1` |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Read timeout for registry tasks (seconds) | `180` |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Read timeout for default tasks (seconds) | `60` |
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |
| `PROCSUITE_PIPELINE_MODE` | Pipeline mode (startup-enforced): `extraction_first` | `extraction_first` |
| `REGISTRY_EXTRACTION_ENGINE` | Registry extraction engine: `engine`, `agents_focus_then_engine`, or `agents_structurer` | `engine` |
| `REGISTRY_AUDITOR_SOURCE` | Registry auditor source (extraction-first): `raw_ml` or `disabled` | `raw_ml` |
| `REGISTRY_ML_AUDIT_USE_BUCKETS` | Audit set = `high_conf + gray_zone` when `1`; else use `top_k + min_prob` | `1` |
| `REGISTRY_ML_AUDIT_TOP_K` | Audit top-k predictions when buckets disabled | `25` |
| `REGISTRY_ML_AUDIT_MIN_PROB` | Audit minimum probability when buckets disabled | `0.50` |
| `REGISTRY_ML_SELF_CORRECT_MIN_PROB` | Min prob for self-correction trigger candidates | `0.95` |
| `REGISTRY_SELF_CORRECT_ENABLED` | Enable guarded self-correction loop | `0` |
| `REGISTRY_SELF_CORRECT_ALLOWLIST` | Comma-separated JSON Pointer allowlist for self-correction patch paths (default: `modules/registry/self_correction/validation.py` `ALLOWED_PATHS`) | `builtin` |
| `REGISTRY_SELF_CORRECT_MAX_ATTEMPTS` | Max successful auto-corrections per case | `1` |
| `REGISTRY_SELF_CORRECT_MAX_PATCH_OPS` | Max JSON Patch ops per proposal | `5` |

---

*Last updated: January 2026*

```

---
### `CLAUDE.md`
```
# Procedure Suite (Claude Guide)

## What This Service Does

- The server is a **stateless coding engine**: **scrubbed note text in → registry fields + CPT codes out**.
- The primary UI/API entrypoint is `POST /api/v1/process` (`modules/api/routes/unified_process.py`).

## How To Run Locally

```bash
./scripts/devserver.sh
```

- UI: `http://localhost:8000/ui/`
- API docs: `http://localhost:8000/docs`

The devserver sources `.env` and the app also loads `.env` (unless `PROCSUITE_SKIP_DOTENV=1`).
Keep secrets (e.g., `OPENAI_API_KEY`) out of git; prefer setting them in your shell or an untracked local `.env`.

## Required Env (Enforced at Startup)

The app refuses to start unless:

- `PROCSUITE_PIPELINE_MODE=extraction_first`

In production (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also require:

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
- `REGISTRY_SCHEMA_VERSION=v3`
- `REGISTRY_AUDITOR_SOURCE=raw_ml`

## PHI Workflow

- Keep `POST /api/v1/process` enabled in production.
- When `CODER_REQUIRE_PHI_REVIEW=true`, responses must default to:
  - `review_status=pending_phi_review`
  - `needs_manual_review=true`

Client-side PHI scrubbing is the long-term direction; the server can still scrub when `already_scrubbed=false`.

## UI (Clinical Dashboard / PHI Redactor)

The devserver mounts the PHI redactor UI as the main UI:

- UI: `http://localhost:8000/ui/` (static files: `modules/api/static/phi_redactor/`)
- Workflow tab: `http://localhost:8000/ui/workflow.html`

Notable workflow features:

- **New Note** clears the editor and all prior outputs (tables + JSON) between cases.
- **Flattened Tables (Editable)** is collapsed by default; edits generate a second payload under **Edited JSON (Training)**:
  - `edited_for_training=true`, `edited_at`, `edited_source=ui_flattened_tables`, and `edited_tables[]`.
- **Export JSON** downloads the raw server response; **Export Tables** downloads the flattened tables as an Excel-readable `.xls` (HTML).
- Clinical tables should reflect **clinical reality** from `registry` (performed/details) even when a related CPT code is bundled/suppressed.

## Recent Updates (2026-01-25)

- **Schema refactor:** shared EBUS node-event types now live in `proc_schemas/shared/ebus_events.py` and are re-exported via `modules/registry/schema/ebus_events.py`.
- **Granular split:** models moved to `modules/registry/schema/granular_models.py` and logic to `modules/registry/schema/granular_logic.py`; `modules/registry/schema_granular.py` is a compat shim.
- **V2 dynamic builder:** moved to `modules/registry/schema/v2_dynamic.py`; `modules/registry/schema.py` is now a thin entrypoint preserving the `__path__` hack.
- **V3 extraction schema:** renamed to `modules/registry/schema/ip_v3_extraction.py` with a compatibility re-export at `modules/registry/schema/ip_v3.py`; the rich registry entry schema remains at `proc_schemas/registry/ip_v3.py`.
- **V3→V2 adapter:** now in `modules/registry/schema/adapters/v3_to_v2.py` with a compat shim at `modules/registry/adapters/v3_to_v2.py`.
- **Refactor notes/tests:** see `NOTES_SCHEMA_REFACTOR.md` and `tests/registry/test_schema_refactor_smoke.py`.

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement now maps to `31647` (initial lobe) + `31651` (each additional lobe), and valve removal maps to `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## Recent Updates (2026-02-05)

- **Hierarchy of truth (conflict resolution):**
  - **Narrative supersedes header codes**: do not treat `PROCEDURE:` CPT lists as “performed” when `PROCEDURE IN DETAIL:` contradicts (e.g., header says “trach change” but narrative describes ETT intubation → do not extract tracheostomy creation).
  - **Narrative supersedes summary**: complications mentioned in narrative override templated “COMPLICATIONS: None” (see `modules/registry/postprocess/complications_reconcile.py`).
  - **Evidence supersedes checkbox heuristics**: unchecked template items must *not* force a procedure to `performed=false` when explicit active-voice narrative evidence supports `true` (see `modules/registry/postprocess/template_checkbox_negation.py`).
- **Anti-hallucination: tools ≠ intent**: mentions of tools (snare/forceps/basket/cryoprobe) do not imply debulking/ablation; require action-on-tissue language (tightened CAO modality parsing in `modules/registry/processing/cao_interventions_detail.py`).
- **Puncture ≠ stoma**: tracheal puncture (CPT `31612`) is *not* percutaneous tracheostomy creation; extraction and CPT derivation distinguish puncture-only from trach creation.
- **Intraprocedural adjustment bundling**:
  - BLVR valve remove/replace in the same session is an adjustment, not foreign body removal; do not derive `31635` for valve exchanges.
  - BLVR now tracks segment tokens (e.g., `RB10`) and counts **final deployed valves** only (removed/replaced devices are not counted).
- **Distinct targets for unbundling**: suppress `31629` when EBUS-TBNA is present unless `peripheral_tbna.targets_sampled` clearly indicates a non-station, anatomically distinct target.

## Parallel NER (“Split Brain”) Notes

When `REGISTRY_EXTRACTION_ENGINE=parallel_ner`, the extraction-first pipeline runs:

- Path A: Granular NER → registry mapping → deterministic registry→CPT rules
- Path B: registry ML predictor (optional); code must not crash if unavailable or if return types differ
- Deterministic uplift fills common misses (BAL/EBBx/radial EBUS/cryotherapy + pleural drains + chest ultrasound) and attaches evidence spans
- Omission scan emits `SILENT_FAILURE:` warnings for missed high-value procedures

Evidence returned to the UI should be V3-shaped:
`{"source","text","span":[start,end],"confidence"}`

## Context/Negation Guardrails (Extraction Quality)

The deterministic layer includes guardrails to reduce “keyword-only” hallucinations:

- **Stents**: inspection-only phrases (e.g., “stent … in good position”) should *not* trigger stent placement (`31636`).
- **Chest tubes**: discontinue/removal phrases (e.g., “D/c chest tube”) should *not* trigger insertion (`32551`).
- **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional`. Use `peripheral_tbna` for lung/lesion TBNA; when peripheral TBNA co-occurs with EBUS (`31652/31653`), keep `31629` with Modifier `59` (distinct site).
- **Tools ≠ intent**: do not infer `31641`/`31640` from tools alone (snare/cryoprobe/forceps); require therapeutic intent + tissue action language.
- **Puncture ≠ stoma**: tracheal puncture language should not set percutaneous trach performed.
- **Header vs narrative**: procedure header CPT/menu content is not source-of-truth when contradicted by the narrative.
- **Radial EBUS**: explicit “radial probe …” language should set `radial_ebus.performed` even without concentric/eccentric markers.
- **Menu masking**: `mask_extraction_noise()` strips CPT/menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations.

## Granular NER — Stent Label Taxonomy

- `DEV_STENT`: stent mentioned as a device with an interaction (placed/deployed/removed/exchanged/migrated).
- `NEG_STENT`: explicit absence (e.g., “no stent was placed”, “stent not indicated”).
- `CTX_STENT_PRESENT`: stent present/in good position with no intervention evidence.
- Labeling helper: `scripts/label_neg_stent.py` (dry-run by default; use `--write` to persist changes).
- Training allowlist: update `scripts/train_registry_ner.py:ALLOWED_LABEL_TYPES` when adding new label types.

## LLM Self-Correction (Recommended)

- Enable by default with `REGISTRY_SELF_CORRECT_ENABLED=1`. This allows the server to call an external LLM on **scrubbed text**
  as a judge to patch missing registry fields when RAW-ML flags high-confidence omissions.
- For faster responses (no self-correction), set `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.

### Debugging Self-Correction

- Self-correction only runs when `REGISTRY_AUDITOR_SOURCE=raw_ml` produces `high_conf_omissions` and the CPT keyword guard passes.
- Keyword gating lives in `modules/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.
- Use the smoke script for visibility into triggers/skips:
  - `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`
  - Look for `Audit high-conf omissions:` and `SELF_CORRECT_SKIPPED:` reasons.

## Files You’ll Touch Most Often

- API app wiring + startup env validation: `modules/api/fastapi_app.py`
- Unified process endpoint: `modules/api/routes/unified_process.py`
- Extraction-first pipeline: `modules/registry/application/registry_service.py`
- Parallel pathway orchestrator: `modules/coder/parallel_pathway/orchestrator.py`
- Omission guardrails: `modules/registry/self_correction/keyword_guard.py`
- Clinical postprocessing guardrails: `modules/extraction/postprocessing/clinical_guardrails.py`
- PHI redactor veto rules: `modules/api/static/phi_redactor/protectedVeto.js`

## Tests

- Run full suite: `make test`
- Run targeted: `pytest -q <path>::<test_name>`

```

---
### `AGENTS.md`
```
# Procedure Suite Agent Guide

This repo is transitioning to **zero‑knowledge client‑side pseudonymization**:
the browser scrubs PHI and the server acts as a **stateless logic engine** (Text In → Codes Out).

## Quick Commands

- Dev server: `./scripts/devserver.sh` (serves UI at `/ui/` and API docs at `/docs`)
- Tests: `make test`
- Lint/typecheck (optional): `make lint`, `make typecheck`
- Smoke test (single note): `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`
- Smoke test (batch): `python scripts/registry_pipeline_smoke_batch.py --count 30 --self-correct --output my_results.txt`

## Required Runtime Configuration

Startup validation enforces these invariants (see `modules/api/fastapi_app.py`):

- `PROCSUITE_PIPELINE_MODE=extraction_first` (required; service fails to start otherwise)
- In production (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also require:
  - `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
  - `REGISTRY_SCHEMA_VERSION=v3`
  - `REGISTRY_AUDITOR_SOURCE=raw_ml`

`.env` is loaded automatically unless `PROCSUITE_SKIP_DOTENV=1`. Shell env vars take precedence.
Keep secrets (e.g., `OPENAI_API_KEY`) out of git; prefer shell env vars or an untracked local `.env`.

## Primary API Surface

- **Authoritative endpoint:** `POST /api/v1/process` (`modules/api/routes/unified_process.py`)
  - If `CODER_REQUIRE_PHI_REVIEW=true`, keep the endpoint enabled but return:
    - `review_status=pending_phi_review`
    - `needs_manual_review=true`
- **Legacy endpoints** are gated (feature flags):
  - `PROCSUITE_ALLOW_LEGACY_ENDPOINTS` controls ID-based extraction endpoints (expected to be locked out in prod).
  - `PROCSUITE_ALLOW_REQUEST_MODE_OVERRIDE` controls request-mode overrides.

## UI (PHI Redactor / Clinical Dashboard)

- Served by `./scripts/devserver.sh` at `/ui/` (static files live in `modules/api/static/phi_redactor/`).
- Workflow explainer page: `/ui/workflow.html` (links from the top bar).
- **New Note**: clears the editor + all prior tables/JSON output to avoid confusion during long-running submits.
- **Flattened Tables (Editable)** (collapsed by default): provides an edit-friendly view of key tables; some fields use dropdowns.
  - When any flattened table value is edited, the UI generates a second payload under **Edited JSON (Training)** with:
    - `edited_for_training=true`, `edited_at`, `edited_source=ui_flattened_tables`, and `edited_tables[]`.
- **Export JSON** downloads the raw server response; **Export Tables** downloads the flattened tables as an Excel-readable `.xls` (HTML).
- Clinical tables are **registry-driven** (e.g., `registry.*.performed`) and should not hide true clinical events due to billing bundling/suppression
  (non-performed rows/cards may render dimmed when details exist).

## Recent Updates (2026-01-25)

- **Schema refactor:** shared EBUS node-event types now live in `proc_schemas/shared/ebus_events.py` and are re-exported via `modules/registry/schema/ebus_events.py`.
- **Granular split:** models moved to `modules/registry/schema/granular_models.py` and logic to `modules/registry/schema/granular_logic.py`; `modules/registry/schema_granular.py` is a compat shim.
- **V2 dynamic builder:** moved to `modules/registry/schema/v2_dynamic.py`; `modules/registry/schema.py` is now a thin entrypoint preserving the `__path__` hack.
- **V3 extraction schema:** renamed to `modules/registry/schema/ip_v3_extraction.py` with a compatibility re-export at `modules/registry/schema/ip_v3.py`; the rich registry entry schema remains at `proc_schemas/registry/ip_v3.py`.
- **V3→V2 adapter:** now in `modules/registry/schema/adapters/v3_to_v2.py` with a compat shim at `modules/registry/adapters/v3_to_v2.py`.
- **Refactor notes/tests:** see `NOTES_SCHEMA_REFACTOR.md` and `tests/registry/test_schema_refactor_smoke.py`.

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement now maps to `31647` (initial lobe) + `31651` (each additional lobe), and valve removal maps to `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## Recent Updates (2026-02-05)

- **Hierarchy of truth (conflict resolution):**
  - **Narrative supersedes header codes**: do not treat `PROCEDURE:` CPT lists as “performed” when `PROCEDURE IN DETAIL:` contradicts (e.g., header says “trach change” but narrative describes ETT intubation → do not extract tracheostomy creation).
  - **Narrative supersedes summary**: complications mentioned in narrative override templated “COMPLICATIONS: None” (see `modules/registry/postprocess/complications_reconcile.py`).
  - **Evidence supersedes checkbox heuristics**: unchecked template items must *not* force a procedure to `performed=false` when explicit active-voice narrative evidence supports `true` (see `modules/registry/postprocess/template_checkbox_negation.py`).
- **Anti-hallucination: tools ≠ intent**: mentions of tools (snare/forceps/basket/cryoprobe) do not imply debulking/ablation; require action-on-tissue language (tightened CAO modality parsing in `modules/registry/processing/cao_interventions_detail.py`).
- **Puncture ≠ stoma**: tracheal puncture (CPT `31612`) is *not* percutaneous tracheostomy creation; extraction and CPT derivation distinguish puncture-only from trach creation.
- **Intraprocedural adjustment bundling**:
  - BLVR valve remove/replace in the same session is an adjustment, not foreign body removal; do not derive `31635` for valve exchanges.
  - BLVR now tracks segment tokens (e.g., `RB10`) and counts **final deployed valves** only (removed/replaced devices are not counted).
- **Distinct targets for unbundling**: suppress `31629` when EBUS-TBNA is present unless `peripheral_tbna.targets_sampled` clearly indicates a non-station, anatomically distinct target.

## Extraction‑First Pipeline Notes

Key path: `modules/registry/application/registry_service.py:_extract_fields_extraction_first()`

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner` runs:
  - Path A: Granular NER → registry mapping → deterministic registry→CPT rules
  - Path B: registry ML predictor (if available); falls back safely when unavailable
- **Deterministic uplift:** in `parallel_ner`, common missed flags are filled from deterministic extractors
  (BAL/EBBx/radial EBUS/cryotherapy + navigational bronchoscopy backstops + pleural chest tube/pigtail + IPC/tunneled pleural catheter + chest ultrasound) and evidence spans are attached.
- **Context/negation guardrails (extraction quality):**
  - **Stents**: inspection-only phrases (e.g., “stent … in good position”) should *not* trigger stent placement (`31636`).
  - **Chest tubes**: discontinue/removal phrases (e.g., “D/c chest tube”) should *not* trigger insertion (`32551`).
  - **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional`. Use `peripheral_tbna` for lung/lesion TBNA; when peripheral TBNA co-occurs with EBUS (`31652/31653`), keep `31629` with Modifier `59` (distinct site).
  - **Tools ≠ intent**: do not infer `31641`/`31640` from tools alone (snare/cryoprobe/forceps); require therapeutic intent + tissue action language.
  - **Puncture ≠ stoma**: tracheal puncture language should not set percutaneous trach performed.
  - **Header vs narrative**: procedure header CPT/menu content is not source-of-truth when contradicted by the narrative.
  - **Radial EBUS**: explicit “radial probe …” language should set `radial_ebus.performed` even without concentric/eccentric markers.
  - **Menu masking**: `mask_extraction_noise()` strips CPT/menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations.
- **Omission scan:** `modules/registry/self_correction/keyword_guard.py:scan_for_omissions()` emits
  `SILENT_FAILURE:` warnings for high-value missed procedures; these should surface to the UI via `/api/v1/process`.
- **LLM self-correction:** enable with `REGISTRY_SELF_CORRECT_ENABLED=1` (recommended). For faster responses, set
  `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.
  - Self-correction only triggers when the RAW-ML auditor emits `high_conf_omissions`, and it is gated by a CPT keyword guard.
  - If you see `SELF_CORRECT_SKIPPED: <CPT>: keyword guard failed (...)`, update `modules/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.

## Evidence Contract (UI Highlighting)

The UI expects V3 evidence items shaped like:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`

See `modules/api/adapters/response_adapter.py:build_v3_evidence_payload()`.

## Granular NER Model Workflow

- Train: see `docs/GRANULAR_NER_UPDATE_WORKFLOW.md`
- Stent labels: `DEV_STENT` (device interaction) vs `NEG_STENT` (explicit absence) vs `CTX_STENT_PRESENT` (present/in good position, no intervention).
- Auto-label helper: `python scripts/label_neg_stent.py` (dry-run by default; use `--write` to persist).
- Training allowlist lives in `scripts/train_registry_ner.py:ALLOWED_LABEL_TYPES`.
- Typical command:
  - `python scripts/train_registry_ner.py --data data/ml_training/granular_ner/ner_bio_format_refined.jsonl --output-dir artifacts/registry_biomedbert_ner_v2 ...`
- Run server with the model:
  - set `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner` (in `.env` or shell)

## Common Pitfalls

- Don’t confuse **pipeline mode** with **extraction engine**:
  - pipeline mode is `extraction_first`
  - extraction engine is `parallel_ner`
- Avoid reintroducing duplicate routes: `/api/v1/process` lives in the router module and is the single source of truth.

```

---
### `pyproject.toml`
```
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "proc-suite"
version = "0.1.0"
requires-python = ">=3.11,<3.14"
dependencies = [
  "pydantic>=2.6,<3",
  "jinja2>=3.1,<4",
  "spacy>=3.7,<4",
  "scispacy==0.5.4",
  "en-core-sci-sm @ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz",
  "medspacy>=1.0,<2",
  "sqlalchemy>=2.0,<3",
  "alembic>=1.13,<2",
  "scikit-learn>=1.5.2,<2.0",
  "scikit-multilearn>=0.2.0,<1",
  "pandas>=2.0,<3",
  "psycopg[binary,pool]>=3.2,<4",
  "python-dotenv>=1.0,<2",
  "rapidfuzz>=3.9,<4",
  "regex>=2024.4.28",
  "jsonschema>=4.23,<5",
  "typer>=0.12,<0.17",
  "rich>=13,<14",
  "httpx>=0.27,<1",
  "boto3>=1.34,<2",
  "google-auth>=2.23,<3",
  "google-generativeai>=0.8,<1",
  "cryptography>=42.0,<45",
  "presidio-analyzer>=2.2,<3",
  "pyyaml>=6.0,<7",
  "onnx>=1.16,<2",
  "optimum[onnxruntime]>=1.20,<2",
]

[project.optional-dependencies]
api = [
  "fastapi>=0.115",
  "uvicorn>=0.30",
]
dev = [
  "pytest",
  "pytest-cov",
  "ruff",
  "mypy",
  "types-regex",
  "httpx",
  "pytest-asyncio",
]

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
"modules.reporting" = ["templates/*.jinja", "templates/**/*.jinja", "templates/**/*.j2", "templates/.keep"]
"configs" = ["**/*.yaml", "**/*.json", "**/*.j2"]
"modules.api" = ["static/**/*"]

[tool.pytest.ini_options]
addopts = "-ra -q"
testpaths = ["tests"]
pythonpath = ["."]
markers = [
    "ebus: mark test as EBUS-specific registry extraction test"
]

[tool.ruff]
line-length = 100
extend-exclude = [
  "proc_nlp",
  "proc_schemas",
  "proc_suite.egg-info",
  "modules/autocode",
  "modules/reporting",
  "modules/registry/legacy",
]
include = [
  "modules/api/**/*.py",
  "modules/common/knowledge*.py",
  "modules/common/knowledge_cli.py",
  "modules/registry/cli.py",
  "modules/reporter/cli.py",
  "tests/api/**/*.py",
  "tests/unit/test_knowledge.py",
  "tests/conftest.py",
  "tests/coder/test_coder_smoke.py",
]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
extend-ignore = ["UP006", "UP035"]

[tool.ruff.lint.per-file-ignores]
"modules/coder/dictionary.py" = ["E501"]

[tool.mypy]
strict = true
plugins = []
exclude = [
    "archive/",
    "docs/",
    "_archive/",
    "data/",
    "scripts/",
    "tests/",
    "procedure_suite_ml_implimentation/",
]
explicit_package_bases = true

```

---
### `requirements.txt`
```
# Requirements for Railway deployment
# Generated from pyproject.toml

# Core dependencies
pydantic>=2.6,<3
jinja2>=3.1,<4
spacy>=3.7,<4
scispacy==0.5.4
# spaCy language model required for umls_linker
en-core-sci-sm @ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz
medspacy>=1.0,<2
sqlalchemy>=2.0,<3
alembic>=1.13,<2
scikit-learn>=1.5.2,<2.0
scikit-multilearn>=0.2.0,<1
pandas>=2.0,<3
psycopg[binary,pool]>=3.2,<4
python-dotenv>=1.0,<2
cryptography>=46.0,<47
rapidfuzz>=3.9,<4
regex>=2024.4.28
jsonschema>=4.23,<5
typer>=0.12,<0.17
rich>=13,<14
httpx>=0.27,<1
boto3>=1.34,<2
google-auth>=2.23,<3
google-generativeai>=0.8,<1
presidio-analyzer>=2.2,<3
pyyaml>=6.0,<7

# ONNX inference (for BiomedBERT registry predictor)
onnx>=1.16,<2
onnxruntime>=1.16,<2
transformers>=4.35,<5
optimum[onnxruntime]>=1.20,<2

# API dependencies (required for FastAPI server)
fastapi>=0.115
uvicorn>=0.30

pydantic-settings>=2.0.0
gunicorn==21.2.0


```

---
### `Makefile`
```
SHELL := /bin/bash
.PHONY: setup lint typecheck test validate-schemas validate-kb validate-knowledge-release test-kb-strict autopatch autocommit codex-train codex-metrics run-coder distill-phi distill-phi-silver sanitize-phi-silver normalize-phi-silver build-phi-platinum eval-phi-client audit-phi-client patch-phi-client-hardneg finetune-phi-client-hardneg finetune-phi-client-hardneg-cpu export-phi-client-model export-phi-client-model-quant export-phi-client-model-quant-static dev-iu pull-model-pytorch prodigy-prepare prodigy-prepare-file prodigy-annotate prodigy-export prodigy-retrain prodigy-finetune prodigy-cycle prodigy-clear-unannotated prodigy-prepare-registry prodigy-annotate-registry prodigy-export-registry prodigy-merge-registry prodigy-retrain-registry prodigy-registry-cycle registry-prodigy-prepare registry-prodigy-annotate registry-prodigy-export check-corrections-fresh gold-export gold-split gold-train gold-finetune gold-audit gold-eval gold-cycle gold-incremental platinum-test platinum-build platinum-sanitize platinum-apply platinum-apply-dry platinum-cycle platinum-final registry-prep registry-prep-with-human registry-prep-dry registry-prep-final registry-prep-raw registry-prep-module test-registry-prep

# Use conda environment medparse-py311 (Python 3.11)
CONDA_ACTIVATE := source ~/miniconda3/etc/profile.d/conda.sh && conda activate medparse-py311
SETUP_STAMP := .setup.stamp
PYTHON := python
KB_PATH := data/knowledge/ip_coding_billing_v3_0.json
SCHEMA_PATH := data/knowledge/IP_Registry.json
NOTES_PATH := data/knowledge/synthetic_notes_with_registry2.json
PORT ?= 8000
MODEL_BACKEND ?= pytorch
PROCSUITE_SKIP_WARMUP ?= 1
REGISTRY_RUNTIME_DIR ?= data/models/registry_runtime
DEVICE ?= cpu
PRODIGY_EPOCHS ?= 1

setup:
	@if [ -f $(SETUP_STAMP) ]; then echo "Setup already done"; exit 0; fi
	$(CONDA_ACTIVATE) && pip install -r requirements.txt
	touch $(SETUP_STAMP)

lint:
	$(CONDA_ACTIVATE) && ruff check --cache-dir .ruff_cache .

typecheck:
	$(CONDA_ACTIVATE) && mypy --cache-dir .mypy_cache proc_schemas config observability

test:
	$(CONDA_ACTIVATE) && pytest

# Validate JSON schemas and Pydantic models
validate-schemas:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/validate_jsonschema.py --schema $(SCHEMA_PATH) || true
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/check_pydantic_models.py

# Validate knowledge base
validate-kb:
	@echo "Validating knowledge base at $(KB_PATH)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import json; json.load(open('$(KB_PATH)'))" && echo "KB JSON valid"

# Validate KB + schema integration (no-op extraction)
validate-knowledge-release:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/validate_knowledge_release.py --kb $(KB_PATH) --schema $(SCHEMA_PATH)

# Run regression tests with KB Strict Mode to catch orphan codes
test-kb-strict:
	@echo "Running smoke tests in KB STRICT mode..."
	$(CONDA_ACTIVATE) && PROCSUITE_PIPELINE_MODE=extraction_first PSUITE_KB_STRICT=1 pytest tests/coder/test_coding_rules_phase7.py -v
	$(CONDA_ACTIVATE) && PROCSUITE_PIPELINE_MODE=extraction_first PSUITE_KB_STRICT=1 $(PYTHON) scripts/registry_pipeline_smoke_batch.py --count 10 --notes-dir "tests/fixtures/notes"

# Knowledge diff report (set OLD_KB=...; NEW_KB defaults to KB_PATH)
OLD_KB ?=
NEW_KB ?= $(KB_PATH)

knowledge-diff:
	@if [ -z "$(OLD_KB)" ]; then echo "ERROR: Set OLD_KB=path/to/old_kb.json"; exit 2; fi
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/knowledge_diff_report.py --old $(OLD_KB) --new $(NEW_KB)

# Run the smart-hybrid coder over notes
run-coder:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/coder_suggestions.jsonl

distill-phi:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model artifacts/phi_distilbert_ner \
		--device cpu

distill-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model artifacts/phi_distilbert_ner \
		--label-schema standard \
		--device $(DEVICE)

sanitize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/sanitize_dataset.py \
		--in data/ml_training/distilled_phi_labels.jsonl \
		--out data/ml_training/distilled_phi_CLEANED.jsonl

normalize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/normalize_phi_labels.py \
		--in data/ml_training/distilled_phi_CLEANED.jsonl \
		--out data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--password-policy id

eval-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--eval-only

audit-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/audit_model_fp.py \
		--model-dir artifacts/phi_distilbert_ner \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--limit 5000

patch-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_hard_negative_patch.py \
		--audit-report artifacts/phi_distilbert_ner/audit_report.json \
		--data-in data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--data-out data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl

# Default: MPS with memory-saving options (gradient accumulation, smaller batches)
# Removes MPS memory limits to use available system RAM
# If OOM on Apple Silicon, use: make finetune-phi-client-hardneg-cpu
finetune-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl \
		--epochs 1 \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--save-steps 500 \
		--eval-steps 500 \
		--logging-steps 50

# CPU fallback: reliable but slower (~5-6 hours for 1 epoch)
finetune-phi-client-hardneg-cpu:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl \
		--epochs 1 \
		--lr 1e-5 \
		--train-batch 8 \
		--eval-batch 16 \
		--save-steps 500 \
		--eval-steps 500 \
		--logging-steps 50 \
		--cpu

export-phi-client-model:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner

export-phi-client-model-quant:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize

export-phi-client-model-quant-static:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize --static-quantize

build-phi-platinum:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/phi_platinum_spans.jsonl

# Prodigy-based PHI label correction workflow
PRODIGY_COUNT ?= 100
PRODIGY_DATASET ?= phi_corrections
# Prodigy should run in the same environment as the rest of the tooling.
# (The previous default hardcoded a macOS system Python path and breaks on Linux/WSL.)
PRODIGY_PYTHON ?= $(PYTHON)

prodigy-prepare:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

# Prepare from a specific input file (e.g., synthetic_phi.jsonl)
PRODIGY_INPUT_FILE ?= synthetic_phi.jsonl
prodigy-prepare-file:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--input-file $(PRODIGY_INPUT_FILE) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

prodigy-annotate:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) -m prodigy ner.manual $(PRODIGY_DATASET) blank:en \
		data/ml_training/prodigy_batch.jsonl \
		--label PATIENT,DATE,ID,GEO,CONTACT

prodigy-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) scripts/prodigy_export_corrections.py \
		--dataset $(PRODIGY_DATASET) \
		--merge-with data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl

# Train from scratch on corrected data
prodigy-retrain:
	@echo "Training from scratch on corrected data..."
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--epochs 3 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0

# Corrections file for Prodigy workflow
CORRECTIONS_FILE := data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl

# Guard: Ensure corrections file exists before fine-tuning
check-corrections-fresh:
	@if [ ! -f $(CORRECTIONS_FILE) ]; then \
		echo "ERROR: $(CORRECTIONS_FILE) not found."; \
		echo "Run 'make prodigy-export' first to export Prodigy corrections."; \
		exit 1; \
	fi
	@echo "Using corrections file: $(CORRECTIONS_FILE)"
	@echo "Last modified: $$(stat -f '%Sm' $(CORRECTIONS_FILE) 2>/dev/null || stat -c '%y' $(CORRECTIONS_FILE) 2>/dev/null || echo 'unknown')"

# Fine-tune existing model on corrected data (recommended for iterative improvement)
# Override epochs: make prodigy-finetune PRODIGY_EPOCHS=3
prodigy-finetune: check-corrections-fresh
	@echo "Fine-tuning existing model on corrected data..."
	@echo "Epochs: $(PRODIGY_EPOCHS)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--epochs $(PRODIGY_EPOCHS) \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0

prodigy-cycle: prodigy-prepare
	@echo "Batch prepared at data/ml_training/prodigy_batch.jsonl"
	@echo "Run 'make prodigy-annotate' to start Prodigy annotation UI"
	@echo "After annotation, run 'make prodigy-export' then either:"
	@echo "  make prodigy-finetune  (recommended - preserves learned weights)"
	@echo "  make prodigy-retrain   (train from scratch)"

# Clear unannotated examples from Prodigy batch file
prodigy-clear-unannotated:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/clear_unannotated_prodigy_batch.py \
		--batch-file data/ml_training/prodigy_batch.jsonl \
		--dataset $(PRODIGY_DATASET) \
		--backup

# ==============================================================================
# Registry Prodigy Workflow (Multi-Label Classification)
# ==============================================================================
# Requires:
#   make registry-prep-final (or otherwise produce registry_train/val/test.csv)
#   and a JSONL of unlabeled notes at $(PRODIGY_REGISTRY_INPUT_FILE)
#
# Workflow: prepare → annotate → export → merge → retrain

PRODIGY_REGISTRY_COUNT ?= 200
PRODIGY_REGISTRY_DATASET ?= registry_corrections_v1
PRODIGY_REGISTRY_INPUT_FILE ?= data/ml_training/registry_unlabeled_notes.jsonl
PRODIGY_REGISTRY_STRATEGY ?= hybrid
PRODIGY_REGISTRY_MODEL_DIR ?= data/models/registry_runtime

PRODIGY_REGISTRY_BATCH_FILE ?= data/ml_training/prodigy_registry_batch.jsonl
PRODIGY_REGISTRY_MANIFEST ?= data/ml_training/prodigy_registry_manifest.json
PRODIGY_REGISTRY_EXPORT_CSV ?= data/ml_training/registry_prodigy_labels.csv
PRODIGY_REGISTRY_TRAIN_AUGMENTED ?= data/ml_training/registry_train_augmented.csv

prodigy-prepare-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_registry.py \
		--input-file $(PRODIGY_REGISTRY_INPUT_FILE) \
		--output-file $(PRODIGY_REGISTRY_BATCH_FILE) \
		--count $(PRODIGY_REGISTRY_COUNT) \
		--strategy $(PRODIGY_REGISTRY_STRATEGY) \
		--model-dir $(PRODIGY_REGISTRY_MODEL_DIR) \
		--manifest $(PRODIGY_REGISTRY_MANIFEST) \
		--exclude-csv data/ml_training/registry_train.csv

prodigy-annotate-registry:
	$(CONDA_ACTIVATE) && LABELS="$$( $(PYTHON) -c 'from modules.ml_coder.registry_label_schema import REGISTRY_LABELS; print(",".join(REGISTRY_LABELS))' )" && \
		$(PRODIGY_PYTHON) -m prodigy textcat.manual $(PRODIGY_REGISTRY_DATASET) \
		$(PRODIGY_REGISTRY_BATCH_FILE) \
		--label $$LABELS

prodigy-export-registry:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) scripts/prodigy_export_registry.py \
		--dataset $(PRODIGY_REGISTRY_DATASET) \
		--output-csv $(PRODIGY_REGISTRY_EXPORT_CSV)

prodigy-merge-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/merge_registry_prodigy.py \
		--base-train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--prodigy-csv $(PRODIGY_REGISTRY_EXPORT_CSV) \
		--out-csv $(PRODIGY_REGISTRY_TRAIN_AUGMENTED)

prodigy-retrain-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_roberta.py \
		--train-csv $(PRODIGY_REGISTRY_TRAIN_AUGMENTED) \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--output-dir data/models/roberta_registry

prodigy-registry-cycle: prodigy-prepare-registry
	@echo "Batch prepared at $(PRODIGY_REGISTRY_BATCH_FILE)"
	@echo "Run 'make prodigy-annotate-registry' to start Prodigy UI (textcat)"
	@echo "After annotation:"
	@echo "  make prodigy-export-registry"
	@echo "  make prodigy-merge-registry"
	@echo "  make prodigy-retrain-registry"

# ==============================================================================
# Registry Distillation (Teacher → Student)
# ==============================================================================
TEACHER_MODEL_NAME ?= data/models/RoBERTa-base-PM-M3-Voc-distill/RoBERTa-base-PM-M3-Voc-distill-hf
TEACHER_OUTPUT_DIR ?= data/models/registry_teacher
TEACHER_EPOCHS ?= 3

TEACHER_LOGITS_IN ?= data/ml_training/registry_unlabeled_notes.jsonl
TEACHER_LOGITS_OUT ?= data/ml_training/teacher_logits.npz

DISTILL_ALPHA ?= 0.5
DISTILL_TEMP ?= 2.0
DISTILL_LOSS ?= mse
STUDENT_DISTILL_OUTPUT_DIR ?= data/models/roberta_registry_distilled

teacher-train:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_roberta_pm3.py \
		--model-name $(TEACHER_MODEL_NAME) \
		--output-dir $(TEACHER_OUTPUT_DIR) \
		--train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--epochs $(TEACHER_EPOCHS)

teacher-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_roberta_pm3.py \
		--evaluate-only \
		--model-dir $(TEACHER_OUTPUT_DIR) \
		--test-csv data/ml_training/registry_test.csv

teacher-logits:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/generate_teacher_logits.py \
		--model-dir $(TEACHER_OUTPUT_DIR) \
		--input-jsonl $(TEACHER_LOGITS_IN) \
		--out $(TEACHER_LOGITS_OUT)

student-distill:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_roberta.py \
		--train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--teacher-logits $(TEACHER_LOGITS_OUT) \
		--distill-alpha $(DISTILL_ALPHA) \
		--distill-temp $(DISTILL_TEMP) \
		--distill-loss $(DISTILL_LOSS) \
		--output-dir $(STUDENT_DISTILL_OUTPUT_DIR)

registry-overlap-report:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/registry_label_overlap_report.py \
		--csv data/ml_training/registry_train.csv \
		--csv data/ml_training/registry_val.csv \
		--csv data/ml_training/registry_test.csv \
		--out reports/registry_label_overlap.json

# ==============================================================================
# Registry “Diamond Loop” targets (brief-compatible aliases)
# ==============================================================================
REG_PRODIGY_COUNT ?= 200
REG_PRODIGY_DATASET ?= registry_v1
REG_PRODIGY_INPUT_FILE ?= data/ml_training/registry_unlabeled_notes.jsonl
REG_PRODIGY_BATCH_FILE ?= data/ml_training/registry_prodigy_batch.jsonl
REG_PRODIGY_MANIFEST ?= data/ml_training/registry_prodigy_manifest.json
REG_PRODIGY_MODEL_DIR ?= data/models/registry_runtime
REG_PRODIGY_STRATEGY ?= disagreement
REG_PRODIGY_SEED ?= 42
REG_PRODIGY_EXPORT_CSV ?= data/ml_training/registry_human.csv
REG_PRODIGY_RESET_ARCHIVE_DIR ?= data/ml_training/_archive/registry_prodigy

# Relabel workflow (build a review batch from an existing human CSV)
REG_RELABEL_INPUT_CSV ?= data/ml_training/registry_human_v1_backup.csv
REG_RELABEL_OUTPUT_FILE ?= data/ml_training/registry_rigid_review.jsonl
REG_RELABEL_FILTER_LABEL ?= rigid_bronchoscopy
REG_RELABEL_LIMIT ?= 0
REG_RELABEL_PREFILL_NON_THERMAL ?= 1

REG_HUMAN_BASE_CSV ?= data/ml_training/registry_human_v1_backup.csv
REG_HUMAN_UPDATES_CSV ?= data/ml_training/registry_human_rigid_review.csv
REG_HUMAN_OUT_CSV ?= data/ml_training/registry_human_v2.csv

# Reset registry Prodigy state (batch + manifest + Prodigy dataset).
# This is safe to run even if some files/datasets don't exist.
registry-prodigy-reset:
	@mkdir -p $(REG_PRODIGY_RESET_ARCHIVE_DIR)
	@ts="$$(date +%Y%m%d_%H%M%S)"; \
	for f in "$(REG_PRODIGY_BATCH_FILE)" "$(REG_PRODIGY_MANIFEST)"; do \
		if [ -f "$$f" ]; then \
			mv "$$f" "$(REG_PRODIGY_RESET_ARCHIVE_DIR)/$$(basename "$$f").$$ts"; \
			echo "Archived $$f → $(REG_PRODIGY_RESET_ARCHIVE_DIR)/$$(basename "$$f").$$ts"; \
		fi; \
	done
	@$(CONDA_ACTIVATE) && REG_PRODIGY_DATASET="$(REG_PRODIGY_DATASET)" $(PRODIGY_PYTHON) - <<'PY'\nfrom prodigy.components.db import connect\nimport os\n\nds = os.environ.get(\"REG_PRODIGY_DATASET\", \"\").strip()\nif not ds:\n    raise SystemExit(\"REG_PRODIGY_DATASET is empty\")\n\ndb = connect()\nif ds in db.datasets:\n    db.drop_dataset(ds)\n    print(f\"Dropped Prodigy dataset: {ds}\")\nelse:\n    print(f\"Prodigy dataset not found (nothing to drop): {ds}\")\nPY

registry-prodigy-prepare:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_registry_batch.py \
		--input-file $(REG_PRODIGY_INPUT_FILE) \
		--output-file $(REG_PRODIGY_BATCH_FILE) \
		--limit $(REG_PRODIGY_COUNT) \
		--strategy $(REG_PRODIGY_STRATEGY) \
		--manifest $(REG_PRODIGY_MANIFEST) \
		--seed $(REG_PRODIGY_SEED) \
		--model-dir $(REG_PRODIGY_MODEL_DIR)

registry-prodigy-prepare-relabel:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_registry_relabel_batch.py \
		--input-csv $(REG_RELABEL_INPUT_CSV) \
		--output-file $(REG_RELABEL_OUTPUT_FILE) \
		--filter-label $(REG_RELABEL_FILTER_LABEL) \
		--limit $(REG_RELABEL_LIMIT) \
		$(if $(filter 1,$(REG_RELABEL_PREFILL_NON_THERMAL)),--prefill-non-thermal-from-rigid,)

registry-human-merge-updates:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/merge_registry_human_labels.py \
		--base-csv $(REG_HUMAN_BASE_CSV) \
		--updates-csv $(REG_HUMAN_UPDATES_CSV) \
		--out-csv $(REG_HUMAN_OUT_CSV) \
		--prefer-updates-meta

registry-prodigy-annotate:
	$(CONDA_ACTIVATE) && LABELS="$$( $(PYTHON) -c 'from modules.ml_coder.registry_label_schema import REGISTRY_LABELS; print(",".join(REGISTRY_LABELS))' )" && \
		$(PRODIGY_PYTHON) -m prodigy textcat.manual $(REG_PRODIGY_DATASET) $(REG_PRODIGY_BATCH_FILE) \
		--loader jsonl \
		--label $$LABELS

registry-prodigy-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) scripts/prodigy_export_registry.py \
		--dataset $(REG_PRODIGY_DATASET) \
		--output-csv $(REG_PRODIGY_EXPORT_CSV)

# ==============================================================================
# Gold Standard PHI Workflow (Pure Human-Verified Data)
# ==============================================================================
# Uses only Prodigy-verified annotations for maximum quality training.
# Run: make gold-cycle (or individual targets)

GOLD_EPOCHS ?= 10
GOLD_DATASET ?= phi_corrections
GOLD_OUTPUT_DIR ?= data/ml_training
GOLD_MODEL_DIR ?= artifacts/phi_distilbert_ner

# Export pure gold from Prodigy (no merging with old data)
# Run in the same conda env as the rest of the pipeline (WSL/Linux friendly).
gold-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) scripts/export_phi_gold_standard.py \
		--dataset $(GOLD_DATASET) \
		--output $(GOLD_OUTPUT_DIR)/phi_gold_standard_v1.jsonl \
		--model-dir $(GOLD_MODEL_DIR)

# Split into train/test (80/20) with grouping by note ID
gold-split:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/split_phi_gold.py \
		--input $(GOLD_OUTPUT_DIR)/phi_gold_standard_v1.jsonl \
		--train-out $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--test-out $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--seed 42

# Train on pure gold data (Higher epochs for smaller high-quality data)
gold-train:
	@echo "Training on pure Gold Standard data..."
	@echo "Epochs: $(GOLD_EPOCHS)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--resume-from $(GOLD_MODEL_DIR) \
		--output-dir $(GOLD_MODEL_DIR) \
		--epochs $(GOLD_EPOCHS) \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--eval-steps 100 \
		--save-steps 200 \
		--logging-steps 50

# Audit on gold test set (Critical for safety verification)
gold-audit:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/audit_model_fp.py \
		--model-dir $(GOLD_MODEL_DIR) \
		--data $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--report-out $(GOLD_MODEL_DIR)/audit_gold_report.json

# Evaluate metrics on gold test set
gold-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--output-dir $(GOLD_MODEL_DIR) \
		--eval-only

# Full cycle: export → split → train → audit → eval
gold-cycle: gold-export gold-split gold-train gold-audit gold-eval
	@echo "Gold standard workflow complete."
	@echo "Audit report: $(GOLD_MODEL_DIR)/audit_gold_report.json"

# Light fine-tune on expanded gold data (fewer epochs, for incremental updates)
GOLD_FINETUNE_EPOCHS ?= 3
gold-finetune:
	@echo "Fine-tuning on expanded Gold Standard data..."
	@echo "Epochs: $(GOLD_FINETUNE_EPOCHS) (use GOLD_FINETUNE_EPOCHS=N to override)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--resume-from $(GOLD_MODEL_DIR) \
		--output-dir $(GOLD_MODEL_DIR) \
		--epochs $(GOLD_FINETUNE_EPOCHS) \
		--lr 5e-6 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--eval-steps 50 \
		--save-steps 100 \
		--logging-steps 25

# Incremental cycle: export → split → finetune → audit (lighter than full train)
gold-incremental: gold-export gold-split gold-finetune gold-audit
	@echo "Incremental gold update complete."

# ==============================================================================
# Platinum PHI Workflow (Registry ML Preprocessing)
# ==============================================================================
# Generates high-quality PHI-scrubbed training data for Registry Model.
# Platinum = Hybrid Redactor (ML+Regex) → char spans → apply [REDACTED] to golden JSONs

PLATINUM_SPANS_FILE ?= data/ml_training/phi_platinum_spans.jsonl
PLATINUM_SPANS_CLEANED ?= data/ml_training/phi_platinum_spans_CLEANED.jsonl
PLATINUM_INPUT_DIR ?= data/knowledge/golden_extractions
PLATINUM_OUTPUT_DIR ?= data/knowledge/golden_extractions_scrubbed
PLATINUM_FINAL_DIR ?= data/knowledge/golden_extractions_final

# Test run (small batch to validate pipeline)
platinum-test:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 100
	@echo "Test run complete. Check $(PLATINUM_SPANS_FILE) for span output."

# Build full platinum spans (all notes)
platinum-build:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 0
	@echo "Platinum spans built: $(PLATINUM_SPANS_FILE)"

# Sanitize platinum spans (post-hoc cleanup)
platinum-sanitize:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/sanitize_platinum_spans.py \
		--in $(PLATINUM_SPANS_FILE) \
		--out $(PLATINUM_SPANS_CLEANED)
	@echo "Sanitized spans: $(PLATINUM_SPANS_CLEANED)"

# Apply redactions to create scrubbed golden JSONs
platinum-apply:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/apply_platinum_redactions.py \
		--spans $(PLATINUM_SPANS_CLEANED) \
		--input-dir $(PLATINUM_INPUT_DIR) \
		--output-dir $(PLATINUM_OUTPUT_DIR)
	@echo "Scrubbed golden JSONs: $(PLATINUM_OUTPUT_DIR)"

# Dry run (show what would be done without writing files)
platinum-apply-dry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/apply_platinum_redactions.py \
		--spans $(PLATINUM_SPANS_CLEANED) \
		--input-dir $(PLATINUM_INPUT_DIR) \
		--output-dir $(PLATINUM_OUTPUT_DIR) \
		--dry-run

# Full platinum cycle: build → sanitize → apply
platinum-cycle: platinum-build platinum-sanitize platinum-apply
	@echo "----------------------------------------------------------------"
	@echo "SUCCESS: Scrubbed Golden JSONs are ready."
	@echo "Location: $(PLATINUM_OUTPUT_DIR)"
	@echo "Next: Use scrubbed data for registry ML training"
	@echo "----------------------------------------------------------------"

# Post-processing: clean hallucinated institution fields and write final output set
platinum-final: platinum-cycle
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/fix_registry_hallucinations.py \
		--input-dir $(PLATINUM_OUTPUT_DIR) \
		--output-dir $(PLATINUM_FINAL_DIR)
	@echo "Final cleaned Golden JSONs: $(PLATINUM_FINAL_DIR)"

pull-model-pytorch:
	MODEL_BUNDLE_S3_URI_PYTORCH="$(MODEL_BUNDLE_S3_URI_PYTORCH)" REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" ./scripts/dev_pull_model.sh

dev-iu:
	$(CONDA_ACTIVATE) && \
		MODEL_BACKEND="$(MODEL_BACKEND)" \
		REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" \
		PROCSUITE_SKIP_WARMUP="$(PROCSUITE_SKIP_WARMUP)" \
		RAILWAY_ENVIRONMENT="local" \
		$(PYTHON) -m uvicorn modules.api.fastapi_app:app --reload --host 0.0.0.0 --port "$(PORT)"

# Run cleaning pipeline with patches
autopatch:
	@mkdir -p autopatches reports
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_cleaning_pipeline.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--schema $(SCHEMA_PATH) \
		--out-json autopatches/patches.json \
		--out-csv reports/errors.csv \
		--apply-minimal-fixes || true

# Autocommit generated patches/reports
autocommit:
	@git add .
	@git commit -m "Autocommit: generated patches/reports" || true

# Run codex training pipeline (full CI-like flow)
codex-train: setup lint typecheck test validate-schemas validate-kb autopatch
	@echo "Codex training pipeline complete"

# Run metrics over a batch of notes
codex-metrics: setup
	@mkdir -p outputs
	@echo "Running metrics pipeline..."
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/metrics_run.jsonl
	@echo "Metrics written to outputs/metrics_run.jsonl"

# Clean generated files
clean:
	rm -rf $(SETUP_STAMP)
	rm -rf .ruff_cache .mypy_cache .pytest_cache
	rm -rf outputs autopatches reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Help target
help:
	@echo "Available targets:"
	@echo "  setup          - Install dependencies in conda env medparse-py311"
	@echo "  lint           - Run ruff linter"
	@echo "  typecheck      - Run mypy type checker"
	@echo "  test           - Run pytest"
	@echo "  validate-schemas - Validate JSON schemas and Pydantic models"
	@echo "  validate-kb    - Validate knowledge base"
	@echo "  run-coder      - Run smart-hybrid coder over notes"
	@echo "  distill-phi    - Distill PHI labels for student NER training"
	@echo "  distill-phi-silver - Distill Piiranha silver PHI labels"
	@echo "  sanitize-phi-silver - Post-hoc sanitizer for silver PHI labels"
	@echo "  normalize-phi-silver - Normalize silver labels to stable schema"
	@echo "  build-phi-platinum - Build hybrid redactor PHI spans"
	@echo "  eval-phi-client - Evaluate DistilBERT NER model (no retraining)"
	@echo "  audit-phi-client - Run false-positive audit guardrails"
	@echo "  patch-phi-client-hardneg - Patch training data with audit violations"
	@echo "  finetune-phi-client-hardneg - Finetune model on hard negatives (MPS w/ gradient accumulation)"
	@echo "  finetune-phi-client-hardneg-cpu - Finetune on CPU (slower but reliable fallback)"
	@echo "  export-phi-client-model - Export client-side ONNX bundle (unquantized) for transformers.js"
	@echo "  export-phi-client-model-quant - Export client-side ONNX bundle + INT8 quantized model (dynamic)"
	@echo "  export-phi-client-model-quant-static - Export client-side ONNX bundle + INT8 quantized model (static, smaller)"
	@echo "  prodigy-prepare - Prepare batch for Prodigy annotation (PRODIGY_COUNT=100)"
	@echo "  prodigy-annotate - Launch Prodigy annotation UI (PRODIGY_DATASET=phi_corrections)"
	@echo "  prodigy-export  - Export Prodigy corrections to training format"
	@echo "  prodigy-retrain - Retrain model from scratch with corrections"
	@echo "  prodigy-finetune - Fine-tune existing model with corrections (recommended)"
	@echo "                    Override epochs: make prodigy-finetune PRODIGY_EPOCHS=3"
	@echo "  prodigy-cycle   - Full Prodigy iteration workflow"
	@echo "  prodigy-clear-unannotated - Remove unannotated examples from batch file"
	@echo ""
	@echo "Registry Prodigy Workflow (multi-label classification):"
	@echo "  prodigy-prepare-registry - Prepare batch for Prodigy choice (PRODIGY_REGISTRY_COUNT=200)"
	@echo "  prodigy-annotate-registry - Launch Prodigy UI (PRODIGY_REGISTRY_DATASET=registry_corrections_v1)"
	@echo "  prodigy-export-registry  - Export accepted labels to CSV"
	@echo "  prodigy-merge-registry   - Merge Prodigy labels into train split (leakage-guarded)"
	@echo "  prodigy-retrain-registry - Retrain registry classifier on augmented train split"
	@echo "  prodigy-registry-cycle   - Convenience: prepare + instructions"
	@echo ""
	@echo "Gold Standard PHI Workflow (pure human-verified data):"
	@echo "  gold-export    - Export pure gold from Prodigy dataset"
	@echo "  gold-split     - 80/20 train/test split with note grouping"
	@echo "  gold-train     - Train on gold data (10 epochs default)"
	@echo "  gold-finetune  - Light fine-tune (3 epochs, lower LR) for incremental updates"
	@echo "  gold-audit     - Safety audit on gold test set"
	@echo "  gold-eval      - Evaluate metrics on gold test set"
	@echo "  gold-cycle     - Full workflow: export → split → train → audit → eval"
	@echo "  gold-incremental - Incremental: export → split → finetune → audit"
	@echo ""
	@echo "Platinum PHI Workflow (Registry ML Preprocessing):"
	@echo "  platinum-test  - Test run on 100 notes to validate pipeline"
	@echo "  platinum-build - Build full platinum spans from all golden JSONs"
	@echo "  platinum-sanitize - Post-hoc cleanup of platinum spans"
	@echo "  platinum-apply - Apply [REDACTED] to golden JSONs"
	@echo "  platinum-apply-dry - Dry run (show what would be done)"
	@echo "  platinum-cycle - Full workflow: build → sanitize → apply"
	@echo ""
	@echo "  autopatch      - Generate patches for registry cleaning"
	@echo "  autocommit     - Git commit generated files"
	@echo "  codex-train    - Full training pipeline"
	@echo "  codex-metrics  - Run metrics over notes batch"
	@echo "  clean          - Remove generated files"
	@echo ""
	@echo "Registry-First ML Data Preparation:"
	@echo "  registry-prep       - Full pipeline: extract, split, save CSVs"
	@echo "  registry-prep-dry   - Validate without saving files"
	@echo "  registry-prep-final - Use PHI-scrubbed final data (recommended)"
	@echo "  registry-prep-module - Use module integration (prepare_registry_training_splits)"
	@echo "  test-registry-prep  - Run registry data prep tests"

# ==============================================================================
# Registry-First ML Training Data Preparation
# ==============================================================================
# Add these targets to your existing Makefile to enable the registry-first
# training data workflow.
#
# Usage:
#   make registry-prep          # Full pipeline: extract, split, save CSVs
#   make registry-prep-dry      # Validate without saving files
#   make registry-prep-final    # Use PHI-scrubbed final data
#
# Output files:
#   data/ml_training/registry_train.csv
#   data/ml_training/registry_val.csv
#   data/ml_training/registry_test.csv
#   data/ml_training/registry_meta.json

# Configuration
REGISTRY_INPUT_DIR ?= data/knowledge/golden_extractions_final
REGISTRY_OUTPUT_DIR ?= data/ml_training
REGISTRY_PREFIX ?= registry
REGISTRY_MIN_LABEL_COUNT ?= 5
REGISTRY_SEED ?= 42

# Full pipeline
registry-prep:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--min-label-count $(REGISTRY_MIN_LABEL_COUNT) \
		--random-seed $(REGISTRY_SEED)

# Full pipeline + Tier-0 merge of human labels (Diamond Loop)
HUMAN_REGISTRY_CSV ?=
registry-prep-with-human:
	@if [ -z "$(HUMAN_REGISTRY_CSV)" ]; then \
		echo "ERROR: HUMAN_REGISTRY_CSV is required (e.g. make registry-prep-with-human HUMAN_REGISTRY_CSV=/tmp/registry_human.csv)"; \
		exit 1; \
	fi
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--min-label-count $(REGISTRY_MIN_LABEL_COUNT) \
		--random-seed $(REGISTRY_SEED) \
		--human-labels-csv $(HUMAN_REGISTRY_CSV)

# Dry run (validate only)
registry-prep-dry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--dry-run

# Use PHI-scrubbed final data (recommended for production)
registry-prep-final:
	$(MAKE) registry-prep REGISTRY_INPUT_DIR=data/knowledge/golden_extractions_final

# Use raw golden extractions (for development/testing)
registry-prep-raw:
	$(MAKE) registry-prep REGISTRY_INPUT_DIR=data/knowledge/golden_extractions

# Alternative: Use the module integration
registry-prep-module:
	$(CONDA_ACTIVATE) && $(PYTHON) -c " \
from modules.ml_coder.registry_data_prep import prepare_registry_training_splits; \
train, val, test = prepare_registry_training_splits(); \
train.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_train.csv', index=False); \
val.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_val.csv', index=False); \
test.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_test.csv', index=False); \
print(f'Train: {len(train)}, Val: {len(val)}, Test: {len(test)}')"

# Test the data prep module
test-registry-prep:
	$(CONDA_ACTIVATE) && pytest tests/ml_coder/test_registry_first_data_prep.py -v

```

---
### `runtime.txt`
```
python-3.11



```

---
### `modules/api/fastapi_app.py`
```
"""FastAPI application wiring for the Procedure Suite services.

⚠️ SOURCE OF TRUTH: This is the MAIN FastAPI application.
- Running on port 8000 via scripts/devserver.sh
- Uses CodingService from modules/coder/application/coding_service.py (new hexagonal architecture)
- DO NOT edit api/app.py - it's deprecated

See AI_ASSISTANT_GUIDE.md for details.
"""

# ruff: noqa: E402

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any, AsyncIterator, List

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _env_value(name: str) -> str:
    return os.getenv(name, "").strip().lower()


def _validate_startup_env() -> None:
    pipeline_mode = _env_value("PROCSUITE_PIPELINE_MODE")
    if pipeline_mode != "extraction_first":
        if pipeline_mode == "parallel_ner":
            raise RuntimeError(
                "PROCSUITE_PIPELINE_MODE=parallel_ner is invalid; use extraction_first."
            )
        raise RuntimeError(
            f"PROCSUITE_PIPELINE_MODE must be 'extraction_first', got '{pipeline_mode or 'unset'}'."
        )

    # In production we enforce a single, deterministic configuration to prevent drift.
    # In dev/tests we allow experimentation (e.g., engine-based extraction).
    is_production = _truthy_env("CODER_REQUIRE_PHI_REVIEW") or (
        _env_value("PROCSUITE_ENV") == "production"
    )
    if not is_production:
        return

    extraction_engine = _env_value("REGISTRY_EXTRACTION_ENGINE")
    allow_registry_engine_override = _truthy_env("PROCSUITE_ALLOW_REGISTRY_ENGINE_OVERRIDE")
    if extraction_engine != "parallel_ner" and not allow_registry_engine_override:
        raise RuntimeError(
            "REGISTRY_EXTRACTION_ENGINE must be 'parallel_ner' in production "
            "(or set PROCSUITE_ALLOW_REGISTRY_ENGINE_OVERRIDE=true for an explicit override)."
        )
    if extraction_engine != "parallel_ner" and allow_registry_engine_override:
        logging.getLogger(__name__).warning(
            "Production override enabled: REGISTRY_EXTRACTION_ENGINE=%s (expected parallel_ner).",
            extraction_engine,
        )

    schema_version = _env_value("REGISTRY_SCHEMA_VERSION")
    if schema_version != "v3":
        raise RuntimeError("REGISTRY_SCHEMA_VERSION must be 'v3' in production.")

    auditor_source = _env_value("REGISTRY_AUDITOR_SOURCE")
    if auditor_source != "raw_ml":
        raise RuntimeError("REGISTRY_AUDITOR_SOURCE must be 'raw_ml' in production.")


# Prefer explicitly-exported environment variables over values in `.env`.
# Tests can opt out (and avoid accidental real network calls) by setting `PROCSUITE_SKIP_DOTENV=1`.
if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    try:
        load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Failed to load .env via python-dotenv (%s); proceeding with OS env only",
            type(e).__name__,
        )

from config.settings import CoderSettings
from modules.api.adapters.response_adapter import build_v3_evidence_payload
from modules.api.coder_adapter import convert_coding_result_to_coder_output
from modules.api.dependencies import (
    get_coding_service,
    get_qa_pipeline_service,
    get_registry_service,
)
from modules.api.guards import (
    enforce_legacy_endpoints_allowed,
    enforce_request_mode_override_allowed,
)

# Coding entry points:
# - Primary: /api/v1/procedures/{id}/codes/suggest (CodingService, PHI-gated)
# - Legacy shim: /v1/coder/run (non-PHI/synthetic only; blocked when CODER_REQUIRE_PHI_REVIEW=true)
# Import ML Advisor router
from modules.api.ml_advisor_router import router as ml_advisor_router
from modules.api.normalization import simplify_billing_cpt_codes
from modules.api.phi_dependencies import get_phi_scrubber
from modules.api.phi_redaction import apply_phi_redaction
from modules.api.readiness import require_ready
from modules.api.routes.metrics import router as metrics_router
from modules.api.routes.phi import router as phi_router
from modules.api.routes.phi_demo_cases import router as phi_demo_router
from modules.api.routes.procedure_codes import router as procedure_codes_router
from modules.api.routes.registry_runs import router as registry_runs_router
from modules.api.routes.unified_process import router as unified_process_router
from modules.api.routes_registry import _prune_none
from modules.api.routes_registry import router as registry_extract_router

# All API schemas (base + QA pipeline)
from modules.api.schemas import (
    # QA pipeline schemas
    CodeEntry,
    CoderData,
    # Base schemas
    CoderRequest,
    CoderResponse,
    HybridPipelineMetadata,
    KnowledgeMeta,
    ModuleResult,
    ModuleStatus,
    QARunRequest,
    QARunResponse,
    QuestionsRequest,
    QuestionsResponse,
    RegistryData,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    ReporterData,
    SeedFromTextRequest,
    SeedFromTextResponse,
    VerifyRequest,
    VerifyResponse,
)

# QA Pipeline service
from modules.api.services.qa_pipeline import (
    ModuleOutcome,
    QAPipelineResult,
    QAPipelineService,
)

# New architecture imports
from modules.coder.application.coding_service import CodingService
from modules.coder.phi_gating import is_phi_review_required
from modules.coder.schema import CodeDecision, CoderOutput
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.infra.executors import run_cpu
from modules.registry.application.registry_service import RegistryService
from modules.registry.engine import RegistryEngine
from modules.registry.schema import RegistryRecord
from modules.registry.summarize import add_procedure_summaries
from modules.reporting import (
    apply_bundle_json_patch,
    BundleJsonPatchError,
    MissingFieldIssue,
    ProcedureBundle,
    build_questions,
)
from modules.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine

# Dependency singletons for FastAPI signatures (avoid B008 warnings)
_coding_service_dep = Depends(get_coding_service)
_registry_service_dep = Depends(get_registry_service)
_phi_scrubber_dep = Depends(get_phi_scrubber)
_ready_dep = Depends(require_ready)
_qa_service_dep = Depends(get_qa_pipeline_service)


# ============================================================================
# Application Lifespan Context Manager
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan with resource management.

    This replaces the deprecated @app.on_event("startup") pattern.

    Startup:
    - Initializes readiness state (/health vs /ready)
    - Starts heavy model warmup (background by default)

    Shutdown:
    - Placeholder for cleanup if needed in the future

    Environment variables (see modules.infra.settings.InfraSettings):
    - SKIP_WARMUP / PROCSUITE_SKIP_WARMUP: Skip warmup entirely
    - BACKGROUND_WARMUP: Run warmup in the background (default: true)
    - WAIT_FOR_READY_S: Optional await time for readiness gating
    """
    # Import here to avoid circular import at module load time
    from modules.infra.nlp_warmup import (
        should_skip_warmup as _should_skip_warmup,
    )
    from modules.infra.nlp_warmup import (
        warm_heavy_resources_sync as _warm_heavy_resources_sync,
    )
    from modules.infra.settings import get_infra_settings

    _validate_startup_env()

    settings = get_infra_settings()
    logger = logging.getLogger(__name__)
    from modules.registry.model_runtime import verify_registry_runtime_bundle

    # Readiness state (liveness vs readiness)
    app.state.model_ready = False
    app.state.model_error = None
    app.state.ready_event = asyncio.Event()
    app.state.cpu_executor = ThreadPoolExecutor(max_workers=settings.cpu_workers)
    app.state.llm_sem = asyncio.Semaphore(settings.llm_concurrency)
    app.state.llm_http = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=10.0,
            read=float(settings.llm_timeout_s),
            write=30.0,
            pool=30.0,
        )
    )

    # Ensure PHI database tables exist (auto-create on startup)
    try:
        from modules.api.phi_dependencies import engine as phi_engine
        from modules.phi import models as _phi_models  # noqa: F401 - register models
        from modules.phi.db import Base as PHIBase

        PHIBase.metadata.create_all(bind=phi_engine)
        logger.info("PHI database tables verified/created")
    except Exception as e:
        logger.warning(f"Could not initialize PHI tables: {e}")

    try:
        runtime_warnings = verify_registry_runtime_bundle()
        for warning in runtime_warnings:
            logger.warning("Registry runtime bundle warning: %s", warning)
    except RuntimeError as exc:
        raise RuntimeError(f"Registry runtime bundle validation failed: {exc}") from exc

    loop = asyncio.get_running_loop()

    def _warmup_worker() -> None:
        try:
            _warm_heavy_resources_sync()
        except Exception as exc:  # noqa: BLE001
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            logger.error("Warmup failed: %s", error, exc_info=True)
        else:
            ok = True
            error = None
        app.state.model_ready = ok
        app.state.model_error = error
        loop.call_soon_threadsafe(app.state.ready_event.set)

    def _bootstrap_registry_models() -> None:
        # Optional: pull registry model bundle from S3 (does not gate readiness).
        try:
            from modules.registry.model_bootstrap import ensure_registry_model_bundle

            ensure_registry_model_bundle()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Registry model bundle bootstrap skipped/failed: %s", exc)

    # Startup phase
    if settings.skip_warmup or _should_skip_warmup():
        logger.info("Skipping heavy NLP warmup (disabled via environment)")
        app.state.model_ready = True
        app.state.ready_event.set()
    elif settings.background_warmup:
        logger.info("Starting background warmup")
        loop.run_in_executor(app.state.cpu_executor, _warmup_worker)
    else:
        logger.info("Running warmup before serving traffic")
        try:
            await loop.run_in_executor(app.state.cpu_executor, _warm_heavy_resources_sync)
        except Exception as exc:  # noqa: BLE001
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            logger.error("Warmup failed: %s", error, exc_info=True)
        else:
            ok = True
            error = None
        app.state.model_ready = ok
        app.state.model_error = error
        app.state.ready_event.set()

    # Kick off model bundle bootstrap in the background (best-effort).
    loop.run_in_executor(app.state.cpu_executor, _bootstrap_registry_models)

    yield  # Application runs

    # Shutdown phase (cleanup if needed)
    llm_http = getattr(app.state, "llm_http", None)
    if llm_http is not None:
        await llm_http.aclose()

    cpu_executor = getattr(app.state, "cpu_executor", None)
    if cpu_executor is not None:
        cpu_executor.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="Procedure Suite API",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS (dev-friendly defaults)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev: allow all
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def _phi_redactor_headers(request: Request, call_next):
    """
    Ensure the PHI redactor UI (including /vendor/* model assets) works in
    cross-origin isolated contexts and when embedded/loaded from other origins
    during development.
    """
    resp = await call_next(request)
    path = request.url.path
    # Apply COEP headers to all /ui/ paths (PHI Redactor is now the main UI)
    if path.startswith("/ui"):
        # Required for SharedArrayBuffer in modern browsers (cross-origin isolation).
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        # Allow these assets to be requested as subresources in COEP contexts.
        resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        # Dev convenience: make vendor assets fetchable from any origin.
        # (CORSMiddleware adds CORS headers when an Origin header is present,
        # but some contexts can still surface this as a "CORS error" without it.)
        resp.headers.setdefault("Access-Control-Allow-Origin", "*")
        resp.headers.setdefault("Access-Control-Allow-Methods", "*")
        resp.headers.setdefault("Access-Control-Allow-Headers", "*")
        # Chrome Private Network Access (PNA): when the UI is loaded from a
        # "public" secure context (e.g., an https webview) and it fetches
        # localhost resources, Chrome sends a preflight with
        # Access-Control-Request-Private-Network: true and expects this header.
        if request.headers.get("access-control-request-private-network", "").lower() == "true":
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
        # Avoid stale caching during rapid iteration/debugging.
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp

# Include ML Advisor router
app.include_router(ml_advisor_router, prefix="/api/v1", tags=["ML Advisor"])
# Include PHI router
app.include_router(phi_router)
# Include procedure codes router
app.include_router(procedure_codes_router, prefix="/api/v1", tags=["procedure-codes"])
# Metrics router
app.include_router(metrics_router, tags=["metrics"])
# PHI demo cases router (non-PHI metadata)
app.include_router(phi_demo_router)
# Registry extraction router (hybrid-first pipeline)
app.include_router(registry_extract_router, tags=["registry"])
# Registry run persistence router (Diamond Loop)
app.include_router(registry_runs_router, prefix="/api", tags=["registry-runs"])
# Unified process router (UI entry point)
app.include_router(unified_process_router, prefix="/api")

def _phi_redactor_response(path: Path) -> FileResponse:
    resp = FileResponse(path)
    # Required for SharedArrayBuffer in modern browsers (cross-origin isolation).
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    # Avoid stale client-side caching during rapid iteration/debugging.
    resp.headers["Cache-Control"] = "no-store"
    return resp


def _phi_redactor_static_dir() -> Path:
    return Path(__file__).parent / "static" / "phi_redactor"


def _static_files_enabled() -> bool:
    return os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes")


@app.get("/ui/phi_redactor")
def phi_redactor_redirect() -> RedirectResponse:
    # Avoid "/ui/phi_redactor" being treated as a file path in the browser (breaks relative URLs).
    # Redirect ensures relative module imports resolve to "/ui/phi_redactor/...".
    resp = RedirectResponse(url="/ui/phi_redactor/")
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/ui/phi_redactor/")
def phi_redactor_index() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    index_path = _phi_redactor_static_dir() / "index.html"
    return _phi_redactor_response(index_path)


@app.get("/ui/phi_redactor/index.html")
def phi_redactor_index_html() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    index_path = _phi_redactor_static_dir() / "index.html"
    return _phi_redactor_response(index_path)


@app.get("/ui/phi_redactor/app.js")
def phi_redactor_app_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "app.js")


@app.get("/ui/phi_redactor/redactor.worker.js")
def phi_redactor_worker_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "redactor.worker.js")

@app.get("/ui/redactor.worker.legacy.js")
def phi_redactor_worker_legacy_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "redactor.worker.legacy.js")

@app.get("/ui/protectedVeto.legacy.js")
def phi_redactor_protected_veto_legacy_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "protectedVeto.legacy.js")

@app.get("/ui/transformers.min.js")
def phi_redactor_transformers_min_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "transformers.min.js")


@app.get("/ui/phi_redactor/styles.css")
def phi_redactor_styles_css() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "styles.css")


@app.get("/ui/phi_redactor/protectedVeto.js")
def phi_redactor_protected_veto_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "protectedVeto.js")


@app.get("/ui/phi_redactor/allowlist_trie.json")
def phi_redactor_allowlist() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "allowlist_trie.json")


@app.get("/ui/phi_redactor/vendor/{asset_path:path}")
def phi_redactor_vendor_asset(asset_path: str) -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    vendor_dir = _phi_redactor_static_dir() / "vendor"
    asset = (vendor_dir / asset_path).resolve()
    if vendor_dir not in asset.parents or not asset.exists() or not asset.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    return _phi_redactor_response(asset)


@app.get("/ui/phi_redactor/sw.js")
def phi_redactor_sw() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "sw.js")


@app.get("/ui/phi_identifiers", include_in_schema=False)
def phi_identifiers_doc() -> FileResponse:
    """Serve the PHI identifiers reference used by the UI confirmation modal."""

    doc_path = Path(__file__).resolve().parents[2] / "docs" / "PHI_IDENTIFIERS.md"
    if not doc_path.exists() or not doc_path.is_file():
        raise HTTPException(status_code=404, detail="PHI identifiers doc not found")

    resp = FileResponse(doc_path, media_type="text/markdown")
    # Required for SharedArrayBuffer in modern browsers (cross-origin isolation).
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    resp.headers["Cache-Control"] = "no-store"
    return resp

# Skip static file mounting when DISABLE_STATIC_FILES is set (useful for testing)
if os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes"):
    # Use absolute path to static directory relative to this file
    # Mount PHI Redactor as the main UI (client-side PHI detection)
    phi_redactor_dir = Path(__file__).parent / "static" / "phi_redactor"
    app.mount("/ui", StaticFiles(directory=str(phi_redactor_dir), html=True), name="ui")
    # Also mount vendor directory for ONNX model files
    vendor_dir = phi_redactor_dir / "vendor"
    if vendor_dir.exists():
        app.mount("/ui/vendor", StaticFiles(directory=str(vendor_dir)), name="ui_vendor")
        app.mount(
            "/ui/phi_redactor/vendor",
            StaticFiles(directory=str(vendor_dir)),
            name="ui_phi_redactor_vendor",
        )

# Configure logging
_logger = logging.getLogger(__name__)


# ============================================================================
# Heavy NLP model preloading (delegated to modules.infra.nlp_warmup)
# ============================================================================
from modules.infra.nlp_warmup import (
    is_nlp_warmed,
)

# NOTE: The lifespan context manager is defined above app creation.
# See lifespan() function for startup/shutdown logic.


class LocalityInfo(BaseModel):
    code: str
    name: str


@lru_cache(maxsize=1)
def _load_gpci_data() -> dict[str, str]:
    """Load GPCI locality data from CSV file.

    Returns a dict mapping locality codes to locality names.
    """
    import csv
    from pathlib import Path

    gpci_file = Path("data/RVU_files/gpci_2025.csv")
    if not gpci_file.exists():
        gpci_file = Path("proc_autocode/rvu/data/gpci_2025.csv")

    localities: dict[str, str] = {}
    if gpci_file.exists():
        try:
            with gpci_file.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("mac_locality", row.get("locality_code", ""))
                    name = row.get("locality_name", "")
                    if code and name:
                        localities[code] = name
        except Exception as e:
            _logger.warning(f"Failed to load GPCI data: {e}")

    # Add default national locality if not present
    if "00" not in localities:
        localities["00"] = "National (Default)"

    return localities


@app.get("/")
async def root(request: Request) -> Any:
    """Root endpoint with API information or redirect to UI."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/ui/")

    return {
        "name": "Procedure Suite API",
        "version": "0.3.0",
        "endpoints": {
            "ui": "/ui/",
            "health": "/health",
            "ready": "/ready",
            "knowledge": "/knowledge",
            "docs": "/docs",
            "redoc": "/redoc",
            "unified_process": "/api/v1/process",  # NEW: Combined registry + coder
            "coder": "/v1/coder/run",
            "localities": "/v1/coder/localities",
            "registry": "/v1/registry/run",
            "report_verify": "/report/verify",
            "report_questions": "/report/questions",
            "report_seed_from_text": "/report/seed_from_text",
            "report_render": "/report/render",
            "qa_run": "/qa/run",
            "ml_advisor": {
                "health": "/api/v1/ml-advisor/health",
                "status": "/api/v1/ml-advisor/status",
                "code": "/api/v1/ml-advisor/code",
                "code_with_advisor": "/api/v1/ml-advisor/code_with_advisor",
                "suggest": "/api/v1/ml-advisor/suggest",
                "traces": "/api/v1/ml-advisor/traces",
                "metrics": "/api/v1/ml-advisor/metrics",
            },
            "registry_extract": "/api/registry/extract",
        },
        "note": (
            "Use /api/v1/process for extraction-first pipeline (registry → CPT codes in one call). "
            "Legacy endpoints /v1/coder/run and /v1/registry/run still available."
        ),
    }


@app.get("/health")
async def health(request: Request) -> dict[str, bool]:
    # Liveness probe: keep payload stable and minimal.
    # Readiness is exposed via `/ready`.
    return {"ok": True}


@app.get("/ready")
async def ready(request: Request) -> JSONResponse:
    is_ready = bool(getattr(request.app.state, "model_ready", False))
    if is_ready:
        return JSONResponse(status_code=200, content={"status": "ok", "ready": True})

    model_error = getattr(request.app.state, "model_error", None)
    content: dict[str, Any] = {"status": "warming", "ready": False}
    if model_error:
        content["status"] = "error"
        content["error"] = str(model_error)
        return JSONResponse(status_code=503, content=content)

    return JSONResponse(status_code=503, content=content, headers={"Retry-After": "10"})


@app.get("/health/nlp")
async def nlp_health() -> JSONResponse:
    """Check NLP model readiness.

    Returns 200 OK if NLP models are loaded and ready.
    Returns 503 Service Unavailable if NLP features are degraded.

    This endpoint can be used by load balancers to route requests
    to instances with fully warmed NLP models.
    """
    if is_nlp_warmed():
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "nlp_ready": True},
        )
    return JSONResponse(
        status_code=503,
        content={"status": "degraded", "nlp_ready": False},
    )


@app.get("/knowledge", response_model=KnowledgeMeta)
async def knowledge() -> KnowledgeMeta:
    return KnowledgeMeta(version=knowledge_version() or "unknown", sha256=knowledge_hash() or "")


@app.get("/v1/coder/localities", response_model=List[LocalityInfo])
async def coder_localities() -> List[LocalityInfo]:
    """List available geographic localities for RVU calculation."""
    gpci_data = _load_gpci_data()
    localities = [
        LocalityInfo(code=code, name=name)
        for code, name in gpci_data.items()
    ]
    localities.sort(key=lambda x: x.name)
    return localities


@app.post("/v1/coder/run", response_model=CoderResponse)
async def coder_run(
    req: CoderRequest,
    request: Request,
    mode: str | None = None,
    coding_service: CodingService = _coding_service_dep,
) -> CoderResponse:
    """Legacy raw-text coder shim (non-PHI).

    Use PHI workflow + /api/v1/procedures/{id}/codes/suggest.
    """
    enforce_legacy_endpoints_allowed()
    require_review = is_phi_review_required()
    procedure_id = str(uuid.uuid4())
    report_text = req.note

    # If PHI review is required, reject direct raw text coding
    if require_review:
        raise HTTPException(
            status_code=400,
            detail=(
                "Direct coding on raw text is disabled; submit via /v1/phi and review "
                "before coding."
            ),
        )

    mode_value = (mode or req.mode or "").strip().lower()

    # Check if ML-first hybrid pipeline is requested
    if req.use_ml_first:
        use_llm_fallback = mode_value != "rules_only"
        return await _run_ml_first_pipeline(
            request,
            report_text,
            req.locality,
            coding_service,
            use_llm_fallback=use_llm_fallback,
        )

    # Determine if LLM should be used based on mode
    use_llm = True
    if mode_value == "rules_only":
        use_llm = False

    # Run the coding pipeline
    result = await run_cpu(
        request.app,
        coding_service.generate_result,
        procedure_id=procedure_id,
        report_text=report_text,
        use_llm=use_llm,
        procedure_type=None,  # Auto-detect
    )

    # Convert to legacy CoderOutput format for backward compatibility
    output = convert_coding_result_to_coder_output(
        result=result,
        kb_repo=coding_service.kb_repo,
        locality=req.locality,
    )

    return output


async def _run_ml_first_pipeline(
    request: Request,
    report_text: str,
    locality: str,
    coding_service: CodingService,
    *,
    use_llm_fallback: bool = True,
) -> CoderResponse:
    """
    Run the ML-first hybrid pipeline (SmartHybridOrchestrator).

    Uses ternary classification (HIGH_CONF/GRAY_ZONE/LOW_CONF) to decide
    whether to use ML+Rules fast path or LLM fallback.

    Args:
        report_text: The procedure note text
        locality: Geographic locality for RVU calculations
        coding_service: CodingService for KB access and RVU calculation

    Returns:
        CoderResponse with codes and hybrid pipeline metadata
    """
    from modules.coder.application.smart_hybrid_policy import build_hybrid_orchestrator

    def _run_hybrid() -> Any:
        if use_llm_fallback:
            orchestrator = build_hybrid_orchestrator()
            return orchestrator.get_codes(report_text)

        from modules.coder.adapters.llm.noop_advisor import NoOpLLMAdvisorAdapter

        orchestrator = build_hybrid_orchestrator(llm_advisor=NoOpLLMAdvisorAdapter())
        result = orchestrator.get_codes(report_text)
        result.metadata = dict(result.metadata or {})
        result.metadata["llm_called"] = False
        result.metadata["llm_disabled"] = True
        if result.source == "hybrid_llm_fallback":
            result.source = "ml_rules_no_llm"
        return result

    result = await run_cpu(request.app, _run_hybrid)

    # Build code decisions from orchestrator result

    code_decisions = []
    for cpt in result.codes:
        proc_info = coding_service.kb_repo.get_procedure_info(cpt)
        desc = proc_info.description if proc_info else ""
        code_decisions.append(
            CodeDecision(
                cpt=cpt,
                description=desc,
                confidence=1.0,  # Hybrid pipeline doesn't return per-code confidence
                modifiers=[],
                rationale=f"Source: {result.source}",
            )
        )

    # Calculate RVU/financials if we have codes
    financials = None
    if code_decisions:
        from modules.coder.schema import FinancialSummary, PerCodeBilling

        per_code_billing: list[PerCodeBilling] = []
        total_work_rvu = 0.0
        total_facility_payment = 0.0
        conversion_factor = CoderSettings().cms_conversion_factor

        for cd in code_decisions:
            proc_info = coding_service.kb_repo.get_procedure_info(cd.cpt)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                payment = total_rvu * conversion_factor

                total_work_rvu += work_rvu
                total_facility_payment += payment

                per_code_billing.append(PerCodeBilling(
                    cpt_code=cd.cpt,
                    description=cd.description,
                    modifiers=cd.modifiers,
                    work_rvu=work_rvu,
                    total_facility_rvu=total_rvu,
                    facility_payment=payment,
                    allowed_facility_rvu=total_rvu,
                    allowed_facility_payment=payment,
                ))

        if per_code_billing:
            financials = FinancialSummary(
                conversion_factor=conversion_factor,
                locality=locality,
                per_code=per_code_billing,
                total_work_rvu=total_work_rvu,
                total_facility_payment=total_facility_payment,
                total_nonfacility_payment=0.0,
            )

    # Build hybrid pipeline metadata
    hybrid_metadata = HybridPipelineMetadata(
        difficulty=result.difficulty.value,  # Use top-level difficulty attribute
        source=result.source,
        llm_used=result.metadata.get("llm_called", False),
        ml_candidates=result.metadata.get("ml_candidates", []),
        fallback_reason=result.metadata.get("reason_for_fallback"),
        rules_error=result.metadata.get("rules_error"),
    )

    # Build response
    return CoderOutput(
        codes=code_decisions,
        financials=financials,
        warnings=[],
        explanation=None,
        hybrid_metadata=hybrid_metadata.model_dump(),
    )


@app.post(
    "/v1/registry/run",
    response_model=RegistryResponse,
    response_model_exclude_none=True,
)
async def registry_run(
    req: RegistryRequest,
    request: Request,
    _ready: None = _ready_dep,
    registry_service: RegistryService = _registry_service_dep,
    phi_scrubber=_phi_scrubber_dep,
) -> RegistryResponse:
    enforce_legacy_endpoints_allowed()

    # Early PHI redaction - scrub once at entry
    redaction = apply_phi_redaction(req.note, phi_scrubber)
    note_text = redaction.text

    mode_value = (req.mode or "").strip().lower()
    enforce_request_mode_override_allowed(mode_value)
    if mode_value == "parallel_ner":
        result = await run_cpu(
            request.app,
            registry_service.extract_fields,
            note_text,
            req.mode,
        )
        payload = _shape_registry_payload(result.record, {}, codes=result.cpt_codes)
        return JSONResponse(content=payload)

    if mode_value in {"engine_only", "no_llm", "deterministic_only"}:
        result = await run_cpu(
            request.app,
            registry_service.extract_fields,
            note_text,
            "parallel_ner",
        )
        payload = _shape_registry_payload(result.record, {}, codes=result.cpt_codes)
        return JSONResponse(content=payload)

    eng = RegistryEngine()
    result = await run_cpu(request.app, eng.run, note_text, explain=req.explain)
    if isinstance(result, tuple):
        record, evidence = result
    else:
        record, evidence = result, getattr(result, "evidence", {})

    payload = _shape_registry_payload(record, evidence)
    return JSONResponse(content=payload)


def _verify_bundle(
    bundle: ProcedureBundle,
) -> tuple[
    ProcedureBundle,
    list[MissingFieldIssue],
    list[str],
    list[str],
    list[str],
]:
    templates = default_template_registry()
    schemas = default_schema_registry()
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)
    return bundle, issues, warnings, suggestions, inference_result.notes


def _render_bundle_markdown(
    bundle: ProcedureBundle,
    *,
    issues: list[MissingFieldIssue],
    warnings: list[str],
    strict: bool,
    embed_metadata: bool,
) -> str:
    templates = default_template_registry()
    schemas = default_schema_registry()
    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    try:
        structured = engine.compose_report_with_metadata(
            bundle,
            strict=strict,
            embed_metadata=embed_metadata,
            validation_issues=issues,
            warnings=warnings,
        )
    except ValueError as exc:
        # In strict mode, the reporter runs style validation on the final rendered
        # text. We still want to return a preview for the interactive UI even if
        # strict style checks fail (e.g., templates render "None" or placeholders).
        message = str(exc)
        if not strict:
            raise
        if not (
            message.startswith("Style validation failed:")
            or message.startswith("Missing required fields for")
        ):
            raise
        _logger.warning(
            "Strict report render failed; falling back to non-strict preview",
            extra={"error": message},
        )
        structured = engine.compose_report_with_metadata(
            bundle,
            strict=False,
            embed_metadata=embed_metadata,
            validation_issues=issues,
            warnings=warnings,
        )
    return structured.text


def _normalize_report_json_patch_ops(ops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Coerce interactive UI patch values into schema-friendly shapes.

    The interactive Reporter Builder UI can emit multiselect answers as arrays, but
    some underlying bundle schema fields are stored as strings (for template compatibility).
    Normalize those here to avoid 500s on render.
    """
    for op in ops:
        path = op.get("path")
        if not isinstance(path, str):
            continue
        value = op.get("value")
        if path.endswith("/echo_features"):
            if not isinstance(value, list):
                continue
            parts = [str(item).strip() for item in value if str(item).strip()]
            op["value"] = ", ".join(parts)
            continue

        if path.endswith("/tests"):
            if isinstance(value, str):
                normalized = value.replace(";", ",").replace("\n", ",")
                op["value"] = [part.strip() for part in normalized.split(",") if part.strip()]
                continue
            if isinstance(value, list):
                op["value"] = [str(item).strip() for item in value if str(item).strip()]
                continue
    return ops


def _apply_render_patch(
    bundle: ProcedureBundle,
    req: RenderRequest,
) -> ProcedureBundle:
    patch_payload = req.patch
    if not patch_payload:
        return bundle
    if isinstance(patch_payload, list):
        ops: list[dict[str, Any]] = []
        for op in patch_payload:
            if isinstance(op, BaseModel):
                ops.append(op.model_dump(exclude_none=False))
            else:
                ops.append(dict(op))
        ops = _normalize_report_json_patch_ops(ops)
        return apply_bundle_json_patch(bundle, ops)
    return apply_bundle_patch(bundle, patch_payload)


def _apply_seed_metadata(bundle: ProcedureBundle, metadata: dict[str, Any]) -> ProcedureBundle:
    if not metadata:
        return bundle

    def _as_text(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)

    payload = bundle.model_dump(exclude_none=False)
    encounter = payload.get("encounter") or {}

    indication = _as_text(metadata.get("indication_text") or metadata.get("indication"))
    if indication:
        payload["indication_text"] = indication

    preop = _as_text(metadata.get("preop_diagnosis_text") or metadata.get("preop_diagnosis"))
    if preop:
        payload["preop_diagnosis_text"] = preop

    postop = _as_text(metadata.get("postop_diagnosis_text") or metadata.get("postop_diagnosis"))
    if postop:
        payload["postop_diagnosis_text"] = postop

    impression = _as_text(metadata.get("impression_plan") or metadata.get("plan") or metadata.get("disposition"))
    if impression:
        payload["impression_plan"] = impression

    attending = _as_text(metadata.get("attending"))
    if attending:
        encounter["attending"] = attending
    location = _as_text(metadata.get("location"))
    if location:
        encounter["location"] = location
    date_value = _as_text(metadata.get("date") or metadata.get("procedure_date"))
    if date_value:
        encounter["date"] = date_value
    encounter_id = _as_text(metadata.get("encounter_id"))
    if encounter_id:
        encounter["encounter_id"] = encounter_id

    payload["encounter"] = encounter
    return ProcedureBundle.model_validate(payload)


@app.post("/report/verify", response_model=VerifyResponse)
async def report_verify(req: VerifyRequest) -> VerifyResponse:
    bundle = build_procedure_bundle_from_extraction(req.extraction)
    bundle, issues, warnings, suggestions, notes = _verify_bundle(bundle)
    return VerifyResponse(
        bundle=bundle,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        inference_notes=notes,
    )


@app.post("/report/questions", response_model=QuestionsResponse)
async def report_questions(req: QuestionsRequest) -> QuestionsResponse:
    bundle, issues, warnings, suggestions, notes = _verify_bundle(req.bundle)
    questions = build_questions(bundle, issues)
    return QuestionsResponse(
        bundle=bundle,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        inference_notes=notes,
        questions=questions,
    )


@app.post("/report/seed_from_text", response_model=SeedFromTextResponse)
async def report_seed_from_text(
    req: SeedFromTextRequest,
    request: Request,
    _ready: None = _ready_dep,
    registry_service: RegistryService = _registry_service_dep,
    phi_scrubber=_phi_scrubber_dep,
) -> SeedFromTextResponse:
    redaction = apply_phi_redaction(req.text, phi_scrubber)
    note_text = redaction.text

    extraction_result = await run_cpu(request.app, registry_service.extract_fields, note_text)
    bundle = build_procedure_bundle_from_extraction(extraction_result.record, source_text=note_text)
    bundle = _apply_seed_metadata(bundle, req.metadata)
    if not bundle.free_text_hint:
        bundle_payload = bundle.model_dump(exclude_none=False)
        bundle_payload["free_text_hint"] = note_text
        bundle = ProcedureBundle.model_validate(bundle_payload)

    bundle, issues, warnings, suggestions, notes = _verify_bundle(bundle)
    questions = build_questions(bundle, issues)
    markdown = _render_bundle_markdown(
        bundle,
        issues=issues,
        warnings=warnings,
        strict=req.strict,
        embed_metadata=False,
    )
    return SeedFromTextResponse(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=notes,
        suggestions=suggestions,
        questions=questions,
    )


@app.post("/report/render", response_model=RenderResponse)
async def report_render(req: RenderRequest) -> RenderResponse:
    bundle = req.bundle
    try:
        bundle = _apply_render_patch(bundle, req)
    except BundleJsonPatchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    bundle, issues, warnings, suggestions, notes = _verify_bundle(bundle)
    markdown = _render_bundle_markdown(
        bundle,
        issues=issues,
        warnings=warnings,
        strict=req.strict,
        embed_metadata=req.embed_metadata,
    )
    return RenderResponse(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=notes,
        suggestions=suggestions,
    )


def _shape_registry_payload(
    record: RegistryRecord,
    evidence: dict[str, list[Span]] | None,
    *,
    codes: list[str] | None = None,
) -> dict[str, Any]:
    """Convert a registry record + evidence into a JSON-safe, null-pruned payload."""
    payload = _prune_none(record.model_dump(exclude_none=True))

    # Optional UI-friendly enrichments
    simplify_billing_cpt_codes(payload)
    add_procedure_summaries(payload)

    payload["evidence"] = build_v3_evidence_payload(
        record=record,
        evidence=evidence,
        codes=codes,
    )
    return payload


# --- QA Sandbox Endpoint ---

def _get_git_info() -> tuple[str | None, str | None]:
    """Extract git branch and commit SHA for version tracking."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return branch, commit
    except Exception:
        return None, None


# Configuration for QA sandbox
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
REPORTER_VERSION = os.getenv("REPORTER_VERSION", "v0.2.0")
CODER_VERSION = os.getenv("CODER_VERSION", "v0.2.0")


def _module_status_from_outcome(outcome: ModuleOutcome) -> ModuleStatus:
    """Convert ModuleOutcome to ModuleStatus enum."""
    if outcome.skipped:
        return ModuleStatus.SKIPPED
    if outcome.ok:
        return ModuleStatus.SUCCESS
    return ModuleStatus.ERROR


def _qapipeline_result_to_response(
    result: QAPipelineResult,
    reporter_version: str,
    coder_version: str,
    repo_branch: str | None,
    repo_commit_sha: str | None,
) -> QARunResponse:
    """Convert QAPipelineResult to QARunResponse.

    Handles status aggregation and data transformation for each module.
    """
    # Build registry ModuleResult
    registry_result: ModuleResult[RegistryData] | None = None
    if not result.registry.skipped:
        registry_data = None
        if result.registry.ok and result.registry.data:
            registry_data = RegistryData(
                record=result.registry.data.get("record", {}),
                evidence=result.registry.data.get("evidence", {}),
            )
        registry_result = ModuleResult[RegistryData](
            status=_module_status_from_outcome(result.registry),
            data=registry_data,
            error_message=result.registry.error_message,
            error_code=result.registry.error_code,
        )

    # Build reporter ModuleResult
    reporter_result: ModuleResult[ReporterData] | None = None
    if not result.reporter.skipped:
        reporter_data = None
        if result.reporter.ok and result.reporter.data:
            data = result.reporter.data
            reporter_data = ReporterData(
                markdown=data.get("markdown"),
                bundle=data.get("bundle"),
                issues=data.get("issues", []),
                warnings=data.get("warnings", []),
                procedure_core=data.get("procedure_core"),
                indication=data.get("indication"),
                postop=data.get("postop"),
                fallback_used=data.get("fallback_used", False),
                render_mode=data.get("render_mode"),
                fallback_reason=data.get("fallback_reason"),
                reporter_errors=data.get("reporter_errors", []),
            )
        reporter_result = ModuleResult[ReporterData](
            status=_module_status_from_outcome(result.reporter),
            data=reporter_data,
            error_message=result.reporter.error_message,
            error_code=result.reporter.error_code,
        )

    # Build coder ModuleResult
    coder_result: ModuleResult[CoderData] | None = None
    if not result.coder.skipped:
        coder_data = None
        if result.coder.ok and result.coder.data:
            data = result.coder.data
            codes = [
                CodeEntry(
                    cpt=c.get("cpt", ""),
                    description=c.get("description"),
                    confidence=c.get("confidence"),
                    source=c.get("source"),
                    hybrid_decision=c.get("hybrid_decision"),
                    review_flag=c.get("review_flag", False),
                )
                for c in data.get("codes", [])
            ]
            coder_data = CoderData(
                codes=codes,
                total_work_rvu=data.get("total_work_rvu"),
                estimated_payment=data.get("estimated_payment"),
                bundled_codes=data.get("bundled_codes", []),
                kb_version=data.get("kb_version"),
                policy_version=data.get("policy_version"),
                model_version=data.get("model_version"),
                processing_time_ms=data.get("processing_time_ms"),
            )
        coder_result = ModuleResult[CoderData](
            status=_module_status_from_outcome(result.coder),
            data=coder_data,
            error_message=result.coder.error_message,
            error_code=result.coder.error_code,
        )

    # Compute overall status
    active_results = []
    if registry_result:
        active_results.append(registry_result)
    if reporter_result:
        active_results.append(reporter_result)
    if coder_result:
        active_results.append(coder_result)

    if not active_results:
        overall_status = "completed"
    else:
        successes = sum(1 for r in active_results if r.status == ModuleStatus.SUCCESS)
        failures = sum(1 for r in active_results if r.status == ModuleStatus.ERROR)

        if failures == 0:
            overall_status = "completed"
        elif successes == 0:
            overall_status = "failed"
        else:
            overall_status = "partial_success"

    from modules.registry.model_runtime import get_registry_model_provenance

    model_provenance = get_registry_model_provenance()

    return QARunResponse(
        overall_status=overall_status,
        registry=registry_result,
        reporter=reporter_result,
        coder=coder_result,
        registry_output=(result.registry.data if result.registry.ok else None),
        reporter_output=(result.reporter.data if result.reporter.ok else None),
        coder_output=(result.coder.data if result.coder.ok else None),
        model_backend=model_provenance.backend,
        model_version=model_provenance.version,
        reporter_version=reporter_version,
        coder_version=coder_version,
        repo_branch=repo_branch,
        repo_commit_sha=repo_commit_sha,
    )


@app.post("/qa/run", response_model=QARunResponse)
async def qa_run(
    payload: QARunRequest,
    request: Request,
    qa_service: QAPipelineService = _qa_service_dep,
) -> QARunResponse:
    """
    QA sandbox endpoint: runs reporter, coder, and/or registry on input text.

    This endpoint does NOT persist data - that is handled by the Next.js layer.
    Returns structured outputs with per-module status + version metadata.

    The pipeline runs synchronously in a thread pool to avoid blocking the
    event loop during heavy NLP/ML processing.

    Returns HTTP 200 for all cases (success, partial failure, full failure).
    Check `overall_status` and individual module `status` fields for results.
    """
    branch, commit = _get_git_info()

    result = await run_cpu(
        request.app,
        qa_service.run_pipeline,
        text=payload.note_text,
        modules=payload.modules_run,
        procedure_type=payload.procedure_type,
    )

    # Convert to response format
    return _qapipeline_result_to_response(
        result=result,
        reporter_version=REPORTER_VERSION,
        coder_version=CODER_VERSION,
        repo_branch=branch,
        repo_commit_sha=commit,
    )


__all__ = ["app"]

```

---
### `modules/coder/application/coding_service.py`
```
"""Coding Service - orchestrates the extraction-first coding pipeline.

This service coordinates registry extraction, deterministic CPT derivation,
and audit metadata to produce CodeSuggestion objects for review.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from config.settings import CoderSettings
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.coder.adapters.nlp.keyword_mapping_loader import KeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import LLMAdvisorPort
from modules.coder.adapters.ml_ranker import MLRankerPort
from modules.coder.application.procedure_type_detector import detect_procedure_type
from modules.domain.coding_rules import apply_mer_rules, apply_ncci_edits
from modules.phi.ports import PHIScrubberPort
from proc_schemas.coding import CodeSuggestion, CodingResult
from proc_schemas.reasoning import ReasoningFields
from observability.timing import timed
from observability.logging_config import get_logger

if TYPE_CHECKING:
    from modules.registry.application.registry_service import RegistryService

logger = get_logger("coding_service")


class CodingService:
    """Orchestrates the extraction-first coding pipeline.

    Pipeline Steps:
    1. Registry extraction → RegistryRecord
    2. Deterministic Registry → CPT derivation
    3. RAW-ML audit metadata (if enabled by RegistryService)
    4. Build CodeSuggestion[] → return for review
    """

    VERSION = "coding_service_v1"
    POLICY_VERSION = "extraction_first_v1"

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        keyword_repo: KeywordMappingRepository,
        negation_detector: SimpleNegationDetector,
        rule_engine: RuleEngine,
        llm_advisor: Optional[LLMAdvisorPort],
        config: CoderSettings,
        phi_scrubber: Optional[PHIScrubberPort] = None,
        ml_ranker: Optional[MLRankerPort] = None,
        registry_service: "RegistryService | None" = None,
    ):
        self.kb_repo = kb_repo
        self.keyword_repo = keyword_repo
        self.negation_detector = negation_detector
        self.rule_engine = rule_engine
        self.llm_advisor = llm_advisor
        self.config = config
        self.phi_scrubber = phi_scrubber
        self.ml_ranker = ml_ranker
        self.registry_service = registry_service

        # Note: PHI scrubbing is now handled at route level (modules/api/phi_redaction.py).
        # The phi_scrubber parameter is deprecated and ignored.
        if phi_scrubber:
            logger.debug(
                "phi_scrubber parameter is deprecated; PHI redaction is now handled at route level"
            )

        # Hybrid pipeline dependencies are accepted for compatibility, but unused in extraction-first.

    def generate_suggestions(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
    ) -> tuple[list[CodeSuggestion], float]:
        """Generate code suggestions for a procedure note.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Ignored (LLM advisor is not used in extraction-first).

        Returns:
            Tuple of (List of CodeSuggestion objects, LLM latency in ms).
        """
        return self._generate_suggestions_extraction_first(procedure_id, report_text)

    def generate_result(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
        procedure_type: str | None = None,
    ) -> CodingResult:
        """Generate a complete coding result with metadata.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Ignored (LLM advisor is not used in extraction-first).
            procedure_type: Classification of the procedure (e.g., bronch_diagnostic,
                          bronch_ebus, pleural, blvr). Used for metrics segmentation.
                          If None or "unknown", auto-detection is attempted.

        Returns:
            CodingResult with suggestions and metadata.
        """
        with timed("coding_service.generate_result") as timing:
            suggestions, llm_latency_ms = self.generate_suggestions(
                procedure_id, report_text, use_llm
            )

        # Auto-detect procedure type if not provided
        if not procedure_type or procedure_type == "unknown":
            suggestion_codes = [s.code for s in suggestions]
            detected_type = detect_procedure_type(
                report_text=report_text,
                codes=suggestion_codes,
            )
            procedure_type = detected_type
            logger.debug(
                "Auto-detected procedure type",
                extra={
                    "procedure_id": procedure_id,
                    "detected_type": detected_type,
                    "codes_used": suggestion_codes[:5],  # Log first 5 codes
                },
            )

        return CodingResult(
            procedure_id=procedure_id,
            suggestions=suggestions,
            final_codes=[],  # Populated after review
            procedure_type=procedure_type,
            warnings=[],
            ncci_notes=[],
            mer_notes=[],
            kb_version=self.kb_repo.version,
            policy_version=self.POLICY_VERSION,
            model_version="",
            processing_time_ms=timing.elapsed_ms,
            llm_latency_ms=llm_latency_ms,
        )

    @staticmethod
    def _base_confidence_from_difficulty(difficulty: str) -> float:
        normalized = (difficulty or "").strip().upper()
        if normalized == "HIGH_CONF":
            return 0.95
        if normalized in ("MEDIUM", "GRAY_ZONE"):
            return 0.80
        if normalized in ("LOW_CONF", "LOW"):
            return 0.70
        return 0.70

    def _generate_suggestions_extraction_first(
        self,
        procedure_id: str,
        report_text: str,
    ) -> tuple[list[CodeSuggestion], float]:
        """Extraction-first pipeline: Registry → Deterministic CPT → ML Audit.

        This pipeline:
        1. Extracts a RegistryRecord from the note text
        2. Derives CPT codes deterministically from the registry fields
        3. Optionally audits the derived codes against raw ML predictions

        Returns:
            Tuple of (List of CodeSuggestion objects, processing latency in ms).
        """
        from modules.registry.application.registry_service import RegistryService

        start_time = time.time()

        logger.info(
            "Starting coding pipeline (extraction-first mode)",
            extra={
                "procedure_id": procedure_id,
                "text_length_chars": len(report_text),
            },
        )

        # Step 1: Extract registry fields + deterministic CPT codes
        registry_service = self.registry_service or RegistryService()
        extraction_result = registry_service.extract_fields_extraction_first(report_text)

        codes = list(extraction_result.cpt_codes or [])
        rationales = dict(extraction_result.code_rationales or {})
        derivation_warnings = list(extraction_result.derivation_warnings or [])

        if not codes:
            rule_result = self.rule_engine.generate_candidates(report_text)
            suggestions: list[CodeSuggestion] = []
            candidates = getattr(rule_result, "candidates", None)
            if candidates is None:
                legacy_codes = list(getattr(rule_result, "codes", []) or [])
                legacy_conf = dict(getattr(rule_result, "confidence", {}) or {})
                candidates = [
                    {
                        "code": code,
                        "confidence": legacy_conf.get(code, 0.9),
                        "rule_path": "RULE_ENGINE_FALLBACK",
                        "rationale": "rule_engine.fallback",
                    }
                    for code in legacy_codes
                ]

            for candidate in candidates:
                if isinstance(candidate, dict):
                    code = str(candidate.get("code", "")).strip()
                    confidence = float(candidate.get("confidence", 0.9))
                    rule_path = str(candidate.get("rule_path", "RULE_ENGINE"))
                    rationale = str(candidate.get("rationale", "derived"))
                else:
                    code = str(getattr(candidate, "code", "")).strip()
                    confidence = float(getattr(candidate, "confidence", 0.9))
                    rule_path = str(getattr(candidate, "rule_path", "RULE_ENGINE"))
                    rationale = str(getattr(candidate, "rationale", "derived"))

                if not code:
                    continue

                proc_info = self.kb_repo.get_procedure_info(code)
                description = proc_info.description if proc_info else ""

                reasoning = ReasoningFields(
                    trigger_phrases=[],
                    evidence_spans=[],
                    rule_paths=[rule_path, rationale],
                    ncci_notes="",
                    mer_notes="",
                    confidence=confidence,
                    kb_version=self.kb_repo.version,
                    policy_version=self.POLICY_VERSION,
                )

                suggestions.append(
                    CodeSuggestion(
                        code=code,
                        description=description,
                        source="rules",
                        hybrid_decision="kept_rule_priority",
                        rule_confidence=confidence,
                        llm_confidence=None,
                        final_confidence=confidence,
                        reasoning=reasoning,
                        review_flag="optional",
                        trigger_phrases=[],
                        evidence_verified=True,
                        suggestion_id=str(uuid.uuid4()),
                        procedure_id=procedure_id,
                    )
                )

            latency_ms = (time.time() - start_time) * 1000
            logger.info(
                "Extraction-first derivation produced no CPT codes; using rules fallback",
                extra={
                    "procedure_id": procedure_id,
                    "fallback_code_count": len(suggestions),
                    "processing_time_ms": int(latency_ms),
                },
            )
            return suggestions, 0.0

        # Step 2: Build audit warnings
        audit_warnings: list[str] = list(extraction_result.audit_warnings or [])
        audit_warnings.extend(derivation_warnings)

        # Determine difficulty level
        base_confidence = self._base_confidence_from_difficulty(
            extraction_result.coder_difficulty
        )

        # Step 3: Build CodeSuggestion objects
        suggestions: list[CodeSuggestion] = []
        for code in codes:
            rationale = rationales.get(code, "derived")

            # Format audit warnings for mer_notes
            mer_notes = ""
            if audit_warnings:
                mer_notes = "AUDIT FLAGS:\n" + "\n".join(f"• {w}" for w in audit_warnings)

            reasoning = ReasoningFields(
                trigger_phrases=[],
                evidence_spans=[],
                rule_paths=[f"DETERMINISTIC: {rationale}"],
                ncci_notes="",
                mer_notes=mer_notes,
                confidence=base_confidence,
                kb_version=self.kb_repo.version,
                policy_version=self.POLICY_VERSION,
            )

            # Determine review flag
            if extraction_result.needs_manual_review:
                review_flag = "required"
            elif audit_warnings:
                review_flag = "recommended"
            else:
                review_flag = "optional"

            # Get procedure description
            proc_info = self.kb_repo.get_procedure_info(code)
            description = proc_info.description if proc_info else ""

            suggestion = CodeSuggestion(
                code=code,
                description=description,
                source="hybrid",  # Extraction-first is a form of hybrid
                hybrid_decision="EXTRACTION_FIRST",
                rule_confidence=base_confidence,
                llm_confidence=None,
                final_confidence=base_confidence,
                reasoning=reasoning,
                review_flag=review_flag,
                trigger_phrases=[],
                evidence_verified=True,
                suggestion_id=str(uuid.uuid4()),
                procedure_id=procedure_id,
            )
            suggestions.append(suggestion)

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            "Coding complete (extraction-first mode)",
            extra={
                "procedure_id": procedure_id,
                "num_suggestions": len(suggestions),
                "processing_time_ms": latency_ms,
                "codes": codes,
            },
        )

        return suggestions, latency_ms

```

---
### `modules/registry/application/registry_service.py`
```
"""Registry Service for exporting procedure data to the IP Registry.

This application-layer service orchestrates:
- Building registry entries from final codes and procedure metadata
- Mapping CPT codes to registry boolean flags
- Validating entries against the registry schema
- Managing export state
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Literal, TYPE_CHECKING

import os
from pydantic import BaseModel, ValidationError

from modules.common.exceptions import RegistryError
from modules.common.logger import get_logger
from modules.registry.adapters.schema_registry import (
    RegistrySchemaRegistry,
    get_schema_registry,
)
from modules.registry.application.cpt_registry_mapping import (
    aggregate_registry_fields,
    aggregate_registry_fields_flat,
    aggregate_registry_hints,
)
from modules.registry.application.registry_builder import (
    RegistryBuilderProtocol,
    get_builder,
)
from modules.registry.engine import RegistryEngine
from modules.registry.schema import RegistryRecord
from modules.registry.schema_granular import derive_procedures_from_granular
from modules.registry.processing.masking import mask_extraction_noise
from modules.registry.audit.audit_types import AuditCompareReport, AuditPrediction

logger = get_logger("registry_service")
from proc_schemas.coding import FinalCode, CodingResult
from proc_schemas.registry.ip_v2 import (
    IPRegistryV2,
    PatientInfo as PatientInfoV2,
    ProcedureInfo as ProcedureInfoV2,
)
from proc_schemas.registry.ip_v3 import (
    IPRegistryV3,
    PatientInfo as PatientInfoV3,
    ProcedureInfo as ProcedureInfoV3,
)
from modules.coder.application.smart_hybrid_policy import (
    SmartHybridOrchestrator,
    HybridCoderResult,
)
from modules.ml_coder.registry_predictor import RegistryMLPredictor
from modules.registry.model_runtime import get_registry_runtime_dir, resolve_model_backend
from modules.coder.parallel_pathway import ParallelPathwayOrchestrator
from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails


if TYPE_CHECKING:
    from modules.registry.self_correction.types import SelfCorrectionMetadata


def focus_note_for_extraction(note_text: str) -> tuple[str, dict[str, Any]]:
    """Optionally focus/summarize a note for deterministic extraction.

    Guardrail: RAW-ML auditing must always run on the full raw note text and
    must never use the focused/summarized text.
    """
    from modules.registry.extraction.focus import focus_note_for_extraction as _focus

    return _focus(note_text)


_HEADER_START_RE = re.compile(
    r"^\s*(?:PROCEDURES?|OPERATIONS?)\b\s*:?",
    re.IGNORECASE | re.MULTILINE,
)
_HEADER_END_RE = re.compile(
    r"^\s*(?:"
    r"ANESTHESIA"
    r"|INDICATION"
    r"|DESCRIPTION"
    r"|FINDINGS"
    r"|EXTUBATION"
    r"|RECOVERY"
    r"|DISPOSITION"
    r"|PROCEDURE\s+IN\s+DETAIL"
    r"|DESCRIPTION\s+OF\s+PROCEDURE"
    r"|PROCEDURE\s+DESCRIPTION"
    r")\b",
    re.IGNORECASE | re.MULTILINE,
)
_CPT_RE = re.compile(r"\b([37]\d{4})\b")


def _extract_procedure_header_block(text: str) -> str | None:
    """Return the block immediately following the procedure header (signals only)."""
    if not text:
        return None

    start = _HEADER_START_RE.search(text)
    if not start:
        return None

    after = text[start.end() :]
    end = _HEADER_END_RE.search(after)
    header_body = after[: end.start()] if end else after[:1500]
    header_body = header_body.strip()
    return header_body or None


def _scan_header_for_codes(text: str) -> set[str]:
    """Scan the procedure header block for explicit CPT codes (e.g., 31653)."""
    header = _extract_procedure_header_block(text)
    if not header:
        return set()
    return set(_CPT_RE.findall(header))


def _hash_note_text(text: str) -> str:
    normalized = (text or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _append_self_correction_log(path: str, payload: dict[str, Any]) -> None:
    if not path:
        return
    try:
        log_path = Path(path)
        if log_path.exists() and log_path.is_dir():
            logger.warning("Self-correction log path is a directory: %s", log_path)
            return
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception as exc:
        logger.warning("Failed to write self-correction log: %s", exc)


def _apply_granular_up_propagation(record: RegistryRecord) -> tuple[RegistryRecord, list[str]]:
    """Apply granular→aggregate propagation using derive_procedures_from_granular().

    This must remain the single place where granular evidence drives aggregate
    performed flags.
    """
    if record.granular_data is None:
        return record, []

    granular = record.granular_data.model_dump()
    existing_procedures = (
        record.procedures_performed.model_dump() if record.procedures_performed is not None else None
    )

    updated_procs, granular_warnings = derive_procedures_from_granular(
        granular_data=granular,
        existing_procedures=existing_procedures,
    )

    if not updated_procs and not granular_warnings:
        return record, []

    record_data = record.model_dump()
    if updated_procs:
        record_data["procedures_performed"] = updated_procs
    record_data.setdefault("granular_validation_warnings", [])
    record_data["granular_validation_warnings"].extend(granular_warnings)

    return RegistryRecord(**record_data), granular_warnings


@dataclass
class RegistryDraftResult:
    """Result from building a draft registry entry."""

    entry: IPRegistryV2 | IPRegistryV3
    completeness_score: float
    missing_fields: list[str]
    suggested_values: dict[str, Any]
    warnings: list[str]
    hints: dict[str, list[str]]  # Aggregated hints from CPT mappings


@dataclass
class RegistryExportResult:
    """Result from exporting a procedure to the registry."""

    entry: IPRegistryV2 | IPRegistryV3
    registry_id: str
    schema_version: str
    export_id: str
    export_timestamp: datetime
    status: Literal["success", "partial", "failed"]
    warnings: list[str] = field(default_factory=list)


@dataclass
class RegistryExtractionResult:
    """Result from hybrid-first registry field extraction.

    Combines:
    - CPT codes from SmartHybridOrchestrator
    - Registry fields mapped from CPT codes
    - Extracted fields from RegistryEngine
    - Validation results and manual review flags
    - ML audit results comparing CPT-derived flags with ML predictions

    Attributes:
        record: The extracted RegistryRecord.
        cpt_codes: CPT codes from the hybrid coder.
        coder_difficulty: Case difficulty (HIGH_CONF/GRAY_ZONE/LOW_CONF).
        coder_source: Where codes came from (ml_rules_fastpath/hybrid_llm_fallback).
        mapped_fields: Registry fields derived from CPT mapping.
        code_rationales: Deterministic derivation rationales keyed by CPT code.
        derivation_warnings: Warnings emitted during deterministic CPT derivation.
        warnings: Non-blocking warnings about the extraction.
        needs_manual_review: Whether this case requires human review.
        validation_errors: List of validation errors found during reconciliation.
        audit_warnings: ML vs CPT discrepancy warnings requiring human review.
    """

    record: RegistryRecord
    cpt_codes: list[str]
    coder_difficulty: str
    coder_source: str
    mapped_fields: dict[str, Any]
    code_rationales: dict[str, str] = field(default_factory=dict)
    derivation_warnings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    needs_manual_review: bool = False
    validation_errors: list[str] = field(default_factory=list)
    audit_warnings: list[str] = field(default_factory=list)
    audit_report: AuditCompareReport | None = None
    self_correction: list["SelfCorrectionMetadata"] = field(default_factory=list)


class RegistryService:
    """Application service for registry export operations.

    This service:
    - Builds registry entries from coding results and procedure metadata
    - Maps CPT codes to registry boolean flags using cpt_registry_mapping
    - Validates entries against Pydantic schemas
    - Produces structured export results with warnings
    """

    VERSION = "registry_service_v1"

    def __init__(
        self,
        schema_registry: RegistrySchemaRegistry | None = None,
        default_version: str = "v2",
        hybrid_orchestrator: SmartHybridOrchestrator | None = None,
        registry_engine: RegistryEngine | None = None,
        parallel_orchestrator: ParallelPathwayOrchestrator | None = None,
    ):
        """Initialize RegistryService.

        Args:
            schema_registry: Registry for versioned schemas. Uses default if None.
            default_version: Default schema version to use if not specified.
            hybrid_orchestrator: Optional SmartHybridOrchestrator for ML-first coding.
            registry_engine: Optional RegistryEngine for field extraction. Lazy-init if None.
        """
        self.schema_registry = schema_registry or get_schema_registry()
        self.default_version = default_version
        self.hybrid_orchestrator = hybrid_orchestrator
        self._registry_engine = registry_engine
        self._registry_ml_predictor: Any | None = None
        self._ml_predictor_init_attempted: bool = False
        self.parallel_orchestrator = parallel_orchestrator or ParallelPathwayOrchestrator()
        self.clinical_guardrails = ClinicalGuardrails()

    @property
    def registry_engine(self) -> RegistryEngine:
        """Lazy initialization of RegistryEngine."""
        if self._registry_engine is None:
            self._registry_engine = RegistryEngine()
        return self._registry_engine

    def _get_registry_ml_predictor(self) -> Any | None:
        """Get registry ML predictor with lazy initialization.

        Behavior:
        - If MODEL_BACKEND is set to "onnx", require ONNX and fail fast if unavailable.
        - If MODEL_BACKEND is set to "pytorch", prefer Torch and fall back to sklearn if unavailable.
        - Otherwise ("auto"), keep legacy behavior: try ONNX first (if available),
          then sklearn TF-IDF.

        Returns the predictor if available, or None if artifacts are missing.
        Logs once on initialization failure to avoid log spam.
        """
        if self._ml_predictor_init_attempted:
            return self._registry_ml_predictor

        self._ml_predictor_init_attempted = True

        backend = resolve_model_backend()
        runtime_dir = get_registry_runtime_dir()

        def _try_pytorch() -> Any | None:
            try:
                from modules.registry.inference_pytorch import TorchRegistryPredictor

                predictor = TorchRegistryPredictor(bundle_dir=runtime_dir)
                if predictor.available:
                    logger.info(
                        "Using TorchRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("Torch predictor initialized but not available")
            except ImportError as e:
                logger.debug("PyTorch/Transformers not available (%s)", e)
            except Exception as e:
                logger.debug("Torch predictor init failed (%s)", e)
            return None

        def _try_onnx() -> Any | None:
            try:
                from modules.registry.inference_onnx import ONNXRegistryPredictor

                # Prefer runtime bundle paths if present; otherwise keep defaults.
                model_path: Path | None = None
                for candidate in ("registry_model_int8.onnx", "registry_model.onnx"):
                    p = runtime_dir / candidate
                    if p.exists():
                        model_path = p
                        break

                tokenizer_path: Path | None = None
                for candidate in ("tokenizer", "roberta_registry_tokenizer"):
                    p = runtime_dir / candidate
                    if p.exists():
                        tokenizer_path = p
                        break

                thresholds_path: Path | None = None
                for candidate in ("thresholds.json", "registry_thresholds.json", "roberta_registry_thresholds.json"):
                    p = runtime_dir / candidate
                    if p.exists():
                        thresholds_path = p
                        break

                label_fields_path: Path | None = None
                candidate_label_fields = runtime_dir / "registry_label_fields.json"
                if candidate_label_fields.exists():
                    label_fields_path = candidate_label_fields
                    # Prefer threshold-aligned labels; if the bundle label list is stale (common),
                    # fall back to the canonical default shipped with the repo.
                    try:
                        thresholds_payload = (
                            json.loads(thresholds_path.read_text())
                            if thresholds_path and thresholds_path.exists()
                            else None
                        )
                        labels_payload = json.loads(candidate_label_fields.read_text())
                        if isinstance(thresholds_payload, dict) and thresholds_payload:
                            threshold_keys = {k for k in thresholds_payload.keys() if isinstance(k, str)}
                            label_keys = (
                                {x for x in labels_payload if isinstance(x, str)}
                                if isinstance(labels_payload, list)
                                else set()
                            )
                            if threshold_keys and label_keys != threshold_keys:
                                label_fields_path = None
                    except Exception:
                        label_fields_path = None

                predictor = ONNXRegistryPredictor(
                    model_path=model_path,
                    tokenizer_path=tokenizer_path,
                    thresholds_path=thresholds_path,
                    label_fields_path=label_fields_path,
                )
                if predictor.available:
                    logger.info(
                        "Using ONNXRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("ONNX model not available")
            except ImportError:
                logger.debug("ONNX runtime not available")
            except Exception as e:
                logger.debug("ONNX predictor init failed (%s)", e)
            return None

        if backend == "pytorch":
            predictor = _try_pytorch()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor
        elif backend == "onnx":
            predictor = _try_onnx()
            if predictor is None:
                model_path = runtime_dir / "registry_model_int8.onnx"
                raise RuntimeError(
                    "MODEL_BACKEND=onnx but ONNXRegistryPredictor failed to initialize. "
                    f"Expected model at {model_path}."
                )
            self._registry_ml_predictor = predictor
            return self._registry_ml_predictor
        else:
            predictor = _try_onnx()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor

        # Fall back to TF-IDF sklearn predictor
        try:
            self._registry_ml_predictor = RegistryMLPredictor()
            if not self._registry_ml_predictor.available:
                logger.warning(
                    "RegistryMLPredictor initialized but not available "
                    "(model artifacts missing). ML hybrid audit disabled."
                )
                self._registry_ml_predictor = None
            else:
                logger.info(
                    "Using RegistryMLPredictor (TF-IDF) with %d labels",
                    len(self._registry_ml_predictor.labels),
                )
        except Exception:
            logger.exception(
                "Failed to initialize RegistryMLPredictor; ML hybrid audit disabled."
            )
            self._registry_ml_predictor = None

        return self._registry_ml_predictor

    def build_draft_entry(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryDraftResult:
        """Build a draft registry entry from final codes and metadata.

        This method:
        1. Maps CPT codes to registry boolean flags
        2. Merges with provided procedure metadata
        3. Validates against the target schema
        4. Computes completeness score and missing fields

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3"), defaults to default_version

        Returns:
            RegistryDraftResult with entry, completeness, and warnings
        """
        version = version or self.default_version
        metadata = procedure_metadata or {}
        warnings: list[str] = []
        missing_fields: list[str] = []

        # Extract CPT codes
        cpt_codes = [fc.code for fc in final_codes]

        # Get aggregated registry fields from CPT mappings
        registry_fields = aggregate_registry_fields_flat(cpt_codes, version)
        hints = aggregate_registry_hints(cpt_codes)

        # Get the appropriate builder for this version
        builder = get_builder(version)

        # Build patient and procedure info using the builder
        patient_info = builder.build_patient(metadata, missing_fields)
        procedure_info = builder.build_procedure(procedure_id, metadata, missing_fields)

        # Build the registry entry using the builder
        entry = builder.build_entry(
            procedure_id=procedure_id,
            patient=patient_info,
            procedure=procedure_info,
            registry_fields=registry_fields,
            metadata=metadata,
        )

        # Validate and generate warnings
        validation_warnings = self._validate_entry(entry, version)
        warnings.extend(validation_warnings)

        # Compute completeness score
        completeness_score = self._compute_completeness(entry, missing_fields)

        # Suggest values based on hints
        suggested_values = self._generate_suggestions(hints, entry)

        return RegistryDraftResult(
            entry=entry,
            completeness_score=completeness_score,
            missing_fields=missing_fields,
            suggested_values=suggested_values,
            warnings=warnings,
            hints=hints,
        )

    def export_procedure(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryExportResult:
        """Export a procedure to the registry.

        This method:
        1. Builds a draft entry using build_draft_entry()
        2. Generates an export ID for tracking
        3. Returns a structured export result

        Note: Actual persistence is handled by the caller (API layer),
        keeping this service focused on business logic.

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3")

        Returns:
            RegistryExportResult with entry and export metadata

        Raises:
            RegistryError: If export fails due to validation errors
        """
        version = version or self.default_version

        # Build the draft entry
        draft = self.build_draft_entry(
            procedure_id=procedure_id,
            final_codes=final_codes,
            procedure_metadata=procedure_metadata,
            version=version,
        )

        # Generate export ID
        export_id = f"export_{uuid.uuid4().hex[:12]}"
        export_timestamp = datetime.utcnow()

        # Determine status based on completeness
        if draft.completeness_score >= 0.8:
            status: Literal["success", "partial", "failed"] = "success"
        elif draft.completeness_score >= 0.5:
            status = "partial"
            draft.warnings.append(
                f"Export completed with partial data (completeness: {draft.completeness_score:.0%})"
            )
        else:
            # Still allow export but mark as partial
            status = "partial"
            draft.warnings.append(
                f"Low completeness score ({draft.completeness_score:.0%}). "
                "Consider adding more procedure metadata."
            )

        return RegistryExportResult(
            entry=draft.entry,
            registry_id="ip_registry",
            schema_version=version,
            export_id=export_id,
            export_timestamp=export_timestamp,
            status=status,
            warnings=draft.warnings,
        )

    # NOTE: _build_patient_info, _build_procedure_info, _build_v2_entry, and
    # _build_v3_entry have been refactored into the registry_builder module
    # using the Strategy Pattern. See registry_builder.py for V2RegistryBuilder
    # and V3RegistryBuilder.

    def _validate_entry(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        version: str,
    ) -> list[str]:
        """Validate an entry and return warnings."""
        warnings: list[str] = []

        # Check for common data quality issues
        if not entry.patient.patient_id and not entry.patient.mrn:
            warnings.append("Patient identifier missing (patient_id or mrn)")

        if not entry.procedure.procedure_date:
            warnings.append("Procedure date not specified")

        if not entry.procedure.indication:
            warnings.append("Procedure indication not specified")

        # Check for procedure-specific completeness
        if entry.ebus_performed and not entry.ebus_stations:
            warnings.append("EBUS performed but no stations documented")

        if entry.tblb_performed and not entry.tblb_sites:
            warnings.append("TBLB performed but no biopsy sites documented")

        if entry.bal_performed and not entry.bal_sites:
            warnings.append("BAL performed but no sites documented")

        if entry.stent_placed and not entry.stents:
            warnings.append("Stent placed but no stent details documented")

        return warnings

    def _compute_completeness(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        missing_fields: list[str],
    ) -> float:
        """Compute a completeness score for the entry.

        Score is based on:
        - Required fields present (patient ID, date, indication)
        - Procedure-specific fields when relevant
        """
        max_score = 10.0
        score = max_score

        # Deduct for missing required fields
        required_deductions = {
            "patient.patient_id or patient.mrn": 2.0,
            "procedure.procedure_date": 1.5,
            "procedure.indication": 1.0,
        }

        for field in missing_fields:
            if field in required_deductions:
                score -= required_deductions[field]

        # Deduct for procedure-specific missing data
        if entry.ebus_performed and not entry.ebus_stations:
            score -= 0.5
        if entry.tblb_performed and not entry.tblb_sites:
            score -= 0.5
        if entry.stent_placed and not entry.stents:
            score -= 0.5

        return max(0.0, score / max_score)

    def _generate_suggestions(
        self,
        hints: dict[str, list[str]],
        entry: IPRegistryV2 | IPRegistryV3,
    ) -> dict[str, Any]:
        """Generate suggested values based on hints and entry state."""
        suggestions: dict[str, Any] = {}

        # Suggest EBUS station count based on CPT hint
        if "station_count_hint" in hints:
            hint_values = hints["station_count_hint"]
            if "3+" in hint_values:
                suggestions["ebus_station_count"] = "3 or more stations (based on 31653)"
            elif "1-2" in hint_values:
                suggestions["ebus_station_count"] = "1-2 stations (based on 31652)"

        # Suggest navigation system if navigation performed
        if entry.navigation_performed and not entry.navigation_system:
            suggestions["navigation_system"] = "Consider specifying navigation system"

        return suggestions

    # -------------------------------------------------------------------------
    # Hybrid-First Registry Extraction
    # -------------------------------------------------------------------------

    def extract_fields(self, note_text: str, mode: str = "default") -> RegistryExtractionResult:
        """Extract registry fields using hybrid-first flow.

        This method orchestrates:
        1. Run hybrid coder to get CPT codes and difficulty classification
        2. Map CPT codes to registry boolean flags
        3. Run RegistryEngine extractor with coder context as hints
        4. Merge CPT-driven fields into the extraction result
        5. Validate and finalize the result

        Args:
            note_text: The procedure note text.
            mode: Optional override (e.g., "parallel_ner").

        Returns:
            RegistryExtractionResult with extracted record and metadata.
        """
        masked_note_text, _mask_meta = mask_extraction_noise(note_text)

        if mode == "parallel_ner":
            predictor = self._get_registry_ml_predictor()
            result = self.parallel_orchestrator.run_parallel_process(
                masked_note_text,
                ml_predictor=predictor,
            )
            return self._apply_guardrails_to_result(masked_note_text, result)

        pipeline_mode = os.getenv("PROCSUITE_PIPELINE_MODE", "current").strip().lower()
        if pipeline_mode != "extraction_first":
            allow_legacy = os.getenv("PROCSUITE_ALLOW_LEGACY_PIPELINES", "0").strip().lower() in {
                "1",
                "true",
                "yes",
                "y",
            }
            if not allow_legacy:
                raise ValueError(
                    "Legacy pipelines are disabled. Set PROCSUITE_ALLOW_LEGACY_PIPELINES=1 to enable."
                )
        if pipeline_mode == "extraction_first":
            return self._extract_fields_extraction_first(note_text)

        # Legacy fallback: if no hybrid orchestrator is injected, run extractor only
        if self.hybrid_orchestrator is None:
            logger.info("No hybrid_orchestrator configured, running extractor-only mode")
            record = self.registry_engine.run(masked_note_text, context={"schema_version": "v3"})
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included
            return RegistryExtractionResult(
                record=record,
                cpt_codes=[],
                coder_difficulty="unknown",
                coder_source="extractor_only",
                mapped_fields={},
                warnings=["No hybrid orchestrator configured - CPT codes not extracted"],
            )

        # 1. Run Hybrid Coder
        logger.debug("Running hybrid coder for registry extraction")
        coder_result: HybridCoderResult = self.hybrid_orchestrator.get_codes(masked_note_text)

        # 2. Map Codes to Registry Fields
        mapped_fields = aggregate_registry_fields(
            coder_result.codes, version=self.default_version
        )
        logger.debug(
            "Mapped %d CPT codes to registry fields",
            len(coder_result.codes),
            extra={"cpt_codes": coder_result.codes, "mapped_fields": list(mapped_fields.keys())},
        )

        # 3. Run Extractor with Coder Hints
        extraction_context = {
            "verified_cpt_codes": coder_result.codes,
            "coder_difficulty": coder_result.difficulty.value,
            "hybrid_source": coder_result.source,
            "ml_metadata": coder_result.metadata.get("ml_result"),
            "schema_version": "v3",
        }

        engine_warnings: list[str] = []
        run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
        if callable(run_with_warnings):
            record, engine_warnings = run_with_warnings(
                masked_note_text,
                context=extraction_context,
            )
        else:
            record = self.registry_engine.run(masked_note_text, context=extraction_context)
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included

        # 4. Merge CPT-driven fields into the extraction result
        merged_record = self._merge_cpt_fields_into_record(record, mapped_fields)

        # 5. Validate and finalize (includes ML hybrid audit)
        final_result = self._validate_and_finalize(
            RegistryExtractionResult(
                record=merged_record,
                cpt_codes=coder_result.codes,
                coder_difficulty=coder_result.difficulty.value,
                coder_source=coder_result.source,
                mapped_fields=mapped_fields,
                warnings=list(engine_warnings),
            ),
            coder_result=coder_result,
            note_text=masked_note_text,
        )

        return final_result

    def extract_fields_extraction_first(self, note_text: str) -> RegistryExtractionResult:
        """Extract registry fields using extraction-first flow.

        This bypasses the hybrid-first pipeline and always runs:
        1) Registry extraction
        2) Deterministic Registry→CPT derivation
        3) RAW-ML audit (if enabled)
        """
        return self._extract_fields_extraction_first(note_text)

    # -------------------------------------------------------------------------
    # Extraction-First Registry → Deterministic CPT → RAW-ML Audit
    # -------------------------------------------------------------------------

    def extract_record(
        self,
        note_text: str,
        *,
        note_id: str | None = None,
    ) -> tuple[RegistryRecord, list[str], dict[str, Any]]:
        """Extract a RegistryRecord from note text without CPT hints.

        This is the extraction-first entrypoint for registry evidence. It must
        not seed extraction with CPT codes, ML-predicted CPT codes, or any
        SmartHybridOrchestrator output.
        """
        warnings: list[str] = []
        meta: dict[str, Any] = {"note_id": note_id}

        extraction_engine = os.getenv("REGISTRY_EXTRACTION_ENGINE", "engine").strip().lower()
        meta["extraction_engine"] = extraction_engine

        raw_note_text = note_text
        masked_note_text, mask_meta = mask_extraction_noise(raw_note_text)
        meta["masked_note_text"] = masked_note_text
        meta["masking_meta"] = mask_meta

        schema_version = os.getenv("REGISTRY_SCHEMA_VERSION", "v3").strip().lower()
        meta["schema_version"] = schema_version

        disease_scan_text: str | None = None

        def _apply_disease_burden_overrides(record_in: RegistryRecord) -> RegistryRecord:
            nonlocal disease_scan_text

            if schema_version != "v3":
                return record_in

            try:
                if disease_scan_text is None:
                    from modules.registry.processing.masking import mask_offset_preserving

                    disease_scan_text = mask_offset_preserving(raw_note_text or "")

                from modules.registry.extractors.disease_burden import apply_disease_burden_overrides

                record_out, burden_warnings = apply_disease_burden_overrides(
                    record_in,
                    note_text=disease_scan_text,
                )
                warnings.extend(burden_warnings)
                return record_out
            except Exception as exc:
                warnings.append(f"DISEASE_BURDEN_OVERRIDE_FAILED: {type(exc).__name__}")
                return record_in

        def _filter_stale_parallel_review_reasons(
            record_in: RegistryRecord,
            reasons: list[str] | None,
        ) -> list[str]:
            """Drop ML-only review reasons when the current record now derives that CPT.

            Parallel review reasons are generated before deterministic uplift/backfills.
            Re-check against the post-uplift record to avoid noisy stale warnings.
            """
            reason_list = [str(r) for r in (reasons or []) if str(r).strip()]
            if not reason_list:
                return []

            try:
                from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta

                derived_codes, _rationales, _warn = derive_all_codes_with_meta(record_in)
                derived_set = {str(code).strip() for code in (derived_codes or []) if str(code).strip()}
            except Exception:
                return reason_list

            filtered: list[str] = []
            for reason in reason_list:
                match = re.match(r"^\s*(\d{5})\s*:", reason)
                if match and match.group(1) in derived_set:
                    continue
                filtered.append(reason)
            return filtered

        text_for_extraction = masked_note_text
        if extraction_engine == "engine":
            pass
        elif extraction_engine == "agents_focus_then_engine":
            # Phase 2: focusing helper is optional; guardrail is that RAW-ML always
            # runs on the raw note text.
            try:
                focused_text, focus_meta = focus_note_for_extraction(masked_note_text)
                meta["focus_meta"] = focus_meta
                text_for_extraction = focused_text or masked_note_text
            except Exception as exc:
                warnings.append(f"focus_note_for_extraction failed ({exc}); using masked note")
                meta["focus_meta"] = {"status": "failed", "error": str(exc)}
                text_for_extraction = masked_note_text
        elif extraction_engine == "agents_structurer":
            try:
                from modules.registry.extraction.structurer import structure_note_to_registry_record

                record, struct_meta = structure_note_to_registry_record(
                    masked_note_text,
                    note_id=note_id,
                )
                meta["structurer_meta"] = struct_meta
                meta["extraction_text"] = masked_note_text

                record, granular_warnings = _apply_granular_up_propagation(record)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    cull_hollow_ebus_claims,
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record, masked_note_text))
                warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))
                warnings.extend(cull_hollow_ebus_claims(record, masked_note_text))

                from modules.registry.application.pathology_extraction import apply_pathology_extraction

                record, pathology_warnings = apply_pathology_extraction(record, masked_note_text)
                warnings.extend(pathology_warnings)

                record = _apply_disease_burden_overrides(record)
                return record, warnings, meta
            except NotImplementedError as exc:
                warnings.append(str(exc))
                meta["structurer_meta"] = {"status": "not_implemented"}
            except Exception as exc:
                warnings.append(f"Structurer failed ({exc}); falling back to engine")
                meta["structurer_meta"] = {"status": "failed", "error": str(exc)}
        elif extraction_engine == "parallel_ner":
            # Parallel NER pathway: Run NER → Registry mapping → Rules + ML safety net
            try:
                predictor = self._get_registry_ml_predictor()
                parallel_result = self.parallel_orchestrator.process(
                    masked_note_text,
                    ml_predictor=predictor,
                )

                # Get record from Path A (NER → Registry → Rules)
                path_a_details = parallel_result.path_a_result.details
                record = path_a_details.get("record")

                if record is None:
                    # Fallback: create empty record if NER pathway failed
                    record = RegistryRecord()
                    warnings.append("Parallel NER path_a produced no record; using empty record")

                ner_evidence = self.parallel_orchestrator._build_ner_evidence(
                    path_a_details.get("ner_entities")
                )
                if ner_evidence:
                    record_evidence = getattr(record, "evidence", None)
                    if not isinstance(record_evidence, dict):
                        record_evidence = {}
                    for key, spans in ner_evidence.items():
                        record_evidence.setdefault(key, []).extend(spans)
                    record.evidence = record_evidence

                # Deterministic fallback: fill common missed procedure flags so
                # extraction-first does not silently drop revenue when NER misses.
                try:
                    import re

                    from modules.common.spans import Span
                    from modules.registry.deterministic_extractors import (
                        AIRWAY_DILATION_PATTERNS,
                        AIRWAY_STENT_DEVICE_PATTERNS,
                        BAL_PATTERNS,
                        BALLOON_OCCLUSION_PATTERNS,
                        BLVR_PATTERNS,
                        BRUSHINGS_PATTERNS,
                        CHEST_TUBE_PATTERNS,
                        CHEST_ULTRASOUND_PATTERNS,
                        CRYOPROBE_PATTERN,
                        CRYOTHERAPY_PATTERNS,
                        CRYOBIOPSY_PATTERN,
                        DIAGNOSTIC_BRONCHOSCOPY_PATTERNS,
                        ESTABLISHED_TRACH_ROUTE_PATTERNS,
                        FOREIGN_BODY_REMOVAL_PATTERNS,
                        IPC_PATTERNS,
                        NAVIGATIONAL_BRONCHOSCOPY_PATTERNS,
                        PERIPHERAL_ABLATION_PATTERNS,
                        RIGID_BRONCHOSCOPY_PATTERNS,
                        ENDOBRONCHIAL_BIOPSY_PATTERNS,
                        TRANSBRONCHIAL_BIOPSY_PATTERNS,
                        RADIAL_EBUS_PATTERNS,
                        TBNA_CONVENTIONAL_PATTERNS,
                        THERMAL_ABLATION_PATTERNS,
                        TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS,
                        TRACHEAL_PUNCTURE_PATTERNS,
                        run_deterministic_extractors,
                    )

                    # Use an offset-preserving mask that removes CPT/menu noise but keeps
                    # non-procedural headings (e.g., INDICATION) so deterministic extractors
                    # can still populate clinical_context while the LLM/NER path stays masked.
                    from modules.registry.processing.masking import mask_offset_preserving

                    seed_text = mask_offset_preserving(raw_note_text or "")
                    seed = run_deterministic_extractors(seed_text)
                    seed_procs = seed.get("procedures_performed") if isinstance(seed, dict) else None
                    seed_pleural = seed.get("pleural_procedures") if isinstance(seed, dict) else None
                    seed_established_trach = (
                        seed.get("established_tracheostomy_route") is True if isinstance(seed, dict) else False
                    )
                    seed_has_context = False
                    if isinstance(seed, dict):
                        for key in ("primary_indication", "sedation_type", "patient_age", "gender", "airway_type"):
                            val = seed.get(key)
                            if val not in (None, "", [], {}):
                                seed_has_context = True
                                break
                    fiducial_candidate = "fiducial" in (masked_note_text or "").lower()
                    tracheal_puncture_candidate = any(
                        re.search(pat, masked_note_text or "", re.IGNORECASE)
                        for pat in TRACHEAL_PUNCTURE_PATTERNS
                    )

                    if (
                        (isinstance(seed_procs, dict) and seed_procs)
                        or (isinstance(seed_pleural, dict) and seed_pleural)
                        or seed_established_trach
                        or fiducial_candidate
                        or seed_has_context
                        or tracheal_puncture_candidate
                    ):
                        record_data = record.model_dump()
                        record_procs = record_data.get("procedures_performed")
                        if not isinstance(record_procs, dict):
                            record_procs = {}
                            record_data["procedures_performed"] = record_procs

                        record_pleural = record_data.get("pleural_procedures")
                        if not isinstance(record_pleural, dict):
                            record_pleural = {}
                            record_data["pleural_procedures"] = record_pleural

                        evidence = record_data.get("evidence")
                        if not isinstance(evidence, dict):
                            evidence = {}
                            record_data["evidence"] = evidence

                        # Merge deterministic extractor evidence spans (attribute-level highlights).
                        seed_evidence = seed.get("evidence") if isinstance(seed, dict) else None
                        if isinstance(seed_evidence, dict):
                            for key, spans in seed_evidence.items():
                                if not isinstance(key, str) or not key:
                                    continue
                                if not isinstance(spans, list) or not spans:
                                    continue
                                for span in spans:
                                    if isinstance(span, Span):
                                        evidence.setdefault(key, []).append(span)

                        uplifted: list[str] = []
                        proc_modified = False
                        pleural_modified = False
                        other_modified = False

                        def _add_first_span(field: str, patterns: list[str]) -> None:
                            for pat in patterns:
                                match = re.search(pat, masked_note_text or "", re.IGNORECASE)
                                if match:
                                    evidence.setdefault(field, []).append(
                                        Span(
                                            text=match.group(0).strip(),
                                            start=match.start(),
                                            end=match.end(),
                                        )
                                    )
                                    return

                        def _add_first_span_skip_cpt_headers(field: str, patterns: list[str]) -> None:
                            cpt_line = re.compile(r"^\s*\d{5}\b")
                            offset = 0
                            for raw_line in (masked_note_text or "").splitlines(keepends=True):
                                line = raw_line.rstrip("\r\n")
                                if cpt_line.match(line):
                                    offset += len(raw_line)
                                    continue
                                for pat in patterns:
                                    match = re.search(pat, line, re.IGNORECASE)
                                    if match:
                                        evidence.setdefault(field, []).append(
                                            Span(
                                                text=match.group(0).strip(),
                                                start=offset + match.start(),
                                                end=offset + match.end(),
                                            )
                                        )
                                        return
                                offset += len(raw_line)

                        def _add_first_literal(field: str, literal: str) -> None:
                            if not literal:
                                return
                            match = re.search(re.escape(literal), raw_note_text or "", re.IGNORECASE)
                            if not match:
                                tokens = re.split(r"\s+", literal.strip())
                                if len(tokens) >= 2:
                                    pattern = r"\s+".join(re.escape(tok) for tok in tokens if tok)
                                    if pattern:
                                        match = re.search(pattern, raw_note_text or "", re.IGNORECASE)
                            if not match:
                                return
                            evidence.setdefault(field, []).append(
                                Span(text=match.group(0).strip(), start=match.start(), end=match.end())
                            )

                        def _apply_seed_context(seed_data: dict[str, Any]) -> None:
                            """Merge deterministic clinical/sedation/demographics into the v3 schema blocks.

                            Important: Only fill missing values, and avoid applying "defaults" that are not
                            explicitly evidenced in the note (e.g., ASA default=3 or GA→ETT default).
                            """

                            nonlocal other_modified

                            if not isinstance(seed_data, dict) or not seed_data:
                                return

                            # Patient demographics
                            age = seed_data.get("patient_age")
                            gender = seed_data.get("gender")
                            if age is not None or gender:
                                demo = record_data.get("patient_demographics") or {}
                                if not isinstance(demo, dict):
                                    demo = {}
                                demo_changed = False
                                if age is not None and demo.get("age_years") is None:
                                    demo["age_years"] = age
                                    demo_changed = True
                                if gender and not demo.get("gender"):
                                    # Normalize common shorthand
                                    g = str(gender).strip()
                                    if g.lower() in {"m"}:
                                        g = "Male"
                                    elif g.lower() in {"f"}:
                                        g = "Female"
                                    demo["gender"] = g
                                    demo_changed = True
                                if demo_changed:
                                    record_data["patient_demographics"] = demo
                                    other_modified = True
                                    if age is not None:
                                        _add_first_literal("patient_demographics.age_years", str(age))
                                    if gender:
                                        _add_first_literal("patient_demographics.gender", str(gender))

                            # Clinical context
                            clinical = record_data.get("clinical_context") or {}
                            if not isinstance(clinical, dict):
                                clinical = {}
                            clinical_changed = False

                            primary_indication = seed_data.get("primary_indication")
                            if primary_indication and not clinical.get("primary_indication"):
                                clinical["primary_indication"] = primary_indication
                                clinical_changed = True
                                _add_first_literal(
                                    "clinical_context.primary_indication",
                                    str(primary_indication),
                                )

                            # Indication category heuristic (only when primary_indication present)
                            if clinical.get("primary_indication") and not clinical.get("indication_category"):
                                ind_lower = str(clinical.get("primary_indication") or "").lower()
                                category = None
                                if re.search(r"\b(?:stenosis|stricture)\b", ind_lower):
                                    category = "Stricture/Stenosis"
                                elif re.search(r"\bmalacia\b", ind_lower):
                                    category = "Tracheobronchomalacia"
                                elif re.search(r"\bhemoptysis\b", ind_lower):
                                    category = "Hemoptysis"
                                elif re.search(r"\b(?:lung|pulmonary)\s+nodule\b|\bnodule\b", ind_lower):
                                    category = "Lung Nodule Evaluation"
                                if category:
                                    clinical["indication_category"] = category
                                    clinical_changed = True

                            # ASA class: avoid applying default=3 when ASA not explicitly documented.
                            asa_val = seed_data.get("asa_class")
                            if asa_val is not None and clinical.get("asa_class") is None:
                                if re.search(r"(?i)\bASA\b", masked_note_text or ""):
                                    clinical["asa_class"] = asa_val
                                    clinical_changed = True
                                    _add_first_span_skip_cpt_headers(
                                        "clinical_context.asa_class",
                                        [r"\bASA(?:\s+Classification)?[\s:]+[IViv123456]+(?:-E)?\b"],
                                    )

                            if clinical_changed:
                                record_data["clinical_context"] = clinical
                                other_modified = True

                            # Sedation: map seed sedation_type→sedation.type (schema v3)
                            sed_type = seed_data.get("sedation_type")
                            if isinstance(sed_type, str) and sed_type.strip():
                                sedation = record_data.get("sedation") or {}
                                if not isinstance(sedation, dict):
                                    sedation = {}
                                if not sedation.get("type"):
                                    sedation["type"] = sed_type.strip()
                                    record_data["sedation"] = sedation
                                    other_modified = True
                                    sed_patterns: list[str] = []
                                    if sed_type.strip().lower() == "general":
                                        sed_patterns = [r"\bgeneral\s+anesthesia\b", r"\banesthesia\b"]
                                    elif sed_type.strip().lower() == "mac":
                                        sed_patterns = [
                                            r"\bmonitored\s+anesthesia\s+care\b",
                                            r"\bmac\b",
                                        ]
                                    elif sed_type.strip().lower() == "moderate":
                                        sed_patterns = [r"\bmoderate\s+sedation\b", r"\bconscious\s+sedation\b"]
                                    elif sed_type.strip().lower() == "local only":
                                        sed_patterns = [r"\blocal\s+anesthesia\b", r"\blidocaine\b"]
                                    if sed_patterns:
                                        _add_first_span_skip_cpt_headers("sedation.type", sed_patterns)

                                    # Provider inference only when explicitly stated
                                    if not sedation.get("anesthesia_provider"):
                                        if re.search(r"(?i)\bCRNA\b", masked_note_text or ""):
                                            sedation["anesthesia_provider"] = "CRNA"
                                        elif re.search(r"(?i)\banesthesiolog(?:ist|y)\b", masked_note_text or ""):
                                            sedation["anesthesia_provider"] = "Anesthesiologist"
                                        if sedation.get("anesthesia_provider"):
                                            record_data["sedation"] = sedation
                                            _add_first_span_skip_cpt_headers(
                                                "sedation.anesthesia_provider",
                                                [
                                                    r"\bCRNA\b",
                                                    r"\banesthesiolog(?:ist|y)\b",
                                                ],
                                            )

                            # Procedure setting: apply airway_type only if explicitly evidenced.
                            airway_type = seed_data.get("airway_type")
                            if isinstance(airway_type, str) and airway_type.strip():
                                airway_type_norm = airway_type.strip()
                                patterns_by_type: dict[str, list[str]] = {
                                    "ETT": [r"\bett\b|endotracheal\s+tube|intubat\w*"],
                                    "LMA": [r"\blma\b|laryngeal\s+mask"],
                                    "iGel": [r"\bi-?gel\b"],
                                    "Tracheostomy": [
                                        r"\bvia\s+(?:an?\s+)?tracheostom\w*\b",
                                        r"\bthrough\s+(?:an?\s+)?trach(?:eostom\w*)?\b",
                                        r"\btrach(?:eostom\w*)?\s+tube\b",
                                    ],
                                }
                                airway_patterns = patterns_by_type.get(airway_type_norm)
                                if airway_patterns and any(
                                    re.search(pat, raw_note_text or "", re.IGNORECASE) for pat in airway_patterns
                                ):
                                    setting = record_data.get("procedure_setting") or {}
                                    if not isinstance(setting, dict):
                                        setting = {}
                                    if not setting.get("airway_type"):
                                        setting["airway_type"] = airway_type_norm
                                        record_data["procedure_setting"] = setting
                                        other_modified = True
                                        _add_first_span_skip_cpt_headers(
                                            "procedure_setting.airway_type",
                                            airway_patterns,
                                        )

                            # Outcomes: disposition / follow-up plan / completion.
                            outcomes_seed = seed_data.get("outcomes")
                            if isinstance(outcomes_seed, dict) and outcomes_seed:
                                outcomes = record_data.get("outcomes") or {}
                                if not isinstance(outcomes, dict):
                                    outcomes = {}
                                outcomes_changed = False

                                for key in (
                                    "procedure_completed",
                                    "procedure_aborted_reason",
                                    "disposition",
                                    "follow_up_plan_text",
                                ):
                                    value = outcomes_seed.get(key)
                                    if value in (None, "", [], {}):
                                        continue
                                    if outcomes.get(key) in (None, "", [], {}):
                                        outcomes[key] = value
                                        outcomes_changed = True

                                if outcomes_changed:
                                    record_data["outcomes"] = outcomes
                                    other_modified = True

                        def _populate_diagnostic_bronchoscopy_findings() -> None:
                            """Fill diagnostic bronchoscopy findings/abnormalities when missing."""
                            nonlocal proc_modified

                            record_procs_local = record_data.get("procedures_performed") or {}
                            if not isinstance(record_procs_local, dict):
                                return
                            proc = record_procs_local.get("diagnostic_bronchoscopy") or {}
                            if not isinstance(proc, dict):
                                return
                            if proc.get("performed") is not True:
                                return

                            abnormalities = proc.get("airway_abnormalities")
                            if abnormalities is None:
                                abnormalities = []
                            if not isinstance(abnormalities, list):
                                abnormalities = []

                            detail_lower = (masked_note_text or "").lower()
                            full_text = raw_note_text or ""
                            full_lower = full_text.lower()
                            found: list[str] = []

                            if "secretions" in detail_lower and "Secretions" not in abnormalities:
                                abnormalities.append("Secretions")
                                found.append("secretions")
                            if re.search(r"\b(tracheomalacia)\b", detail_lower):
                                if "Tracheomalacia" not in abnormalities:
                                    abnormalities.append("Tracheomalacia")
                                    found.append("tracheomalacia")
                            elif re.search(r"\b(bronchomalacia)\b", detail_lower):
                                if "Bronchomalacia" not in abnormalities:
                                    abnormalities.append("Bronchomalacia")
                                    found.append("bronchomalacia")
                            elif "malacia" in detail_lower and "Tracheomalacia" not in abnormalities:
                                abnormalities.append("Tracheomalacia")
                                found.append("malacia")

                            # "Stenosis" often appears in INDICATION, which is masked for the LLM/NER path.
                            # Use the raw note as a backstop (avoids missing stenosis for cases explicitly
                            # scoped to stenosis).
                            try:
                                # Prevent CPT definition/header noise (e.g., "relief of stenosis") from
                                # leaking into airway findings.
                                from modules.registry.processing.masking import mask_offset_preserving

                                findings_text = mask_offset_preserving(full_text)
                            except Exception:
                                findings_text = full_text
                            if "stenosis" in findings_text.lower() and "Stenosis" not in abnormalities:
                                if not re.search(r"(?i)\bno\s+stenosis\b", findings_text):
                                    abnormalities.append("Stenosis")
                                    found.append("stenosis")

                            # Vocal cord abnormality should only be set when explicitly abnormal near the mention
                            # (avoid false positives from unrelated "abnormal" elsewhere in the note).
                            if "Vocal cord abnormality" not in abnormalities:
                                m = re.search(r"(?i)\bvocal\s+cords?\b[^.\n]{0,160}", full_text)
                                if m:
                                    sentence = (m.group(0) or "").lower()
                                    if "normal" not in sentence and re.search(
                                        r"\b(?:abnormal|paraly|paralysis|immobil|immobile|lesion|dysfunction)\w*\b",
                                        sentence,
                                    ):
                                        abnormalities.append("Vocal cord abnormality")
                                        found.append("vocal_cord_abnormality")

                            findings_changed = False
                            if abnormalities and proc.get("airway_abnormalities") in (None, [], {}):
                                proc["airway_abnormalities"] = abnormalities
                                findings_changed = True
                                # Evidence anchors for the abnormalities
                                if "secretions" in found:
                                    _add_first_span_skip_cpt_headers(
                                        "procedures_performed.diagnostic_bronchoscopy.airway_abnormalities",
                                        [r"\bsecretions?\b[^.\n]{0,80}\b(?:suction|clear)\w*\b", r"\bsecretions?\b"],
                                    )
                                if any(tok in found for tok in ("tracheomalacia", "bronchomalacia", "malacia")):
                                    _add_first_span_skip_cpt_headers(
                                        "procedures_performed.diagnostic_bronchoscopy.airway_abnormalities",
                                        [r"\b(?:tracheo|broncho)?malacia\b"],
                                    )
                                if "stenosis" in found:
                                    _add_first_literal(
                                        "procedures_performed.diagnostic_bronchoscopy.airway_abnormalities",
                                        "tracheal stenosis",
                                    )
                                    _add_first_literal(
                                        "procedures_performed.diagnostic_bronchoscopy.airway_abnormalities",
                                        "stenosis",
                                    )
                                if "vocal_cord_abnormality" in found:
                                    _add_first_span_skip_cpt_headers(
                                        "procedures_performed.diagnostic_bronchoscopy.airway_abnormalities",
                                        [
                                            r"\bvocal\s+cords?\b[^.\n]{0,120}\b(?:abnormal|paraly|paralysis|immobil|immobile|lesion|dysfunction)\w*\b"
                                        ],
                                    )

                            if not proc.get("inspection_findings"):
                                parts: list[str] = []
                                patterns = [
                                    r"\bvocal\s+cords?\b[^.\n]{0,160}",
                                    r"\bprevious\s+tracheostomy\s+site\b[^.\n]{0,160}",
                                    r"\bmalacia\b[^.\n]{0,160}",
                                    r"\bsecretions?\b[^.\n]{0,160}",
                                ]
                                for pat in patterns:
                                    match = re.search(pat, masked_note_text or "", re.IGNORECASE)
                                    if match:
                                        snippet = match.group(0).strip()
                                        if snippet and snippet not in parts:
                                            parts.append(snippet)
                                if parts:
                                    proc["inspection_findings"] = " ".join(parts)[:700]
                                    findings_changed = True
                                    _add_first_span_skip_cpt_headers(
                                        "procedures_performed.diagnostic_bronchoscopy.inspection_findings",
                                        [r"\binitial\s+airway\s+inspection\s+findings\b", r"\bthe\s+airway\s+was\s+inspected\b"],
                                    )

                            if findings_changed:
                                record_procs_local["diagnostic_bronchoscopy"] = proc
                                record_data["procedures_performed"] = record_procs_local
                                proc_modified = True

                        def _populate_navigation_equipment() -> None:
                            """Populate equipment navigation/CBCT flags when strongly evidenced."""
                            nonlocal other_modified

                            equipment = record_data.get("equipment") or {}
                            if not isinstance(equipment, dict):
                                equipment = {}

                            changed = False
                            lowered = (masked_note_text or "").lower()

                            # Navigation platform (schema enum values)
                            if not equipment.get("navigation_platform"):
                                platform_raw = None
                                if re.search(r"(?i)\bintuitive\s+ion\b|\bion\b", masked_note_text or ""):
                                    platform_raw = "Ion"
                                elif re.search(r"(?i)\bmonarch\b", masked_note_text or ""):
                                    platform_raw = "Monarch"
                                elif re.search(r"(?i)\bgalaxy\b|\bnoah\b", masked_note_text or ""):
                                    platform_raw = "Galaxy"
                                elif re.search(r"(?i)\bsuperdimension\b|\bEMN\b|\belectromagnetic\s+navigation\b", masked_note_text or ""):
                                    platform_raw = "superDimension"
                                elif re.search(r"(?i)\billumisite\b", masked_note_text or ""):
                                    platform_raw = "ILLUMISITE"
                                elif re.search(r"(?i)\bspin(?:drive)?\b", masked_note_text or ""):
                                    platform_raw = "SPiN"
                                elif re.search(r"(?i)\blungvision\b", masked_note_text or ""):
                                    platform_raw = "LungVision"
                                elif re.search(r"(?i)\barchimedes\b", masked_note_text or ""):
                                    platform_raw = "ARCHIMEDES"

                                if platform_raw:
                                    from modules.registry.postprocess import normalize_navigation_platform

                                    normalized = normalize_navigation_platform(platform_raw)
                                    if normalized:
                                        equipment["navigation_platform"] = normalized
                                        changed = True
                                        _add_first_span_skip_cpt_headers(
                                            "equipment.navigation_platform",
                                            [
                                                r"\bintuitive\s+ion\b",
                                                r"\bion\b",
                                                r"\bmonarch\b",
                                                r"\bgalaxy\b",
                                                r"\bnoah\b",
                                                r"\bsuperdimension\b",
                                                r"\belectromagnetic\s+navigation\b",
                                                r"\billumisite\b",
                                                r"\bspin(?:drive)?\b",
                                                r"\blungvision\b",
                                                r"\barchimedes\b",
                                            ],
                                        )

                            # Cone-beam CT usage
                            if equipment.get("cbct_used") is None:
                                if re.search(
                                    r"(?i)\bcone[-\s]?beam\s+ct\b|\bcbct\b|\bcios\b|\bspin\s+system\b|\blow\s+dose\s+spin\b",
                                    masked_note_text or "",
                                ):
                                    equipment["cbct_used"] = True
                                    changed = True
                                    _add_first_span_skip_cpt_headers(
                                        "equipment.cbct_used",
                                        [
                                            r"\bcone[-\s]?beam\s+ct\b",
                                            r"\bcbct\b",
                                            r"\bcios\b",
                                            r"\bspin\s+system\b",
                                            r"\blow\s+dose\s+spin\b",
                                        ],
                                    )

                            # 3D rendering / reconstruction (proxy via augmented_fluoroscopy flag)
                            if equipment.get("augmented_fluoroscopy") is None:
                                if re.search(
                                    r"(?i)\b3[-\s]?d\s+(?:reconstruction|reconstructions|rendering)\b|\b3d\s+(?:reconstruction|rendering)\b",
                                    masked_note_text or "",
                                ):
                                    equipment["augmented_fluoroscopy"] = True
                                    changed = True
                                    _add_first_span_skip_cpt_headers(
                                        "equipment.augmented_fluoroscopy",
                                        [
                                            r"\b3[-\s]?d\s+reconstructions?\b",
                                            r"\b3d\s+reconstructions?\b",
                                            r"\b3[-\s]?d\s+rendering\b",
                                            r"\b3d\s+rendering\b",
                                            r"\bplanning\s+station\b",
                                        ],
                                    )

                            # Fluoroscopy is commonly present when CBCT/fiducials are used.
                            if equipment.get("fluoroscopy_used") is None:
                                if (
                                    equipment.get("cbct_used") is True
                                    or "fluoroscopy" in lowered
                                    or re.search(r"(?i)\bunder\s+fluoroscopy\s+guidance\b", masked_note_text or "")
                                ):
                                    equipment["fluoroscopy_used"] = True
                                    changed = True

                            if changed:
                                record_data["equipment"] = equipment
                                other_modified = True

                        if isinstance(seed_procs, dict):
                            for proc_name, proc_data in seed_procs.items():
                                if not isinstance(proc_data, dict):
                                    continue
                                if proc_data.get("performed") is not True:
                                    continue

                                existing = record_procs.get(proc_name) or {}
                                if not isinstance(existing, dict):
                                    existing = {}
                                already_performed = existing.get("performed") is True
                                proc_changed = False

                                if not already_performed:
                                    existing["performed"] = True
                                    uplifted.append(proc_name)
                                    proc_changed = True

                                for key, value in proc_data.items():
                                    if key == "performed":
                                        continue
                                    if proc_name == "airway_stent":
                                        if key == "airway_stent_removal" and value is True and existing.get(key) is not True:
                                            existing[key] = True
                                            proc_changed = True
                                            continue
                                        if key == "action" and isinstance(value, str) and value.strip():
                                            incoming_action = value.strip()
                                            existing_action_raw = existing.get("action")
                                            existing_action = (
                                                str(existing_action_raw).strip()
                                                if existing_action_raw is not None
                                                else ""
                                            )
                                            can_override_action = existing_action in ("", "Placement")
                                            # If deterministic extraction sees an exchange/repositioning,
                                            # prefer revision semantics over a removal-only NER action.
                                            if (
                                                incoming_action == "Revision/Repositioning"
                                                and existing_action == "Removal"
                                            ):
                                                can_override_action = True
                                            if can_override_action and existing_action != incoming_action:
                                                existing[key] = incoming_action
                                                action_type_by_action = {
                                                    "Placement": "placement",
                                                    "Removal": "removal",
                                                    "Revision/Repositioning": "revision",
                                                    "Assessment only": "assessment_only",
                                                }
                                                normalized_action_type = action_type_by_action.get(incoming_action)
                                                if normalized_action_type:
                                                    existing["action_type"] = normalized_action_type
                                                proc_changed = True
                                                continue

                                    if existing.get(key) in (None, "", [], {}):
                                        existing[key] = value
                                        proc_changed = True

                                if proc_changed:
                                    record_procs[proc_name] = existing
                                    proc_modified = True

                                if not already_performed:
                                    field_key = f"procedures_performed.{proc_name}.performed"
                                    if proc_name == "bal":
                                        _add_first_span(field_key, list(BAL_PATTERNS))
                                    elif proc_name == "endobronchial_biopsy":
                                        _add_first_span(
                                            field_key,
                                            list(ENDOBRONCHIAL_BIOPSY_PATTERNS),
                                        )
                                    elif proc_name == "radial_ebus":
                                        _add_first_span(field_key, list(RADIAL_EBUS_PATTERNS))
                                    elif proc_name == "navigational_bronchoscopy":
                                        _add_first_span(
                                            field_key,
                                            list(NAVIGATIONAL_BRONCHOSCOPY_PATTERNS),
                                        )
                                    elif proc_name == "tbna_conventional":
                                        _add_first_span(
                                            field_key,
                                            list(TBNA_CONVENTIONAL_PATTERNS),
                                        )
                                    elif proc_name == "peripheral_tbna":
                                        _add_first_span(
                                            field_key,
                                            list(TBNA_CONVENTIONAL_PATTERNS),
                                        )
                                    elif proc_name == "brushings":
                                        _add_first_span(field_key, list(BRUSHINGS_PATTERNS))
                                    elif proc_name == "rigid_bronchoscopy":
                                        _add_first_span(
                                            field_key,
                                            list(RIGID_BRONCHOSCOPY_PATTERNS),
                                        )
                                    elif proc_name == "transbronchial_biopsy":
                                        _add_first_span(
                                            field_key,
                                            list(TRANSBRONCHIAL_BIOPSY_PATTERNS),
                                        )
                                    elif proc_name == "transbronchial_cryobiopsy":
                                        _add_first_span(
                                            field_key,
                                            list(TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS),
                                        )
                                    elif proc_name == "airway_dilation":
                                        _add_first_span(field_key, list(AIRWAY_DILATION_PATTERNS))
                                    elif proc_name == "airway_stent":
                                        _add_first_span(field_key, list(AIRWAY_STENT_DEVICE_PATTERNS))
                                    elif proc_name == "blvr":
                                        _add_first_span_skip_cpt_headers(
                                            field_key,
                                            list(BLVR_PATTERNS) + list(BALLOON_OCCLUSION_PATTERNS),
                                        )
                                    elif proc_name == "foreign_body_removal":
                                        _add_first_span(field_key, list(FOREIGN_BODY_REMOVAL_PATTERNS))
                                    elif proc_name == "percutaneous_tracheostomy":
                                        _add_first_span_skip_cpt_headers(
                                            field_key,
                                            list(TRACHEAL_PUNCTURE_PATTERNS)
                                            + [
                                                r"\bpercutaneous\s+(?:dilatational\s+)?tracheostomy\b",
                                                r"\bperc\s+trach\b",
                                                r"\btracheostomy\b[^.\n]{0,60}\b(?:performed|placed|inserted|created)\b",
                                            ],
                                        )
                                    elif proc_name == "peripheral_ablation":
                                        _add_first_span(
                                            field_key,
                                            list(PERIPHERAL_ABLATION_PATTERNS),
                                        )
                                    elif proc_name == "thermal_ablation":
                                        _add_first_span_skip_cpt_headers(
                                            field_key,
                                            list(THERMAL_ABLATION_PATTERNS),
                                        )
                                    elif proc_name == "cryotherapy":
                                        cryo_patterns = list(CRYOTHERAPY_PATTERNS)
                                        if not re.search(
                                            CRYOBIOPSY_PATTERN,
                                            masked_note_text or "",
                                            re.IGNORECASE,
                                        ):
                                            cryo_patterns.append(CRYOPROBE_PATTERN)
                                        _add_first_span_skip_cpt_headers(field_key, cryo_patterns)
                                    elif proc_name == "diagnostic_bronchoscopy":
                                        _add_first_span_skip_cpt_headers(
                                            field_key,
                                            list(DIAGNOSTIC_BRONCHOSCOPY_PATTERNS),
                                        )
                                    elif proc_name == "chest_ultrasound":
                                        _add_first_span(
                                            field_key,
                                            list(CHEST_ULTRASOUND_PATTERNS),
                                        )

                        if isinstance(seed_pleural, dict):
                            for proc_name, proc_data in seed_pleural.items():
                                if not isinstance(proc_data, dict):
                                    continue
                                if proc_data.get("performed") is not True:
                                    continue

                                existing = record_pleural.get(proc_name) or {}
                                if not isinstance(existing, dict):
                                    existing = {}
                                already_performed = existing.get("performed") is True
                                proc_changed = False

                                if not already_performed:
                                    existing["performed"] = True
                                    uplifted.append(f"pleural_procedures.{proc_name}")
                                    proc_changed = True

                                for key, value in proc_data.items():
                                    if key == "performed":
                                        continue
                                    if existing.get(key) in (None, "", [], {}):
                                        existing[key] = value
                                        proc_changed = True

                                if proc_changed:
                                    record_pleural[proc_name] = existing
                                    pleural_modified = True

                                if not already_performed:
                                    field_key = f"pleural_procedures.{proc_name}.performed"
                                    if proc_name == "chest_tube":
                                        _add_first_span(field_key, list(CHEST_TUBE_PATTERNS))
                                    elif proc_name == "ipc":
                                        _add_first_span(field_key, list(IPC_PATTERNS))

                        if seed_established_trach and not record_data.get("established_tracheostomy_route"):
                            record_data["established_tracheostomy_route"] = True
                            other_modified = True
                            _add_first_span_skip_cpt_headers(
                                "established_tracheostomy_route",
                                list(ESTABLISHED_TRACH_ROUTE_PATTERNS),
                            )

                        # Tracheal puncture (31612 family) is NOT a tracheostomy creation. Capture evidence
                        # for coding without flipping percutaneous_tracheostomy.performed=true.
                        tracheal_puncture_key = "procedures_performed.tracheal_puncture.performed"
                        if not evidence.get(tracheal_puncture_key):
                            if any(
                                re.search(pat, masked_note_text or "", re.IGNORECASE)
                                for pat in TRACHEAL_PUNCTURE_PATTERNS
                            ):
                                _add_first_span_skip_cpt_headers(
                                    tracheal_puncture_key,
                                    list(TRACHEAL_PUNCTURE_PATTERNS),
                                )
                                if evidence.get(tracheal_puncture_key):
                                    other_modified = True

                        def _mark_subsequent_aspiration() -> None:
                            """Attach an evidence marker when header/body indicates subsequent aspiration (31646)."""
                            nonlocal other_modified

                            procs_local = record_data.get("procedures_performed") or {}
                            if not isinstance(procs_local, dict):
                                return
                            asp = procs_local.get("therapeutic_aspiration") or {}
                            if not (isinstance(asp, dict) and asp.get("performed") is True):
                                return

                            # Avoid duplicating markers
                            if evidence.get("procedures_performed.therapeutic_aspiration.is_subsequent"):
                                return

                            header_codes_local = _scan_header_for_codes(raw_note_text)
                            has_header_31646 = "31646" in header_codes_local
                            has_body_signal = bool(
                                re.search(
                                    r"(?i)\bsubsequent\s+aspirat|repeat\s+aspirat|subsequent\s+episode",
                                    raw_note_text or "",
                                )
                            )
                            if not (has_header_31646 or has_body_signal):
                                return

                            # Prefer anchoring to the explicit code when present; otherwise to the phrase.
                            if has_header_31646:
                                _add_first_literal(
                                    "procedures_performed.therapeutic_aspiration.is_subsequent",
                                    "31646",
                                )
                            else:
                                _add_first_span_skip_cpt_headers(
                                    "procedures_performed.therapeutic_aspiration.is_subsequent",
                                    [
                                        r"\bsubsequent\s+aspirat\w*\b",
                                        r"\brepeat\s+aspirat\w*\b",
                                        r"\bsubsequent\s+episode(?:s)?\b",
                                    ],
                                )
                            other_modified = True

                        # Fill common missing clinical context/sedation/demographics from deterministic extractors.
                        _apply_seed_context(seed)

                        # Backstop diagnostic bronchoscopy findings/abnormalities when present.
                        _populate_diagnostic_bronchoscopy_findings()

                        # Backstop subsequent aspiration episode marker for 31646 vs 31645.
                        _mark_subsequent_aspiration()

                        # Backstop navigation/CBCT imaging signals for downstream coding.
                        _populate_navigation_equipment()

                        # Prefer real code evidence when explicit CPT codes appear in the procedure header.
                        header_codes = _scan_header_for_codes(raw_note_text)
                        if header_codes:
                            for code in sorted(header_codes):
                                match = re.search(rf"\b{re.escape(code)}\b", raw_note_text or "")
                                if match:
                                    evidence.setdefault("code_evidence", []).append(
                                        Span(text=match.group(0), start=match.start(), end=match.end())
                                    )

                        if fiducial_candidate:
                            from modules.registry.processing.navigation_fiducials import (
                                apply_navigation_fiducials,
                            )

                            if apply_navigation_fiducials(record_data, masked_note_text):
                                other_modified = True

                        if uplifted:
                            warnings.append(
                                "DETERMINISTIC_UPLIFT: added performed=true for "
                                + ", ".join(sorted(set(uplifted)))
                            )

                        if proc_modified:
                            record_data["procedures_performed"] = record_procs
                        if pleural_modified:
                            record_data["pleural_procedures"] = record_pleural
                        if evidence and (proc_modified or pleural_modified or other_modified):
                            record_data["evidence"] = evidence

                        if proc_modified or pleural_modified or other_modified:
                            record = RegistryRecord(**record_data)
                except Exception as exc:
                    warnings.append(f"Deterministic uplift failed ({exc})")

                # Store parallel pathway metadata
                meta["parallel_pathway"] = {
                    "path_a": {
                        "source": parallel_result.path_a_result.source,
                        "codes": parallel_result.path_a_result.codes,
                        "processing_time_ms": parallel_result.path_a_result.processing_time_ms,
                        "ner_entity_count": path_a_details.get("ner_entity_count", 0),
                        "stations_sampled_count": path_a_details.get("stations_sampled_count", 0),
                    },
                    "path_b": {
                        "source": parallel_result.path_b_result.source,
                        "codes": parallel_result.path_b_result.codes,
                        "confidences": parallel_result.path_b_result.confidences,
                        "processing_time_ms": parallel_result.path_b_result.processing_time_ms,
                    },
                    "final_codes": parallel_result.final_codes,
                    "final_confidences": parallel_result.final_confidences,
                    "needs_review": parallel_result.needs_review,
                    "review_reasons": parallel_result.review_reasons,
                    "total_time_ms": parallel_result.total_time_ms,
                }
                meta["extraction_text"] = masked_note_text

                # Apply standard postprocessing
                record, granular_warnings = _apply_granular_up_propagation(record)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    cull_hollow_ebus_claims,
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record, masked_note_text))
                warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))
                warnings.extend(cull_hollow_ebus_claims(record, masked_note_text))

                from modules.registry.application.pathology_extraction import apply_pathology_extraction

                record, pathology_warnings = apply_pathology_extraction(record, masked_note_text)
                warnings.extend(pathology_warnings)

                # Add review warnings if parallel pathway flagged discrepancies
                if parallel_result.needs_review:
                    warnings.extend(
                        _filter_stale_parallel_review_reasons(record, parallel_result.review_reasons)
                    )

                record = _apply_disease_burden_overrides(record)
                return record, warnings, meta
            except Exception as exc:
                warnings.append(f"Parallel NER pathway failed ({exc}); falling back to engine")
                meta["parallel_pathway"] = {"status": "failed", "error": str(exc)}
        else:
            warnings.append(f"Unknown REGISTRY_EXTRACTION_ENGINE='{extraction_engine}', using engine")

        meta["extraction_text"] = text_for_extraction
        context: dict[str, Any] = {"schema_version": "v3"}
        if note_id:
            context["note_id"] = note_id
        engine_warnings: list[str] = []
        run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
        if callable(run_with_warnings):
            record, engine_warnings = run_with_warnings(text_for_extraction, context=context)
        else:
            record = self.registry_engine.run(text_for_extraction, context=context)
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included
        warnings.extend(engine_warnings)

        record, granular_warnings = _apply_granular_up_propagation(record)
        warnings.extend(granular_warnings)

        from modules.registry.evidence.verifier import verify_evidence_integrity
        from modules.registry.postprocess import (
            cull_hollow_ebus_claims,
            populate_ebus_node_events_fallback,
            sanitize_ebus_events,
        )

        record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
        warnings.extend(verifier_warnings)
        warnings.extend(sanitize_ebus_events(record, masked_note_text))
        warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))
        warnings.extend(cull_hollow_ebus_claims(record, masked_note_text))

        from modules.registry.application.pathology_extraction import apply_pathology_extraction

        record, pathology_warnings = apply_pathology_extraction(record, masked_note_text)
        warnings.extend(pathology_warnings)

        record = _apply_disease_burden_overrides(record)
        return record, warnings, meta

    def _extract_fields_extraction_first(self, raw_note_text: str) -> RegistryExtractionResult:
        """Extraction-first registry pipeline.

        Order (must not call orchestrator / CPT seeding):
        1) extract_record(raw_note_text)
        2) deterministic Registry→CPT derivation (Phase 3)
        3) RAW-ML audit via MLCoderPredictor.classify_case(raw_note_text)
        """
        from modules.registry.audit.raw_ml_auditor import RawMLAuditor
        from modules.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt
        from modules.registry.audit.compare import build_audit_compare_report
        from modules.registry.self_correction.apply import SelfCorrectionApplyError, apply_patch_to_record
        from modules.registry.self_correction.judge import RegistryCorrectionJudge
        from modules.registry.self_correction.keyword_guard import (
            apply_required_overrides,
            keyword_guard_check,
            keyword_guard_passes,
            scan_for_omissions,
        )
        from modules.registry.self_correction.types import SelfCorrectionMetadata, SelfCorrectionTrigger
        from modules.registry.self_correction.validation import (
            ALLOWED_PATHS,
            ALLOWED_PATH_PREFIXES,
            validate_proposal,
        )

        # Guardrail: auditing must always use the original raw note text. Do not
        # overwrite this variable with focused/summarized text.
        raw_text_for_audit = raw_note_text

        masked_note_text, _mask_meta = mask_extraction_noise(raw_note_text)

        def _env_flag(name: str, default: str = "0") -> bool:
            return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y"}

        def _env_int(name: str, default: int) -> int:
            raw = os.getenv(name)
            if raw is None:
                return default
            raw = raw.strip()
            if not raw:
                return default
            try:
                return int(raw)
            except ValueError:
                return default

        def _apply_navigation_target_heuristics(
            note_text: str, record_in: RegistryRecord
        ) -> tuple[RegistryRecord, list[str]]:
            if record_in is None:
                return RegistryRecord(), []

            text = note_text or ""
            if ("\n" not in text and "\r" not in text) and ("\\n" in text or "\\r" in text):
                text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
            nav_hint = re.search(
                r"(?i)\b(navigational bronchoscopy|robotic bronchoscopy|electromagnetic navigation|\benb\b|\bion\b|monarch|galaxy|planning station)\b",
                text,
            )
            if not nav_hint:
                return record_in, []

            from modules.registry.processing.navigation_targets import (
                extract_cryobiopsy_sites,
                extract_navigation_targets,
            )

            parsed_targets = extract_navigation_targets(text)
            target_lines = [
                line
                for line in text.splitlines()
                if re.search(r"(?i)target lesion", line)
                or re.search(r"(?i)^\s*target\s*\d{1,2}\s*[:\\-]", line)
            ]
            if not parsed_targets and not target_lines:
                return record_in, []

            record_data = record_in.model_dump()
            granular = record_data.get("granular_data")
            if granular is None or not isinstance(granular, dict):
                granular = {}

            targets_raw = granular.get("navigation_targets")
            if isinstance(targets_raw, list):
                targets = [dict(t) for t in targets_raw if isinstance(t, dict)]
            else:
                targets = []

            def _is_placeholder_location(value: object) -> bool:
                if value is None:
                    return True
                s = str(value).strip().lower()
                if not s:
                    return True
                # Common boilerplate lines that are not target locations.
                if "robotic navigation bronchoscopy was performed" in s:
                    return True
                if "partial registration" in s and "target lesion" in s:
                    return True
                if "||" in s:
                    return True
                if re.search(r"(?i)^(?:pt|patient)\\s*:", s):
                    return True
                if re.search(r"(?i)\\b(?:mrn|dob)\\b\\s*:", s):
                    return True
                if re.search(r"(?i)\\b(?:attending|fellow)\\b\\s*:", s):
                    return True
                return s in {
                    "unknown",
                    "unknown target",
                    "target",
                    "target lesion",
                    "target lesion 1",
                    "target lesion 2",
                    "target lesion 3",
                } or s.startswith("target lesion")

            def _is_more_specific_location(existing_value: object, candidate_value: object) -> bool:
                existing = str(existing_value or "").strip()
                candidate = str(candidate_value or "").strip()
                if not candidate:
                    return False
                if not existing:
                    return True
                existing_lower = existing.lower()
                candidate_lower = candidate.lower()
                existing_has_bronchus = bool(re.search(r"\\b[LR]B\\d{1,2}\\b", existing, re.IGNORECASE))
                candidate_has_bronchus = bool(re.search(r"\\b[LR]B\\d{1,2}\\b", candidate, re.IGNORECASE))
                if candidate_has_bronchus and not existing_has_bronchus:
                    return True
                if "segment" in candidate_lower and "segment" not in existing_lower:
                    return True
                if ("(" in candidate and ")" in candidate) and ("(" not in existing or ")" not in existing):
                    return True
                if ("nodule" in candidate_lower or "#" in candidate_lower) and (
                    "nodule" not in existing_lower and "#" not in existing_lower
                ):
                    return True
                return False

            def _sanitize_target_location(value: str) -> str:
                raw = (value or "").strip()
                if not raw:
                    return ""
                for stop_word in ("PROCEDURE", "INDICATION", "TECHNIQUE", "DESCRIPTION"):
                    match = re.search(rf"(?i)\b{re.escape(stop_word)}\b", raw)
                    if match:
                        raw = raw[: match.start()].strip()
                if len(raw) > 100:
                    clipped = raw[:100].rsplit(" ", 1)[0].strip()
                    raw = clipped or raw[:100].strip()
                return raw

            warnings: list[str] = []
            updated = False

            if parsed_targets:
                # Merge parsed targets (from TARGET headings / "Target:" lines) into existing targets.
                max_len = max(len(targets), len(parsed_targets))
                merged: list[dict[str, Any]] = []
                for idx in range(max_len):
                    base = targets[idx] if idx < len(targets) else {}
                    parsed = parsed_targets[idx] if idx < len(parsed_targets) else {}
                    out = dict(base)

                    # Always normalize target_number to 1..N for consistency.
                    out["target_number"] = idx + 1

                    for key, value in parsed.items():
                        if value in (None, "", [], {}):
                            continue
                        if key == "target_location_text":
                            if _is_placeholder_location(out.get(key)) or _is_more_specific_location(
                                out.get(key), value
                            ):
                                out[key] = value
                                updated = True
                            continue
                        if key == "fiducial_marker_placed":
                            if value is True and out.get(key) is not True:
                                out[key] = True
                                updated = True
                            continue
                        if out.get(key) in (None, "", [], {}):
                            out[key] = value
                            updated = True

                    merged.append(out)

                targets = merged
                warnings.append(
                    f"NAV_TARGET_HEURISTIC: parsed {len(parsed_targets)} navigation target(s) from target text"
                )
            else:
                existing_count = len(targets)
                needed_count = len(target_lines)
                if existing_count >= needed_count:
                    return record_in, []

                for idx in range(existing_count, needed_count):
                    line = _sanitize_target_location(target_lines[idx])
                    targets.append(
                        {
                            "target_number": idx + 1,
                            "target_location_text": line or f"Target lesion {idx + 1}",
                        }
                    )
                added = needed_count - existing_count
                warnings.append(f"NAV_TARGET_HEURISTIC: added {added} navigation target(s) from text")
                updated = True

            granular["navigation_targets"] = targets

            # Cryobiopsy sites: populate granular per-site detail when target sections include cryobiopsy.
            existing_sites = granular.get("cryobiopsy_sites")
            if not existing_sites:
                sites = extract_cryobiopsy_sites(text)
                if sites:
                    granular["cryobiopsy_sites"] = sites
                    warnings.append(f"CRYOBIOPSY_SITE_HEURISTIC: added {len(sites)} cryobiopsy site(s) from text")
                    updated = True

            record_data["granular_data"] = granular
            record_out = RegistryRecord(**record_data)
            if not updated:
                return record_in, []
            return record_out, warnings

        def _apply_linear_ebus_station_detail_heuristics(
            note_text: str, record_in: RegistryRecord
        ) -> tuple[RegistryRecord, list[str]]:
            if record_in is None:
                return RegistryRecord(), []

            text = note_text or ""
            if not re.search(r"(?i)\b(?:ebus|endobronchial\s+ultrasound|ebus-tbna)\b", text):
                return record_in, []

            from modules.registry.processing.linear_ebus_stations_detail import (
                extract_linear_ebus_stations_detail,
            )

            parsed = extract_linear_ebus_stations_detail(text)
            if not parsed:
                return record_in, []

            record_data = record_in.model_dump()
            granular = record_data.get("granular_data")
            if granular is None or not isinstance(granular, dict):
                granular = {}

            existing_raw = granular.get("linear_ebus_stations_detail")
            existing: list[dict[str, Any]] = []
            if isinstance(existing_raw, list):
                existing = [dict(item) for item in existing_raw if isinstance(item, dict)]

            by_station: dict[str, dict[str, Any]] = {}
            order: list[str] = []
            for item in existing:
                station = str(item.get("station") or "").strip()
                if not station:
                    continue
                if station not in by_station:
                    order.append(station)
                by_station[station] = item

            added = 0
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                station = str(item.get("station") or "").strip()
                if not station:
                    continue
                existing_item = by_station.get(station)
                if existing_item is None:
                    by_station[station] = dict(item)
                    order.append(station)
                    added += 1
                    continue
                updated = False
                for key, value in item.items():
                    if key == "station":
                        continue
                    if value in (None, "", [], {}):
                        continue
                    if existing_item.get(key) in (None, "", [], {}):
                        existing_item[key] = value
                        updated = True
                if updated:
                    by_station[station] = existing_item

            merged = [by_station[s] for s in order if s in by_station]
            granular["linear_ebus_stations_detail"] = merged

            record_data["granular_data"] = granular
            record_out = RegistryRecord(**record_data)
            return (
                record_out,
                [f"EBUS_STATION_DETAIL_HEURISTIC: parsed {len(parsed)} station detail entr{'y' if len(parsed) == 1 else 'ies'} from text"],
            )

        def _apply_cao_detail_heuristics(
            note_text: str, record_in: RegistryRecord
        ) -> tuple[RegistryRecord, list[str]]:
            if record_in is None:
                return RegistryRecord(), []

            text = note_text or ""
            if not re.search(
                r"(?i)\b(?:"
                r"central\s+airway|airway\s+obstruct\w*|"
                r"rigid\s+bronchos\w*|"
                r"debulk\w*|"
                r"tumou?r\s+(?:ablation|destruction)|"
                r"stent"
                r")\b",
                text,
            ):
                return record_in, []

            from modules.registry.processing.cao_interventions_detail import (
                extract_cao_interventions_detail,
            )

            parsed = extract_cao_interventions_detail(text)
            if not parsed:
                return record_in, []

            record_data = record_in.model_dump()
            granular = record_data.get("granular_data")
            if granular is None or not isinstance(granular, dict):
                granular = {}

            existing_raw = granular.get("cao_interventions_detail")
            existing: list[dict[str, Any]] = []
            if isinstance(existing_raw, list):
                existing = [dict(item) for item in existing_raw if isinstance(item, dict)]

            def _key(item: dict[str, Any]) -> str:
                return str(item.get("location") or "").strip()

            by_loc: dict[str, dict[str, Any]] = {}
            order: list[str] = []
            for item in existing:
                loc = _key(item)
                if not loc:
                    continue
                if loc not in by_loc:
                    order.append(loc)
                by_loc[loc] = item

            added = 0
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                loc = _key(item)
                if not loc:
                    continue
                existing_item = by_loc.get(loc)
                if existing_item is None:
                    by_loc[loc] = dict(item)
                    order.append(loc)
                    added += 1
                    continue

                updated = False
                for key, value in item.items():
                    if key == "location":
                        continue
                    if value in (None, "", [], {}):
                        continue
                    if key == "modalities_applied":
                        existing_apps = existing_item.get("modalities_applied")
                        if not isinstance(existing_apps, list):
                            existing_apps = []
                        existing_mods = {
                            str(a.get("modality"))
                            for a in existing_apps
                            if isinstance(a, dict) and a.get("modality")
                        }
                        new_apps = []
                        if isinstance(value, list):
                            for app in value:
                                if not isinstance(app, dict):
                                    continue
                                mod = app.get("modality")
                                if not mod or str(mod) in existing_mods:
                                    continue
                                new_apps.append(app)
                        if new_apps:
                            existing_apps.extend(new_apps)
                            existing_item["modalities_applied"] = existing_apps
                            updated = True
                        continue
                    if existing_item.get(key) in (None, "", [], {}):
                        existing_item[key] = value
                        updated = True
                if updated:
                    by_loc[loc] = existing_item

            merged = [by_loc[loc] for loc in order if loc in by_loc]
            granular["cao_interventions_detail"] = merged

            record_data["granular_data"] = granular
            record_out = RegistryRecord(**record_data)
            return (
                record_out,
                [f"CAO_DETAIL_HEURISTIC: parsed {len(parsed)} CAO site entr{'y' if len(parsed) == 1 else 'ies'} from text"],
            )

        def _coverage_failures(note_text: str, record_in: RegistryRecord) -> list[str]:
            failures: list[str] = []
            text = note_text or ""

            ebus_hit = re.search(r"(?i)EBUS[- ]Findings|EBUS Lymph Nodes Sampled|\blinear\s+ebus\b", text)
            ebus_performed = False
            try:
                ebus_obj = (
                    record_in.procedures_performed.linear_ebus
                    if record_in.procedures_performed
                    else None
                )
                ebus_performed = bool(getattr(ebus_obj, "performed", False))
            except Exception:
                ebus_performed = False
            if ebus_hit and not ebus_performed:
                failures.append("linear_ebus missing")

            eus_hit = re.search(
                r"(?i)\bEUS-?B\b|\bleft adrenal\b|\btransgastric\b|\btransesophageal\b",
                text,
            )
            procedures = record_in.procedures_performed if record_in.procedures_performed else None
            if eus_hit and procedures is not None and hasattr(procedures, "eus_b"):
                eus_b_performed = False
                try:
                    eus_b_obj = getattr(procedures, "eus_b", None)
                    eus_b_performed = bool(getattr(eus_b_obj, "performed", False)) if eus_b_obj else False
                except Exception:
                    eus_b_performed = False
                if not eus_b_performed:
                    failures.append("eus_b missing")

            nav_hit = re.search(
                r"(?i)\b(navigational bronchoscopy|robotic bronchoscopy|electromagnetic navigation|\benb\b|\bion\b|monarch|galaxy)\b",
                text,
            )
            if nav_hit:
                target_mentions = len(re.findall(r"(?i)target lesion", text))
                try:
                    nav_targets = (
                        record_in.granular_data.navigation_targets
                        if record_in.granular_data is not None
                        else None
                    )
                    nav_count = len(nav_targets or [])
                except Exception:
                    nav_count = 0
                if target_mentions and nav_count < target_mentions:
                    failures.append(f"navigation_targets {nav_count} < {target_mentions}")

            return failures

        def _run_structurer_fallback(note_text: str) -> tuple[RegistryRecord | None, list[str]]:
            warnings: list[str] = []
            context: dict[str, Any] = {"schema_version": "v3"}
            try:
                run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
                if callable(run_with_warnings):
                    record_out, engine_warnings = run_with_warnings(note_text, context=context)
                    warnings.extend(engine_warnings or [])
                else:
                    record_out = self.registry_engine.run(note_text, context=context)
                    if isinstance(record_out, tuple):
                        record_out = record_out[0]

                record_out, granular_warnings = _apply_granular_up_propagation(record_out)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    cull_hollow_ebus_claims,
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record_out, verifier_warnings = verify_evidence_integrity(record_out, note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record_out, note_text))
                warnings.extend(populate_ebus_node_events_fallback(record_out, note_text))
                warnings.extend(cull_hollow_ebus_claims(record_out, note_text))
                return record_out, warnings
            except Exception as exc:
                warnings.append(f"STRUCTURER_FALLBACK_FAILED: {exc}")
                return None, warnings

        record, extraction_warnings, meta = self.extract_record(raw_note_text)
        extraction_text = meta.get("extraction_text") if isinstance(meta.get("extraction_text"), str) else None
        if isinstance(meta.get("masked_note_text"), str):
            masked_note_text = meta["masked_note_text"]

        record, override_warnings = apply_required_overrides(masked_note_text, record)
        if override_warnings:
            extraction_warnings.extend(override_warnings)

        from modules.registry.processing.masking import mask_offset_preserving

        nav_scan_text = mask_offset_preserving(raw_note_text or "")
        record, nav_target_warnings = _apply_navigation_target_heuristics(nav_scan_text, record)
        if nav_target_warnings:
            extraction_warnings.extend(nav_target_warnings)

        record, ebus_station_warnings = _apply_linear_ebus_station_detail_heuristics(nav_scan_text, record)
        if ebus_station_warnings:
            extraction_warnings.extend(ebus_station_warnings)

        # Use the extraction-masked text so CAO/stent heuristics don't read non-procedural
        # plan/assessment sections (common source of "possible stent placement" false positives).
        record, cao_detail_warnings = _apply_cao_detail_heuristics(masked_note_text, record)
        if cao_detail_warnings:
            extraction_warnings.extend(cao_detail_warnings)

        # Re-run granular→aggregate propagation after any heuristics/overrides that
        # update granular_data (e.g., navigation targets, cryobiopsy sites).
        record, granular_warnings = _apply_granular_up_propagation(record)
        if granular_warnings:
            extraction_warnings.extend(granular_warnings)

        from modules.registry.postprocess import (
            cull_hollow_ebus_claims,
            enrich_bal_from_procedure_detail,
            enrich_ebus_node_event_outcomes,
            enrich_ebus_node_event_sampling_details,
            enrich_eus_b_sampling_details,
            enrich_linear_ebus_needle_gauge,
            enrich_medical_thoracoscopy_biopsies_taken,
            enrich_outcomes_complication_details,
            enrich_procedure_success_status,
            populate_ebus_node_events_fallback,
            reconcile_ebus_sampling_from_narrative,
            reconcile_ebus_sampling_from_specimen_log,
            sanitize_ebus_events,
        )

        ebus_fallback_warnings = populate_ebus_node_events_fallback(record, masked_note_text)
        if ebus_fallback_warnings:
            extraction_warnings.extend(ebus_fallback_warnings)
        ebus_sanitize_warnings = sanitize_ebus_events(record, masked_note_text)
        if ebus_sanitize_warnings:
            extraction_warnings.extend(ebus_sanitize_warnings)
        ebus_narrative_warnings = reconcile_ebus_sampling_from_narrative(record, masked_note_text)
        if ebus_narrative_warnings:
            extraction_warnings.extend(ebus_narrative_warnings)
        ebus_specimen_warnings = reconcile_ebus_sampling_from_specimen_log(record, masked_note_text)
        if ebus_specimen_warnings:
            extraction_warnings.extend(ebus_specimen_warnings)
        ebus_sampling_detail_warnings = enrich_ebus_node_event_sampling_details(record, masked_note_text)
        if ebus_sampling_detail_warnings:
            extraction_warnings.extend(ebus_sampling_detail_warnings)
        ebus_outcome_warnings = enrich_ebus_node_event_outcomes(record, masked_note_text)
        if ebus_outcome_warnings:
            extraction_warnings.extend(ebus_outcome_warnings)
        ebus_gauge_warnings = enrich_linear_ebus_needle_gauge(record, masked_note_text)
        if ebus_gauge_warnings:
            extraction_warnings.extend(ebus_gauge_warnings)
        eus_b_detail_warnings = enrich_eus_b_sampling_details(record, masked_note_text)
        if eus_b_detail_warnings:
            extraction_warnings.extend(eus_b_detail_warnings)
        ebus_hollow_warnings = cull_hollow_ebus_claims(record, masked_note_text)
        if ebus_hollow_warnings:
            extraction_warnings.extend(ebus_hollow_warnings)
        pleural_biopsy_warnings = enrich_medical_thoracoscopy_biopsies_taken(record, masked_note_text)
        if pleural_biopsy_warnings:
            extraction_warnings.extend(pleural_biopsy_warnings)
        bal_detail_warnings = enrich_bal_from_procedure_detail(record, masked_note_text)
        if bal_detail_warnings:
            extraction_warnings.extend(bal_detail_warnings)
        outcomes_status_warnings = enrich_procedure_success_status(record, masked_note_text)
        if outcomes_status_warnings:
            extraction_warnings.extend(outcomes_status_warnings)
        complication_detail_warnings = enrich_outcomes_complication_details(record, masked_note_text)
        if complication_detail_warnings:
            extraction_warnings.extend(complication_detail_warnings)

        guardrail_outcome = self.clinical_guardrails.apply_record_guardrails(
            masked_note_text, record
        )
        record = guardrail_outcome.record or record
        if guardrail_outcome.warnings:
            extraction_warnings.extend(guardrail_outcome.warnings)

        # Production backstop: apply raw-text checkbox negation after all heuristics/guardrails
        # so downstream omission scan + CPT derivation never build on template false-positives.
        from modules.registry.postprocess.template_checkbox_negation import apply_template_checkbox_negation

        record, checkbox_warnings = apply_template_checkbox_negation(raw_note_text or "", record)
        if checkbox_warnings:
            extraction_warnings.extend(checkbox_warnings)

        # Evidence enforcement pass on the final record state (post-heuristics + checkbox negation).
        from modules.registry.evidence.verifier import verify_evidence_integrity

        record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
        if verifier_warnings:
            extraction_warnings.extend(verifier_warnings)

        # Narrative supersedes templated summary: preserve explicitly documented complications
        # even when a final "COMPLICATIONS: None" line exists.
        from modules.registry.postprocess.complications_reconcile import (
            reconcile_complications_from_narrative,
        )

        comp_warnings = reconcile_complications_from_narrative(record, masked_note_text)
        if comp_warnings:
            extraction_warnings.extend(comp_warnings)

        # Reconcile granular validation warnings against the final record state.
        # Guardrails and other postprocess steps may flip performed flags after
        # granular propagation has already emitted structural warnings.
        def _reconcile_granular_validation_warnings(record_in: RegistryRecord) -> tuple[RegistryRecord, set[str]]:
            warnings_in = getattr(record_in, "granular_validation_warnings", None)
            if not isinstance(warnings_in, list) or not warnings_in:
                return record_in, set()

            procs = getattr(record_in, "procedures_performed", None)

            def _performed(proc_name: str) -> bool:
                if procs is None:
                    return False
                proc = getattr(procs, proc_name, None)
                if proc is None:
                    return False
                return bool(getattr(proc, "performed", False))

            linear_performed = _performed("linear_ebus")
            tbna_performed = _performed("tbna_conventional")
            peripheral_tbna_performed = _performed("peripheral_tbna")
            brushings_performed = _performed("brushings")
            tbbx_performed = _performed("transbronchial_biopsy")
            bronchial_wash_performed = _performed("bronchial_wash")

            removed: set[str] = set()
            cleaned: list[str] = []
            seen: set[str] = set()
            for warning in warnings_in:
                if not isinstance(warning, str) or not warning.strip():
                    continue
                if (
                    "procedures_performed.linear_ebus.performed=true" in warning
                    and not linear_performed
                ):
                    removed.add(warning)
                    continue
                if (
                    "procedures_performed.tbna_conventional.performed=true" in warning
                    and not tbna_performed
                ):
                    removed.add(warning)
                    continue
                if (
                    "procedures_performed.peripheral_tbna.performed=true" in warning
                    and not peripheral_tbna_performed
                ):
                    removed.add(warning)
                    continue
                if "procedures_performed.brushings.performed=true" in warning and not brushings_performed:
                    removed.add(warning)
                    continue
                if (
                    "procedures_performed.transbronchial_biopsy.performed=true" in warning
                    and not tbbx_performed
                ):
                    removed.add(warning)
                    continue
                if (
                    "procedures_performed.bronchial_wash.performed=true" in warning
                    and not bronchial_wash_performed
                ):
                    removed.add(warning)
                    continue
                if warning in seen:
                    continue
                seen.add(warning)
                cleaned.append(warning)

            if not removed and len(cleaned) == len(warnings_in):
                return record_in, set()

            record_data = record_in.model_dump()
            record_data["granular_validation_warnings"] = cleaned
            return RegistryRecord(**record_data), removed

        record, removed_granular_warnings = _reconcile_granular_validation_warnings(record)
        if removed_granular_warnings:
            extraction_warnings = [
                w for w in extraction_warnings if not (isinstance(w, str) and w in removed_granular_warnings)
            ]

        # Omission detection: flag "silent failures" where high-value terms are present
        # in the text but the corresponding registry fields are missing/false.
        # Run this late so deterministic/postprocess backfills don't create false alarms.
        omission_warnings = scan_for_omissions(masked_note_text, record)
        if omission_warnings:
            extraction_warnings.extend(omission_warnings)

        derivation = derive_registry_to_cpt(record)
        derived_codes = [c.code for c in derivation.codes]
        base_warnings = list(extraction_warnings)
        self_correct_warnings: list[str] = []
        coverage_warnings: list[str] = []
        self_correction_meta: list[SelfCorrectionMetadata] = []

        auditor_source = os.getenv("REGISTRY_AUDITOR_SOURCE", "raw_ml").strip().lower()
        audit_warnings: list[str] = []
        audit_report: AuditCompareReport | None = None
        coder_difficulty = "unknown"
        needs_manual_review = bool(omission_warnings) or guardrail_outcome.needs_review

        code_guardrail = self.clinical_guardrails.apply_code_guardrails(
            masked_note_text, derived_codes
        )
        if code_guardrail.warnings:
            base_warnings.extend(code_guardrail.warnings)
        if code_guardrail.needs_review:
            needs_manual_review = True

        baseline_needs_manual_review = needs_manual_review

        if auditor_source == "raw_ml":
            from modules.registry.audit.raw_ml_auditor import RawMLAuditConfig

            auditor = RawMLAuditor()
            cfg = RawMLAuditConfig.from_env()
            ml_case = auditor.classify(raw_text_for_audit)
            coder_difficulty = ml_case.difficulty.value

            audit_preds = auditor.audit_predictions(ml_case, cfg)

            audit_report = build_audit_compare_report(
                derived_codes=derived_codes,
                cfg=cfg,
                ml_case=ml_case,
                audit_preds=audit_preds,
            )

            header_codes = _scan_header_for_codes(raw_note_text)

            def _apply_balanced_triggers(
                report: AuditCompareReport, current_codes: list[str]
            ) -> None:
                nonlocal needs_manual_review

                derived_code_set = {str(c) for c in (current_codes or [])}
                missing_header_codes = sorted(header_codes - derived_code_set)
                if missing_header_codes:
                    # Suppress known "header template" codes that are intentionally dropped by
                    # deterministic bundling/mutual-exclusion rules.
                    suppressed: set[str] = set()
                    if "31653" in derived_code_set:
                        suppressed.add("31652")
                    if "31652" in derived_code_set or "31653" in derived_code_set:
                        suppressed.add("31645")
                    if "76982" in derived_code_set or "76983" in derived_code_set:
                        suppressed.add("76981")
                    if suppressed:
                        missing_header_codes = [c for c in missing_header_codes if c not in suppressed]
                if missing_header_codes:
                    warning = (
                        "HEADER_EXPLICIT: header lists "
                        f"{missing_header_codes} but deterministic derivation missed them"
                    )
                    if warning not in audit_warnings:
                        logger.info(
                            "HEADER_EXPLICIT mismatch: header has %s but derivation missed them.",
                            missing_header_codes,
                        )
                        audit_warnings.append(warning)

                    existing = {p.cpt for p in (report.high_conf_omissions or [])}
                    # Only promote header-listed codes to high-conf omissions when there is
                    # independent narrative support. Exception: for very short headers, treat
                    # the header as authoritative (tests + common short templates).
                    supported: list[str] = []
                    if len(header_codes) <= 3:
                        supported = list(missing_header_codes)
                    else:
                        for missing in missing_header_codes:
                            passes, _reason = keyword_guard_check(cpt=missing, evidence_text=masked_note_text)
                            if passes:
                                supported.append(missing)

                    for missing in supported:
                        if missing in existing:
                            continue
                        report.high_conf_omissions.append(
                            AuditPrediction(cpt=missing, prob=1.0, bucket="HEADER_EXPLICIT")
                        )
                        existing.add(missing)

                try:
                    ebus_obj = (
                        record.procedures_performed.linear_ebus
                        if record.procedures_performed
                        else None
                    )
                    ebus_performed = bool(getattr(ebus_obj, "performed", False))
                    stations = getattr(ebus_obj, "stations_sampled", None)
                    stations_empty = not stations
                except Exception:
                    ebus_performed = False
                    stations_empty = False

                if ebus_performed and stations_empty:
                    warning = (
                        "STRUCTURAL_FAILURE: linear_ebus performed but stations_sampled is empty "
                        "(station extraction likely failed)"
                    )
                    if warning not in audit_warnings:
                        audit_warnings.append(warning)
                    needs_manual_review = True

                    if "31653" in header_codes and "31653" not in derived_code_set:
                        existing = {p.cpt for p in (report.high_conf_omissions or [])}
                        if "31653" not in existing:
                            report.high_conf_omissions.append(
                                AuditPrediction(cpt="31653", prob=1.0, bucket="STRUCTURAL_FAILURE")
                            )

            def _audit_requires_review(report: AuditCompareReport, evidence: str) -> bool:
                if not report.high_conf_omissions:
                    return False
                for pred in report.high_conf_omissions:
                    if pred.bucket in {"HEADER_EXPLICIT", "STRUCTURAL_FAILURE"}:
                        return True
                    try:
                        ml_prob = float(pred.prob)
                    except Exception:
                        ml_prob = None
                    passes, reason = keyword_guard_check(cpt=pred.cpt, evidence_text=evidence, ml_prob=ml_prob)
                    if passes or reason == "no keywords configured":
                        return True
                return False

            needs_manual_review = baseline_needs_manual_review
            _apply_balanced_triggers(audit_report, derived_codes)
            needs_manual_review = needs_manual_review or _audit_requires_review(
                audit_report, masked_note_text
            )

            self_correct_enabled = _env_flag("REGISTRY_SELF_CORRECT_ENABLED", "0")
            if self_correct_enabled and audit_report.high_conf_omissions:
                max_attempts = max(0, _env_int("REGISTRY_SELF_CORRECT_MAX_ATTEMPTS", 1))
                bucket_by_cpt: dict[str, str | None] = {}
                for pred in (audit_report.ml_audit_codes or []):
                    bucket_by_cpt[pred.cpt] = pred.bucket
                for pred in (audit_report.high_conf_omissions or []):
                    if pred.bucket and pred.cpt not in bucket_by_cpt:
                        bucket_by_cpt[pred.cpt] = pred.bucket
                trigger_preds = sorted(
                    audit_report.high_conf_omissions,
                    key=lambda p: float(p.prob),
                    reverse=True,
                )

                judge = RegistryCorrectionJudge()

                def _allowlist_snapshot() -> list[str]:
                    raw = os.getenv("REGISTRY_SELF_CORRECT_ALLOWLIST", "").strip()
                    if raw:
                        return sorted({p.strip() for p in raw.split(",") if p.strip()})
                    defaults = set(ALLOWED_PATHS)
                    defaults.update(f"{prefix}/*" for prefix in ALLOWED_PATH_PREFIXES)
                    return sorted(defaults)

                corrections_applied = 0
                evidence_text = (
                    extraction_text
                    if extraction_text is not None and extraction_text.strip()
                    else masked_note_text
                )
                for pred in trigger_preds:
                    if corrections_applied >= max_attempts:
                        break

                    bucket = bucket_by_cpt.get(pred.cpt) or getattr(pred, "bucket", None) or "UNKNOWN"
                    bypass_guard = bucket in {"HEADER_EXPLICIT", "STRUCTURAL_FAILURE"}
                    guard_evidence = evidence_text
                    if bypass_guard:
                        header_block = _extract_procedure_header_block(masked_note_text)
                        if not header_block:
                            header_block = _extract_procedure_header_block(raw_note_text)
                        if header_block and header_block.strip():
                            guard_evidence = header_block

                    if bypass_guard:
                        passes, reason = True, "bucket bypass"
                    else:
                        try:
                            ml_prob = float(pred.prob)
                        except Exception:
                            ml_prob = None
                        passes, reason = keyword_guard_check(
                            cpt=pred.cpt, evidence_text=guard_evidence, ml_prob=ml_prob
                        )
                    if not passes:
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: keyword guard failed ({reason})"
                        )
                        continue

                    derived_codes_before = list(derived_codes)
                    trigger = SelfCorrectionTrigger(
                        target_cpt=pred.cpt,
                        ml_prob=float(pred.prob),
                        ml_bucket=bucket,
                        reason=bucket if bucket != "UNKNOWN" else "RAW_ML_HIGH_CONF_OMISSION",
                    )

                    if bucket == "HEADER_EXPLICIT":
                        discrepancy = (
                            f"Procedure header explicitly lists CPT {pred.cpt}, but deterministic "
                            "derivation missed it. Patch the registry fields (not billing codes) "
                            "so deterministic derivation includes this CPT if supported by the note."
                        )
                    elif bucket == "STRUCTURAL_FAILURE":
                        discrepancy = (
                            f"Registry shows a structural extraction failure related to CPT {pred.cpt}. "
                            "Patch the registry fields (not billing codes) so deterministic derivation "
                            "includes this CPT if supported by the note."
                        )
                    else:
                        discrepancy = (
                            f"RAW-ML suggests missing CPT {pred.cpt} "
                            f"(prob={float(pred.prob):.2f}, bucket={bucket})."
                        )
                    proposal = judge.propose_correction(
                        note_text=raw_note_text,
                        record=record,
                        discrepancy=discrepancy,
                        focused_procedure_text=extraction_text,
                    )
                    if proposal is None:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: judge returned null")
                        continue

                    is_valid, reason = validate_proposal(
                        proposal,
                        masked_note_text,
                        extraction_text=extraction_text,
                    )
                    if not is_valid:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: {reason}")
                        continue

                    try:
                        patched_record = apply_patch_to_record(record=record, patch=proposal.json_patch)
                    except SelfCorrectionApplyError as exc:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: apply failed ({exc})")
                        continue

                    if patched_record.model_dump() == record.model_dump():
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: patch produced no change"
                        )
                        continue

                    candidate_record, candidate_granular_warnings = _apply_granular_up_propagation(
                        patched_record
                    )

                    candidate_derivation = derive_registry_to_cpt(candidate_record)
                    candidate_codes = [c.code for c in candidate_derivation.codes]
                    if trigger.target_cpt not in candidate_codes:
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: patch did not derive target CPT"
                        )
                        continue

                    record = candidate_record
                    derivation = candidate_derivation
                    derived_codes = candidate_codes
                    corrections_applied += 1
                    self_correct_warnings.extend(candidate_granular_warnings)

                    self_correct_warnings.append(f"AUTO_CORRECTED: {pred.cpt}")
                    applied_paths = [
                        str(op.get("path"))
                        for op in proposal.json_patch
                        if isinstance(op, dict) and op.get("path") is not None
                    ]
                    allowlist_snapshot = _allowlist_snapshot()
                    config_snapshot = {
                        "max_attempts": max_attempts,
                        "allowlist": allowlist_snapshot,
                        "audit_config": audit_report.config.to_dict(),
                        "judge_rationale": proposal.rationale,
                    }
                    self_correction_meta.append(
                        SelfCorrectionMetadata(
                            trigger=trigger,
                            applied_paths=applied_paths,
                            evidence_quotes=[proposal.evidence_quote],
                            config_snapshot=config_snapshot,
                        )
                    )
                    log_path = os.getenv("REGISTRY_SELF_CORRECT_LOG_PATH", "").strip()
                    if log_path:
                        _append_self_correction_log(
                            log_path,
                            {
                                "event": "AUTO_CORRECTED",
                                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "note_sha256": _hash_note_text(raw_note_text),
                                "note_length": len((raw_note_text or "").strip()),
                                "trigger": {
                                    "target_cpt": pred.cpt,
                                    "ml_prob": float(pred.prob),
                                    "bucket": bucket,
                                    "reason": trigger.reason,
                                },
                                "derived_codes_before": derived_codes_before,
                                "derived_codes_after": list(candidate_codes),
                                "json_patch": proposal.json_patch,
                                "evidence_quote": proposal.evidence_quote,
                                "judge_rationale": proposal.rationale,
                                "applied_paths": applied_paths,
                                "config_snapshot": config_snapshot,
                            },
                        )

                    audit_report = build_audit_compare_report(
                        derived_codes=derived_codes,
                        cfg=cfg,
                        ml_case=ml_case,
                        audit_preds=audit_preds,
                    )
                    needs_manual_review = baseline_needs_manual_review
                    _apply_balanced_triggers(audit_report, derived_codes)
                    needs_manual_review = needs_manual_review or _audit_requires_review(
                        audit_report, masked_note_text
                    )

            if _env_flag("REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL", "0"):
                coverage_failures = _coverage_failures(masked_note_text, record)
                if coverage_failures:
                    coverage_warnings.append(
                        "COVERAGE_FAIL: " + "; ".join(coverage_failures)
                    )
                    needs_manual_review = True

                    fallback_record, fallback_warns = _run_structurer_fallback(masked_note_text)
                    if fallback_warns:
                        coverage_warnings.extend(fallback_warns)

                    if fallback_record is not None:
                        record = fallback_record
                        derivation = derive_registry_to_cpt(record)
                        derived_codes = [c.code for c in derivation.codes]

                        audit_report = build_audit_compare_report(
                            derived_codes=derived_codes,
                            cfg=cfg,
                            ml_case=ml_case,
                            audit_preds=audit_preds,
                        )
                        needs_manual_review = baseline_needs_manual_review
                        _apply_balanced_triggers(audit_report, derived_codes)
                        needs_manual_review = needs_manual_review or _audit_requires_review(
                            audit_report, masked_note_text
                        )

                        remaining = _coverage_failures(masked_note_text, record)
                        if remaining:
                            coverage_warnings.append(
                                "COVERAGE_FAIL_REMAINS: " + "; ".join(remaining)
                            )
        elif auditor_source == "disabled":
            from modules.registry.audit.raw_ml_auditor import RawMLAuditConfig

            cfg = RawMLAuditConfig.from_env()
            audit_report = build_audit_compare_report(
                derived_codes=derived_codes,
                cfg=cfg,
                ml_case=None,
                audit_preds=None,
                warnings=["REGISTRY_AUDITOR_SOURCE=disabled; RAW-ML audit set is empty"],
            )
            coder_difficulty = "disabled"
        else:
            raise ValueError(f"Unknown REGISTRY_AUDITOR_SOURCE='{auditor_source}'")

        if audit_report and audit_report.missing_in_derived:
            for pred in audit_report.missing_in_derived:
                bucket = pred.bucket or "AUDIT_SET"
                audit_warnings.append(
                    f"RAW_ML_AUDIT[{bucket}]: model suggests {pred.cpt} (prob={pred.prob:.2f}), "
                    "but deterministic derivation missed it"
                )

        derivation_warnings = list(derivation.warnings)
        code_rationales = {c.code: c.rationale for c in derivation.codes}

        # Populate billing CPT codes deterministically (never from the LLM).
        if derived_codes:
            from modules.registry.application.coding_support_builder import (
                build_coding_support_payload,
                build_traceability_for_code,
                get_kb_repo,
            )

            record_data = record.model_dump()
            billing = record_data.get("billing")
            if not isinstance(billing, dict):
                billing = {}
            has_ebus_sampling_code = any(str(code) in {"31652", "31653"} for code in derived_codes)
            peripheral_tbna = (
                (record_data.get("procedures_performed") or {}).get("peripheral_tbna") or {}
            )
            peripheral_tbna_performed = (
                isinstance(peripheral_tbna, dict) and peripheral_tbna.get("performed") is True
            )

            kb_repo = get_kb_repo()

            cpt_payload: list[dict[str, Any]] = []
            from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_units_for_codes

            code_units = derive_units_for_codes(record, derived_codes)
            for code in derived_codes:
                code_str = str(code).strip()
                if not code_str:
                    continue

                proc_info = kb_repo.get_procedure_info(code_str)
                item: dict[str, Any] = {
                    "code": code_str,
                    "description": proc_info.description if proc_info else None,
                }
                units = int(code_units.get(code_str, 1) or 1)
                if units != 1:
                    item["units"] = units
                derived_from, evidence_items = build_traceability_for_code(record=record, code=code_str)
                if derived_from:
                    item["derived_from"] = derived_from
                if evidence_items:
                    item["evidence"] = evidence_items
                if (
                    code_str == "31629"
                    and has_ebus_sampling_code
                    and peripheral_tbna_performed
                ):
                    item["modifiers"] = ["59"]
                cpt_payload.append(item)

            billing["cpt_codes"] = cpt_payload
            record_data["billing"] = billing

            record_data["coding_support"] = build_coding_support_payload(
                record=record,
                codes=derived_codes,
                code_units=code_units,
                code_rationales=code_rationales,
                derivation_warnings=derivation_warnings,
                kb_repo=kb_repo,
            )

            record = RegistryRecord(**record_data)

        warnings = list(base_warnings) + derivation_warnings + list(self_correct_warnings) + list(coverage_warnings)
        if any(isinstance(w, str) and w.startswith("NEEDS_REVIEW:") for w in warnings):
            needs_manual_review = True
        mapped_fields = (
            aggregate_registry_fields(derived_codes, version="v3") if derived_codes else {}
        )
        return RegistryExtractionResult(
            record=record,
            cpt_codes=derived_codes,
            coder_difficulty=coder_difficulty,
            coder_source="extraction_first",
            mapped_fields=mapped_fields,
            code_rationales=code_rationales,
            derivation_warnings=derivation_warnings,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            validation_errors=[],
            audit_warnings=audit_warnings,
            audit_report=audit_report,
            self_correction=self_correction_meta,
        )

    def _apply_guardrails_to_result(
        self,
        note_text: str,
        result: RegistryExtractionResult,
    ) -> RegistryExtractionResult:
        record_outcome = self.clinical_guardrails.apply_record_guardrails(
            note_text, result.record
        )
        record = record_outcome.record or result.record
        warnings = list(result.warnings) + list(record_outcome.warnings)
        needs_manual_review = result.needs_manual_review or record_outcome.needs_review

        if record_outcome.changed:
            from modules.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt

            derivation = derive_registry_to_cpt(record)
            result.cpt_codes = [c.code for c in derivation.codes]
            result.derivation_warnings = list(derivation.warnings)
            result.code_rationales = {c.code: c.rationale for c in derivation.codes}
            result.mapped_fields = (
                aggregate_registry_fields(result.cpt_codes, version="v3")
                if result.cpt_codes
                else {}
            )

        result.record = record
        result.warnings = warnings
        result.needs_manual_review = needs_manual_review

        code_outcome = self.clinical_guardrails.apply_code_guardrails(note_text, result.cpt_codes)
        if code_outcome.warnings:
            result.warnings.extend(code_outcome.warnings)
        if code_outcome.needs_review:
            result.needs_manual_review = True

        return result

    def _merge_cpt_fields_into_record(
        self,
        record: RegistryRecord,
        mapped_fields: dict[str, Any],
    ) -> RegistryRecord:
        """Apply CPT-based mapped fields onto the registry record.

        Handles the NESTED structure from aggregate_registry_fields:
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True},
                "bal": {"performed": True},
            },
            "pleural_procedures": {
                "thoracentesis": {"performed": True},
            }
        }

        This is conservative: only overwrite fields that are currently unset/False,
        unless there's a strong reason to prefer CPT over text extraction.

        Args:
            record: The extracted RegistryRecord from RegistryEngine.
            mapped_fields: Nested dict of fields from CPT mapping.

        Returns:
            Updated RegistryRecord with merged fields.
        """
        record_data = record.model_dump()

        # Handle procedures_performed section
        proc_map = mapped_fields.get("procedures_performed") or {}
        if proc_map:
            current_procs = record_data.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                current_proc = current_procs.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    # Only overwrite if current is falsy
                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field procedures_performed.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        # For boolean flags, CPT evidence is strong
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode procedures_performed.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_procs[proc_name] = current_proc
            record_data["procedures_performed"] = current_procs

        # Handle pleural_procedures section
        pleural_map = mapped_fields.get("pleural_procedures") or {}
        if pleural_map:
            current_pleural = record_data.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                current_proc = current_pleural.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field pleural_procedures.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode pleural_procedures.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_pleural[proc_name] = current_proc
            record_data["pleural_procedures"] = current_pleural

        # Reconstruct the record
        return RegistryRecord(**record_data)

    def _validate_and_finalize(
        self,
        result: RegistryExtractionResult,
        *,
        coder_result: HybridCoderResult,
        note_text: str = "",
    ) -> RegistryExtractionResult:
        """Central validation and finalization logic.

        Compare CPT-driven signals (coder_result.codes) with registry fields and
        set validation flags accordingly. Also performs ML hybrid audit to detect
        procedures that ML predicted but CPT-derived flags did not capture.

        Marks cases for manual review when:
        - CPT codes don't match extracted registry fields
        - Case difficulty is LOW_CONF or GRAY_ZONE
        - ML predictor detects procedures not captured by CPT pathway

        Args:
            result: The extraction result to validate.
            coder_result: The original hybrid coder result for cross-validation.
            note_text: Original procedure note text for ML prediction.

        Returns:
            Validated and finalized RegistryExtractionResult with validation flags.
        """
        from modules.ml_coder.thresholds import CaseDifficulty

        codes = set(result.cpt_codes)
        record = result.record
        validation_errors: list[str] = list(result.validation_errors)
        warnings = list(result.warnings)
        audit_warnings: list[str] = list(result.audit_warnings)
        needs_manual_review = result.needs_manual_review

        # Get nested procedure objects (may be None)
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # Helper to safely check if a nested procedure is present
        def _proc_is_set(obj, attr: str) -> bool:
            if obj is None:
                return False
            sub_obj = getattr(obj, attr, None)
            if sub_obj is None:
                return False
            # For nested Pydantic models, check if 'performed' field exists and is True
            if hasattr(sub_obj, "performed"):
                return bool(getattr(sub_obj, "performed", False))
            # Otherwise, just check if the object is truthy
            return bool(sub_obj)

        # -------------------------------------------------------------------------
        # 1. Derive aggregate procedure flags from granular_data if present
        # -------------------------------------------------------------------------
        granular = None
        if record.granular_data is not None:
            granular = record.granular_data.model_dump()

        existing_procedures = None
        if record.procedures_performed is not None:
            existing_procedures = record.procedures_performed.model_dump()

        if granular is not None:
            updated_procs, granular_warnings = derive_procedures_from_granular(
                granular_data=granular,
                existing_procedures=existing_procedures,
            )
            # Re-apply to record via reconstruction
            record_data = record.model_dump()
            if updated_procs:
                record_data["procedures_performed"] = updated_procs
            # Append warnings to both record + result
            record_data.setdefault("granular_validation_warnings", [])
            record_data["granular_validation_warnings"].extend(granular_warnings)
            validation_errors.extend(granular_warnings)
            # Reconstruct record with updated procedures
            record = RegistryRecord(**record_data)

        # Re-fetch procedures/pleural after potential update
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # -------------------------------------------------------------------------
        # 2. CPT-to-Registry Field Consistency Checks
        # -------------------------------------------------------------------------

        # Linear EBUS: 31652 (1-2 stations), 31653 (3+ stations)
        if "31652" in codes or "31653" in codes:
            if not _proc_is_set(procedures, "linear_ebus"):
                validation_errors.append(
                    f"CPT {'31652' if '31652' in codes else '31653'} present "
                    "but procedures_performed.linear_ebus is not marked."
                )
            # Check station count hint
            if procedures and getattr(procedures, "linear_ebus", None):
                ebus_obj = procedures.linear_ebus
                stations = getattr(ebus_obj, "stations_sampled", None)
                if "31653" in codes and stations:
                    # 31653 implies 3+ stations
                    try:
                        station_count = len(stations) if isinstance(stations, list) else int(stations)
                        if station_count < 3:
                            warnings.append(
                                f"CPT 31653 implies 3+ EBUS stations, but only {station_count} recorded."
                            )
                    except (ValueError, TypeError):
                        pass

        # Radial EBUS: 31654
        if "31654" in codes:
            if not _proc_is_set(procedures, "radial_ebus"):
                validation_errors.append(
                    "CPT 31654 present but procedures_performed.radial_ebus is not marked."
                )

        # BAL: 31624, 31625
        if "31624" in codes or "31625" in codes:
            if not _proc_is_set(procedures, "bal"):
                validation_errors.append(
                    "CPT 31624/31625 present but procedures_performed.bal is not marked."
                )

        # Transbronchial biopsy: 31628, 31632
        if "31628" in codes or "31632" in codes:
            if not _proc_is_set(procedures, "transbronchial_biopsy"):
                validation_errors.append(
                    "CPT 31628/31632 present but procedures_performed.transbronchial_biopsy is not marked."
                )

        # Peripheral/lung TBNA: 31629, 31633
        if "31629" in codes or "31633" in codes:
            if not _proc_is_set(procedures, "peripheral_tbna"):
                validation_errors.append(
                    "CPT 31629/31633 present but procedures_performed.peripheral_tbna is not marked."
                )

        # Navigation: 31627
        if "31627" in codes:
            if not _proc_is_set(procedures, "navigational_bronchoscopy"):
                validation_errors.append(
                    "CPT 31627 present but procedures_performed.navigational_bronchoscopy is not marked."
                )

        # Stent: 31636, 31637
        if "31636" in codes or "31637" in codes:
            if not _proc_is_set(procedures, "airway_stent"):
                validation_errors.append(
                    "CPT 31636/31637 present but procedures_performed.airway_stent is not marked."
                )

        # Dilation: 31630, 31631
        if "31630" in codes or "31631" in codes:
            if not _proc_is_set(procedures, "airway_dilation"):
                validation_errors.append(
                    "CPT 31630/31631 present but procedures_performed.airway_dilation is not marked."
                )

        # BLVR / valves / Chartis: 31634, 31647, 31651, 31648, 31649
        blvr_codes = {"31634", "31647", "31648", "31649", "31651"}
        if blvr_codes & codes:
            if not _proc_is_set(procedures, "blvr"):
                validation_errors.append(
                    "CPT 31634/31647/31651/31648/31649 present but procedures_performed.blvr is not marked."
                )

        # Thermoplasty: 31660, 31661
        if "31660" in codes or "31661" in codes:
            if not _proc_is_set(procedures, "bronchial_thermoplasty"):
                validation_errors.append(
                    "CPT 31660/31661 present but procedures_performed.bronchial_thermoplasty is not marked."
                )

        # Rigid bronchoscopy: 31641
        if "31641" in codes:
            if not _proc_is_set(procedures, "rigid_bronchoscopy"):
                # Only warn, as 31641 can also be thermal ablation
                warnings.append(
                    "CPT 31641 present - verify rigid_bronchoscopy or thermal ablation is marked."
                )

        # Tube thoracostomy: 32551
        if "32551" in codes:
            if not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "CPT 32551 present but pleural_procedures.chest_tube is not marked."
                )

        # Thoracentesis: 32554, 32555, 32556, 32557
        thoracentesis_codes = {"32554", "32555", "32556", "32557"}
        if thoracentesis_codes & codes:
            if not _proc_is_set(pleural, "thoracentesis") and not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "Thoracentesis CPT codes present but no pleural procedure marked."
                )

        # Medical thoracoscopy / pleuroscopy: 32601
        if "32601" in codes:
            if not _proc_is_set(pleural, "medical_thoracoscopy"):
                validation_errors.append(
                    "CPT 32601 present but pleural_procedures.medical_thoracoscopy is not marked."
                )

        # Pleurodesis: 32560, 32650
        if "32560" in codes or "32650" in codes:
            if not _proc_is_set(pleural, "pleurodesis"):
                validation_errors.append(
                    "CPT 32560/32650 present but pleural_procedures.pleurodesis is not marked."
                )

        # -------------------------------------------------------------------------
        # 3. Difficulty-based Manual Review Flags
        # -------------------------------------------------------------------------

        # Low-confidence cases: always require manual review
        if coder_result.difficulty == CaseDifficulty.LOW_CONF:
            needs_manual_review = True
            if not validation_errors:
                validation_errors.append(
                    "Hybrid coder marked this case as LOW_CONF; manual review required."
                )

        # Gray zone cases: also require manual review
        if coder_result.difficulty == CaseDifficulty.GRAY_ZONE:
            needs_manual_review = True

        # Any validation errors trigger manual review
        if validation_errors and not needs_manual_review:
            needs_manual_review = True

        # Granular validation warnings also trigger manual review
        granular_warnings_on_record = getattr(record, "granular_validation_warnings", [])
        if granular_warnings_on_record and not needs_manual_review:
            needs_manual_review = True

        # -------------------------------------------------------------------------
        # 4. ML Hybrid Audit: Compare ML predictions with CPT-derived flags
        # -------------------------------------------------------------------------
        # This is an audit overlay that cross-checks ML predictions against
        # CPT-derived flags to catch procedures the CPT pathway may have missed.

        ml_predictor = self._get_registry_ml_predictor()
        if ml_predictor is not None and note_text:
            ml_case = ml_predictor.classify_case(note_text)

            # Build CPT-derived flags dict from mapped_fields
            # The mapped_fields has structure like:
            # {"procedures_performed": {"linear_ebus": {"performed": True}, ...}}
            cpt_flags: dict[str, bool] = {}
            proc_map = result.mapped_fields.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            pleural_map = result.mapped_fields.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            # Build ML flags dict
            ml_flags: dict[str, bool] = {}
            for pred in ml_case.predictions:
                ml_flags[pred.field] = pred.is_positive

            # Compare flags and generate audit warnings
            # Scenario C: ML detected a procedure that CPT pathway did not
            for field_name, ml_positive in ml_flags.items():
                cpt_positive = cpt_flags.get(field_name, False)

                if ml_positive and not cpt_positive:
                    # ML detected a procedure the CPT pathway did not capture
                    # Find the probability for context
                    prob = next(
                        (p.probability for p in ml_case.predictions if p.field == field_name),
                        0.0,
                    )
                    audit_warnings.append(
                        f"ML detected procedure '{field_name}' with high confidence "
                        f"(prob={prob:.2f}), but no corresponding CPT-derived flag was set. "
                        f"Please review."
                    )
                    needs_manual_review = True

            # Log ML audit summary
            ml_detected_count = sum(1 for f, v in ml_flags.items() if v and not cpt_flags.get(f, False))
            if ml_detected_count > 0:
                logger.info(
                    "ml_hybrid_audit_discrepancy",
                    extra={
                        "ml_detected_not_in_cpt": ml_detected_count,
                        "audit_warnings": audit_warnings,
                    },
                )

        # -------------------------------------------------------------------------
        # Telemetry: Log validation outcome for monitoring
        # -------------------------------------------------------------------------
        logger.info(
            "registry_validation_complete",
            extra={
                "coder_difficulty": coder_result.difficulty.value,
                "coder_source": coder_result.source,
                "needs_manual_review": needs_manual_review,
                "validation_error_count": len(validation_errors),
                "warning_count": len(warnings),
                "audit_warning_count": len(audit_warnings),
                "cpt_code_count": len(codes),
            },
        )

        # -------------------------------------------------------------------------
        # 5. Return Updated Result
        # -------------------------------------------------------------------------
        return RegistryExtractionResult(
            record=record,  # Use potentially updated record from granular derivation
            cpt_codes=result.cpt_codes,
            coder_difficulty=result.coder_difficulty,
            coder_source=result.coder_source,
            mapped_fields=result.mapped_fields,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            validation_errors=validation_errors,
            audit_warnings=audit_warnings,
        )


# Factory function for DI
def get_registry_service() -> RegistryService:
    """Get a RegistryService instance with default configuration."""
    return RegistryService()

```

---
### `modules/agents/contracts.py`
```
"""Agent contracts defining I/O schemas for the 3-agent reporter pipeline.

This module defines the data contracts between:
- ParserAgent: Splits raw text into segments and extracts entities
- SummarizerAgent: Produces section summaries from segments/entities
- StructurerAgent: Maps summaries to registry model and generates codes
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Tuple, Literal


class AgentWarning(BaseModel):
    """A warning from an agent that doesn't prevent output."""

    code: str  # "MISSING_HEADER", "AMBIGUOUS_SECTION"
    message: str
    section: Optional[str] = None


class AgentError(BaseModel):
    """An error from an agent that may prevent successful output."""

    code: str  # "NO_SECTIONS_FOUND", "PARSING_FAILED"
    message: str
    section: Optional[str] = None


class Segment(BaseModel):
    """A segmented portion of the note with optional character spans."""

    id: str = ""
    type: str  # "HISTORY", "PROCEDURE", "FINDINGS", "IMPRESSION", etc.
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    spans: List[Tuple[int, int]] = Field(default_factory=list)


class Entity(BaseModel):
    """An entity extracted from the note, such as a station or stent."""

    label: str
    value: str
    name: str = ""  # For backwards compatibility
    type: str = ""
    offsets: Optional[Tuple[int, int]] = None
    evidence_segment_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class Trace(BaseModel):
    """Trace metadata capturing what triggered an agent's output."""

    trigger_phrases: List[str] = Field(default_factory=list)
    rule_paths: List[str] = Field(default_factory=list)
    confounders_checked: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    notes: Optional[str] = None


class ParserIn(BaseModel):
    """Input to the Parser agent."""

    note_id: str
    raw_text: str


class ParserOut(BaseModel):
    """Output from the Parser agent."""

    note_id: str = ""
    segments: List[Segment] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class SummarizerIn(BaseModel):
    """Input to the Summarizer agent."""

    parser_out: ParserOut


class SummarizerOut(BaseModel):
    """Output from the Summarizer agent."""

    note_id: str = ""
    summaries: Dict[str, str] = Field(default_factory=dict)
    caveats: List[str] = Field(default_factory=list)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class StructurerIn(BaseModel):
    """Input to the Structurer agent."""

    summarizer_out: SummarizerOut


class StructurerOut(BaseModel):
    """Output from the Structurer agent."""

    note_id: str = ""
    registry: Dict[str, Any] = Field(default_factory=dict)
    codes: Dict[str, Any] = Field(default_factory=dict)
    rationale: Dict[str, Any] = Field(default_factory=dict)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class PipelineResult(BaseModel):
    """Full result from running the 3-agent pipeline."""

    pipeline_status: Literal["ok", "degraded", "failed_parser", "failed_summarizer", "failed_structurer"]
    parser: Optional[ParserOut] = None
    summarizer: Optional[SummarizerOut] = None
    structurer: Optional[StructurerOut] = None
    registry: Optional[Dict[str, Any]] = None
    codes: Optional[Dict[str, Any]] = None

```

---
### `modules/agents/run_pipeline.py`
```
"""Pipeline orchestrator for parser, summarizer, and structurer agents.

This module orchestrates the 3-agent reporter pipeline with proper
status tracking, error handling, and graceful degradation.
"""

from typing import Literal

from modules.agents.contracts import (
    ParserIn,
    ParserOut,
    SummarizerIn,
    SummarizerOut,
    StructurerIn,
    StructurerOut,
    PipelineResult,
    AgentError,
)
from modules.agents.parser.parser_agent import ParserAgent
from modules.agents.summarizer.summarizer_agent import SummarizerAgent
from modules.agents.structurer.structurer_agent import StructurerAgent
from observability.timing import timed
from observability.logging_config import get_logger

logger = get_logger("pipeline")


def run_pipeline(note: dict) -> dict:
    """Run the full agent pipeline on a single note dict.

    Args:
        note: Dict with keys 'note_id' and 'raw_text'.

    Returns:
        Dict with pipeline_status, agent outputs, registry, and codes.
    """
    result = run_pipeline_typed(note)
    return result.model_dump()


def run_pipeline_typed(note: dict) -> PipelineResult:
    """Run the full agent pipeline with typed output.

    The pipeline runs through three stages:
    1. Parser: Splits raw text into segments and extracts entities
    2. Summarizer: Produces section summaries from segments/entities
    3. Structurer: Maps summaries to registry model and generates codes

    If any stage fails (status='failed'), the pipeline stops and returns
    the partial result. Degraded stages continue but mark the overall
    pipeline as degraded.

    Args:
        note: Dict with keys 'note_id' and 'raw_text'.

    Returns:
        PipelineResult with status, agent outputs, registry, and codes.
    """
    note_id = note.get("note_id", "")
    raw_text = note.get("raw_text", "")

    parser_ms = 0.0
    summarizer_ms = 0.0
    structurer_ms = 0.0

    with timed("pipeline.total") as timing:
        # Stage 1: Parser
        with timed("pipeline.parser") as t_parser:
            parser_out = _run_parser(note_id, raw_text)
        parser_ms = t_parser.elapsed_ms

        if parser_out.status == "failed":
            logger.warning(
                "Pipeline failed at parser stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in parser_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_parser",
                parser=parser_out,
            )

        # Stage 2: Summarizer
        with timed("pipeline.summarizer") as t_summarizer:
            summarizer_out = _run_summarizer(parser_out)
        summarizer_ms = t_summarizer.elapsed_ms

        if summarizer_out.status == "failed":
            logger.warning(
                "Pipeline failed at summarizer stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in summarizer_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_summarizer",
                parser=parser_out,
                summarizer=summarizer_out,
            )

        # Stage 3: Structurer
        with timed("pipeline.structurer") as t_structurer:
            structurer_out = _run_structurer(summarizer_out)
        structurer_ms = t_structurer.elapsed_ms

        if structurer_out.status == "failed":
            logger.warning(
                "Pipeline failed at structurer stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in structurer_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_structurer",
                parser=parser_out,
                summarizer=summarizer_out,
                structurer=structurer_out,
            )

        # Determine overall status
        statuses = [parser_out.status, summarizer_out.status, structurer_out.status]
        if all(s == "ok" for s in statuses):
            pipeline_status: Literal["ok", "degraded", "failed_parser", "failed_summarizer", "failed_structurer"] = "ok"
        else:
            pipeline_status = "degraded"

    logger.info(
        "Pipeline complete",
        extra={
            "note_id": note_id,
            "pipeline_status": pipeline_status,
            "processing_time_ms": timing.elapsed_ms,
            "parser_time_ms": parser_ms,
            "summarizer_time_ms": summarizer_ms,
            "structurer_time_ms": structurer_ms,
            "parser_status": parser_out.status,
            "summarizer_status": summarizer_out.status,
            "structurer_status": structurer_out.status,
        },
    )

    return PipelineResult(
        pipeline_status=pipeline_status,
        parser=parser_out,
        summarizer=summarizer_out,
        structurer=structurer_out,
        registry=structurer_out.registry,
        codes=structurer_out.codes,
    )


def _run_parser(note_id: str, raw_text: str) -> ParserOut:
    """Run the parser agent with error handling."""
    try:
        parser_in = ParserIn(note_id=note_id, raw_text=raw_text)
        parser_agent = ParserAgent()
        parser_out = parser_agent.run(parser_in)

        # Ensure note_id is set
        parser_out.note_id = note_id

        return parser_out

    except Exception as e:
        logger.error(f"Parser agent threw exception: {e}")
        return ParserOut(
            note_id=note_id,
            status="failed",
            errors=[
                AgentError(
                    code="PARSER_EXCEPTION",
                    message=str(e),
                )
            ],
        )


def _run_summarizer(parser_out: ParserOut) -> SummarizerOut:
    """Run the summarizer agent with error handling."""
    try:
        summarizer_in = SummarizerIn(parser_out=parser_out)
        summarizer_agent = SummarizerAgent()
        summarizer_out = summarizer_agent.run(summarizer_in)

        # Ensure note_id is set
        summarizer_out.note_id = parser_out.note_id

        return summarizer_out

    except Exception as e:
        logger.error(f"Summarizer agent threw exception: {e}")
        return SummarizerOut(
            note_id=parser_out.note_id,
            status="failed",
            errors=[
                AgentError(
                    code="SUMMARIZER_EXCEPTION",
                    message=str(e),
                )
            ],
        )


def _run_structurer(summarizer_out: SummarizerOut) -> StructurerOut:
    """Run the structurer agent with error handling."""
    try:
        structurer_in = StructurerIn(summarizer_out=summarizer_out)
        structurer_agent = StructurerAgent()
        structurer_out = structurer_agent.run(structurer_in)

        # Ensure note_id is set
        structurer_out.note_id = summarizer_out.note_id

        return structurer_out

    except Exception as e:
        logger.error(f"Structurer agent threw exception: {e}")
        return StructurerOut(
            note_id=summarizer_out.note_id,
            status="failed",
            errors=[
                AgentError(
                    code="STRUCTURER_EXCEPTION",
                    message=str(e),
                )
            ],
        )

```

---
### `docs/AGENTS.md`
```
# Multi-Agent Pipeline Documentation

This document describes the 3-agent pipeline used for structured note processing in the Procedure Suite.

Note (2026-01): Production is moving to a **stateless extraction-first** architecture (Text In → Codes Out)
driven by `POST /api/v1/process`. Hybrid-first/ID-based workflows are legacy and gated.

## Overview

The agents module (`modules/agents/`) provides **deterministic, structured note processing** that can be used in two ways:

- **Focused extraction helper (optional)**: `ParserAgent` is used to segment notes and optionally “focus” extraction onto high-yield sections for deterministic registry extraction (see `modules/registry/extraction/focus.py`).
- **Full 3-agent pipeline (available, experimental)**: `Parser → Summarizer → Structurer` via `modules/agents/run_pipeline.py`. Today, `StructurerAgent` is a placeholder and the “agents structurer” extraction mode is intentionally guarded/fallbacks to the engine.

The goal is to make downstream extraction more reliable and auditable without seeding registry extraction with CPT hints when running in extraction-first mode.

## Registry V3 focusing (LLM input slicing)

Registry V3 introduces a stricter, section-aware focusing helper used to limit what the V3 extractor sees:

- **Entry point:** `modules/registry/processing/focus.py:get_procedure_focus()`
- **Sources:** prefers `ParserAgent` segmentation, then `SectionizerService`, with a regex fallback.
- **Target sections:** `PROCEDURE`, `FINDINGS`, `IMPRESSION`, `TECHNIQUE`, `OPERATIVE REPORT`
- **Fail-safe:** if no target headings are found, returns the full original note text (never empty).

## Where this fits in the system

The system has two major registry flows:

- **Extraction-first (production direction)**: extract registry from (scrubbed) note text (no CPT hints) → deterministic registry→CPT derivation → optional auditing/self-correction.
- **Hybrid-first (legacy)**: CPT coder → CPT→registry mapping → registry engine extraction → merge/validate.

Agents are relevant primarily to **extraction-first**:

- `PROCSUITE_PIPELINE_MODE=extraction_first` is enforced at startup (`modules/api/fastapi_app.py:_validate_startup_env()`).
- When `REGISTRY_EXTRACTION_ENGINE=agents_focus_then_engine`, the system will use `ParserAgent` to focus the note text for the deterministic engine extraction. Guardrail: auditing always uses the full raw note text.

### Configuration

These environment variables control whether/where agents are used:

- **`PROCSUITE_PIPELINE_MODE`**: must be `extraction_first` (startup-enforced).
- **`REGISTRY_EXTRACTION_ENGINE`** (extraction-first): `parallel_ner` (recommended; required in production), `engine`, `agents_focus_then_engine`, or `agents_structurer`.
- **`REGISTRY_SCHEMA_VERSION`**: `v3` is recommended (and required in production); `v2` is legacy.
- **`REGISTRY_AUDITOR_SOURCE`**: `raw_ml` enables the RAW-ML audit safety net (required in production).

Notes:
- `agents_structurer` is currently **not implemented** (it is expected to raise `NotImplementedError` and fall back to the deterministic engine).
- CPT coding is handled by the coder module (`modules/coder/`) and is **not** produced by agents in the current architecture.

## Registry V3 Guardrails (Post-Extraction)

Even when agents are used for **focusing**, the extraction-first pipeline applies Python-side guardrails to the **full raw note text** before deterministic registry→CPT derivation:

- **Evidence integrity**: `modules/registry/evidence/verifier.py:verify_evidence_integrity()` verifies that hallucination-prone `performed=True` fields are supported by verifiable quotes (with fuzzy fallback) and wipes unsupported details (e.g., therapeutic aspiration; hallucinated trach `device_name`).
- **EBUS negation sanitizer**: `modules/registry/postprocess.py:sanitize_ebus_events()` forces `needle_aspiration` → `inspected_only` when the station context is explicitly negated (e.g., “not biopsied/not sampled”, “benign ultrasound characteristics”).
- **Clinical guardrails**: `modules/extraction/postprocessing/clinical_guardrails.py` prevents known failure modes (failed navigation, airway dilation false positives, rigid bronch header/body conflict, etc).
- **Recall/omission detector**: `modules/registry/self_correction/keyword_guard.py:scan_for_omissions()` flags “silent misses” for high-value procedures (BAL/EBBx/radial EBUS/cryotherapy/laser/rigid/etc) and emits `SILENT_FAILURE:` warnings.
- **Short-token keyword safety**: `modules/registry/self_correction/keyword_guard.py:_keyword_hit()` requires word boundaries for short tokens (e.g., `bal`, `ipc`) to reduce false positives.
- **Evidence schema**: the UI/API expects V3 evidence items shaped like `{"source","text","span":[start,end],"confidence"}` (see `modules/api/adapters/response_adapter.py`).

Chokepoints:
- `modules/registry/application/registry_service.py:RegistryService.extract_record()` (runs guardrails immediately after extraction)
- `modules/registry/application/registry_service.py:RegistryService._extract_fields_extraction_first()` (runs omission scan before deterministic coding)

Tests to run: `pytest -q` (see `tests/registry/test_registry_guardrails.py`, `tests/registry/test_keyword_guard_omissions.py`, `tests/registry/test_provider_name_sanitization.py`).

## Full pipeline (conceptual)

The agents module implements a pipeline of three specialized agents that process procedure notes sequentially:

```
Raw Text → Parser → Summarizer → Structurer → Registry + Codes
```

Each agent has:
- **Input contract** (Pydantic model)
- **Output contract** (Pydantic model)
- **Status tracking** (ok, degraded, failed)
- **Error/warning collection**
- **Trace metadata** for debugging

## Architecture

```
modules/agents/
├── contracts.py                # I/O schemas for all agents
├── run_pipeline.py             # Pipeline orchestration
├── parser/
│   └── parser_agent.py         # ParserAgent implementation
├── summarizer/
│   └── summarizer_agent.py     # SummarizerAgent implementation
└── structurer/
    └── structurer_agent.py     # StructurerAgent implementation
```

## Current implementation status

- **ParserAgent**: implemented and used for deterministic section segmentation and focusing.
- **SummarizerAgent**: implemented, used primarily in the standalone 3-agent pipeline.
- **StructurerAgent**: currently a placeholder that returns empty structures. It is **not** used for production registry extraction.

## Agent Contracts

All contracts are defined in `modules/agents/contracts.py`:

### Common Types

```python
class AgentWarning(BaseModel):
    """Non-blocking warning from an agent."""
    code: str           # e.g., "MISSING_HEADER", "AMBIGUOUS_SECTION"
    message: str
    section: Optional[str] = None

class AgentError(BaseModel):
    """Error that may prevent successful output."""
    code: str           # e.g., "NO_SECTIONS_FOUND", "PARSING_FAILED"
    message: str
    section: Optional[str] = None

class Segment(BaseModel):
    """A segmented portion of the note."""
    id: str
    type: str           # "HISTORY", "PROCEDURE", "FINDINGS", etc.
    text: str
    start_char: Optional[int]
    end_char: Optional[int]
    spans: List[Tuple[int, int]]

class Entity(BaseModel):
    """An extracted entity (e.g., EBUS station, stent type)."""
    label: str
    value: str
    name: str
    type: str
    offsets: Optional[Tuple[int, int]]
    evidence_segment_id: Optional[str]
    attributes: Optional[Dict[str, Any]]

class Trace(BaseModel):
    """Debugging metadata for agent output."""
    trigger_phrases: List[str]
    rule_paths: List[str]
    confounders_checked: List[str]
    confidence: float
    notes: Optional[str]
```

### Parser Contracts

```python
class ParserIn(BaseModel):
    """Input to Parser agent."""
    note_id: str
    raw_text: str

class ParserOut(BaseModel):
    """Output from Parser agent."""
    note_id: str
    segments: List[Segment]      # Extracted segments
    entities: List[Entity]       # Extracted entities
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Summarizer Contracts

```python
class SummarizerIn(BaseModel):
    """Input to Summarizer agent."""
    parser_out: ParserOut

class SummarizerOut(BaseModel):
    """Output from Summarizer agent."""
    note_id: str
    summaries: Dict[str, str]    # Section -> summary mapping
    caveats: List[str]           # Important notes/caveats
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Structurer Contracts

```python
class StructurerIn(BaseModel):
    """Input to Structurer agent."""
    summarizer_out: SummarizerOut

class StructurerOut(BaseModel):
    """Output from Structurer agent."""
    note_id: str
    registry: Dict[str, Any]     # Structured registry fields
    codes: Dict[str, Any]        # Generated CPT codes
    rationale: Dict[str, Any]    # Coding rationale
    trace: Trace
    warnings: List[AgentWarning]
    errors: List[AgentError]
    status: Literal["ok", "degraded", "failed"]
```

### Pipeline Result

```python
class PipelineResult(BaseModel):
    """Full result from running the 3-agent pipeline."""
    pipeline_status: Literal[
        "ok",
        "degraded",
        "failed_parser",
        "failed_summarizer",
        "failed_structurer"
    ]
    parser: Optional[ParserOut]
    summarizer: Optional[SummarizerOut]
    structurer: Optional[StructurerOut]
    registry: Optional[Dict[str, Any]]
    codes: Optional[Dict[str, Any]]
```

## Agent Implementations

### 1. ParserAgent

**Purpose:** Split raw procedure notes into structured segments and extract entities.

**Location:** `modules/agents/parser/parser_agent.py`

**Algorithm:**
1. Search for common section headings (HPI, History, Procedure, Findings, etc.)
2. Split text at heading boundaries
3. Create `Segment` objects with type, text, and character offsets
4. Fallback: treat entire note as single "full" segment if no headings found

**Recognized Headings:**
- HPI
- History
- Procedure
- Findings
- Sedation
- Complications
- Disposition

**Example Input:**
```python
ParserIn(
    note_id="note_001",
    raw_text="History: 65yo male with lung nodule.\nProcedure: Bronchoscopy with EBUS."
)
```

**Example Output:**
```python
ParserOut(
    note_id="note_001",
    segments=[
        Segment(type="History", text="65yo male with lung nodule.", ...),
        Segment(type="Procedure", text="Bronchoscopy with EBUS.", ...),
    ],
    entities=[],
    status="ok",
    trace=Trace(rule_paths=["parser.heading_split.v1"], ...)
)
```

### 2. SummarizerAgent

**Purpose:** Generate section summaries from parsed segments and entities.

**Location:** `modules/agents/summarizer/summarizer_agent.py`

**Algorithm:**
1. Iterate through segments from parser output
2. Generate concise summaries for each section type
3. Collect caveats (important notes requiring attention)
4. Handle missing or ambiguous sections gracefully

**Example Output:**
```python
SummarizerOut(
    note_id="note_001",
    summaries={
        "History": "65-year-old male evaluated for lung nodule",
        "Procedure": "EBUS bronchoscopy performed",
    },
    caveats=[],
    status="ok"
)
```

### 3. StructurerAgent

**Purpose:** Map summaries to structured registry fields and generate CPT codes.

**Location:** `modules/agents/structurer/structurer_agent.py`

**Algorithm:**
1. Extract demographic info from History summary
2. Identify procedures from Procedure summary
3. Map to registry schema fields
4. Generate appropriate CPT codes
5. Provide coding rationale

**Example Output:**
```python
StructurerOut(
    note_id="note_001",
    registry={
        "patient_demographics": {"age_years": 65, "gender": "Male"},
        "procedures_performed": {"linear_ebus": {"performed": True}},
    },
    codes={"cpt_codes": ["31652"]},
    rationale={"31652": "EBUS-TBNA performed"},
    status="ok"
)
```

## Pipeline Orchestration

The pipeline is orchestrated by `run_pipeline()` in `modules/agents/run_pipeline.py`:

```python
from modules.agents.run_pipeline import run_pipeline, run_pipeline_typed

# Dict interface
result = run_pipeline({"note_id": "123", "raw_text": "..."})

# Typed interface
result = run_pipeline_typed({"note_id": "123", "raw_text": "..."})
```

### Pipeline Flow

```
1. Parser
   ├── Success (ok) → Continue to Summarizer
   ├── Degraded → Continue with warning
   └── Failed → Return failed_parser result

2. Summarizer
   ├── Success (ok) → Continue to Structurer
   ├── Degraded → Continue with warning
   └── Failed → Return failed_summarizer result

3. Structurer
   ├── Success (ok) → Return ok result
   ├── Degraded → Return degraded result
   └── Failed → Return failed_structurer result
```

### Error Handling

Each agent stage is wrapped in error handling:
- Exceptions are caught and converted to `AgentError`
- Failed stages stop the pipeline
- Degraded stages continue with warnings
- Partial results are preserved for debugging

### Timing

Pipeline execution is timed using `observability.timing`:
- `pipeline.total` - Total pipeline time
- `pipeline.parser` - Parser stage time
- `pipeline.summarizer` - Summarizer stage time
- `pipeline.structurer` - Structurer stage time

## Usage Examples

### Basic Usage

```python
from modules.agents.run_pipeline import run_pipeline

note = {
    "note_id": "test_001",
    "raw_text": """
    History: 65-year-old male with 2cm RUL nodule.
    Procedure: EBUS bronchoscopy with TBNA of station 4R and 7.
    Findings: Lymph nodes appeared abnormal on ultrasound.
    Complications: None
    """
}

result = run_pipeline(note)

print(f"Status: {result['pipeline_status']}")
print(f"Registry: {result['registry']}")
print(f"Codes: {result['codes']}")
```

### Error Handling

```python
result = run_pipeline({"note_id": "123", "raw_text": ""})

if result["pipeline_status"].startswith("failed"):
    stage = result["pipeline_status"].split("_")[1]
    errors = result.get(stage, {}).get("errors", [])
    for error in errors:
        print(f"Error [{error['code']}]: {error['message']}")
```

### Accessing Intermediate Results

```python
result = run_pipeline_typed(note)

# Access parser output
for segment in result.parser.segments:
    print(f"Section: {segment.type}")
    print(f"Text: {segment.text[:100]}...")

# Access summarizer output
for section, summary in result.summarizer.summaries.items():
    print(f"{section}: {summary}")

# Access structurer output
print(f"Registry: {result.structurer.registry}")
print(f"Rationale: {result.structurer.rationale}")
```

## Extending the Pipeline

### Adding a New Agent

1. Create a new directory: `modules/agents/myagent/`
2. Define the agent class in `myagent_agent.py`:

```python
from modules.agents.contracts import MyAgentIn, MyAgentOut

class MyAgent:
    def run(self, input: MyAgentIn) -> MyAgentOut:
        # Implementation
        return MyAgentOut(...)
```

3. Add contracts to `contracts.py`:

```python
class MyAgentIn(BaseModel):
    ...

class MyAgentOut(BaseModel):
    status: Literal["ok", "degraded", "failed"]
    ...
```

4. Update `run_pipeline.py` to include the new stage.

### Customizing Existing Agents

Each agent can be subclassed or replaced:

```python
class CustomParserAgent(ParserAgent):
    def run(self, parser_in: ParserIn) -> ParserOut:
        # Custom implementation
        ...
```

## Best Practices

1. **Status Tracking**: Always set appropriate status (ok/degraded/failed)
2. **Error Collection**: Add errors with descriptive codes and messages
3. **Trace Metadata**: Include rule paths and trigger phrases for debugging
4. **Graceful Degradation**: Continue with warnings when possible
5. **Contract Compliance**: Always return valid contract objects

---

*Last updated: January 2026*

```

---
### `docs/DEVELOPMENT.md`
```
# Development Guide

This document is the **Single Source of Truth** for developers and AI assistants working on the Procedure Suite.

## Core Mandates

1.  **Main Application**: Always edit `modules/api/fastapi_app.py`. Never edit `api/app.py` (deprecated).
2.  **Coding Service**: Use `CodingService` from `modules/coder/application/coding_service.py`. The old `modules.coder.engine.CoderEngine` is deprecated.
3.  **Registry Service**: Use `RegistryService` from `modules/registry/application/registry_service.py`.
4.  **Knowledge Base**: The source of truth for coding rules is `data/knowledge/ip_coding_billing_v3_0.json`.
5.  **Tests**: Preserve existing tests. Run `make test` before committing.

---

## System Architecture

### Directory Structure

| Directory | Status | Purpose |
|-----------|--------|---------|
| `modules/api/` | **ACTIVE** | Main FastAPI app (`fastapi_app.py`) |
| `modules/coder/` | **ACTIVE** | CPT Coding Engine with CodingService (8-step pipeline) |
| `modules/coder/parallel_pathway/` | **EXPERIMENTAL** | Parallel NER+ML pathway for extraction-first coding |
| `modules/ner/` | **EXPERIMENTAL** | Granular NER model (DistilBERT for entity extraction) |
| `modules/ml_coder/` | **ACTIVE** | ML-based code prediction and training |
| `modules/registry/` | **ACTIVE** | Registry extraction with RegistryService and RegistryEngine |
| `modules/registry/ner_mapping/` | **EXPERIMENTAL** | NER-to-Registry entity mapping |
| `modules/agents/` | **ACTIVE** | 3-agent pipeline (Parser, Summarizer, Structurer) |
| `modules/reporter/` | **ACTIVE** | Report generation with Jinja templates |
| `modules/common/` | **ACTIVE** | Shared utilities, logging, exceptions |
| `modules/domain/` | **ACTIVE** | Domain models and business rules |
| `api/` | **DEPRECATED** | Old API entry point. Do not use. |

### Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| `CodingService` | `modules/coder/application/coding_service.py` | 8-step CPT coding pipeline |
| `RegistryService` | `modules/registry/application/registry_service.py` | Hybrid-first registry extraction |
| `SmartHybridOrchestrator` | `modules/coder/application/smart_hybrid_policy.py` | ML-first hybrid coding |
| `RegistryEngine` | `modules/registry/engine.py` | LLM-based field extraction |
| `ParallelPathwayOrchestrator` | `modules/coder/parallel_pathway/orchestrator.py` | NER+ML parallel pathway (experimental) |
| `GranularNERPredictor` | `modules/ner/inference.py` | DistilBERT NER inference |
| `NERToRegistryMapper` | `modules/registry/ner_mapping/entity_to_registry.py` | Map NER entities to registry fields |

### Data Flow

```
[Procedure Note]
       │
       ▼
[API Layer] (modules/api/fastapi_app.py)
       │
       ├─> [CodingService] ──> [SmartHybridOrchestrator] ──> [Codes + RVUs]
       │        │                    │
       │        │                    ├── ML Prediction
       │        │                    ├── Rules Engine
       │        │                    └── LLM Advisor (fallback)
       │        │
       │        └──> NCCI/MER Compliance ──> Final Codes
       │
       ├─> [RegistryService] ──> [CPT Mapping + LLM Extraction] ──> [Registry Record]
       │
       └─> [Reporter] ──────> [Jinja Templates] ───> [Synoptic Report]
```

---

## AI Agent Roles

### 1. Coder Agent

**Focus**: `modules/coder/`

**Key Files:**
- `modules/coder/application/coding_service.py` - Main orchestrator
- `modules/coder/application/smart_hybrid_policy.py` - Hybrid decision logic
- `modules/coder/domain_rules/` - NCCI bundling, domain rules
- `modules/coder/rules_engine.py` - Rule-based inference

**Responsibilities:**
- Maintain the 8-step coding pipeline in `CodingService`
- Update domain rules in `modules/coder/domain_rules/`
- Ensure NCCI/MER compliance logic is correct
- Keep confidence thresholds tuned in `modules/ml_coder/thresholds.py`

**Rule**: Do not scatter logic. Keep business rules central in the Knowledge Base or `modules/coder/domain_rules/`.

### 2. Registry Agent

**Focus**: `modules/registry/`

**Key Files:**
- `modules/registry/application/registry_service.py` - Main service
- `modules/registry/application/cpt_registry_mapping.py` - CPT → registry mapping
- `modules/registry/engine.py` - LLM extraction engine
- `modules/registry/prompts.py` - LLM prompts
- `modules/registry/schema.py` - RegistryRecord model
- `modules/registry/v2_booleans.py` - V2→V3 boolean mapping for ML
- `modules/registry/postprocess.py` - Output normalization

**Responsibilities:**
- Maintain schema definitions in `schema.py` and `schema_granular.py`
- Update LLM prompts in `prompts.py`
- Handle LLM list outputs by adding normalizers in `postprocess.py`
- Keep CPT-to-registry mapping current in `cpt_registry_mapping.py`
- Update V2→V3 boolean mapping in `v2_booleans.py` when schema changes

**Critical (v3 / extraction-first)**: When changing the registry schema, update:
1. `data/knowledge/IP_Registry.json` - Canonical v3 nested schema (drives dynamic `RegistryRecord`)
2. `modules/registry/schema.py` / `modules/registry/schema_granular.py` - Custom type overrides + granular helpers
3. `modules/registry/v2_booleans.py` - Boolean field list (ML label order)
4. `modules/registry/application/cpt_registry_mapping.py` - CPT mappings

Note: `schemas/IP_Registry.json` is a legacy flat schema used by `modules/registry_cleaning/`. Do not try to keep it identical to the v3 schema unless you also migrate the cleaning pipeline.

### 3. ML Agent

**Focus**: `modules/ml_coder/`

**Key Files:**
- `modules/ml_coder/predictor.py` - CPT code predictor
- `modules/ml_coder/registry_predictor.py` - Registry field predictor
- `modules/ml_coder/training.py` - Model training
- `modules/ml_coder/data_prep.py` - Data preparation
- `modules/ml_coder/thresholds.py` - Confidence thresholds

**Responsibilities:**
- Maintain ML model training pipelines
- Tune confidence thresholds for hybrid policy
- Prepare training data from golden extractions
- Ensure ML predictions align with registry schema

### 4. Reporter Agent

**Focus**: `modules/reporter/`

**Responsibilities:**
- Edit Jinja templates for report formatting
- Maintain validation logic for required fields
- Ensure inference logic derives fields correctly
- **Rule**: Use `{% if %}` guards in templates. Never output "None" or "missing" in final reports.

### 5. DevOps/API Agent

**Focus**: `modules/api/`

**Responsibilities:**
- Maintain `fastapi_app.py`
- Ensure endpoints `/v1/coder/run`, `/v1/registry/run`, `/report/render` work correctly
- **Warning**: Do not create duplicate routes. Check existing endpoints first.

---

## Module Dependencies

```
modules/api/
    └── depends on: modules/coder/, modules/registry/, modules/reporter/

modules/coder/
    ├── depends on: modules/ml_coder/, modules/domain/, modules/phi/
    └── provides: CodingService, SmartHybridOrchestrator

modules/registry/
    ├── depends on: modules/coder/, modules/ml_coder/
    └── provides: RegistryService, RegistryEngine

modules/ml_coder/
    └── provides: MLPredictor, RegistryMLPredictor

modules/agents/
    └── provides: run_pipeline(), ParserAgent, SummarizerAgent, StructurerAgent
```

---

## Testing

### Test Commands

```bash
# All tests
make test

# Specific test suites
pytest tests/coder/ -v              # Coder tests
pytest tests/registry/ -v           # Registry tests
pytest tests/ml_coder/ -v           # ML coder tests
pytest tests/api/ -v                # API tests

# Validation
make validate-registry              # Registry extraction validation
make preflight                      # Pre-flight checks
make lint                           # Linting
```

### LLM Tests

By default, tests run in offline mode with stub LLMs. To test actual extraction:

```bash
# Gemini
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="..."
pytest tests/registry/test_extraction.py

# OpenAI (uses Responses API by default)
export OPENAI_OFFLINE=0
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o"
pytest tests/unit/test_openai_responses_primary.py

# OpenAI with Chat Completions API (legacy mode)
export OPENAI_PRIMARY_API=chat
pytest tests/unit/test_openai_timeouts.py
```

**Note**: The OpenAI integration uses the Responses API (`/v1/responses`) by default. When writing tests that mock httpx for OpenAI, set `OPENAI_PRIMARY_API=chat` to use the Chat Completions path if your mock expects that format.

### Test Data

- Golden extractions: `data/knowledge/golden_extractions/`
- Synthetic test data: Use fixtures in test files
- **Never** commit PHI (real patient data)

---

## Development Workflow

### Before Making Changes

1. Read relevant documentation:
   - [ARCHITECTURE.md](ARCHITECTURE.md) for system design
   - [AGENTS.md](AGENTS.md) for multi-agent pipeline
   - [Registry_API.md](Registry_API.md) for registry service

2. Understand the data flow:
   - Trace the code path from API endpoint to service to engine
   - Identify which module owns the logic you're changing

3. Check existing tests:
   - Run relevant test suite before changes
   - Understand what behavior is expected

### Making Changes

1. **Edit the correct files**:
   - API: `modules/api/fastapi_app.py` (not `api/app.py`)
   - Coder: `modules/coder/` (not legacy engine)
   - Registry: `modules/registry/`

2. **Follow the architecture**:
   - Services orchestrate, engines execute
   - Keep business rules in domain modules
   - Use adapters for external dependencies

3. **Maintain contracts**:
   - Don't break existing API contracts
   - Update Pydantic schemas if needed
   - Add deprecation warnings, not breaking changes

### After Making Changes

1. Run tests: `make test` or specific test suite
2. Run linting: `make lint`
3. Test the dev server: `./scripts/devserver.sh`
4. Verify no PHI was committed

---

## Development Checklist

Before committing changes:

- [ ] I am editing `modules/api/fastapi_app.py` (not `api/app.py`)
- [ ] I am using `CodingService` (not legacy `CoderEngine`)
- [ ] I am using `RegistryService` (not direct engine calls)
- [ ] I have run `make test` (or relevant unit tests)
- [ ] I have checked `scripts/devserver.sh` to ensure the app starts
- [ ] I have not committed any PHI (real patient data)
- [ ] I have updated documentation if changing APIs or schemas

---

## Common Pitfalls

1. **Editing deprecated files**: Always check if a file is deprecated before editing
2. **Duplicate routes**: Check existing endpoints before adding new ones
3. **Breaking contracts**: Don't change API response shapes without versioning
4. **Scattered logic**: Keep business rules in domain modules, not scattered across services
5. **Missing normalization**: LLM outputs often need post-processing in `postprocess.py`
6. **Schema drift**: When changing registry schema, update all dependent files

---

*Last updated: December 2025*

```

---
### `docs/ARCHITECTURE.md`
```
# Procedure Suite Architecture

This document describes the system architecture, module organization, and data flow of the Procedure Suite.

## Overview

The Procedure Suite is a modular system for automated medical coding, registry extraction, and report generation. It follows a **hexagonal architecture** pattern with clear separation between:

- **Domain logic** (business rules, schemas)
- **Application services** (orchestration, workflows)
- **Adapters** (LLM, ML, database, API)

> **Current Production Mode (2026-01):** The server enforces
> `PROCSUITE_PIPELINE_MODE=extraction_first` at startup. The authoritative
> endpoint is `POST /api/v1/process`, and its primary pipeline is
> **Extraction‑First**: **Registry extraction → deterministic Registry→CPT**
> (with auditing + optional self-correction).
>
> **Legacy note:** CPT-first / hybrid-first flows still exist in code for older
> endpoints and tooling, but are expected to be gated/disabled in production.

## Directory Structure

```
Procedure_suite/
├── modules/                    # Core application modules
│   ├── api/                    # FastAPI endpoints and routes
│   ├── coder/                  # CPT coding engine
│   ├── ml_coder/               # ML-based prediction
│   ├── registry/               # Registry extraction
│   ├── agents/                 # 3-agent pipeline
│   ├── reporter/               # Report generation
│   ├── common/                 # Shared utilities
│   ├── domain/                 # Domain models and rules
│   └── phi/                    # PHI handling
├── data/
│   └── knowledge/              # Knowledge bases and training data
├── schemas/                    # JSON Schema definitions
├── proc_schemas/               # Pydantic schema definitions
├── config/                     # Configuration settings
├── scripts/                    # CLI tools and utilities
├── tests/                      # Test suites
└── docs/                       # Documentation
```

## Core Modules

### 1. API Layer (`modules/api/`)

The FastAPI application serving REST endpoints.

**Key Files:**
- `fastapi_app.py` - Main application with route registration
- `routes/` - Endpoint handlers
- `schemas/` - Request/response models
- `dependencies.py` - Dependency injection

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/process` | POST | **Authoritative** unified extraction-first pipeline (UI uses this) |
| `/v1/coder/run` | POST | Legacy CPT coding endpoint (gated in production) |
| `/v1/registry/run` | POST | Legacy registry extraction endpoint (gated in production) |
| `/v1/report/render` | POST | Generate synoptic report |
| `/health` | GET | Health check |

### 2. Coder Module (`modules/coder/`)

CPT code prediction using rules, ML, and LLM.

**Architecture:**
```
modules/coder/
├── application/
│   ├── coding_service.py       # Main orchestrator (8-step pipeline)
│   └── smart_hybrid_policy.py  # ML-first hybrid decision logic
├── adapters/
│   ├── llm/                    # LLM advisor adapter
│   ├── nlp/                    # Keyword mapping, negation detection
│   └── ml_ranker.py            # ML prediction adapter
├── domain_rules/               # NCCI bundling + deterministic registry→CPT
├── rules_engine.py             # Rule-based code inference
└── engine.py                   # Legacy coder (deprecated)
```

**CodingService 8-Step Pipeline (legacy coding endpoints / tooling):**
1. Rule engine → rule_codes + confidence
2. (Optional) ML ranker → ml_confidence
3. LLM advisor → advisor_codes + confidence
4. Smart hybrid merge → HybridDecision flags
5. Evidence validation → verify codes in text
6. Non-negotiable rules (NCCI/MER) → remove invalid combos
7. Confidence aggregation → final_confidence, review_flag
8. Build CodeSuggestion[] → return for review

### 3. ML Coder Module (`modules/ml_coder/`)

Machine learning models for CPT and registry prediction.

**Key Files:**
- `predictor.py` - CPT code predictor
- `registry_predictor.py` - Registry field predictor
- `training.py` - Model training pipeline
- `registry_training.py` - Registry ML training
- `data_prep.py` - Data preparation utilities
- `thresholds.py` - Confidence thresholds

**ML-First Hybrid Policy:**
```
Note → ML Predict → Classify Difficulty → Decision Gate → Final Codes
                         ↓
         HIGH_CONF: ML + Rules (fast path)
         GRAY_ZONE: LLM as judge
         LOW_CONF:  LLM primary
```

### 4. Registry Module (`modules/registry/`)

Registry data extraction from procedure notes.

**Architecture:**
```
modules/registry/
├── application/
│   ├── registry_service.py     # Main service (extraction-first; hybrid-first legacy still present)
│   ├── registry_builder.py     # Build registry entries
│   └── cpt_registry_mapping.py # CPT → registry field mapping
├── adapters/
│   └── schema_registry.py      # Schema validation
├── engine.py                   # LLM extraction engine
├── prompts.py                  # LLM prompts
├── schema.py                   # RegistryRecord model
├── schema_granular.py          # Granular per-site data
├── v2_booleans.py              # V2→V3 boolean mapping for ML
├── deterministic_extractors.py # Rule-based extractors
├── normalization.py            # Field normalization
└── postprocess.py              # Output post-processing
```

**Hybrid-First Extraction Flow:**
1. CPT Coding (SmartHybridOrchestrator)
2. CPT Mapping (aggregate_registry_fields)
3. LLM Extraction (RegistryEngine)
4. Reconciliation (merge CPT-derived + LLM-extracted)
5. Validation (IP_Registry.json schema)
6. ML Audit (compare CPT-derived vs ML predictions)

**Target: Extraction-First Registry Flow (feature-flagged)**
1. Registry extraction from raw note text (no CPT hints)
2. Granular → aggregate propagation (`derive_procedures_from_granular`)
3. Deterministic RegistryRecord → CPT derivation (no note text)
4. RAW-ML auditor calls `MLCoderPredictor.classify_case(raw_note_text)` directly (no orchestrator/rules)
5. Compare deterministic CPT vs RAW-ML audit set and report discrepancies
6. Optional guarded self-correction loop (default off)

### 5. Agents Module (`modules/agents/`)

3-agent pipeline for structured note processing.

**Current usage:**
- `ParserAgent` is used as a deterministic sectionizer and can be used to *focus* the note text for registry extraction (see `modules/registry/extraction/focus.py`).
- The full `Parser → Summarizer → Structurer` pipeline exists, but `StructurerAgent` is currently a placeholder and is **not** used for production registry extraction.

**Architecture:**
```
modules/agents/
├── contracts.py                # I/O schemas (Pydantic)
├── run_pipeline.py             # Pipeline orchestration
├── parser/
│   └── parser_agent.py         # Segment extraction
├── summarizer/
│   └── summarizer_agent.py     # Section summarization
└── structurer/
    └── structurer_agent.py     # Registry mapping
```

**Pipeline Flow:**
```
Raw Text → Parser → Segments/Entities
                        ↓
              Summarizer → Section Summaries
                              ↓
                    Structurer → Registry + Codes
```

See [AGENTS.md](AGENTS.md) for detailed agent documentation.

### 6. Reporter Module (`modules/reporter/`)

Synoptic report generation from structured data.

**Key Components:**
- Jinja2 templates for report formatting
- Validation logic for required fields
- Inference logic for derived fields

## Data Flow

### CPT Coding Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw Note  │ ──▶ │  ML Predict │ ──▶ │   Classify  │
└─────────────┘     └─────────────┘     │  Difficulty │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌────────────────┐       ┌─────────────────┐       ┌────────────────┐
           │   HIGH_CONF    │       │    GRAY_ZONE    │       │   LOW_CONF     │
           │ ML + Rules     │       │  LLM as Judge   │       │ LLM Primary    │
           └───────┬────────┘       └────────┬────────┘       └───────┬────────┘
                   │                         │                        │
                   └─────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ NCCI/MER Rules  │
                                    │  (Compliance)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Final Codes    │
                                    │ CodeSuggestion[]│
                                    └─────────────────┘
```

### Registry Extraction Flow

```
┌───────────────┐
│    Raw Note   │
└───────┬───────┘
        │
        ▼
┌──────────────────────────────────────────┐
│ Registry extraction (engine selected by  │
│ REGISTRY_EXTRACTION_ENGINE; production   │
│ requires parallel_ner)                   │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│ RegistryRecord (V3-shaped)   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Deterministic Registry→CPT derivation    │
│ (no raw note parsing)                    │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│ Audit + guardrails + optional self-fix   │
│ (RAW-ML auditor, keyword guard, etc.)    │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│ Codes + evidence + review    │
│ flags (returned by /process) │
└──────────────────────────────┘
```

## Schema System

### JSON Schemas
- `schemas/IP_Registry.json` - Registry entry validation
- `data/knowledge/IP_Registry.json` - Registry schema (dynamic model)

### Pydantic Schemas
- `proc_schemas/coding.py` - CodeSuggestion, CodingResult
- `proc_schemas/registry/ip_v2.py` - IPRegistryV2
- `proc_schemas/registry/ip_v3.py` - IPRegistryV3
- `modules/registry/schema.py` - RegistryRecord (extraction record model)

### Registry Procedure Flags

The registry uses 30 boolean procedure presence flags for ML training:

**Bronchoscopy Procedures (23):**
- diagnostic_bronchoscopy, bal, bronchial_wash, brushings
- endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
- navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
- therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
- thermal_ablation, tumor_debulking_non_thermal, cryotherapy, blvr, peripheral_ablation
- bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy

**Pleural Procedures (7):**
- thoracentesis, chest_tube, ipc, medical_thoracoscopy
- pleurodesis, pleural_biopsy, fibrinolytic_therapy

See `modules/registry/v2_booleans.py` for the canonical V2→V3 mapping.

## Configuration

### Settings (`config/settings.py`)

Key configuration classes:
- `CoderSettings` - Coder thresholds and behavior
- `RegistrySettings` - Registry extraction settings
- `MLSettings` - ML model paths and parameters

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | LLM backend: `gemini` or `openai_compat` |
| `GEMINI_API_KEY` | Gemini LLM API key |
| `GEMINI_OFFLINE` | Skip LLM calls (use stubs) |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry |
| `OPENAI_API_KEY` | API key for OpenAI-protocol backend (openai_compat) |
| `OPENAI_BASE_URL` | Base URL for OpenAI-protocol backend (no `/v1`) |
| `OPENAI_MODEL` | Default model name for openai_compat |
| `OPENAI_MODEL_SUMMARIZER` | Model override for summarizer/focusing tasks (openai_compat only) |
| `OPENAI_MODEL_STRUCTURER` | Model override for structurer tasks (openai_compat only) |
| `OPENAI_MODEL_JUDGE` | Model override for self-correction judge (openai_compat only) |
| `OPENAI_OFFLINE` | Disable openai_compat network calls (use stubs) |
| `OPENAI_PRIMARY_API` | Primary API: `responses` or `chat` (default: `responses`) |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat Completions on 404 (default: `1`) |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Read timeout for registry tasks (default: `180`) |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Read timeout for default tasks (default: `60`) |
| `PROCSUITE_SKIP_WARMUP` | Skip model warmup |
| `PROCSUITE_PIPELINE_MODE` | **Startup-enforced:** must be `extraction_first` |
| `REGISTRY_EXTRACTION_ENGINE` | Extraction engine (production requires `parallel_ner`) |
| `REGISTRY_SCHEMA_VERSION` | Registry schema version (production requires `v3`) |
| `REGISTRY_AUDITOR_SOURCE` | Auditor source (production requires `raw_ml`) |

## Dependencies

### External Services
- **OpenAI-compatible API** (`LLM_PROVIDER=openai_compat`) - LLM judge/self-correction and (in legacy modes) extraction
- **Gemini API** (optional) - Alternative LLM provider for extraction/self-correction in non-openai_compat setups
- **spaCy** - NLP for entity extraction

### Key Libraries
- FastAPI - Web framework
- Pydantic - Data validation
- scikit-learn - ML models
- onnxruntime - ONNX model inference (when `MODEL_BACKEND=onnx`)
- Jinja2 - Report templating

## Testing Strategy

### Test Organization
```
tests/
├── coder/           # CodingService tests
├── registry/        # RegistryService tests
├── ml_coder/        # ML predictor tests
├── agents/          # Agent pipeline tests
└── api/             # API endpoint tests
```

### Test Categories
- **Unit tests** - Individual function testing
- **Integration tests** - Service-level testing
- **Contract tests** - Schema validation
- **Validation tests** - Ground truth comparison

### Running Tests
```bash
make test                           # All tests
pytest tests/coder/ -v              # Coder only
pytest tests/registry/ -v           # Registry only
make validate-registry              # Registry validation
```

---

*Last updated: 2026-01-30*

```

---
### `docs/INSTALLATION.md`
```
# Installation & Setup Guide

This guide covers setting up the Procedure Suite environment, including Python dependencies, spaCy models, and Gemini API configuration.

## 1. Prerequisites

- **Python 3.11+** (Required: `>=3.11,<3.14`)
- **micromamba** or **conda** (Recommended for environment management)
- **Git**

## 2. Environment Setup

### Create Python Environment

Using `micromamba` (recommended) or `conda`:

```bash
# Create environment
micromamba create -n medparse-py311 python=3.11
micromamba activate medparse-py311
```

### Install Dependencies

Install the project in editable mode along with API and dev dependencies:

```bash
make install
# Or manually: pip install -e ".[api,dev]"
```

### Install spaCy Models

The project requires specific spaCy models for NLP tasks:

```bash
# Install scispaCy model (Required - may take a few minutes)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Install standard spaCy model
python -m spacy download en_core_web_sm
```

## 3. Configuration (.env)

Create a `.env` file in the project root to store configuration and secrets:

```bash
touch .env
```

### Gemini API Configuration (Required for Extraction)

The system uses Google's Gemini models for registry extraction.

**Option 1: API Key (Simpler)**
Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite  # Optional: Override default model
```

**Option 2: OAuth2 / Service Account (For Cloud Subscriptions)**
If running on GCP or using a service account:

```bash
GEMINI_USE_OAUTH=true
# Optional: Path to service account JSON if not using default credentials
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### OpenAI-Compatible API Configuration (Alternative to Gemini)

If using an OpenAI-compatible backend (including OpenAI, Azure OpenAI, or local models):

```bash
# Required settings
LLM_PROVIDER=openai_compat
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o  # or your preferred model

# Optional: Custom endpoint (for Azure, local models, etc.)
# OPENAI_BASE_URL=https://your-endpoint.com  # No /v1 suffix

# API Selection (default: Responses API)
# OPENAI_PRIMARY_API=responses        # Use Responses API (default)
# OPENAI_PRIMARY_API=chat             # Use Chat Completions API

# Fallback behavior (when Responses API returns 404)
# OPENAI_RESPONSES_FALLBACK_TO_CHAT=1  # Fall back to Chat (default)
# OPENAI_RESPONSES_FALLBACK_TO_CHAT=0  # Disable fallback

# Timeout configuration (seconds)
# OPENAI_TIMEOUT_READ_REGISTRY_SECONDS=180  # Registry tasks (default: 180s)
# OPENAI_TIMEOUT_READ_DEFAULT_SECONDS=60    # Other tasks (default: 60s)
```

**Note**: The system uses the OpenAI Responses API (`POST /v1/responses`) by default. If your endpoint doesn't support it, set `OPENAI_PRIMARY_API=chat` or enable fallback with `OPENAI_RESPONSES_FALLBACK_TO_CHAT=1`.

### Other Settings

```bash
# Enable LLM Advisor for Coder (Optional)
CODER_USE_LLM_ADVISOR=1

# Supabase Integration (Optional - for DB export)
# SUPABASE_DB_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

## 4. Verification

Run the preflight check to validate your setup:

```bash
make preflight
```

This script checks:
- ✅ Python version
- ✅ Installed dependencies (including `sklearn` version)
- ✅ spaCy models
- ✅ Configuration validity

## 5. Running Tests (Offline vs Online)

By default, tests run in **offline mode** using a stub LLM to avoid API costs and network dependency.

### Offline Mode (Default)
```bash
pytest -q
```

### Online Mode (Live API)
To test with the real Gemini API:

```bash
# Override default offline flags
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="your-key"

pytest -q
```

## 6. Starting the API Server

To run the FastAPI backend locally:

```bash
make api
# Or: ./scripts/devserver.sh
```

The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`

```

---
### `docs/USER_GUIDE.md`
```
# Procedure Suite - User Guide

This guide explains how to use the Procedure Suite tools for generating reports, coding procedures, and validating registry data.

---

## Important: Current Production Mode (2026-01)

- The server is a **stateless logic engine**: **(scrubbed) note text in → registry + CPT codes out**.
- **Primary endpoint:** `POST /api/v1/process`
- Startup enforces `PROCSUITE_PIPELINE_MODE=extraction_first` (service will not start otherwise).
- In production (`CODER_REQUIRE_PHI_REVIEW=true`), `/api/v1/process` stays enabled and returns:
  - `review_status="pending_phi_review"`
  - `needs_manual_review=true`
- Optional: `REGISTRY_SELF_CORRECT_ENABLED=1` allows an external LLM to act as a **judge** on **scrubbed text** to patch missing fields
  when high-confidence omissions are detected (slower but higher quality).
  - Self-correction is gated by a CPT keyword guard; skips will include `SELF_CORRECT_SKIPPED:` warnings when enabled.

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement uses `31647` (initial lobe) + `31651` (each additional lobe); valve removal uses `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## How the System Works (Plain Language)

The Procedure Suite is an intelligent medical coding assistant that reads procedure notes and suggests appropriate CPT billing codes. Here's how it works in simple terms:

### The Three Brains

1. **Granular NER**: A trained model that finds procedure actions/devices (e.g., BAL, EBUS stations, cryotherapy) as text spans to drive structured extraction.

2. **Rules Engine**: A set of explicit business rules that encode medical billing knowledge, such as:
   - "You can't bill these two codes together" (bundling rules)
   - "This code requires specific documentation" (validation rules)
   - "If procedure X was done, code Y is required" (inference rules)

3. **ML Auditor + Guardrails**: A safety net that flags likely omissions/mismatches and forces review when extraction degrades. Optional LLM components are used for advisor/self-correction when enabled.

### Extraction-First Pipeline (Current)

Recommended runtime configuration uses the `parallel_ner` extraction engine:

```
(Scrubbed) Note Text
  → [Path A] Granular NER → Registry mapping → Deterministic Registry→CPT rules
  → [Path B] Optional ML classifier/auditor (may be unavailable)
  → Guardrails + omission scan (surface warnings, require review when needed)
```

Key behaviors:
- **Deterministic uplift** prevents “silent revenue loss” when NER misses common procedures (BAL/EBBx/radial EBUS/cryotherapy, plus backstops like navigational bronchoscopy and pleural IPC/tunneled catheter).
- `audit_warnings` surfaces `SILENT_FAILURE:` and other degraded-mode warnings to the UI.
- **Context guardrails (anti-hallucination)** reduce over-coding from “keyword only” matches:
  - **Stents**: inspection-only phrases like “stent … in good position” clear `airway_stent.performed` (prevents CPT `31636`).
  - **Chest tubes**: discontinue/removal phrases like “D/c chest tube” do not set `pleural_procedures.chest_tube.performed` (prevents CPT `32551`).
  - **TBNA**: EBUS-TBNA does not set `tbna_conventional` (prevents double-coding `31629` alongside `31652/31653`).
  - **Radial EBUS**: explicit “radial probe” language sets `radial_ebus.performed` even without “concentric/eccentric” markers.
- **Noise masking** strips CPT menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations (laser/APC/etc).
- **Self-correction (LLM judge)**: when `REGISTRY_SELF_CORRECT_ENABLED=1`, RAW-ML high-confidence omissions can trigger a small number of
  evidence-gated patches (verbatim quote required). This is designed to fix “empty/under-coded” cases without making the LLM the primary extractor.

### Legacy: ML-First Hybrid Pipeline

Older “hybrid-first” workflows may still exist behind feature flags, but production is moving to extraction-first stateless processing via `/api/v1/process`.

```
Note Text → ML Predicts → Classify Difficulty → Decision Gate → Final Codes
                              ↓
            HIGH_CONF: ML + Rules (fast path, no LLM)
            GRAY_ZONE: LLM as judge (ML provides hints)
            LOW_CONF:  LLM as primary coder
```

**Step-by-step:**

1. **ML Prediction**: The ML model reads the note and predicts CPT codes with confidence scores.

2. **Difficulty Classification**: Based on confidence scores, the case is classified:
   - **HIGH_CONF** (High Confidence): ML is very sure about the codes
   - **GRAY_ZONE**: ML sees multiple possibilities, needs help
   - **LOW_CONF** (Low Confidence): ML is unsure, note may be unusual

3. **Decision Gate**:
   - If HIGH_CONF and rules pass → Use ML codes directly (fast, cheap, no LLM call)
   - If GRAY_ZONE or rules fail → Ask LLM to make the final decision
   - If LOW_CONF → Let LLM be the primary coder

4. **Rules Validation**: Final codes always pass through rules engine for safety checks

This approach is **faster** (43% of cases skip LLM entirely) and **more accurate** (ML catches patterns, LLM handles edge cases).

---

## 🚀 Quick Start: The Dev Server

The easiest way to interact with the system is the development server, which provides a web UI and API documentation.

```bash
./scripts/devserver.sh
```
*Starts the server on port 8000.*

- **Web UI**: [http://localhost:8000/ui/](http://localhost:8000/ui/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- The devserver sources `.env`. If you change `.env`, restart the devserver.
- Keep secrets (e.g., `OPENAI_API_KEY`) out of version control; prefer shell env vars or an untracked local `.env`.
- To use the current granular NER model, set `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner` (in `.env` or your shell).
  Example (shell): `export GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner`
  Example (`.env`): `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner`
- For faster responses (disable self-correction LLM calls), run with `PROCSUITE_FAST_MODE=1`.
---

## 🛠 CLI Tools

The suite includes several command-line scripts for batch processing and validation.

### 1. Validate Registry Extraction
Run the extraction pipeline on synthetic notes and compare against ground truth.

```bash
make validate-registry
```
*Output*: `reports/registry_validation_output.txt` and `data/registry_errors.jsonl`

### 2. Evaluate CPT Coder
Test the CPT coding engine against the training dataset.

```bash
python scripts/evaluate_cpt.py
```
*Output*: Accuracy metrics and error logs in `data/cpt_errors.jsonl`.

### 3. Self-Correction (LLM)
Ask the LLM to analyze specific registry fields or errors and suggest improvements.

```bash
# Analyze errors for a specific field
make self-correct-registry FIELD=sedation_type
```
*Output*: `reports/registry_self_correction_sedation_type.md`

### 3b. Smoke Test (Registry Extraction + Self-Correction Diagnostics)

Use these scripts to quickly sanity-check extraction behavior and see why self-correction did or did not apply.

#### Single Note Smoke Test

Test a single note file:

```bash
# Basic usage
python scripts/registry_pipeline_smoke.py --note <note.txt>

# With self-correction enabled
python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct

# With real LLM calls enabled (OpenAI)
python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct --real-llm

# With inline text (no file needed)
python scripts/registry_pipeline_smoke.py --text "Procedure: EBUS bronchoscopy..."
```

**Output shows:**
- Performed flags from `extract_record()`
- Flags added by deterministic uplift
- Extract warnings
- Omission warnings
- Self-correction diagnostics (if `--self-correct` flag is used)

#### Batch Smoke Test

Test multiple random notes from a directory:

```bash
# Basic usage (30 random notes, default output file)
python scripts/registry_pipeline_smoke_batch.py

# Custom number of notes
python scripts/registry_pipeline_smoke_batch.py --count 50

# Specify output file
python scripts/registry_pipeline_smoke_batch.py --output my_results.txt

# Use a random seed for reproducibility
python scripts/registry_pipeline_smoke_batch.py --seed 42

# Enable self-correction testing
python scripts/registry_pipeline_smoke_batch.py --self-correct

# Custom notes directory (default: data/knowledge/patient_note_texts)
python scripts/registry_pipeline_smoke_batch.py --notes-dir path/to/notes

python scripts/registry_pipeline_smoke_batch.py --output my_results.txt --self-correct --real-llm
python scripts/registry_pipeline_smoke_batch.py --output my_results_V2.txt --self-correct --real-llm

python scripts/registry_pipeline_smoke_batch.py \
  --notes-dir "data/granular annotations/Additional_notes" \
  --count 96 \
  --output my_results.txt \
  --self-correct \
  --real-llm
```

**Output file format:**
- Header with test metadata
- For each note:
  - Note ID
  - Performed flags (before/after uplift)
  - Extract warnings
  - Omission warnings
  - Self-correction diagnostics (if enabled)
- Summary with success/failure counts

**What to look for in the output:**
- `Audit high-conf omissions:` indicates RAW-ML thinks something high-value was missed (self-correct triggers are sourced from this list).
- `SELF_CORRECT_SKIPPED:` indicates self-correction was eligible but blocked (commonly keyword guard failures).
- `AUTO_CORRECTED:` indicates self-correction successfully applied a fix.
- Keyword gating is configured in `modules/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.

**Note:** The batch script automatically sets `REGISTRY_USE_STUB_LLM=1` and `GEMINI_OFFLINE=1` for offline testing. To test with real LLM/self-correction, ensure `REGISTRY_SELF_CORRECT_ENABLED=1` is set in your environment and pass the `--self-correct` flag.
The single-note smoke test supports `--real-llm`, which disables stub/offline defaults for that run.

#### LLM usage + cost reporting (tokens / $)

If you want your batch runs to print **LLM token usage** and an **estimated USD cost**:

- **Enable per-call logging**: `OPENAI_LOG_USAGE_PER_CALL=1`
- **Enable end-of-run summary**: `OPENAI_LOG_USAGE_SUMMARY=1`
- **Configure pricing** (so `$` can be estimated): `OPENAI_PRICING_JSON=...`

Example (bash):

```bash
export OPENAI_PRICING_JSON='{"gpt-5-mini":{"input_per_1k":0.00025,"output_per_1k":0.00200},"gpt-5.2":{"input_per_1k":0.00175,"output_per_1k":0.01400}}'
OPENAI_LOG_USAGE_PER_CALL=1 OPENAI_LOG_USAGE_SUMMARY=1 \
python scripts/registry_pipeline_smoke_batch.py --output my_results.txt --self-correct --real-llm
or
export OPENAI_PRICING_JSON='{"gpt-5-mini":{"input_per_1k":0.00025,"output_per_1k":0.00200},"gpt-5.2":{"input_per_1k":0.00175,"output_per_1k":0.01400}}'
OPENAI_LOG_USAGE_PER_CALL=1 OPENAI_LOG_USAGE_SUMMARY=1 \
python scripts/unified_pipeline_batch.py --output my_results.txt --real-llm
```

Notes:
- `OPENAI_PRICING_JSON` must be set **once** (include multiple models in a single JSON object).
- Cost reporting currently applies to **OpenAI-compatible** calls (`LLM_PROVIDER=openai_compat`). If pricing is not configured, tokens/latency still print and cost will show as “pricing not configured”.

### 3c. Unified Pipeline Batch Test

Test the full unified pipeline (same as the UI at `/ui/`) on multiple random notes:

```bash
# Basic usage (10 random notes from notes_text directory, default output file)
python scripts/unified_pipeline_batch.py

# Custom number of notes
python scripts/unified_pipeline_batch.py --count 20

# Specify output file
python scripts/unified_pipeline_batch.py --output my_results.txt

# Use a random seed for reproducibility
python scripts/unified_pipeline_batch.py --seed 42

# Exclude financials or evidence
python scripts/unified_pipeline_batch.py --no-financials --no-explain

# Custom notes directory (default: data/granular annotations/notes_text)
python scripts/unified_pipeline_batch.py --notes-dir path/to/notes

# With real LLM calls enabled
python scripts/unified_pipeline_batch.py --output my_results.txt --real-llm

# Check which provider is configured
python -c "import os; print('LLM_PROVIDER:', os.getenv('LLM_PROVIDER', 'gemini (default)'))"

# Check if API keys are set (without showing values)
python -c "import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"

python scripts/unified_pipeline_batch.py \
  --notes-dir "data/granular annotations/Additional_notes" \
  --count 20 \
  --output my_results.txt \
  --real-llm
```

**Output file format:**
- Header with test metadata
- For each note:
  - Note ID
  - Full note text
  - Complete JSON results (same format as `/api/v1/process` endpoint):
    - `registry`: Extracted registry fields
    - `evidence`: Evidence spans with confidence scores
    - `cpt_codes`: Derived CPT codes
    - `suggestions`: Code suggestions with confidence and rationale
    - `total_work_rvu`: Total work RVU
    - `estimated_payment`: Estimated payment
    - `per_code_billing`: Per-code RVU and payment breakdown
    - `audit_warnings`: Warnings and self-correction messages
    - `review_status`: Review status
    - `processing_time_ms`: Processing time
- Summary with success/failure counts

**This script:**
- Uses the same pipeline as the UI (`/api/v1/process` endpoint)
- Includes PHI redaction (same as UI)
- Processes notes from `.txt` files in the notes directory
- Automatically sets `REGISTRY_USE_STUB_LLM=1` and `GEMINI_OFFLINE=1` for offline testing
- Returns the complete unified response with registry, CPT codes, financials, and evidence

**Use cases:**
- Testing extraction quality on a random sample of notes
- Generating example outputs for documentation
- Validating pipeline behavior after code changes
- Comparing results across different configurations

### 4. Clean & Normalize Registry
Run the full cleaning pipeline (Schema Norm -> CPT Logic -> Consistency -> Clinical QC) on a raw dataset.

```bash
python scripts/clean_ip_registry.py \
  --registry-data data/samples/my_registry_dump.jsonl \
  --output-json reports/cleaned_registry_data.json \
  --issues-log reports/issues_log.csv
```

### 5. Generate LLM “repo context” docs (gitingest)
When you want to share repo context with an LLM, use the gitingest generator to produce:

- `gitingest.md`: a **lightweight**, curated repo snapshot (structure + a few key files)
- `gitingest_details.md`: an **optional** second document with more granular, **text-only** code/docs

```bash
# Base (light) doc only
python scripts/generate_gitingest.py

# Generate both base + details
python scripts/generate_gitingest.py --details

# Details only (no base)
python scripts/generate_gitingest.py --no-base --details
```

#### Details document controls
The details doc is designed to stay readable and safe for LLM ingestion:
- Skips common large/binary/unreadable files (best-effort)
- Enforces a per-file size cap
- Can avoid minified JS/TS bundles

```bash
# Include only specific folders (repeatable), cap size and inline count
python scripts/generate_gitingest.py --details \
  --details-include scripts/ \
  --details-include modules/registry/ \
  --details-max-bytes 200000 \
  --details-max-files 75 \
  --details-inline curated
```

---

## 🔌 API Usage

You can interact with the system programmatically via the REST API.

### Machine Extraction Endpoint (Stateless)
**POST** `/api/v1/process`

This is the production extraction engine. It expects **already scrubbed** text and
returns structured registry data plus derived CPT codes. When
`CODER_REQUIRE_PHI_REVIEW=true`, the response includes
`review_status="pending_phi_review"` and `needs_manual_review=true`.

If `REGISTRY_SELF_CORRECT_ENABLED=1`, the server may call an external LLM on **scrubbed text**
as a judge to propose and apply small JSON patches when high-confidence omissions are detected.

Evidence is returned in a UI-friendly V3 shape:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`.

Input:
```json
{
  "note": "Scrubbed procedure note text...",
  "already_scrubbed": true,
  "include_financials": true,
  "explain": true
}
```

Output (excerpt):
```json
{
  "registry": { "...": "..." },
  "cpt_codes": ["31654"],
  "audit_warnings": ["SILENT_FAILURE: ..."],
  "review_status": "pending_phi_review",
  "needs_manual_review": true
}
```

### CPT Coding Endpoint
**POST** `/v1/coder/run` (legacy; returns 410 unless `PROCSUITE_ALLOW_LEGACY_ENDPOINTS=1`)

Input:
```json
{
  "note": "Bronchoscopy with EBUS at station 7.",
  "locality": "00",
  "setting": "facility"
}
```

Output:
```json
{
  "codes": [
    {
      "cpt": "31652",
      "description": "Bronchoscopy w/ EBUS 1-2 stations",
      "confidence": 0.95
    }
  ],
  "financials": {
    "total_work_rvu": 4.46
  }
}
```

### Registry Extraction Endpoint
**POST** `/v1/registry/run` (legacy; returns 410 unless `PROCSUITE_ALLOW_LEGACY_ENDPOINTS=1`)

Input:
```json
{
  "note": "Patient is a 65yo male..."
}
```

Optional mode override:
```json
{
  "note": "Patient is a 65yo male...",
  "mode": "parallel_ner"
}
```

Output:
```json
{
  "record": {
    "patient_age": 65,
    "gender": "M",
    "cpt_codes": [...]
  }
}
```

---

## Parallel Pathway Configuration

Use the parallel NER+ML pathway globally by setting these environment flags:

- `PROCSUITE_PIPELINE_MODE=extraction_first`
- `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
- `REGISTRY_SCHEMA_VERSION=v3` (recommended; required in production)
- `MODEL_BACKEND=auto` (or `pytorch`)

Example:
```bash
PROCSUITE_PIPELINE_MODE=extraction_first \
REGISTRY_EXTRACTION_ENGINE=parallel_ner \
REGISTRY_SCHEMA_VERSION=v3 \
MODEL_BACKEND=auto \
./scripts/devserver.sh
```

Note: `MODEL_BACKEND=onnx` (the devserver default) may skip the registry ML classifier if ONNX artifacts are missing.

---

## 📊 Key Files

- **`data/knowledge/ip_coding_billing_v3_0.json`**: The "Brain". Contains all CPT codes, RVUs, and bundling rules.
- **`schemas/IP_Registry.json`**: The "Law". Defines the valid structure for registry data.
- **`reports/`**: Where output logs and validation summaries are saved.

---

## 🖥️ Using the Web UI (Unicorn Frontend)

The Web UI provides a simple interface for coding procedure notes.

### Basic Usage

1. **Start the server**: `./scripts/devserver.sh`
2. **Open the UI**: Navigate to [http://localhost:8000/ui/](http://localhost:8000/ui/)
3. **Select "Unified" tab** (recommended; production-style flow)
4. **Paste your procedure note** into the text area
5. **Configure options**:
   - **Include financials**: Adds RVU/payment estimates
   - **Explain**: Returns evidence spans for UI display/debugging
6. **Click "Run Processing"**

### Understanding the Results

In **Unified** mode, the UI runs the PHI workflow and then calls `POST /api/v1/process` with `already_scrubbed=true`.
You’ll see:

- **Pipeline metadata**: `pipeline_mode`, `review_status`, `needs_manual_review`
- **Audit warnings**: includes degraded-mode warnings like `SILENT_FAILURE:` and `DETERMINISTIC_UPLIFT:`
- **Evidence**: V3 evidence objects with `source/text/span/confidence`

- **Billing Codes**: The final CPT codes with descriptions

- **RVU & Payment**: Work RVUs and estimated Medicare payment

---

## 🧠 Model Improvement

This section covers supported workflows for improving the repo’s ML models.

### ✅ Registry Procedure Classifier (Prodigy “Diamond Loop”)

This repo supports a human-in-the-loop loop for the **registry multi-label procedure classifier** using Prodigy’s `textcat` UI (multi-label `cats`) and disagreement sampling.

References:
- `docs/REGISTRY_PRODIGY_WORKFLOW.md` (the detailed “Diamond Loop” spec)
- `docs/MAKEFILE_COMMANDS.md` (Makefile target reference)

#### 0) One-time sanity check (do this first)

```bash
make lint
make typecheck
make test
```

#### 1) Build (or rebuild) your registry CSV splits

Run the recommended “final” prep (PHI-scrubbed) to produce the standard train/val/test CSVs:

```bash
make registry-prep-final

# If you need the raw (non-scrubbed) corpus for debugging:
# make registry-prep-raw
```

You should now have:
- `data/ml_training/registry_train.csv`
- `data/ml_training/registry_val.csv`
- `data/ml_training/registry_test.csv`

#### 2) Train a baseline model (1 epoch smoke test)

This confirms your training pipeline + artifacts are good.

```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 1
```

After it finishes, verify these exist:
- `data/models/roberta_registry/thresholds.json`
- `data/models/roberta_registry/label_order.json`

If you’re deciding “local CUDA vs VM”, check now:

```bash
python -c "import torch; print('cuda:', torch.cuda.is_available()); print('mps:', hasattr(torch.backends,'mps') and torch.backends.mps.is_available())"
```

- If **cuda: True** → keep going locally (fast iteration).
- If **cuda: False** and you’re on CPU/MPS → fine for a 1-epoch smoke test, but for real runs (3–5 epochs + repeated loops) a GPU VM will feel much better.

#### 3) Create (or confirm) your unlabeled notes file for Prodigy

Prodigy prep expects a JSONL where each line includes `note_text` (or `text` / `note`).

Default path used by the make targets:
- `data/ml_training/registry_unlabeled_notes.jsonl`

If you already have it, skip this.

#### 4) Prepare a Prodigy batch (disagreement sampling + pre-checked labels)

This generates:
- `data/ml_training/registry_prodigy_batch.jsonl`
- `data/ml_training/registry_prodigy_manifest.json`

```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl \
  REG_PRODIGY_COUNT=200
```

##### Annotating a specific JSONL file (example)

If you want to annotate a targeted file, override `REG_PRODIGY_INPUT_FILE` and give the dataset a descriptive name:

```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_trach_peg.jsonl \
  REG_PRODIGY_COUNT=150

make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_trach_peg_v1
```

#### 5) Annotate in Prodigy (checkbox UI)

```bash
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_v1
```

Notes:
- The annotation UI is served at `http://localhost:8080` (Prodigy’s default).
- This workflow uses **`textcat.manual`** (multi-label checkboxes via `cats`), not NER. If you see “Using 32 label(s): …” you’re in the right place.

##### Working across machines (Google Drive sync — safe “export/import”)

Do **not** cloud-sync the raw Prodigy SQLite DB file (risk of corruption). Instead, sync by exporting/importing a JSONL snapshot to a shared Google Drive folder.

Pick a single “source of truth” folder in Google Drive, e.g. `proc_suite_sync/`, and keep these inside it:
- `prodigy/registry_v1.prodigy.jsonl` (the Prodigy dataset snapshot)
- `diamond_loop/registry_prodigy_manifest.json` (recommended: avoids re-sampling across machines)
- `diamond_loop/registry_unlabeled_notes.jsonl` (recommended: consistent sampling universe)

###### Recommended: one-command Diamond Loop sync

Use `scripts/diamond_loop_cloud_sync.py` to sync the dataset snapshot + key Diamond Loop files.

**WSL + Google Drive on Windows `G:` (your setup):**

```bash
# Pull latest from Drive before annotating on this machine
python scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync" \
  --reset

# Push back to Drive after finishing a session
python scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync"
```

**macOS (Drive path varies by install):**

```bash
python scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync" \
  --reset

python scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync"
```

Optional flags:
- Add `--include-batch` to also sync `data/ml_training/registry_prodigy_batch.jsonl` (resume the exact same batch on another machine)
- Add `--include-human` to also sync `data/ml_training/registry_human.csv`

###### Manual fallback: dataset-only export/import

If you prefer to sync just the Prodigy dataset snapshot file, you can use `scripts/prodigy_cloud_sync.py` directly.

**Before you start annotating on a machine** (pull latest from Drive):

```bash
python scripts/prodigy_cloud_sync.py import \
  --dataset registry_v1 \
  --in "/path/to/GoogleDrive/proc_suite_sync/prodigy/registry_v1.prodigy.jsonl" \
  --reset
```

**After you finish a session** (push to Drive):

```bash
python scripts/prodigy_cloud_sync.py export \
  --dataset registry_v1 \
  --out "/path/to/GoogleDrive/proc_suite_sync/prodigy/registry_v1.prodigy.jsonl"
```

Rules:
- Only annotate on **one machine at a time**.
- Always **export after** you finish a session, and **import before** you start on another machine.
- If you rely on avoiding re-sampling, also keep `data/ml_training/registry_prodigy_manifest.json` synced alongside the dataset snapshot.

Annotate as many as you can tolerate in one sitting (even 50 is enough for the first iteration).

If you need to restart cleanly (wrong batch, wrong dataset, switching strategies), reset the dataset + batch/manifest:

```bash
make registry-prodigy-reset REG_PRODIGY_DATASET=registry_v1
```

#### 6) Export Prodigy annotations → a human labels CSV

Important:
- Export reads **everything currently in the Prodigy dataset** and writes a fresh CSV.
- The export **overwrites** the output path you provide (it does not append to an existing CSV file).

```bash
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

#### 7) (Recommended) Keep a single “master” human CSV across iterations

If you want to retain prior human labels while adding new annotation sessions/batches, use an “updates” file and merge it into your master:

```bash
# Export current dataset snapshot to an "updates" file
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human_updates.csv

# Merge updates into your master file (append new encounter_ids, override overlaps)
make registry-human-merge-updates \
  REG_HUMAN_BASE_CSV=data/ml_training/registry_human.csv \
  REG_HUMAN_UPDATES_CSV=data/ml_training/registry_human_updates.csv \
  REG_HUMAN_OUT_CSV=data/ml_training/registry_human.csv
```

Notes:
- This works even if the updates contain **no overlapping** `encounter_id`s (common when you annotate a new batch).
- Merge keys on `encounter_id` (computed from `note_text` when missing).

#### 8) Merge human labels as Tier-0 and rebuild splits (no leakage)

This is critical: merge **before splitting**.

```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

#### 9) Retrain for real (3–5 epochs)

```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 5
```

#### 10) Repeat the Diamond Loop

Repeat steps **4 → 9** until disagreement rate drops and metrics plateau.

Notes:
- Canonical label schema/order is `modules/ml_coder/registry_label_schema.py`.
- Training uses `label_confidence` as a per-row loss weight when present.

### ➕ CPT Coding Model: Adding Training Cases

To improve the CPT model’s accuracy, you can add new training cases. Here's how:

#### Step 1: Prepare Your Data

Create a JSONL file with your cases. Each line should be a JSON object with:

```json
{
  "note": "Your procedure note text here...",
  "cpt_codes": ["31622", "31628"],
  "dataset": "my_new_cases"
}
```

**Required fields:**
- `note`: The full procedure note text
- `cpt_codes`: List of correct CPT codes for this note

**Optional fields:**
- `dataset`: A label for grouping (e.g., "bronchoscopy", "pleural")
- `procedure_type`: The type of procedure (auto-detected if not provided)

#### Step 2: Add Cases to Training Data

Place your JSONL file in the training data directory:

```bash
# Copy your cases to the training data folder
cp my_new_cases.jsonl data/training/
```

#### Step 3: Validate Your Cases

Before training, validate that your cases are properly formatted:

```bash
python scripts/validate_training_data.py data/training/my_new_cases.jsonl
```

#### Step 4: Retrain the Model (Optional)

If you have enough new cases (50+), you can retrain the ML model:

```bash
# Run the training pipeline
python scripts/train_ml_coder.py --include data/training/my_new_cases.jsonl
```

#### Tips for Good Training Data

1. **Diverse examples**: Include various procedure types and complexity levels
2. **Accurate labels**: Double-check the CPT codes are correct
3. **Representative notes**: Use real-world note formats and writing styles
4. **Edge cases**: Include tricky cases where coding is non-obvious
5. **Clean text**: Remove any PHI (patient identifying information)

---

## 🔍 Reviewing Errors

When the system makes mistakes, you can review them to improve future performance.

### Run the Error Review Script

```bash
# Review all errors
python scripts/review_llm_fallback_errors.py --mode all

# Review only fast path errors (ML+Rules mistakes)
python scripts/review_llm_fallback_errors.py --mode fastpath

# Review only LLM fallback errors
python scripts/review_llm_fallback_errors.py --mode llm_fallback
```

This generates a markdown report in `data/eval_results/` with:
- Error patterns and common mistakes
- Per-case review with recommendations
- Codes that were incorrectly predicted or missed

### Using Error Analysis to Improve the System

1. **False Positives** (codes predicted but shouldn't be):
   - May need to add negative rules to the rules engine
   - May need more training examples without these codes

2. **False Negatives** (codes missed):
   - May need to add new keyword patterns
   - May need more training examples with these codes

3. **ML was correct but LLM overrode it**:
   - Consider adjusting confidence thresholds
   - May need to improve LLM prompt constraints

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |
| `CODER_REQUIRE_PHI_REVIEW` | Require PHI review before coding | `false` |
| `DEMO_MODE` | Enable demo mode (synthetic data only) | `false` |

### OpenAI Configuration

When using an OpenAI-compatible backend (`LLM_PROVIDER=openai_compat`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key for OpenAI | Required |
| `OPENAI_MODEL` | Model name (e.g., `gpt-4o`) | Required |
| `OPENAI_BASE_URL` | Base URL (no `/v1` suffix) | `https://api.openai.com` |
| `OPENAI_PRIMARY_API` | API path: `responses` or `chat` | `responses` |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat on 404 | `1` |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Registry task timeout (seconds) | `180` |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Default task timeout (seconds) | `60` |

**Note**: The system uses OpenAI's Responses API by default. For endpoints that don't support it, use `OPENAI_PRIMARY_API=chat`.

### Adjusting ML Thresholds

The ML model's confidence thresholds can be tuned in `modules/ml_coder/thresholds.py`:

```python
# High confidence threshold (codes above this are HIGH_CONF)
HIGH_CONF_THRESHOLD = 0.80

# Gray zone lower bound (codes between this and HIGH_CONF are GRAY_ZONE)
GRAY_ZONE_THRESHOLD = 0.45

# Codes below GRAY_ZONE_THRESHOLD are LOW_CONF
```

Higher thresholds = more cases go to LLM (safer but slower)
Lower thresholds = more cases use fast path (faster but may miss edge cases)

---

## 🛡️ PHI Redaction & Training

The Procedure Suite includes tools for training and improving PHI (Protected Health Information) redaction models.

### PHI Audit

Audit a note for PHI detection:

```bash
python scripts/phi_audit.py --note-path test_redact.txt
```

### Scrubbing Golden JSON Files

Scrub PHI from golden extraction files:

```bash
python scripts/scrub_golden_jsons.py \
  --input-dir data/knowledge/golden_extractions \
  --pattern 'golden_*.json' \
  --report-path artifacts/redactions.jsonl
```

### Platinum Redaction Pipeline (Golden → Scrubbed/Final)

For registry ML training data, use the **Platinum** workflow (hybrid redactor → character spans → applied redactions).

**Key behavior:**
- Scrubs both `note_text` **and** `registry_entry.evidence` to prevent PHI leakage
- Standardizes all PHI placeholders to the single token: `[REDACTED]`
- Does **not** redact physician/provider names (e.g., `Dr. Stevens`)

**Run the pipeline (recommended):**
```bash
make platinum-final
```
This produces:
- `data/knowledge/golden_extractions_scrubbed/` (PHI-scrubbed)
- `data/knowledge/golden_extractions_final/` (scrubbed + institution cleanup)

**Or run step-by-step:**
```bash
make platinum-build      # data/ml_training/phi_platinum_spans.jsonl
make platinum-sanitize   # data/ml_training/phi_platinum_spans_CLEANED.jsonl
make platinum-apply      # data/knowledge/golden_extractions_scrubbed/
python scripts/fix_registry_hallucinations.py \
  --input-dir data/knowledge/golden_extractions_scrubbed \
  --output-dir data/knowledge/golden_extractions_final
```

**Optional: align synthetic names before building spans**
```bash
python scripts/align_synthetic_names.py \
  --input-dir data/knowledge/golden_extractions \
  --output-dir data/knowledge/golden_extractions_aligned
```
If you use the aligned directory, point the pipeline at it:
```bash
PLATINUM_INPUT_DIR=data/knowledge/golden_extractions_aligned make platinum-cycle
```

### PHI Model Training with Prodigy

Use Prodigy for iterative PHI model improvement:

**Workflow:**
```bash
make prodigy-prepare      # Sample new notes for annotation
make prodigy-annotate     # Annotate in Prodigy UI
make prodigy-export       # Export corrections to training format
make prodigy-finetune     # Fine-tune model (recommended)
```

**Training Options:**

| Command | Description |
|---------|-------------|
| `make prodigy-finetune` | Fine-tunes existing model (1 epoch, low LR), preserves learned weights |
| `make prodigy-retrain` | Trains from scratch (3 epochs), loses previous training |

**Fine-tuning details:**
- `--resume-from artifacts/phi_distilbert_ner` - Starts from your trained weights
- `--epochs 1` - Just one pass over the data (override with `PRODIGY_EPOCHS=3`)
- `--lr 1e-5` - Low learning rate to avoid catastrophic forgetting
- Automatically detects and uses Metal (MPS) or CUDA when available
- Removes MPS memory limits to use full system memory

**Manual fine-tuning (same as `make prodigy-finetune`):**
```bash
python scripts/train_distilbert_ner.py \
    --resume-from artifacts/phi_distilbert_ner \
    --patched-data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
    --output-dir artifacts/phi_distilbert_ner \
    --epochs 1 \
    --lr 1e-5 \
    --train-batch 4 \
    --eval-batch 16 \
    --gradient-accumulation-steps 2 \
    --mps-high-watermark-ratio 0.0
```

### Model Locations & Exporting for UI

The PHI model exists in two locations:

1. **Training location** (PyTorch format): `artifacts/phi_distilbert_ner/`
   - Updated by `make prodigy-finetune` or `make prodigy-retrain`
   - Contains PyTorch model weights, tokenizer, and label mappings

2. **Client-side location** (ONNX format): `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/`
   - Used by the browser UI at `http://localhost:8000/ui/phi_redactor/`
   - Contains ONNX model files, tokenizer, and configuration

**Important**: After training, you must export the model to update the UI:

```bash
make export-phi-client-model
```

This converts the PyTorch model to ONNX format and copies it to the static directory. The UI will continue using the old model until you run this export step.

**Export options:**
- `make export-phi-client-model` - Exports unquantized ONNX model (default)
- `make export-phi-client-model-quant` - Exports quantized ONNX model (smaller, but may have accuracy trade-offs)

### Hard Negative Fine-tuning

Fine-tune on hard negatives (cases where the model made mistakes):

```bash
make finetune-phi-client-hardneg
```

This uses:
- `--resume-from artifacts/phi_distilbert_ner`
- `--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl`
- Memory-optimized settings for MPS/CUDA

### Gold Standard PHI Training Workflow

Train on pure human-verified data from Prodigy annotations. This workflow uses only Prodigy-verified annotations for maximum quality training.

**Complete Workflow (Step-by-Step):**

```bash
# Step 1: Export pure gold from Prodigy
make gold-export

# Step 2: Split into train/test (80/20 with note grouping)
make gold-split

# Step 3: Train on gold data (10 epochs default)
make gold-train

# Step 4: Safety audit on gold test set
make gold-audit

# Step 5: Evaluate F1 metrics on gold test set
make gold-eval

# Step 6: Export updated ONNX for browser
make export-phi-client-model
```

**Or run the full cycle (Steps 1-5) with one command:**

```bash
make gold-cycle
```

**Training Configuration:**
- **Epochs**: 10 (default, override with `GOLD_EPOCHS=15`)
- **Learning rate**: 1e-5
- **Batch size**: 4 (with gradient accumulation = 2, effective batch = 8)
- **GPU acceleration**: Automatically detects and uses Metal (MPS) or CUDA
- **Memory optimization**: Removes MPS memory limits to use full system memory on Mac

**Output Files:**
- `data/ml_training/phi_gold_standard_v1.jsonl` - Exported gold data
- `data/ml_training/phi_train_gold.jsonl` - Training split (80%)
- `data/ml_training/phi_test_gold.jsonl` - Test split (20%)
- `artifacts/phi_distilbert_ner/audit_gold_report.json` - Safety audit report

**When to use:**
- When you have a sufficient amount of Prodigy-verified annotations
- For maximum quality training on human-verified data
- When you want to train for more epochs on smaller, high-quality datasets

### Testing PHI Redaction

Test the client-side PHI redactor:

```bash
cd scripts/phi_test_node
node test_phi_redaction.mjs --count 30
```

### Server Configuration for PHI

Start the dev server with different model backends:

```bash
# Use PyTorch backend (for PHI without registry ONNX)
MODEL_BACKEND=pytorch ./scripts/devserver.sh

# Auto-detect best backend
MODEL_BACKEND=auto ./scripts/devserver.sh
```
http://localhost:8000/ui/phi_redactor/
---

## 📞 Getting Help

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Technical Issues**: Check the logs in `logs/` directory
- **Questions**: Open an issue on the repository

---

## 🏷️ Registry NER training (granular)

Use this workflow to retrain the **granular registry NER** model with the **BiomedBERT** tokenizer/model.

### Step 1) Regenerate BIO training data (crucial)
This rebuilds `ner_bio_format.jsonl` using the target tokenizer. Do this any time you change the base model/tokenizer.

```bash
python scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.jsonl \
  --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext \
  --max-length 512
```

### Step 2) Train the model
Note: the training script uses **hyphenated** flags like `--output-dir`, `--train-batch`, and the learning rate flag is `--lr`.

```bash
python scripts/train_registry_ner.py \
  --data data/ml_training/granular_ner/ner_bio_format.jsonl \
  --output-dir artifacts/registry_biomedbert_ner \
  --epochs 20 \
  --lr 2e-5 \
  --train-batch 16 \
  --eval-batch 16
```

---

*Last updated: January 2026*
run all granular python updates:
python scripts/run_python_update_scripts.py

```

---
### `.claude/commands/phi-redactor.md`
```
# PHI Redactor Development Skill

Use this skill when working on the PHI (Protected Health Information) redaction pipeline, including the client-side UI, veto layer, ML model, or training data.

## Architecture Overview

The PHI redactor is a **hybrid client-side detection system** combining:
1. **ML Detection** (DistilBERT via Transformers.js) - Probabilistic PHI detection
2. **Regex Detection** - Deterministic header/pattern matching
3. **Veto Layer** - Post-processing filter to prevent false positives

**Detection Mode:** Union (default) - Both ML and regex run, results combined, overlaps resolved after veto.

```
Input Text
    ↓
[Windowed Processing: 2500 chars, 250 overlap]
    ↓
ML NER (DistilBERT) + Regex Patterns  ← Union mode: both run
    ↓
Combine Results (dedupeSpans)
    ↓
Expand to Word Boundaries
    ↓
Apply Veto Layer (protectedVeto.js)
    ↓
Final Overlap Resolution
    ↓
Final Detections (red highlighting)
    ↓
Manual Additions (amber highlighting) ← User selects text + clicks "Add"
    ↓
Apply Redactions → [REDACTED] placeholders
    ↓
Submit to Server → Formatted Results Display
```

## Key Files

### Client-Side UI (Browser)
| File | Purpose |
|------|---------|
| `modules/api/static/phi_redactor/redactor.worker.js` | Web Worker: ML inference + regex detection (union mode) |
| `modules/api/static/phi_redactor/protectedVeto.js` | Veto/allow-list layer (prevents false positives) |
| `modules/api/static/phi_redactor/app.js` | Main UI application (Monaco editor integration) |
| `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/` | ONNX model bundle |
| `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json` | Protected clinical terms config |

### Server-Side (Python)
| File | Purpose |
|------|---------|
| `modules/phi/adapters/phi_redactor_hybrid.py` | Server-side hybrid redactor |
| `modules/phi/adapters/presidio_scrubber.py` | Presidio-based scrubber |

### Training Pipeline
| File | Purpose |
|------|---------|
| `scripts/distill_phi_labels.py` | Silver: Piiranha → BIO token distillation |
| `scripts/sanitize_dataset.py` | Clean false positives from training data |
| `scripts/normalize_phi_labels.py` | Map labels to standard schema |
| `scripts/train_distilbert_ner.py` | Train DistilBERT NER model |
| `scripts/export_phi_model_for_transformersjs.py` | Export ONNX for browser |
| `scripts/audit_model_fp.py` | Audit for false positive violations |
| `scripts/prodigy_prepare_phi_batch.py` | Prodigy: Pre-annotate notes with DistilBERT |
| `scripts/prodigy_export_corrections.py` | Prodigy: Export corrections to BIO format |
| `scripts/export_phi_gold_standard.py` | Gold: Export pure Prodigy annotations |
| `scripts/split_phi_gold.py` | Gold: Train/test split with note grouping |

### Training Data
| Location | Purpose |
|----------|---------|
| `data/ml_training/phi_gold_standard_v1.jsonl` | **Gold Standard**: Pure Prodigy exports |
| `data/ml_training/phi_train_gold.jsonl` | Gold training set (80% of notes) |
| `data/ml_training/phi_test_gold.jsonl` | Gold test set (20% of notes) |
| `data/ml_training/ARCHIVE_distilled_phi_raw.jsonl` | Old mixed data (archived) |
| `data/ml_training/distilled_phi_labels.jsonl` | Raw Piiranha output |
| `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl` | Normalized silver data |
| `data/ml_training/prodigy_batch.jsonl` | Current Prodigy annotation batch |
| `data/ml_training/prodigy_manifest.json` | Tracks annotated windows |
| `synthetic_phi.jsonl` | Dense synthetic PHI data |

## PHI Label Schema

| Label | Description | Examples |
|-------|-------------|----------|
| PATIENT | Patient names | "John Smith", "Mrs. Jones" |
| DATE | Dates, DOB | "01/15/2024", "Jan 15" |
| ID | MRN, SSN, IDs | "MRN: 12345", "123-45-6789" |
| GEO | Addresses, locations | "New York", "123 Main St" |
| CONTACT | Phone, email | "555-123-4567" |
| O | Not PHI | (background) |

## Common Tasks

### 1. Fix False Positives (Over-Redaction)
Clinical terms being incorrectly redacted.

**Quick Fix (Veto Layer):**
Edit `protectedVeto.js`:
- Add to `STOPWORDS_ALWAYS` for single words
- Add to `CLINICAL_ALLOW_LIST` for clinical terms
- Add regex pattern for structured patterns (device models, durations)

**Example:**
```javascript
// In STOPWORDS_ALWAYS - add clinical verbs
"intubated", "identified", "placed", "transferred"

// In CLINICAL_ALLOW_LIST - add abbreviations
"ip", "d/c", "medical thoracoscopy"
```

### 2. Fix False Negatives (PHI Leaking)
Patient names or IDs not being detected.

**Quick Fix (Regex):**
Edit `redactor.worker.js`:
- Add new regex pattern for the pattern type
- Update `runRegexDetectors()` to process it
- Include provider exclusion logic if name-like

**Example:**
```javascript
const INLINE_PATIENT_NAME_RE = /\b([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:a\s+)?\d+-year-old/gi;
```

### 3. Gold Standard Training (RECOMMENDED)
Pure human-verified Prodigy annotations for highest quality.

```bash
# Full gold workflow (initial training or major updates)
make gold-export      # Export from Prodigy dataset
make gold-split       # 80/20 train/test split with note grouping
make gold-train       # Train with 10 epochs
make gold-audit       # Safety audit on test set
make gold-eval        # Evaluate F1 metrics

# Or run full cycle:
make gold-cycle

# Export to browser
make export-phi-client-model
```

**Key Files:**
- `phi_gold_standard_v1.jsonl` - Full gold export
- `phi_train_gold.jsonl` - Training set (80% of notes)
- `phi_test_gold.jsonl` - Test set (20% of notes)

### 4. Adding More Training Data (Incremental)
When you have new notes to add to gold training data.

```bash
# 1. Prepare new notes for Prodigy
make prodigy-prepare-file PRODIGY_INPUT_FILE=new_notes.jsonl PRODIGY_COUNT=50

# 2. Annotate in Prodigy UI
make prodigy-annotate

# 3. Incremental update (lighter than full train)
make gold-incremental   # export → split → finetune(3 epochs) → audit

# Or step-by-step:
make gold-export        # Re-export ALL gold (old + new)
make gold-split         # Re-split expanded dataset
make gold-finetune      # Light fine-tune (3 epochs, 5e-6 LR)
make gold-audit         # Verify safety

# Export to browser
make export-phi-client-model
```

**Override fine-tune epochs:**
```bash
make gold-finetune GOLD_FINETUNE_EPOCHS=5
```

### 5. Legacy Silver Training (From Scratch)
When starting fresh from Piiranha distillation.

```bash
# 1. Distill new training data
make distill-phi-silver

# 2. Sanitize (remove false positives)
make sanitize-phi-silver

# 3. Normalize labels
make normalize-phi-silver

# 4. Train
python scripts/train_distilbert_ner.py --epochs 3

# 5. Evaluate & audit
make eval-phi-client
make audit-phi-client

# 6. Export to ONNX
make export-phi-client-model
```

### 6. Prodigy Annotation Workflow
Human-in-the-loop using [Prodigy](https://prodi.gy/).

```bash
# Option A: From golden notes (random sample)
make prodigy-prepare PRODIGY_COUNT=100

# Option B: From specific file
make prodigy-prepare-file PRODIGY_INPUT_FILE=synthetic_phi.jsonl

# Launch Prodigy UI (opens at http://localhost:8080)
make prodigy-annotate

# After annotation, use gold workflow
make gold-export
make gold-split
make gold-finetune  # or gold-train for full training
```

**Prodigy Tips:**
- Prodigy runs in system Python 3.12 (not conda)
- Drop dataset to re-annotate: `prodigy drop phi_corrections`
- Check stats: `prodigy stats phi_corrections`

### 7. Update Protected Terms Config
Edit `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json`:
- `anatomy_terms`: Anatomical terms to protect
- `device_manufacturers`: Company names that look like person names
- `protected_device_names`: Device names to protect
- `station_markers`: LN station context words
- `code_markers`: CPT/billing context words

## Makefile Quick Reference

| Target | Description |
|--------|-------------|
| `gold-export` | Export pure gold from Prodigy |
| `gold-split` | 80/20 split with note grouping |
| `gold-train` | Full training (10 epochs, 1e-5 LR) |
| `gold-finetune` | Light fine-tune (3 epochs, 5e-6 LR) |
| `gold-audit` | Safety audit on gold test |
| `gold-eval` | Evaluate metrics on gold test |
| `gold-cycle` | Full: export → split → train → audit → eval |
| `gold-incremental` | Incremental: export → split → finetune → audit |
| `prodigy-prepare` | Prepare batch from golden folder |
| `prodigy-prepare-file` | Prepare batch from specific file |
| `prodigy-annotate` | Launch Prodigy UI |
| `audit-phi-client` | Audit on silver data |
| `export-phi-client-model` | Export ONNX for browser |

## Debugging

### Console Logging
Enable debug mode in the UI:
```javascript
// In app.js WORKER_CONFIG or via URL ?debug=1
const WORKER_CONFIG = {
  debug: true,  // Enables console logging
  aiThreshold: 0.45,
  forceUnquantized: true,
  mergeMode: "union",  // default: both ML + regex
};
```

### Check Detection Sources
With debug enabled:
```
[PHI] mergeMode: union
[PHI] mlSpans: X  regexSpans: Y
[PHI] afterVeto: Z
```

### Check Veto Reasons
```
[VETO] reason "text" (LABEL score=0.xx)
```

Common veto reasons:
- `stopword` - Word in STOPWORDS_ALWAYS
- `anatomy_list` - In IP_SPECIFIC_ANATOMY
- `clinical_allow_list` - In CLINICAL_ALLOW_LIST
- `provider_role_or_credential` - Detected as provider name
- `device_model_number` - Matches device model pattern
- `passive_voice_verb` - Preceded by "was/were"

### Model Output Issues
If model returns 0 detections:
1. Check `[PHI] raw spans count: X` in console
2. If 0, model may have cold-start issue
3. Regex patterns should still catch header PHI (union mode)
4. Try refreshing the page (re-initializes model)

## Testing

```bash
# Audit for must-not-redact violations (gold test set)
make gold-audit

# Audit on silver data
make audit-phi-client

# Evaluate metrics
make gold-eval
```

## Manual Redaction Feature

Users can add redactions for PHI missed by auto-detection:

1. **Select text** in the Monaco editor
2. **Choose entity type** from dropdown:
   - Patient Name (default)
   - MRN / ID
   - Date
   - Phone
   - Location
   - Other
3. **Click "Add" button**

### Visual Distinction
| Source | Highlighting | Sidebar Tag |
|--------|--------------|-------------|
| Auto-detected (ML/Regex) | Red background | `ner` or `regex_*` |
| Manual addition | Amber/yellow background | `manual` |

### Key Code Locations
```javascript
// In app.js - Selection tracking
editor.onDidChangeCursorSelection((e) => {
  currentSelection = e.selection.isEmpty() ? null : e.selection;
  addRedactionBtn.disabled = !currentSelection || running;
});

// In app.js - Add button handler
addRedactionBtn.addEventListener("click", () => {
  const newDetection = {
    id: `manual_${Date.now()}_...`,
    label: entityTypeSelect.value,  // e.g., "PATIENT"
    source: "manual",
    score: 1.0,
    // ...
  };
  detections.push(newDetection);
  renderDetections();
});
```

### CSS Classes
- `.phi-detection-manual` - Amber highlighting for Monaco decorations
- `.pill.source-manual` - Amber pill styling in sidebar

---

## Formatted Results Display

After submitting a scrubbed note, the UI renders structured results:

### Status Banner
| State | Color | Condition |
|-------|-------|-----------|
| Success | Green | `needs_manual_review=false` and no `audit_warnings` |
| Warning | Yellow | `audit_warnings` array has items |
| Error | Red | `needs_manual_review=true` |

### CPT Codes Table
Displays data from `suggestions[]` and `per_code_billing[]`:
- Code, Description, Confidence %, RVU, Payment
- Totals row with `total_work_rvu` and `estimated_payment`

### Registry Summary
Recursively extracts ALL non-null fields from `registry` response:
- Nested paths: `linear_ebus.performed` → "Linear Ebus → Performed"
- Skips: `null`, `undefined`, `false`, empty arrays
- Formats: booleans → "Yes"/"No", arrays → comma-joined

### Key Functions
```javascript
renderResults(data)           // Main entry - banner, CPT, registry
renderCPTTable(data)          // CPT codes with billing lookup
renderRegistrySummary(registry)  // Recursive field extraction
```

### HTML Structure
```html
<div id="resultsContainer">
  <div id="statusBanner" class="status-banner hidden"></div>
  <div id="cptTable" class="result-section hidden">
    <h3>CPT Codes</h3>
    <table id="cptTableBody"></table>
  </div>
  <div id="registrySummary" class="result-section hidden">
    <h3>Registry Data</h3>
    <table id="registryTableBody"></table>
  </div>
  <details class="raw-json-toggle">
    <summary>View Raw JSON</summary>
    <pre id="serverResponse"></pre>
  </details>
</div>
```

---

### Smoke Test Checklist
Paste this in the UI at `/ui/phi_redactor/`:

```
Patient: John Smith, 65-year-old male
MRN: 12345678
DOB: 01/15/1960

Attending: Dr. Laura Brennan
Assistant: Dr. Miguel Santos (Fellow)

Procedure: Rigid bronchoscopy with EBUS-TBNA of stations 4R, 7, 11L.
The patient was intubated with size 8.0 ETT. Navigation performed
using Pentax EB-1990i scope. Follow-up in 1-2wks.

Pathology showed adenocarcinoma at station 7.
```

**Expected Detection:**
- REDACTED: "John Smith", "12345678", "01/15/1960"
- NOT REDACTED: "Dr. Laura Brennan", "Dr. Miguel Santos", "4R", "7", "11L", "intubated", "EB-1990i", "1-2wks", "adenocarcinoma"

**Test Manual Redaction:**
1. Select "adenocarcinoma" in the editor
2. Verify "Add" button becomes enabled
3. Select entity type "Other" from dropdown
4. Click "Add" - verify amber highlighting appears
5. Check sidebar shows detection with "manual" source

**Test Formatted Results:**
1. Click "Apply redactions"
2. Click "Submit scrubbed note"
3. Verify status banner appears (green/yellow/red)
4. Verify CPT Codes table shows codes with RVU/Payment
5. Verify Registry Data table shows extracted fields
6. Expand "View Raw JSON" to see full response

## Common Patterns to Remember

### Provider Name Detection (Keep Visible)
The veto layer protects provider names when:
- Preceded by "Dr.", "Attending:", "Proceduralist:", etc.
- Followed by credentials: ", MD", ", RN", ", PhD"
- In attribution context: "performed by", "supervised by"

### Passive Voice Pattern
"was placed", "was identified" - the veto catches these via:
1. Check if preceded by "was/were/is/are/been/being"
2. Check if span ends in -ed/-en or is in STOPWORDS_ALWAYS
3. If both true, veto (don't redact)

### Device Model Numbers
Pattern: `EB-1990i`, `BF-H190`, `CV-180`
Regex: `/^(?:EB|BF|CV|EU|GIF|...)[-\s]?[A-Z0-9]{2,10}$/i`

### Duration Patterns
Pattern: `1-2wks`, `3-5 days`, `2hrs`
Regex: `/^\d+(?:-\d+)?\s*(?:wks?|days?|hrs?|...)$/i`

## Safety Requirements

**Post-veto must-not-redact violations MUST be 0.**

The audit script checks that these are never redacted:
- CPT codes (31653, 77012) in billing context
- LN stations (4R, 7, 11L) with station context
- Anatomical terms (Left Upper Lobe, RUL)
- Device names (Monarch, ION, PleurX)
- Clinical measurements (24 French, 5 ml)

Raw model violations may be non-zero; the veto layer guarantees safety.

```

---
### `.claude/commands/registry-data-prep.md`
```
# Registry Data Prep Skill

Use this skill when working on ML training data preparation for the registry prediction model. This includes extracting labels from golden JSONs, running the 3-tier hydration pipeline, deduplication, and generating train/val/test splits.

## Architecture Overview

The registry data prep uses a **3-tier extraction with hydration** approach:

```
Golden JSON Entry
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Structured Extraction (confidence: 0.95)            │
│ extract_v2_booleans(registry_entry)                         │
│ Source: modules/registry/v2_booleans.py                     │
└─────────────────────────────────────────────────────────────┘
       │ (if all-zero)
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: CPT-Based Derivation (confidence: 0.80)             │
│ derive_booleans_from_json(entry)                            │
│ Uses: cpt_codes field from golden JSON                      │
└─────────────────────────────────────────────────────────────┘
       │ (if still all-zero)
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: Keyword Hydration (confidence: 0.60)                │
│ hydrate_labels_from_text(note_text)                         │
│ Uses: 40+ regex patterns with negation filtering            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ DEDUPLICATION: Priority-based duplicate removal             │
│ structured > cpt > keyword                                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ STRATIFIED SPLIT: 70/15/15 with encounter grouping          │
│ Uses: skmultilearn IterativeStratification                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Files

### Core Modules
| File | Purpose |
|------|---------|
| `modules/ml_coder/registry_data_prep.py` | Main data prep logic (3-tier extraction, dedup, splits) |
| `modules/ml_coder/label_hydrator.py` | 3-tier extraction + keyword hydration |
| `modules/registry/v2_booleans.py` | Canonical 30 procedure boolean fields |
| `scripts/golden_to_csv.py` | CLI interface for data prep |

### Test Files
| File | Purpose |
|------|---------|
| `tests/ml_coder/test_registry_first_data_prep.py` | Tests for data prep functions |
| `tests/ml_coder/test_label_hydrator.py` | Tests for hydration + deduplication |

### Data Locations
| Location | Purpose |
|----------|---------|
| `data/knowledge/golden_extractions_final/` | PHI-scrubbed golden JSONs (preferred) |
| `data/knowledge/golden_extractions/` | Original golden JSONs (fallback) |
| `data/ml_training/registry_train.csv` | Training set output |
| `data/ml_training/registry_val.csv` | Validation set output |
| `data/ml_training/registry_test.csv` | Test set output |
| `data/ml_training/registry_meta.json` | Extraction metadata |

## Procedure Label Schema

30 canonical procedure boolean fields:

### Bronchoscopy (23 fields)
| Field | Description |
|-------|-------------|
| `diagnostic_bronchoscopy` | Basic diagnostic bronchoscopy |
| `bal` | Bronchoalveolar lavage |
| `bronchial_wash` | Bronchial washing |
| `brushings` | Bronchial brushings |
| `endobronchial_biopsy` | Endobronchial biopsy |
| `tbna_conventional` | Conventional TBNA |
| `linear_ebus` | Linear EBUS (stations) |
| `radial_ebus` | Radial EBUS (peripheral) |
| `navigational_bronchoscopy` | Navigation bronchoscopy |
| `fiducial_placement` | Fiducial marker placement |
| `transbronchial_biopsy` | Transbronchial biopsy |
| `transbronchial_cryobiopsy` | Transbronchial cryobiopsy |
| `therapeutic_aspiration` | Therapeutic aspiration |
| `foreign_body_removal` | Foreign body removal |
| `airway_dilation` | Airway dilation |
| `airway_stent` | Airway stent placement |
| `thermal_ablation` | Thermal ablation |
| `cryotherapy` | Cryotherapy |
| `blvr` | Bronchoscopic lung volume reduction |
| `peripheral_ablation` | Peripheral ablation |
| `bronchial_thermoplasty` | Bronchial thermoplasty |
| `whole_lung_lavage` | Whole lung lavage |
| `rigid_bronchoscopy` | Rigid bronchoscopy |

### Pleural (7 fields)
| Field | Description |
|-------|-------------|
| `thoracentesis` | Thoracentesis |
| `chest_tube` | Chest tube placement |
| `ipc` | Indwelling pleural catheter |
| `medical_thoracoscopy` | Medical thoracoscopy |
| `pleurodesis` | Pleurodesis |
| `pleural_biopsy` | Pleural biopsy |
| `fibrinolytic_therapy` | Fibrinolytic therapy |

## Common Tasks

### 1. Generate Training Data (Full Pipeline)

**Using Make:**
```bash
make registry-prep        # Generate train/val/test CSVs
make registry-prep-dry    # Dry run (preview stats only)
```

**Using CLI:**
```bash
python scripts/golden_to_csv.py \
  --input-dir data/knowledge/golden_extractions_final \
  --output-dir data/ml_training \
  --prefix registry
```

**Using Python API:**
```python
from modules.ml_coder.registry_data_prep import prepare_registry_training_splits

train_df, val_df, test_df = prepare_registry_training_splits()
train_df.to_csv("data/ml_training/registry_train.csv", index=False)
```

### 2. Debug Label Extraction for Single Entry

```python
from modules.ml_coder.label_hydrator import extract_labels_with_hydration

entry = {
    "note_text": "EBUS bronchoscopy with TBNA of stations 4R and 7.",
    "registry_entry": {"linear_ebus_stations": ["4R", "7"]},
    "cpt_codes": [31653],
}

result = extract_labels_with_hydration(entry)
print(f"Source: {result.source}")  # "structured", "cpt", or "keyword"
print(f"Confidence: {result.confidence}")
print(f"Labels: {result.labels}")
```

### 3. Check for Duplicates in Dataset

```python
from modules.ml_coder.registry_data_prep import deduplicate_records

records = [...]  # Your records list
deduped, stats = deduplicate_records(records)

print(f"Removed: {stats['duplicates_removed']}")
print(f"Conflicts: {stats['conflicts_by_source']}")
```

### 4. Add New Keyword Pattern (Tier 3)

Edit `modules/ml_coder/label_hydrator.py`:

```python
KEYWORD_TO_PROCEDURE_MAP = {
    # Add new pattern:
    r"\bnew_procedure\b": [
        ("procedure_field", 0.8),  # (field_name, confidence)
    ],
    ...
}
```

### 5. Add New Alias Mapping

Edit `modules/ml_coder/registry_data_prep.py`:

```python
LABEL_ALIASES = {
    # Add alias → canonical mapping:
    "new_alias": "canonical_field_name",
    ...
}
```

### 6. Run Tests

```bash
# All data prep tests
pytest tests/ml_coder/test_registry_first_data_prep.py -v
pytest tests/ml_coder/test_label_hydrator.py -v

# Deduplication tests only
pytest tests/ml_coder/test_label_hydrator.py::TestDeduplication -v
```

## Output Schema

Each output CSV contains:

| Column | Type | Description |
|--------|------|-------------|
| `note_text` | str | Procedure note text |
| `encounter_id` | str | Stable hash for encounter-level grouping |
| `source_file` | str | Origin golden JSON file |
| `label_source` | str | Extraction tier ("structured", "cpt", "keyword") |
| `label_confidence` | float | Confidence score (0.60-0.95) |
| `[30 procedure columns]` | int | Binary (0/1) procedure labels |

## Expected Statistics

Typical extraction results:
- **Tier 1 (Structured):** ~79%
- **Tier 2 (CPT):** ~18%
- **Tier 3 (Keyword):** ~3%
- **Deduplication:** ~2-3% removed
- **Final dataset:** ~9,400 unique records

## Troubleshooting

### Too Many All-Zero Rows
Check if Tier 1 extraction is working:
1. Verify `registry_entry` structure in golden JSONs
2. Check alias mappings in `LABEL_ALIASES`
3. Ensure `extract_v2_booleans()` handles your schema version

### High Duplicate Count
This is expected when same note appears in multiple golden files:
1. Verify deduplication is enabled (`use_hydration=True`)
2. Check `label_source` distribution in output
3. Review conflict stats in extraction summary

### Stratification Failures
When using `skmultilearn`:
1. Ensure enough samples per label (`min_label_count >= 5`)
2. Check for rare labels that should be filtered
3. Verify encounter grouping isn't creating too few groups

## Related Documentation

- See `CLAUDE.md` section "ML Training Data Workflow" for full pipeline details
- See `docs/optimization_12_16_25.md` for roadmap context

```
