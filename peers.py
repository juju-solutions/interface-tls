#!/usr/bin/env python3

from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import is_leader
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class TlsPeer(RelationBase):
    '''The peer class uses the unit scope to communicate with the
    individual units.'''
    scope = scopes.UNIT

    @hook('{peers:tls}-relation-joined')
    def joined(self):
        '''When peers join set the create certificate signing request state.'''
        # Get the conversation scoped to the unit name.
        conv = self.conversation()
        # Set the start state here for the layers to handle the logic.
        conv.set_state('create certificate signing request')

    def set_csr(self, csr):
        '''Set the certificate signing request (CSR) on the relation data.'''
        # Get the conversation scoped to the unit name.
        conv = self.conversation()
        # Normaly we do not get the conversation this way, but for the peer
        # relation we want to set the value for this unit's conversation only.

        # Remove the old state.
        conv.remove_state('create certificate signing request')
        # Set the value on the relation.
        conv.set_remote(data={'csr': csr})

    def get_csr_map(self):
        '''Return a map of name and csr for each unit requesting a signed cert.
        Encapsulate the communication for all the units in this peer relation.
        '''
        csr_map = {}
        # Get all conversations of this type.
        conversations = self.conversations()
        # For each converation get the name and csr put them in a map.
        for conv in conversations:
            name = conv.scope
            csr = conv.get_remote('csr')
            csr_map[name] = csr
        return csr_map

    def set_cert(self, unit_name, certificate):
        '''Set the signed server certificate on the relation data.'''
        # Get the conversation scoped to the specific unit name.
        conv = self.conversation(unit_name)
        # Remove the sign
        conv.remove_state('sign certificate signing request')
        conv.set_remote(data={'signed_certificate': certificate})

    @hook('{peers:tls}-relation-changed')
    def changed(self):
        '''Only the leader should change the state to sign the request. '''
        # Get the conversation scoped to the unit name.
        conv = self.conversation()
        # Normaly we do not get the conversation this way, but for the peer
        # relation we want to get the value for this unit's conversation only.
        if is_leader():
            if conv.get_remote('csr'):
                conv.set_state('sign certificate signing request')
        else:
            if conv.get_remote('signed_certificate'):
                conv.set_state('signed certificate available')

    def get_signed_cert(self):
        '''Return the signed certificate from the relation data.'''
        # Get the conversation scoped to the unit name.
        conv = self.conversation()
        # Normaly we do not get the conversation this way, but for the peer
        # relation we want to get the value for this unit's conversation only.
        return conv.get_remote('signed_certificate')

    @hook('{peers:tls}-relation-{broken,departed}')
    def broken(self):
        '''Can peer relations even be broken?'''
        unit = hookenv.remote_unit()
        print(unit)
        print('{relation_name}.available')
        state = '{0}.available'.format(unit)
        print(state)
        # Get the unit name here and remove that state.
        self.remove_state(state)
