#!/usr/bin/env python3

import sys
import threading
import traceback

from requests import HTTPError
from wazo_auth_client import Client as Auth
from wazo_webhookd_client import Client as Webhookd

try:
    token = sys.argv[1]
except IndexError:
    print(f'Usage: {sys.argv[0]} <token>')
    sys.exit(1)

auth = Auth(
    https=False,
    host='localhost',
    port=9497,
    prefix=None,
    token=token,
)
webhookd = Webhookd(
    https=False,
    host='localhost',
    port=9300,
    prefix=None,
    token=token,
)

timers = []


def process_tenant(tenant):
    print(f'Processing tenant {tenant["uuid"]} - {tenant["name"]}')
    try:
        mobile_config = auth.external.get_config('mobile', tenant_uuid=tenant['uuid'])
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            print('Tenant has no mobile config, skipping')
            return
        raise

    if not mobile_config.get('fcm_api_key'):
        print('Tenant has no mobile config key fcm_api_key, migrating mobile config silently')
        auth.external.delete_config('mobile', tenant_uuid=tenant['uuid'])
        return
    if not mobile_config.get('fcm_sender_id'):
        print('Tenant has no mobile config key fcm_sender_id, migrating mobile config silently')
        auth.external.delete_config('mobile', tenant_uuid=tenant['uuid'])
        return

    refresh_tokens = auth.refresh_tokens.list(tenant_uuid=tenant['uuid'])['items']
    mobile_user_uuids = set(
        token['user_uuid']
        for token in refresh_tokens
        if token['mobile'] is True and token['user_uuid']
    )

    if not mobile_user_uuids:
        print('Tenant has no mobile users, migrating mobile config silently')
        auth.external.delete_config('mobile', tenant_uuid=tenant['uuid'])
        return

    # enable subscription to new server so that client apps can register to the new SenderID
    mobile_config_new_sender_id = dict(mobile_config)
    mobile_config_new_sender_id['fcm_sender_id'] = None
    auth.external.update_config('mobile', mobile_config_new_sender_id, tenant_uuid=tenant['uuid'])

    # send notification to migrate client-side subscription
    print(f'Sending alert notification to {len(mobile_user_uuids)} users')
    webhookd.set_tenant(tenant['uuid'])
    for user_uuid in mobile_user_uuids:
        notification = {
            'notification_type': 'pushNotificationServerMigration',
            'user_uuid': user_uuid,
            'title': 'Redémarrez l\'application pour continuer à recevoir vos appels',
            'body': ('Une mise à jour importante de votre application à eu lieu, '
                     'veuillez redémarrer l\'application pour continuer à recevoir des appels'),
        }
        webhookd.mobile_notifications.send(notification)

    # Finish migration to new server 10 seconds later, so that future push
    # notifications are sent with the new key/SenderID
    # We need the delay to let the notifications be sent, before changing the
    # push mobile configuration
    timer = threading.Timer(10, delete_mobile_config, args=[tenant['uuid']])
    timer.name = f'tenant-{tenant["uuid"]}'
    timers.append(timer)
    timer.start()


def delete_mobile_config(tenant_uuid):
    print(f'Migrating mobile config for tenant {tenant_uuid}')
    auth.external.delete_config('mobile', tenant_uuid=tenant_uuid)


print('Starting')
tenants = auth.tenants.list()['items']
success = True
for tenant in tenants:
    try:
        process_tenant(tenant)
    except Exception:
        traceback.print_exc()
        success = False

print('Waiting for the remaining migrations to finish (10 seconds max)...')
for timer in timers:
    timer.join()

if not success:
    print('Finished with errors')
    sys.exit(2)

print('Finished')

# todo: how fast can we send push notifs? about 0.3 sec per notif
# how much time for 3000 mobile users over 2000 tenants? around 0.1 sec per tenant

