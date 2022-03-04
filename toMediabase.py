import json
import re
from collections import defaultdict

fport_config = "/Users/yecsong/code/serdes-to-mediabase/1x100Gb_31x4x100Gb/port_config.ini"
fserdes_json = "/Users/yecsong/code/serdes-to-mediabase/1x100Gb_31x4x100Gb/P4/8201_32fh_o.json"
final_json = "./media_settings_new.json"


f1 = open(fport_config,"r")
f2 = open(fserdes_json,"r")
load_dict = json.load(f2)

serdes_dict = {}
#serdes_dict: '2,1,8,25,OPTIC': 1288
media_dict = {}
#2560: {'PRE1': -75, 'POST': -125, 'MAIN': 800, 'speed': u'10', 'meterial': u'COPPER'},
for serpram in load_dict['devices'][0]['serdes_params']:
    temp = {}
    if serpram.find(',') == 1:
        slice_id = serpram.split(',')[0]
        ifg_id = serpram.split(',')[1]
        serdes_id = serpram.split(',')[2]
        speed = serpram.split(',')[3]
        meterial = serpram.split(',')[4]
        first_lane_num = int((int(slice_id) * 2 + int(ifg_id)) * (0x100) + int(serdes_id))
        serdes_dict[serpram] = first_lane_num
        temp['speed'] = speed
        temp['meterial'] = meterial
        temp['main'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_MAIN"]
        temp['post1'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_POST"]
        temp['pre1'] = load_dict['devices'][0]['serdes_params'][serpram]["TX_PRE1"]
        temp['ser'] = serpram

        k = str(first_lane_num) + '_' + str(speed) + '_' + str(meterial)
        media_dict[k] = temp

eth_dict = {}
#eth_dict: '8': {'lane3': '2835', 'lane2': '2834', 'lane1': '2833', 'lane0': '2832'}
lane_num = {}
for line in f1:
    if line.split(' ')[0] == "#":
        continue
    Eth = re.split(r'\s+',line)[0]
    index = re.split(r'\s+',line)[3]
    lanes = re.split(r'\s+',line)[1]
    n = 0
    subdict = {}
    if int(index) in eth_dict:
        n = lane_num[int(index)]
        subdict = eth_dict[int(index)]
    for lane in lanes.split(','):
        n_str = "lane" + str(n)
        subdict[n_str] = lane
        n= n + 1
        lane_num[int(index)] = n
    eth_dict[int(index)] = subdict    


tree = lambda: defaultdict(tree)
final_dict = tree()

for e in eth_dict:
    for l in eth_dict[e]:
        for m in media_dict:
            if int(eth_dict[e][l]) == int(m.split('_')[0]):
                if media_dict[m]['meterial'] == 'COPPER':
                    new_key = str(int(media_dict[m]['speed']) * int(lane_num[e])) + 'G' + '_' + 'COPPER'
                else:
                    new_key = str(int(media_dict[m]['speed']) * int(lane_num[e])) + 'G' + '_' + 'OPTIC'
                final_dict[e][new_key]['main'][l] = media_dict[m]['main']
                final_dict[e][new_key]['pre1'][l] = media_dict[m]['pre1']
                final_dict[e][new_key]['post1'][l] = media_dict[m]['post1']

pre = {}
pre["PORT_MEDIA_SETTINGS"] = final_dict
data = json.dumps(pre, indent = 4)
with open(final_json,"w") as f:
    f.write(data)
    print("done!")