from data.models import Wallets

WALLETS = Wallets.parse_obj([
    {
        'address': '0x75f588f259a1aec0c14b60cf01dea40f6f5f3bd7c12500e1ec4868815b2f3c9c',
        'private_key': '0xf22930915b3e7d5ce08cf89f12b5c36ab15ea908b8e23781ab440b759024a370',
    },
]).root
