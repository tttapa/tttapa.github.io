bluetoothctl
scan le
scan off
pair F4:12:FA:E3:47:51
connect F4:12:FA:E3:47:51
menu gatt
list-attributes
select-attribute /org/bluez/hci0/dev_F4_12_FA_E3_47_51/service000a/char000b
notify on
read
write "0x80 0x80 0x90 0x12 0x13" 0 command
back
disconnect