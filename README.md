# wazo-android-push-proxy-migration-plugin

Switches Android push notifications to the Wazo Push Notification Proxy.

## Installation

```sh
wazo-plugind-cli -c "install git https://github.com/wazo-communication/wazo-android-push-proxy-migration-plugin"
```

This will remove the configuration made in the stack to send Android Push
Notifications to the Firebase servers and use the default behavior, i.e.
sending push notifications through the Wazo Push Notification Proxy.

## Uninstallation

```sh
wazo-plugind-cli -c "uninstall wazocommunication/wazo-android-push-proxy-migration"
```

Uninstalling this plugin will not restore the previous configuration. Removing
this plugin can be done safely at any time and will keep the Wazo Push
Notification Proxy settings.
