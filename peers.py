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

    @hook('{peers:certificates}-relation-joined')
    def joined(self):
        ''' '''
        conv = self.conversation()
        # start state
        conv.set_state('create certificate signing request')


    def get_units_in_state(self):
        return [conv.scope for conv in self.conversations()]


    def set_csr(self, csr):
        # Get the conversation scoped to the unit name.
        # We are setting the CSR for this unit's conversation only.
        conv = self.conversation()
        # Remove the old state.
        conv.remove_state('create certificate signing request')
        conv.set_remote({'csr': csr})


    def get_csr_map():
        '''Return a map of name and csr for each unit requesting a csr.
        Encapsulate the communication for all the units in this peer relation.
        '''
        csr_map = {}
        converstations = self.conversations()
        for conv in conversations:
            name = conv.scope
            csr = conv.get_remote('csr')
            csr_map[name] = csr
        return csr_map


    def set_cert(name, certificate):
        conv = self.conversation(name)
        conv.remove_state('sign certificate signing request')
        conv.set_remote({'signed_certificate': certificate})


    @hook('{peers:certificates}-relation-changed')
    def changed(self):
        '''Only the leader should change the state to sign the request. '''
        conv = self.conversation()
        if is_leader():
            if conv.get_remote('csr'):
                conv.set_state('sign certificate signing request')
        else:
            if conv.get_remote('signed_certificate'):
                conv.set_state('signed certificate available')

    def get_signed_cert(self):
        ''' '''
        conv = self.conversation()
        return conv.get_remote('signed_certificate')

    @hook('{peers:certificates}-relation-{broken,departed}')
    def broken(self):
        unit = hookenv.remote_unit()
        print(unit)
        print('{relation_name}.available')
        state = '{0}.available'.format(unit)
        print(state)
        # Get the unit name here and remove that state.
        self.remove_state(state)

    def configure(self):
        # Generate the certs here?
        print('configure')
        unit = hookenv.remote_unit()
        public_address = hookenv.relation_get('public-address')
        private_address = hookenv.relation_get('private-address')
        relation_info = {
            '{0}_certificate'.format(unit): 'this certificate is for {0},{1}'.format(public_address, private_address),
            '{0}_key'.format(unit): 'this key for {0},{1}'.format(public_address, private_address),
        }

        self.set_remote(**relation_info)
