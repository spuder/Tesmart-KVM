# Tesmart KVM with Home Assistant Connect AUX-2

This guide connects a Tesmart KVM's RS-232 control port to Home Assistant using the RS-232 serial proxy on Home Assistant Connect AUX-2.

## Requirements

- Home Assistant 2026.5 or later, for ESPHome serial ports over the network.
- Home Assistant Connect AUX-2, configured with the ESPHome integration.
- A Tesmart KVM model with RS-232 control. Serial command support varies by model; see [Supported models and commands](README.md#supported-models).

Read Nabu Casa's [Control your TV and AV receiver](https://nabucasa.github.io/public-product-testing-resources/aux-2-52v8mj/02-what-you-can-do/01-starter-projects/02-control-your-tv-and-av-receiver/) and [Controlling devices over serial](https://nabucasa.github.io/public-product-testing-resources/aux-2-52v8mj/02-what-you-can-do/03-controlling-devices-over-serial/) guides, and Home Assistant's [serial-over-network release notes](https://www.home-assistant.io/blog/2026/05/06/release-20265/#serial-ports-over-the-network-with-esphome).

The AUX-2's [published firmware](https://github.com/NabuCasa/aux-2/blob/815fa2a3cb715caa8c8f1d7877ae7d6a5f4151/packages/aux-2.yaml#L221-L244) exposes two ports as RS-232 serial proxies. This does not require AUX-2 to appear as a local USB serial device. The firmware documents the ports as RS-232, but does not specify a separate AUX-2 switch or jumper position for serial mode. Check the markings and manuals for both devices before wiring; do not infer connector pin order from the firmware's internal GPIO numbers.

Connect the AUX-2 RS-232 port to the KVM's RS-232 connector, matching the signal labels on both devices. The KVM commands documented in this repository use 9600 baud, 8 data bits, no parity, and 1 stop bit (9600 8N1). The KVM command protocol is model-dependent.

## Install the Tesmart integration

The Home Assistant serial proxy makes an RS-232 stream available to integrations, but does not itself provide a Home Assistant action to transmit arbitrary bytes. The built-in [Serial integration](https://www.home-assistant.io/integrations/serial/) reads incoming serial lines into a sensor; it cannot send the Tesmart's binary switching commands.

To add a **Tesmart** integration entry and an **Input** selector:

1. Copy `custom_components/tesmart` from this repository into Home Assistant's `config/custom_components/tesmart` directory.
2. Restart Home Assistant.
3. In **Settings → Devices & services**, choose **Add integration**, search for **Tesmart**, and select the AUX-2 RS-232 serial proxy.
4. Use the resulting **Input** selector to send the command for PC 1–4.

The integration uses Home Assistant's serial-port selector and serial-proxy transport. It does not open a local `/dev/tty*` path. When asked about native integration options, Home Assistant Core's Serial integration currently exposes only a read-only sensor platform, and the ESPHome serial proxy is a connection transport rather than a user-facing serial-write service. Therefore sending the Tesmart commands through the proxy requires a custom integration.

An alternative without a Python custom integration would be to customize and rebuild the AUX-2 ESPHome firmware to expose Home Assistant buttons or selectors that write the desired commands. That would replace the general serial proxy workflow with device-specific firmware configuration and is not accomplished using only Home Assistant's built-in Serial integration.

## Integration behavior and limitations

The selector sends the documented command to set both KVM outputs to a selected PC. It updates its displayed option after a successful send, but it does not query the KVM or track changes made with the KVM's front-panel buttons or remote. On the tested DKS402-E23-USBK, serial status messages do not identify which output changed, and there is no working query command; the selector cannot reliably represent the KVM's actual state after external changes or a Home Assistant restart.
