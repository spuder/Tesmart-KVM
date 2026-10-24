# Testmart-KVM Hacks


![](https://cdn.shopify.com/s/files/1/0271/3429/6200/products/tesmart-dual-monitor-kvm-switcher-us-plug-tesmart-dual-monitor-kvm-switch-4-displayport-pcs-2-displayport-monitors-updated-4k-60hz-support-cascading-for-quad-monitor-hdr-10-hdcp-2-2-b.jpg?v=1637964889) 

## Supported models

Tesmart sells many KVM models (HDMI, DisplayPort, USB-C; 2 or 4 PCs; 1 or 2 monitors), and the serial commands are not identical across them. This repo was built and tested against:

- **[DKS402-E23-USBK](https://www.tesmart.com/products/dks402-e23)**: 4 PCs, 2 monitors, DisplayPort 4K60Hz with EDID (older part number PKS0802A10)
- **HKS0802A10**: 4 PCs, 2 monitors, HDMI (discontinued; the current HDMI equivalent is the HKS402-E23)

Other 4×2 dual-monitor models, such as the [DKS402-P23](https://www.tesmart.com/products/dks402-p23) (DisplayPort) and [HKS402-P24](https://www.tesmart.com/products/hks402-p24) (HDMI), may use the same protocol but are untested. Check your model's manual before relying on the command table below.


This repo contains a collection of code and examples to interface with tesmart devices using a varriety of interfaces

- Serial Port
- Infrared Remote control emulation

## Serial UART control

Buadrate: 9600


| Command | Content | 
| --- | --- |
| AA BB 03 01 01 EE | Switch to PC 1 | 
| AA BB 03 01 02 EE | Switch to PC 2 |
| AA BB 03 01 03 EE | Switch to PC 3 | 
| AA BB 03 01 04 EE | Switch to PC 4 | 
| AA BB 03 02 00 EE | Turn off Buzzer | 
| AA BB 03 02 01 EE | Turn on Buzzer | 
| AA BB 03 03 00 EE | Output A decrease input by 1 | 
| AA BB 03 03 01 EE | Output A increase input by 1 |
| AA BB 03 04 00 EE | Output B decrease input by 1 | 
| AA BB 03 04 01 EE | Output B increase input by 1 |
| AA BB 03 05 01 EE | Switch usb between outputs (in display mode 2) | 
| AA BB 03 06 00 EE | Turn on keyboard mouse passthrough|
| AA BB 03 06 01 EE | Turn off keyboard mouse passthrough|
| AA BB 03 07 01 EE | switch the control hot key to right ctrl|
| AA BB 03 07 00 EE | switch the control hot key to right scrolllock|
| AA BB 03 08 01 EE | turn on auto switching mode|
| AA BB 03 08 00 EE | turn off auto switching mode|
| AA BB 04 09 MM SS EE | Set auto switching time 0x00-0x38, (min 5s)|


Note: I spoke with support and it is not currently possible to emulate the functionality of the Output A and Output B buttons exactly. You can get close by using ` AA BB 03 03 01 EE` and `AA BB 03 04 01 EE` to toggle output A and B between all inputs. 

### Home Assistant Connect AUX-2

The AUX-2 exposes its RS-232 ports to Home Assistant over the ESPHome serial proxy; it does not need to appear as a local USB serial device. Follow Nabu Casa's [AUX-2 TV/AV receiver guide](https://nabucasa.github.io/public-product-testing-resources/aux-2-52v8mj/02-what-you-can-do/01-starter-projects/02-control-your-tv-and-av-receiver/) and [serial-control guide](https://nabucasa.github.io/public-product-testing-resources/aux-2-52v8mj/02-what-you-can-do/03-controlling-devices-over-serial/), then add the AUX-2 to Home Assistant through the ESPHome integration. The [serial-over-network release notes](https://www.home-assistant.io/blog/2026/05/06/release-20265/#serial-ports-over-the-network-with-esphome) explain how the proxy exposes serial devices (Home Assistant 2026.5 or later). The [published AUX-2 firmware](https://github.com/NabuCasa/aux-2/blob/815fa2a3cb715caa8c8dcd33e21e1776924762ba/packages/aux-2.yaml#L221-L244) exposes two RS-232 ports; it does not document a hardware switch or jumper position for serial mode.

Connect the AUX-2 RS-232 port to the KVM's RS-232 connector, verifying the TX, RX, and ground labels on both devices. The KVM uses 9600 baud, 8N1. The tested serial commands below are model-dependent; see [Supported models](#supported-models).

To add Tesmart to Home Assistant's integration list, copy `custom_components/tesmart` into the Home Assistant `config/custom_components/tesmart` directory and restart Home Assistant. Select **Settings → Devices & services → Add integration → Tesmart**, then choose the AUX-2 RS-232 serial proxy. The resulting **Input** selector sends the command to switch both outputs to PC 1–4.

### KVM serial output (undocumented)

Tesmart's documentation says the KVM sends nothing back over serial, but it does. Whenever the input changes, from the front panel or from a serial command, the KVM's TX line sends plain ASCII status lines at 9600 baud, 8N1. Captured on a DKS402-E23-USBK:

| Message | Hex | Meaning |
| --- | --- | --- |
| `Set ch is 0\r\r\n` | `53 65 74 20 63 68 20 69 73 20 30 0D 0D 0A` | An output switched to PC 1 |
| `Set ch is 1\r\r\n` | `53 65 74 20 63 68 20 69 73 20 31 0D 0D 0A` | An output switched to PC 2 |
| `Set ch is 2\r\r\n` | `53 65 74 20 63 68 20 69 73 20 32 0D 0D 0A` | An output switched to PC 3 |
| `Set ch is 3\r\r\n` | `53 65 74 20 63 68 20 69 73 20 33 0D 0D 0A` | An output switched to PC 4 |
| `Querry pc LED\r\r\n` | `51 75 65 72 72 79 20 70 63 20 4C 45 44 0D 0D 0A` | Follows about 0.7 s after a switch (the misspelling is the KVM's) |
| `Write EEPROM \r\n` | `57 72 69 74 65 20 45 45 50 52 4F 4D 20 0D 0A` | The KVM has settled and saved its state (note the trailing space) |

Notes:

- The channel number starts at 0, so `Set ch is 0` means PC 1.
- How many times `Set ch is N` repeats depends on what triggered the switch:

  | Trigger | `Set ch is N` lines |
  | --- | --- |
  | Serial command `AA BB 03 01 0N EE` | 3 |
  | Front-panel 1–4 buttons | 2 |
  | Output A or Output B button | 1 |

  The lines in a burst arrive a few ms apart, and the IR remote's buttons weren't measured separately.
- The Output A and Output B buttons don't say which output changed. Because they step that output to the next PC, firmware that knows both outputs' current PCs can usually work out which one moved. When both outputs are on the same PC it has to guess.
- The auto-switch (scan) button produced no output in testing.

> **No query command on this model.** Some Tesmart switches answer `AA BB 03 10 00 EE` with the active input. The DKS402-E23-USBK sends nothing back, so the only way to track state is to listen for the messages above.

`BYO_keyboard_kit/python/code.py` reads these lines to keep its LED in sync with the KVM.

The tesmart comes with a Pheonix connector. You will need a Serial to pheonix cable

![](https://imgur.com/lg1xJxe.jpg)


- [Bhphoto pheonix cable](https://www.bhphotovideo.com/c/product/1591175-REG/black_box_avs_cbl_rs232_rs_232_db9_to_phoenix.html)

![](https://imgur.com/ZK4hFCC.jpg)

- [Serial to TTL Adapter](https://www.amazon.com/gp/product/B07BJJ1T5G/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
![](https://imgur.com/xGfRZJF.jpg)

- [USB to DB9 Adapter](https://www.amazon.com/gp/product/B00BUZ0K68/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

![](https://imgur.com/ZrJkdki.jpg)

![](https://imgur.com/52FF5sh.jpg)


### Computer control

You must have an application that can send Serial Communication as "Binary" or "Hex" values. 

Putty is _not_ capable of sending Binary. Instead use [RealTerm](https://sourceforge.net/projects/realterm/) or [USR-TCP Test](https://www.pusr.com/support/downloads/usr-tcp232-test-V13.html)

![](https://imgur.com/WvbeC4y.jpg)
![](https://imgur.com/AOH2BeE.jpg)



### Microcontroller control

Arduino Code

```
void setup() {
      Serial.begin(9600);    //TX/RX pins 0/1 on most arduinos
      Serial1.begin(9600);   //TX/RX pins 17/18 on arduino Mega
      const size_t packet_length = 6;
      uint8_t packet[packet_length] = {0xaa, 0xbb, 0x03, 0x01, 0x01, 0xee};
      Serial1.write(packet, packet_length);
}
void loop() {
}
```

See BYO_keyboard_kid/arduino for more examples


Circuit Python

```
uart = busio.UART(board.D1, board.D0, baudrate=9600)
text = bytearray([0xAA, 0xBB, 0x03, 0x01, 0x01, 0xEE])
uart.write(text)
```

See BYO_keyboard_kid/python for more examples

![](https://imgur.com/hKvm8zE.jpg)

![](https://imgur.com/flNKfRR.jpg)

Note many USB keyboards that are based on custom microcontrollers like the [UHK keyboard](https://www.google.com/search?q=uhk+keyboard+kvm&rlz=1C5CHFA_enUS991US991&oq=uhk+keyboard+kvm&aqs=chrome..69i57j0i512l2j0i22i30l3j69i60l2.2316j0j4&sourceid=chrome&ie=UTF-8) or BYO Keyboard, are not capable of using the scroll lock + shortcut functionality to switch inputs. Furthermore attempting to use the specialized USB ports will result in media keys (like volume) not working. 

It is recomended to plug keyboards into the non-smart USB ports. 


Additional Information

- https://arduino.stackexchange.com/a/90196/27311
- https://gist.github.com/spuder/628a42e605cd4caa7c4f46dbf7bf47ea
- https://superuser.com/questions/245926/how-does-realterm-send-numbers/1732191#1732191

I am using a 6 key keyboard with a micro controller to send 
- See [BYO_keyboard_kit/README.md](./BYO_keyboard_kit/README.md)



## Infrared

![](https://imgur.com/QmkE7U5.jpg)


### IR Codes

Codes were captured with a wemos D1 and ESPHome

https://oliverfalvai.com/infrared-smart-remote-esphome/

Remote is `Pronto` format
http://www.remotecentral.com/features/irdisp2.htm


```
# M
# Same as Output A button on device
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AB 0017 003F 0017 003F 0017 003F 0017 0014 0017 003F 0017 0014 0017 0014 0017 0014 0017 0015 0017 0014 0017 0014 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 0015 0017 0014 0017 003F 0017 0014 0017 0014 0017 0014 0017 003F 0017 0015 0017 003F 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 0015 0017 003F 0017 06C3
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015B 0055 0017 06C3
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0056 0017 06C3
```

```
# P
# Same as Output B button on device
[13:01:32][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AC 0015 0041 0016 0041 0017 003F 0016 0016 0017 003F 0016 0016 0016 0015 0016 0016 0015 0016 0016 0015 0016 0016 0016 0041 0017 0014 0016 0040 0016 0041 0016 0040 0016 0041 0016 0040 0016 0040 0016 0016 0016 0016 0016 0015 0016 0040 0016 0015 0016 0016 0016 0015 0016 0015 0016 0040 0016 0040 0016 0040 0016 0015 0016 0040 0016 06C3
[13:01:32][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0056 0016 06C3

```

```
# 1
# Same as button 1 on device
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AB 0017 003F 0017 003F 0017 003F 0017 0014 0017 003F 0017 0014 0017 0014 0017 0014 0017 0015 0017 0014 0017 0014 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 0015 0017 0014 0017 003F 0017 0014 0017 0014 0017 0014 0017 003F 0017 0015 0017 003F 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 0015 0017 003F 0017 06C3
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015B 0055 0017 06C3
[12:59:01][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0056 0017 06C3
```
```
# 2
# Same as button 2 on device
[12:59:41][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015B 00AC 0016 0040 0016 0040 0016 0040 0016 0016 0016 0040 0016 0016 0016 0016 0016 0016 0016 0015 0016 0016 0016 0016 0016 0040 0016 0015 0016 0040 0016 0040 0016 0040 0016 0040 0016 0040 0016 0016 0016 0016 0016 0016 0016 0016 0016 0040 0016 0015 0016 0015 0016 0015 0016 0040 0016 0040 0016 0040 0016 0040 0016 0016 0015 0040 0016 06C3
[12:59:41][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015B 0055 0016 06C3

```
```
# 3
# Same as button 3 on device
[12:59:41][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015B 0055 0016 06C3
[13:00:06][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AB 0017 003F 0017 003F 0017 003F 0017 0014 0017 003F 0017 0014 0017 0014 0017 0014 0017 0014 0017 0014 0017 0014 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 003F 0017 003F 0017 003F 0017 0014 0017 0015 0017 0014 0017 0014 0017 0014 0017 0014 0017 0014 0017 0014 0017 003F 0017 003F 0017 003F 0017 003F 0017 003F 0017 06C3
[13:00:13][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 0079 0004 0008 06C3

```

```
# 4
# Same as button 4 on device
[13:00:43][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015B 00AB 0017 003F 0016 0040 0017 003F 0016 0017 0015 003F 0017 0015 0016 0015 0017 0015 0016 0016 0017 0015 0017 0015 0016 0040 0017 0015 0017 003F 0017 003F 0017 003F 0017 003F 0016 0015 0017 0015 0017 003F 0017 0015 0017 0015 0016 0015 0017 0015 0017 0015 0017 003F 0017 003F 0017 0015 0017 003F 0017 003F 0017 003F 0017 003F 0017 06C3
[13:00:44][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0055 0017 06C3

```

```
# 5
# Same as button 5 on device
[13:01:00][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AB 0017 003F 0017 003F 0017 003F 0017 0015 0017 003F 0016 0016 0016 0016 0016 0016 0017 0015 0016 0015 0017 0015 0017 003F 0016 0016 0017 003F 0017 003F 0016 0040 0016 0015 0017 003F 0017 003F 0017 0014 0017 003F 0017 0015 0017 0014 0017 0015 0017 003F 0017 0014 0017 0014 0017 003F 0017 0014 0017 003F 0017 003F 0017 003F 0017 06C3
[13:01:00][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0055 0016 06C3

```


```
# Circle
# Same as Circle 
[13:01:55][D][remote.pronto:229]: Received Pronto: data=0000 006D 0022 0000 015C 00AC 0016 0040 0017 003F 0017 003F 0017 0015 0017 003F 0016 0016 0017 0016 0015 0015 0017 0016 0015 0015 0017 0015 0017 003F 0016 0015 0017 003F 0017 003F 0017 003F 0016 0040 0017 0015 0016 0040 0017 003F 0017 0015 0017 0014 0017 0015 0017 0014 0017 0014 0017 003F 0017 0015 0017 0015 0017 003F 0017 003F 0017 0040 0016 0040 0017 06C3
[13:01:55][D][remote.pronto:229]: Received Pronto: data=0000 006D 0002 0000 015C 0055 0016 06C3

```