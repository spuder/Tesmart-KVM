# Testmart-KVM Hacks


![](https://cdn.shopify.com/s/files/1/0271/3429/6200/products/tesmart-dual-monitor-kvm-switcher-us-plug-tesmart-dual-monitor-kvm-switch-4-displayport-pcs-2-displayport-monitors-updated-4k-60hz-support-cascading-for-quad-monitor-hdr-10-hdcp-2-2-b.jpg?v=1637964889) 

Tesmart https://www.tesmart.com/collections/dual-monitor/products/4-port-dual-monitor-kvm-switch-hdmi-usb-c-4k60hz-with-usb-hub


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