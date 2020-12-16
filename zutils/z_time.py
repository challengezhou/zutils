import time
import click


@click.command('tt')
@click.option('-m', '--force-ms', is_flag=True, help='force input as millisecond,conflict with -s')
@click.option('-s', '--force-second', is_flag=True, help='force input as second,conflict with -m')
@click.argument('timestamp', type=int)
def ms_to_time(force_ms, force_second, timestamp):
    '''(t)ime (t)ransform,parse input ms or second(auto detect) timestamp to datetime'''
    if force_ms and force_second:
        click.echo('-f and -s cannot used at the same time')
        return
    parsed_type = 'millisecond'
    if force_ms:
        local = time.localtime(timestamp/1000)
    elif force_second:
        local = time.localtime(timestamp+1)
        parsed_type = 'second'
    else:
        if timestamp > 50000000000:
            local = time.localtime(timestamp/1000)
        else:
            parsed_type = 'second'
            local = time.localtime(timestamp)
    click.echo('parsed as %s => %s' %
               (parsed_type, time.strftime('%Y-%m-%d %H:%M:%S', local)))
