# Testmart-KVM Hacks

This repo contains a collection of code and examples to interface with tesmart devices using a varriety of interfaces

- Serial Port
- Infrared Remote control emulation

## Serial UART control


The tesmart comes with a Pheonix connector. You will need a Serial to pheonix cable



- [Bhphoto pheonix cable](https://www.bhphotovideo.com/c/product/1591175-REG/black_box_avs_cbl_rs232_rs_232_db9_to_phoenix.html)

![](https://imgur.com/ZK4hFCC.jpg)

- [Serial to TTL Adapter](https://www.amazon.com/gp/product/B07BJJ1T5G/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
![](https://imgur.com/xGfRZJF.jpg)

- [USB to DB9 Adapter](https://www.amazon.com/gp/product/B00BUZ0K68/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

![](https://imgur.com/ZrJkdki.jpg)


### Computer control

You must have an application that can send Serial Communication as "Binary" or "Hex" values. 

Putty is _not_ capable of sending Binary. Instead use RealTerm USR-TCP322 

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

![](https://imgur.com/hKvm8zE.jpg)

![](https://imgur.com/flNKfRR.jpg)


Additional Information

- https://arduino.stackexchange.com/a/90196/27311
- https://gist.github.com/spuder/628a42e605cd4caa7c4f46dbf7bf47ea


I am using a 6 key keyboard with a micro controller to send 
- See [BYO_keyboard_kit/README.md](./BYO_keyboard_kit/README.md)



## Infrared

![](https://imgur.com/QmkE7U5.jpg)


### IR Codes

Codes were captured with a wemos D1 and ESPHome

https://oliverfalvai.com/infrared-smart-remote-esphome/

Remote is `Pronto` format
http://www.remotecentral.com/features/irdisp2.htm


If you are able to translate these codes into something that ~