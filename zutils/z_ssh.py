import click
import pickle
from .z_config import default_dir
import os


default_file_name = 'ssh_conn_db.pkl'
_homed_path = os.path.expanduser(default_dir)


@click.command('s')
@click.option('-a', '--add', is_flag=True, help='Add a new ip relevance')
@click.option('-d', '--delete', is_flag=True, help='Delete a ip relevance')
@click.option('-u', '--upload-key', is_flag=True, help='Use ssh-copy-id to upload ssh key, option -a enhanced')
@click.option('-l', '--ls', is_flag=True, help='List all ip (short_ip  ip  user  port)')
@click.option('-m', '--migrate', help='migrate db to add field')
@click.argument('short_ip', default='', type=str)
@click.argument('user', default='', type=str)
@click.argument('port', default='22', type=str)
def ssh_conn(add, delete, upload_key, ls, migrate, short_ip, user, port):
    '''Utility for ssh connect,use a short ip related to actual_ip'''
    db = _get_db()
    if not db:
        db = {}
        _save_db(db)
    if migrate:
        _db_add_field(db, migrate)
        _save_db(db)
    elif ls:
        _list_ip(db)
    elif delete:
        del db[short_ip]
        _save_db(db)
    elif add:
        _add_ip(upload_key, short_ip, db, user, port)
    else:
        _conn_ip(short_ip, db, user, port)


def _db_add_field(db, field):
    for key in db:
        if field in db[key]:
            click.echo('%s already contains' % field)
            return
        db[key][field] = None


def _list_ip(db):
    record_format = '{:<10s}{:<20s}{:<20s}{:<6s}'
    click.echo(record_format.format('short', 'ip', 'user', 'port'))
    for key in db:
        click.echo(record_format.format(key, db[key]['ip'], db[key]['user'], db[key]['port'] if db[key]['port'] else '22'))


def _add_ip(upload_key, ip, db, user, port):
    ip_suffix = ip.split('.')[-1]
    p = _take_port(port)
    db[ip_suffix] = {'ip': ip, 'user': user, 'port': p}
    _save_db(db)
    if upload_key:
        os.system('ssh-copy-id -p %s %s@%s' % (p, user, ip))


def _conn_ip(short_ip, db, user, port):
    if len(db.keys()) == 0:
        click.echo('DB no any ip,use -a option to add some')
    elif not short_ip:
        click.echo('Short_ip must be gaven')
    else:
        target = db[short_ip]
        actual_ip = target['ip']
        if not target:
            click.echo('No any ip related to %s' % short_ip)
        else:
            if not user:
                user = target.get('user', 'root')
            if not port:
                port = target.get('port', '22')
            click.echo(
                'Attempt to conn [ \33[32m%s@%s %s\033[0m ]' % (user, actual_ip, port))
            os.system('ssh -p %s %s@%s' % (port, user, actual_ip))


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
        return 22
    return port


def _save_db(db):
    if not os.path.exists(_homed_path):
        os.makedirs(_homed_path)
    with open(_homed_path + default_file_name, 'wb') as f:
        target = pickle.dump(db, f)
        return target
