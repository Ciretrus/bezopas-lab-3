import sys
import os
import ctypes
import uuid
import hashlib

LICENSE_FILE = "license.key"


def get_disk_serial_number(drive_letter: str = "C:\\") -> str:
    """
    Получение серийного номера раздела жесткого диска 
    через Windows API (GetVolumeInformationW).
    """
    volume_serial_number = ctypes.c_ulong()
    max_component_length = ctypes.c_ulong()
    file_system_flags = ctypes.c_ulong()

    res = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive_letter),
        None,
        0,
        ctypes.byref(volume_serial_number),
        ctypes.byref(max_component_length),
        ctypes.byref(file_system_flags),
        None,
        0
    )

    if not res:
        raise RuntimeError(f"Не удалось получить серийный номер раздела {drive_letter}")

    return f"{volume_serial_number.value:08X}"


def get_mac_address() -> str:
    """
    Получение аппаратного MAC-адреса сетевой карты.
    """
    mac_num = uuid.getnode()
    mac_hex = f"{mac_num:012X}"
    return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))


def generate_hardware_hash(disk_sn: str, mac_addr: str) -> str:
    """
    Генерация контрольного SHA-256 хеша на основе характеристик ПК.
    """
    combined_data = f"{disk_sn}|{mac_addr}"
    return hashlib.sha256(combined_data.encode("utf-8")).hexdigest()


def register_system():
    """Режим привязки: генерация и сохранение ключа лицензии."""
    disk_sn = get_disk_serial_number("C:\\")
    mac_addr = get_mac_address()
    hw_hash = generate_hardware_hash(disk_sn, mac_addr)

    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(hw_hash)

    print("[+] Регистрация успешно завершена!")
    print(f"    - Серийный номер диска (C:): {disk_sn}")
    print(f"    - MAC-адрес сетевой карты:  {mac_addr}")
    print(f"    - Ключ лицензии сохранен в: {LICENSE_FILE}")


def verify_protection() -> bool:
    """Проверка соответствия текущей системы сохраненной лицензии."""
    if not os.path.exists(LICENSE_FILE):
        print("[-] Ошибка: Файл лицензии не найден!")
        print("    Для первичной привязки выполните скрипт с ключом: python protection_lab.py --register")
        return False

    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        saved_hash = f.read().strip()

    try:
        current_disk_sn = get_disk_serial_number("C:\\")
        current_mac_addr = get_mac_address()
    except Exception as e:
        print(f"[-] Ошибка сбора характеристик системы: {e}")
        return False

    current_hash = generate_hardware_hash(current_disk_sn, current_mac_addr)

    print("--- Проверка конфигурации ---")
    print(f"Текущий серийный номер диска: {current_disk_sn}")
    print(f"Текущий MAC-адрес сетевой карты: {current_mac_addr}")

    if current_hash == saved_hash:
        print("[+] Идентификация пройдена: программа запущена на авторизованном ПК.")
        return True
    else:
        print("[-] ОШИБКА ЗАЩИТЫ: Характеристики системы не совпадают!")
        print("    Запуск на данном оборудовании запрещен.")
        return False


def main_protected_payload():
    """Основной защищенный полезный код приложения."""
    print("\n=========================================")
    print("Доступ разрешен! Программа выполняет свою полезную работу.")
    print("=========================================\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--register":
        register_system()
    else:
        if verify_protection():
            main_protected_payload()
        else:
            sys.exit(1)