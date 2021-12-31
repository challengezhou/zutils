import click
import pickle
from .z_config import default_dir
import os


default_file_name = 'ssh_conn_db.pkl'
_homed_path = os.path.expanduser(default_dir)


@click.command('s')
@click.option('-i', '--ip', help='Add a new ip relevance')
@click.option('-s', '--spec-ip', help='Specify the short ip or update existed ip relevance')
@click.option('--des', help='Add description to ip')
@click.option('-d', '--delete', is_flag=True, help='Delete a ip relevance')
@click.option('-k', '--upload-key', is_flag=True, help='Use ssh-copy-id to upload ssh pub key, option -i enhanced')
@click.option('-l', '--ls', is_flag=True, help='List all ip')
@click.option('--migrate', help='migrate db to add field， only for dev')
@click.option('-u', '--user', help='User to connect')
@click.option('-p', '--port', help='Port to connect')
@click.argument('short_ip', default='', type=str)
def ssh_conn(ip, spec_ip, des, delete, upload_key, ls, migrate, short_ip, user, port):
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
    elif ip:
        _add_ip(db, upload_key, ip, user if user else 'root', port, des, spec_ip)
    elif upload_key:
        _upload_key(ip, user, port)
    else:
        _conn_ip(db, short_ip, user, port)


def _db_add_field(db, field):
    for key in db:
        if field in db[key]:
            click.echo('%s already contains' % field)
            return
        db[key][field] = None


def _list_ip(db):
    record_format = '{:<10s}{:<20s}{:<20s}{:<10s}{:<20s}'
    click.echo(record_format.format('short', 'ip', 'user', 'port', 'des'))
    for key in db:
        click.echo(record_format.format(key, db[key]['ip'], db[key]['user'], str(db[key]['port'] if db[key]['port'] else '22'), 
        db[key]['des'] if db[key]['des'] else ''))


def _add_ip(db, upload_key, ip, user, port, des, spec_ip):
    if spec_ip:
        short_ip = spec_ip
    else:
        short_ip = ip.split('.')[-1]
        if short_ip in db:
            click.echo("short_ip [" + short_ip + '] exist!')
    p = _take_port(port)

    db[short_ip] = {'ip': ip, 'user': user, 'port': p, 'des': des}
    _save_db(db)
    if upload_key:
        _upload_key(ip, user, p)


def _upload_key(ip, user, port):
    click.echo('Upload ssh pub key to ' + ip + ',user:' + user)
    os.system('ssh-copy-id -p %s %s@%s' % (port, user, ip))


def _conn_ip(db, short_ip, user, port):
    if len(db.keys()) == 0:
        click.echo('DB no any ip,use -a option to add')
    elif not short_ip:
        click.echo('Short_ip must be gaven')
    else:
        target = db.get(short_ip)
        if not target:
            click.echo('No any ip related to %s' % short_ip)
        else:
            actual_ip = target['ip']
            # no pass user param
            if not user:
                user = _take_user(target.get('user'))
            if not port:
                port = _take_port(target.get('port'))
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
