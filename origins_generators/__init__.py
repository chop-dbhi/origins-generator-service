import subprocess


__version_info__ = {
    'major': 0,
    'minor': 1,
    'micro': 0,
    'releaselevel': 'alpha',
    'serial': 1
}


def get_git_sha1():
    try:
        value = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                        stderr=subprocess.DEVNULL)
        return value.decode('ascii').strip()
    except Exception:
        pass


def get_version(short=False):
    # Fallback to specific version
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')

    vers = ['{major}.{minor}.{micro}'.format(**__version_info__)]

    if __version_info__['releaselevel'] != 'final' and not short:
        sha1 = get_git_sha1()

        if sha1:
            vers.append('{}{}-{}'.format(__version_info__['releaselevel'][0],
                                         __version_info__['serial'], sha1[:8]))

    return ''.join(vers)


__version__ = get_version()
