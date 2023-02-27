import click
import pickle
from .z_config import default_dir
import os


default_file_name = 'ssh_conn_db.pkl'
_homed_path = os.path.expanduser(default_dir)


@click.command('s')
@click.option('-s', '--short', help='Specify the shortcut for host ssh login')
@click.option('-h', '--host', help='Host to connect')
@click.option('-p', '--port', help='Port to connect')
@click.option('-u', '--user', help='User to connect')
@click.option('-a', '--add',  is_flag=True, help='Add or update a new shortcut')
@click.option('-d', '--delete', is_flag=True, help='Delete by shortcut')
@click.option('--des', help='Add description to shortcut')
@click.option('--upload-key', is_flag=True, help='Use ssh-copy-id to upload ssh pub key, option -a enhanced')
@click.option('-l', '--ls', is_flag=True, help='List all shortcut')
@click.option('--migrate', help='migrate db to add field, only for dev')
@click.argument('shortcut', default='', type=str)
def ssh_conn(host, short, des, add, delete, upload_key, ls, migrate, shortcut, user, port):
    '''Utility for ssh connect,use a shortcut login actual_host'''
    db = _get_db()
    if not db:
        db = {}
        _save_db(db)
    if migrate:
        _db_add_field(db, migrate)
        _save_db(db)
        return
    elif ls:
        _list_ip(db)
        return
    if delete:
        del db[short]
        _save_db(db)
        return
    if add:
        if host:
            _add_ip(db, upload_key, host, user if user else 'root', port, des, short)
        else:
            click.echo('must provide host -h/--host')
        return
    else:
        _conn_ip(db, shortcut, user, port)


def _db_add_field(db, field):
    for key in db:
        if field in db[key]:
            click.echo('%s already contains' % field)
            return
        db[key][field] = None


def _list_ip(db):
    record_format = '{:<10s}{:<20s}{:<20s}{:<10s}{:<20s}'
    click.echo(record_format.format('shortcut', 'host', 'user', 'port', 'des'))
    for key in db:
        click.echo(record_format.format(key, db[key]['host'], db[key]['user'], str(db[key]['port'] if db[key]['port'] else '22'), 
        db[key]['des'] if db[key]['des'] else ''))


def _add_ip(db, upload_key, host, user, port, des, spec_shortcut):
    if spec_shortcut:
        shortcut = spec_shortcut
    else:
        shortcut = host.split('.')[-1]
        if shortcut in db:
            click.echo("shortcut [" + shortcut + '] exist!')
            return
    p = _take_port(port)

    db[shortcut] = {'host': host, 'user': user, 'port': p, 'des': des}
    _save_db(db)
    if upload_key:
        _upload_key(host, user, p)


def _upload_key(host, user, port):
    click.echo('Upload ssh pub key to ' + host + ',user:' + user)
    os.system('ssh-copy-id -p %s %s@%s' % (port, user, host))


def _conn_ip(db, shortcut, user, port):
    if not shortcut:
        click.echo('shortcut must be gaven')
        return
    if len(db.keys()) == 0:
        click.echo('DB no any shortcut,use -a option to add')
        return
    target = db.get(shortcut)
    if not target:
        click.echo('shortcut %s not found ' % shortcut)
    else:
        actual_host = target['host']
        # no pass user param
        if not user:
            user = _take_user(target.get('user'))
        if not port:
            port = _take_port(target.get('port'))
        click.echo(
            'Attempt to conn [ \33[32m%s@%s %s\033[0m ]' % (user, actual_host, port))
        os.system('ssh -p %s %s@%s' % (port, user, actual_host))


def _get_db():
    file_path = _homed_path + default_file_name
    if not os.path.exists(_homed_path):
        os.makedirs(_homed_path)
    try:
        with open(file_path, 'rb') as f:
            target = pickle.load(f)
            return target
    except FileNotFoundError:
        return None
    except pickle.UnpicklingError:
        click.echo('unpickle [%s] failed,removing file!!!' % file_path)
        os.remove(file_path)


def _take_port(port):
    if not port:
        return '22'
    return port


def _take_user(user):
    if not user:
        return 'root'
    return user


def _save_db(db):
    if not os.path.exists(_homed_path):
        os.makedirs(_homed_path)
    with open(_homed_path + default_file_name, 'wb') as f:
        target = pickle.dump(db, f)
        return target
