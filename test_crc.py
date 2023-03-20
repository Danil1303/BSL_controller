output_command = '0f ec 06 87 fd 07 87 01'

#адрес 2 '0f ec 06 87 fd 07 87 01' = d8

hex_count = output_command.rstrip().count(' ') + 4
message = output_command.replace(' ', '')
message = 'A' + hex(hex_count)[2:] + '01' + message
output_message_list = [message[i-1:i+1] for i in range (1, len(message)) if i%2 !=0]
# output_command = bytearray.fromhex(output_command)
#
# for i in range(2, len(output_command)-1):
#     print(bytearray[i])


start = (int(output_message_list[0],16)) | int('A0',16)
acc = start
# & - and
# | - or
# start = 10100100
for i in range (1, len(output_message_list)):
    b = bin(acc & int('80',16))
    if acc & int('80',16) != 0:
        carry = 1
    else:
        carry = 0
    rn = bin(acc)
    acc = (acc << 1) & 0xFF
    n = (acc)
    acc = (((acc + int(output_message_list[i], 16))& 0xFF) + carry)& 0xFF
    ny = (acc)
    bn = hex(acc)
    print(bn)

