import json
import re
from collections import defaultdict

f1 = open("/Users/yecsong/code/sonic-buildimage-games/platform/cisco/device/x86_64-8201_32fh_o-r0/30x100Gb_2x400Gb/port_config.ini","r")
f2 = open("/Users/yecsong/code/sonic-buildimage-games/platform/cisco/device/x86_64-8201_32fh_o-r0/30x100Gb_2x400Gb/P4/8201_32fh_o.json","r")
load_dict = json.load(f2)

serdes_dict = {}
#serdes_dict: '2,1,8,25,OPTIC': 1288
media_dict = {}
#2560: {'PRE1': -75, 'POST': -125, 'MAIN': 800, 'speed': u'10', 'meterial': u'COPPER'},
for serpram in load_dict['devices'][0]['serdes_params']:
    # print(serpram)
    temp = {}
    if serpram.find(',') == 1:
        slice_id = serpram.split(',')[0]
        ifg_id = serpram.split(',')[1]
        serdes_id = serpram.split(',')[2]
        speed = serpram.split(',')[3]
        meterial = serpram.split(',')[4]
        # print("slice:{}, ifg:{}, serdes:{}, speed:{}, meterial:{}".format(slice_id, ifg_id, serdes_id, speed, meterial))
        first_lane_num = int((int(slice_id) * 2 + int(ifg_id)) * (0x100) + int(serdes_id))
        # print("first_lan_num:{}".format(first_lane_num))
        serdes_dict[serpram] = first_lane_num
        temp['speed'] = speed
        temp['meterial'] = meterial
        temp['MAIN'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_MAIN"]
        temp['POST'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_POST"]
        temp['PRE1'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_PRE1"]
        temp['ser'] = serpram

        k = str(first_lane_num) + '_' + str(speed) + '_' + str(meterial)
        media_dict[k] = temp

# print(serdes_dict)
print(json.dumps(sorted(media_dict.items()), indent = 1))
eth_dict = {}
#eth_dict: '8': {'lane3': '2835', 'lane2': '2834', 'lane1': '2833', 'lane0': '2832'}
lane_num = {}
for line in f1:
    if line.split(' ')[0] == "#":
        continue
    Eth = re.split(r'\s+',line)[0]
    index = re.split(r'\s+',line)[3]
    lanes = re.split(r'\s+',line)[1]
    # print(lanes)
    n = 0
    subdict = {}
    for lane in lanes.split(','):
        # print(lane)
        n_str = "lane" + str(n)
        subdict[n_str] = lane
        n= n + 1
        lane_num[int(index)] = n
    eth_dict[int(index)] = subdict    

# print(sorted(eth_dict.items()))
# print(eth_dict)
tree = lambda: defaultdict(tree)
final_dict = tree()

for e in eth_dict:
    for l in eth_dict[e]:
        for m in media_dict:
            if int(eth_dict[e][l]) == int(m.split('_')[0]):
                # print("e:{}, m:{}, {}".format(e,m, media_dict[m]))
                if media_dict[m]['meterial'] == 'COPPER':
                    new_key = str(int(media_dict[m]['speed']) * int(lane_num[e])) + 'G' + '_' + 'COPPER'
                else:
                    new_key = str(int(media_dict[m]['speed']) * int(lane_num[e])) + 'G' + '_' + 'OPTIC'
                # print(new_key)
                final_dict[e][new_key]['TX_MAIN'][l] = media_dict[m]['MAIN']
                final_dict[e][new_key]['TX_PRE1'][l] = media_dict[m]['PRE1']
                final_dict[e][new_key]['TX_POST'][l] = media_dict[m]['POST']

final = sorted(final_dict.items())
# data = json.dumps(final, indent = 1)
# with open("./new.json","w") as f:
#     f.write(data)
#     print("done!")