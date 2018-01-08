from ipaddress import ip_network


class _TrieNode(object):
    __slots__ = ['children', 'network']

    def __init__(self):
        self.children = [None, None]
        self.network = None

    def add_child(self, bit):
        child = _TrieNode()
        self.children[bit] = child

        return child


class IPTrie(object):
    def __init__(self, *addresses, max_prefixlen=None):
        """Create a new trie, optionally pre-populated with *addresses*, which
        is a sequence of :obj:`ipaddress.ip_address` objects.

        *max_prefixlen* can optionally be set to either 32 (for IPv4), or
        128 (for IPv6). If it is ``None``, it will be set after the first
        address is inserted.
        """
        self.root = _TrieNode()
        self.max_prefixlen = max_prefixlen

        for address in addresses:
            self.insert(address)

    def _get_bits(self, ip_n, prefixlen):
        """Given IP address *ip_n* as an integer, return a list of its host
        bits, the number of which is given by *prefixlen*.
        """
        ret = []
        for i in range(prefixlen):
            mask = 1 << (self.max_prefixlen - i - 1)
            bit = bool(ip_n & mask)
            ret.append(bit)

        return ret

    def insert(self, network):
        """Given :obj:`ipaddress.ip_network` object *network*, insert it into
        the trie.
        """
        network = ip_network(network)

        # Set the IP version based on the first entry; reject mixed inserts
        if self.max_prefixlen is None:
            self.max_prefixlen = network.max_prefixlen
        elif self.max_prefixlen != network.max_prefixlen:
            raise TypeError('{} is of an incompatible version'.format(network))

        # Find the spot for the new entry
        node = self.root
        ip_n = int(network.network_address)
        for bit in self._get_bits(ip_n, network.prefixlen):
            child = node.children[bit]
            node = node.add_child(bit) if (child is None) else child

        node.network = network

    def find(self, address):
        """Given :obj:`ipaddress.ip_address` object *address*, return the
        :obj:`ipaddress.ip_network` object representing the most specific match
        for the address in the trie.
        """
        network = ip_network(address, strict=False)
        if self.max_prefixlen != network.max_prefixlen:
            raise TypeError('{} is of an incompatible version'.format(network))

        ip_n = int(network.network_address)

        # Walk through the trie, following each bit that matches the bits in
        # the address.
        node = self.root
        ret = None
        for bit in self._get_bits(ip_n, self.max_prefixlen):
            child = node.children[bit]
            if not child:
                break

            node = child
            if node.network:
                ret = node.network

        # Return the match with the longest prefix (if one was found), the
        # root (if it was the only match), or None
        if ret is not None:
            return ret
        elif self.root.network:
            return self.root.network
        else:
            return None

    def networks(self):
        """Yield each of the :obj:`ipaddress.ip_network` objects stored in the
        trie.
        """
        stack = [self.root]
        while stack:
            node = stack.pop()

            if node.network:
                yield node.network

            for bit in (0, 1):
                child = node.children[bit]
                if child is not None:
                    stack.append(child)
