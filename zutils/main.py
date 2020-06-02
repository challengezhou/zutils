import click
from zutils import z_time, z_ssh


@click.group()
def main():
    pass


def add_all_command():
    main.add_command(z_time.ms_to_time)
    main.add_command(z_ssh.ssh_conn)


add_all_command()


if __name__ == "__main__":
    main()
