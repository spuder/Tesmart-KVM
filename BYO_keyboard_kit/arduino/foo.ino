void setup() {
      Serial.begin(9600);    //TX/RX pins 0/1 on most arduinos
      Serial1.begin(9600);   //TX/RX pins 17/18 on arduino Mega
      const size_t packet_length = 6;
      uint8_t packet[packet_length] = {0xaa, 0xbb, 0x03, 0x01, 0x01, 0xee};
      Serial1.write(packet, packet_length);
}
void loop() {
}