import socket
import logging
import random
import time

from itertools import product

PORT = 5002

class Robot:
    EMPTY, MOUNTING, DISMOUNTING, DRYING, OCCUPIED = range(5)

    def __init__(self, motion_time: float = 3.0, dry_time: float = 3.0):
        self.dewar = set(product('ABCDEFGHIJKLMNOP', range(1,17)))
        self.motion_time = motion_time
        self.dry_time = dry_time
        self.state = self.EMPTY
        self.started = None

    def dry(self) -> str:
        return 'normal Drying'

    def center(self) -> str:
        return 'normal Moving to center'

    def safe(self) -> str:
        return 'normal Moving to Safe'

    def status(self):
        is_busy = self.state not in (self.EMPTY, self.OCCUPIED)

        if is_busy and time.time() - self.started > self.motion_time:
            self.started = None
            self.state = {
                self.DISMOUNTING: self.EMPTY,
                self.MOUNTING: self.OCCUPIED,
            }[self.state]

        return {
            self.EMPTY: '0',
            self.MOUNTING: '1',
            self.DISMOUNTING: '2',
            self.DRYING: '4',
            self.OCCUPIED: '8'
        }[self.state]

    def clear(self) -> str:
        if self.state & self.OCCUPIED:
            self.state ^= self.OCCUPIED
        return ''

    def mount(self, puck: str, samp: int) -> str:
        if self.state != self.EMPTY:
            return 'error 64'

        if (puck, samp) not in self.dewar:
            raise RuntimeError(f"Sample {samp}{puck} not in dewar")

        self.dewar.remove((puck, samp))

        self.state = self.MOUNTING
        self.started = time.time()
        time.sleep(5)
        return 'normal'

    def dismount(self, puck: str, samp: int) -> str:
        if self.state != self.OCCUPIED:
            return 'error 8'

        if (puck, samp) in self.dewar:
            raise RuntimeError(f"Sample {samp}{puck} already in dewar")

        self.dewar.add((puck, samp))

        self.state = self.DISMOUNTING
        self.started = time.time()
        time.sleep(5)
        return 'normal'

    def scan(self, puck: str) -> str:
        return ''

    def check(self, puck: str, samp: int) -> str:
        self.state = self.OCCUPIED  # Bug compatible
        return '1' if (puck, samp) in self.dewar else '0'

    def anneal(self, t: int) -> str:
        return ''


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s|%(levelname)8s| %(message)s', level=logging.DEBUG)

    logger = logging.getLogger('Robot')
    logger.info('NYX Robot Simulator')

    robot = Robot()

    # Crude parsing
    def process(request: str) -> str:
        no_args = {
            'DRY': robot.dry,
            'CENTER': robot.center,
            'STATUS': robot.status,
            'CLEAR': robot.clear,
            'SAFE': robot.safe
        }

        full_sample_arg = {
            'MOUNT': robot.mount,
            'DISMOUNT': robot.dismount,
            'CHECK': robot.check,
        }

        if request in no_args:
            return no_args[request]()

        elif any(request.startswith(cmd) for cmd in full_sample_arg):
            action, whole_sample = request.split(' ')
            sample = int(whole_sample[:-1])
            puck = whole_sample[-1]
            return full_sample_arg[action](puck, sample)

        elif request.startswith('SCANPUCK'):
            puck = request[-1]
            return robot.scan(puck)

        elif request.startswith('ANNEAL'):
            t = int(request.split(' ')[-1])
            return robot.anneal(t)

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', PORT))
            s.listen(1)

            logger.info(f'Listening on {PORT}')

            conn, addr = s.accept()
            logger.info(f'Accepted connection from {addr}')

            with conn:
                buffer = b''
                while True:
                    try:
                        new_data = conn.recv(1024)

                        if not new_data:
                            break

                        buffer += new_data

                        try:
                            idx = buffer.index(b'\n') + 1
                        except ValueError:
                            continue

                        request, buffer = buffer[:idx], buffer[idx:]
                        request = request.decode().strip()
                        response = process(request)
                        logger.info(f"'{request}' -> '{response}'")
                        if response:
                            conn.sendall((response + '\r\n').encode())

                    except Exception as e:
                        logger.exception(e)
                        break

            logger.info('Connection closed')
