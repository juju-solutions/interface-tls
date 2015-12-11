# TLS interface

This is a [Juju](https://jujucharms.com) interface layer that handles the
transport layer security (TLS) between charms of the same type (a.k.a. peers
relation).  Meaning the charms that use this layer can communicate securely
with each other based on TLS certificates.

To get started please read the
[Introduction to PKI](https://github.com/OpenVPN/easy-rsa/blob/master/doc/Intro-To-PKI.md)
which defines some PKI terms, concepts and processes used in this document.

> *NOTE*: It is important to point out that this interface does not do the actual
work of issuing requests or signing certificates.  The interface layer only
handles the communication between the peers and the charm layer must react to
the states correctly for this interface to work.  

The [layer-tls](https://github.com/mbruzek/layer-tls) charm layer was created
to implement this using the [easy-rsa](https://github.com/OpenVPN/easy-rsa)
project.  This interface could be implemented with other PKI technology tools
(such as openssl commands) in other charm layers.

# States

The interface layer emits several reactive states that a charm layer can respond
to:

## create certificate signing request
This is the start state that is generated when the peer relation is joined.
A charm layer responding to this state should create a certificate signing
request (CSR) and set the CSR on relation object using the `set_csr(csr)`
method.

## sign certificate signing request
Once the CSR is set on the relation, the leader will emit this  
"sign certificate signing request" state that the charm layer can react to.
The leader could then import the CSR and sign the CSR and set the signed
certificate on the relation object using the 'set_cert(unit_name, certificate)'
method.  Here the `unit_name` uniquely identifies the signed certificate for
each unit.

## signed certificate available
Once the signed certificate is set on the relation, the interface layer will
emit the "signed certificate available" state, indicating that the signed
certificate is available to the charm layer in the
[unitdata](http://pythonhosted.org/charmhelpers/api/charmhelpers.core.unitdata.html)
with the key `[unit-name]_signed_certificate`.  The charm layer can retrieve
the certificate and use it in the code.

```python
from charmhelpers.core import unitdata
database = unitdata.kv()
cert = database.get('tls.server.certificate')
```

# Contact Information

Interface author: Matt Bruzek &lt;Matthew.Bruzek@canonical.com&gt;
Contributor: Charles Butler &lt;Charles.Butler@canonical.com&gt;
Contributor: Cory Johns &lt;Cory.Johns@canonical.com&gt;
