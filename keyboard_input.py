import os, sys, select

if os.name != 'nt':
    import termios

class KeyboardInput:
    def __init__(self):
        self.system = os.name
        if self.system == 'nt':
            import msvcrt
            self.msvcrt = msvcrt
        else:
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)

            # Neue Einstellungen: kein Kanonisch, kein Echo, kurze Lese-Timeouts
            new = termios.tcgetattr(self.fd)
            lflag = new[3]
            lflag &= ~(termios.ICANON | termios.ECHO)  # sofortige Eingabe, kein Echo
            new[3] = lflag

            # WICHTIG: VMIN/VTIME so setzen, dass read() kurze Zeit wartet,
            # um ESC-Sequenzen (Pfeiltasten) komplett einzusammeln.
            cc = new[6]
            cc[termios.VMIN]  = 0    # 0 Bytes minimum
            cc[termios.VTIME] = 1    # 0.1s Timeout pro read
            new[6] = cc

            termios.tcsetattr(self.fd, termios.TCSANOW, new)

    def close(self):
        if self.system != 'nt':
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    # Context-Manager, damit immer sauber zurückgestellt wird
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        self.close()

    def kbhit(self):
        if self.system == 'nt':
            return self.msvcrt.kbhit()
        r, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(r)

    def getch(self):
        if self.system == 'nt':
            b = self.msvcrt.getch()
            # Spezialtasten: Prefix 0x00 oder 0xE0 + zweites Byte
            if b in (b'\x00', b'\xe0'):
                b2 = self.msvcrt.getch()
                # Mappe auf die selben ESC-Sequenzen wie unter POSIX
                mapping = {b'H': '\x1b[A', b'P': '\x1b[B', b'M': '\x1b[C', b'K': '\x1b[D'}
                return mapping.get(b2, '')
            return b.decode('utf-8', errors='ignore')

        # POSIX: mit VMIN=0/VTIME=1 wartet os.read bis zu 0.1s und gibt alles zurück, was da ist
        first = os.read(self.fd, 1)
        if not first:
            return ''  # nichts da
        if first == b'\x1b':
            # Folgebytes einsammeln (max. 6 reichen für übliche CSI-Sequenzen)
            seq = first
            for _ in range(6):
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not r:
                    break
                nxt = os.read(self.fd, 1)
                if not nxt:
                    break
                seq += nxt
                # heuristisch abbrechen: ESC [ <final>
                if seq.startswith(b'\x1b[') and seq[-1:] in b'ABCD~HF':
                    break
            return seq.decode('ascii', errors='ignore')
        else:
            return first.decode('utf-8', errors='ignore')
