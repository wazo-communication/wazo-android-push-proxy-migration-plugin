# wazo-android-push-proxy-migration-plugin

Switches Android push notifications to the Wazo Push Notification Proxy.

## Installation

```sh
wazo-plugind-cli -c "install git https://github.com/wazo-communication/wazo-android-push-proxy-migration-plugin"
```

This will remove the configuration made in the stack to send Android Push
Notifications to the Firebase servers and use the default behavior, i.e.
sending push notifications through the Wazo Push Notification Proxy.

Mobile users will need to restart their mobile application for the migration to
be complete, and for push notifications and calls to work correctly. Calls
received after the migration and before starting the app will be lost. If the
mobile application is already active and in foreground at the moment of the
migration, the app will have to be closed and opened again for future push
notifications and calls to work.

This plugin will send a notification to every mobile user on the server,
before doing the migration. The migration is done tenant by tenant.

The default language for the notification is in French. For an English message,
please use:

```sh
wazo-plugind-cli -c "install git https://github.com/wazo-communication/wazo-android-push-proxy-migration-plugin --ref english"
```

Due to technical limitations, the notification will be sent to all mobile users,
including the iOS users, even if they are not impacted by this Android-only
migration.

The push notification history (a.k.a Webhook logs) will also be deleted during
the migration.

The migration logs are stored in `/var/log/wazo-android-push-proxy-migration.log`.

No services will be restarted by installing this plugin. During the migration of
a tenant, calls received by mobile users may be lost if they require a push
notification. The installation may take some time for stacks with many users or
tenants, expect around 1 minute for every 1500 tenants, plus 1 minute for every
200 users, i.e. around 11 minutes for 2000 users in 1500 tenants.

## Uninstallation

```sh
wazo-plugind-cli -c "uninstall wazocommunication/wazo-android-push-proxy-migration"
```

Uninstalling this plugin will not restore the previous configuration. Removing
this plugin can be done safely at any time and will keep the Wazo Push
Notification Proxy settings.
