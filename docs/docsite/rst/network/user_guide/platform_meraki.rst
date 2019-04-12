.. _meraki_platform_options:

***************************************
Meraki Dashboard Platform Options
***************************************

Meraki modules support multiple connections. This page offers details on how each connection works in Ansible and how to use it.

.. contents:: Topics

Connections Available
================================================================================

+---------------------------+-----------------------------------------------+---------------------------------------------+
|..                         | Legacy                                        | httpapi                                     |
+===========================+===============================================+=============================================+
| | **API key**             | | Specified in each task                      | | Specified in inventory                    |
+---------------------------+-----------------------------------------------+---------------------------------------------+
| | **Connection Settings** | | ``connection: localhost``                   | | ``ansible_connection: httpapi``           |
| |                         | |                                             | | with ``transport: meraki``                |
+---------------------------+-----------------------------------------------+---------------------------------------------+
| | **Rate Limiting**       | | None                                        | | Persistent within playbook execution      |
+---------------------------+-----------------------------------------------+---------------------------------------------+


For legacy playbooks, Ansible's Meraki modules still support ``connection: localhost``. However, the legacy functionality is likely
to be deprecated in Ansible version 2.12.

Using Legacy Connections in Ansible Meraki Modules
==================================================

Example Task
----------------

.. code-block:: yaml

   - name: Retrieve organizatinos
     meraki_organization:
       auth_key: !vault...
       state: query
     delegate_to: localhost

Using httpapi Connections in Ansible Meraki Modules
==================================================

Example httpapi inventory ``[meraki:vars]``
--------------------------------------

.. code-block:: yaml

   [meraki:vars]
   ansible_connection=httpapi
   ansible_network_os=meraki
   meraki_key=!vault...


Example Task
----------------

.. code-block:: yaml

   - name: Retrieve organizatinos
     meraki_organization:
       state: query
