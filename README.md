# sonic_tool-serdes_to_media

Sonic serdes base port format to media base port format transformation

### Usage:
  
   python toMediabase.py -p "/Users/yecsong/code/serdes-to-mediabase/1x100Gb_31x4x100Gb/port_config.ini" -s "/Users/yecsong/code/serdes-to-mediabase/1x100Gb_31x4x100Gb/P4/8201_32fh_o.json" -f "./media_settings_new.json"

  -p fport_config: port_config.ini file location(reuqired)
  
  -s fserdes_json: serdes json file location(required)
  
  -f final_json: output file(required)
