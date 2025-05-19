def is_virtual_machine():
    try:
        with open("/sys/class/dmi/id/product_name", "r") as f:
            name = f.read().lower()
            return any(kw in name for kw in ["vmware", "virtualbox", "qemu", "kvm", "hyper-v"])
    except Exception:
        return False

