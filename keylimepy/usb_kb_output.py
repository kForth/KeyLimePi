import codecs

from usb_hid_scancodes import scancodes

# USB Keyboard Output
class UsbKeyboardOutput:
    MOD_BYTES = 2
    KEY_BYTES = 6

    # DEVICE = '/dev/hidg0'
    DEVICE = '.dev.hidg0'
    NONE_KEY = scancodes['KEY_NONE']
    MOD_KEYS = ("KEY_MOD_LCTRL", "KEY_MOD_LSHIFT", "KEY_MOD_LALT", "KEY_MOD_LMETA", "KEY_MOD_RCTRL", "KEY_MOD_RSHIFT", "KEY_MOD_RALT", "KEY_MOD_RMETA")

    ENABLE_NKRO = True

    def _write(self, out_bytes):
        print(out_bytes)

        with open(self.DEVICE, 'wb+') as kb:
            kb.write(''.join([chr(e) for e in out_bytes]).encode())

    def write_6kro(self, active_keys):
        keys = set()
        mods = set()
        for key in active_keys:
            (mods if key in self.MOD_KEYS else keys).add(eval(key, scancodes))
        num_keys = len(keys)

        if num_keys > self.KEY_BYTES:
            key_bytes = [scancodes['KEY_ERR_OVF']] * self.KEY_BYTES
        else:
            key_bytes = keys + [self.NONE_KEY for _ in range(self.KEY_BYTES - num_keys)]        

        self._write([sum(mods), self.NONE_KEY] + key_bytes)

    # https://www.devever.net/~hl/usbnkro
    def write_nkro(self, active_keys):
        keys = set()
        mods = set()
        for key in active_keys:
            (mods if key in self.MOD_KEYS else keys).add(eval(key, scancodes))
        keys_val = 0
        for key in keys:
            if key > 0x67:
                continue
            keys_val += 1 << key
        keys_val += 1 << 67
                
        self._write(codecs.decode(f"{sum(mods):02x}{self.NONE_KEY:02x}{(0x01+0x02):02x}{(0x03+0x04):02x}{(0x05+0x06):02x}{keys_val:026x}", 'hex_codec'))