import sys
import getopt
import csv
import random
import re

class Config:
    def __init__(self):
        self.range = [0,0]
        self.warfare = False
        self.day = False
        self.night = False
        self.offensive = False
        self.axis = False
        self.allies = False

def readConfig(configStr):
    config = Config()
    
    result = re.search(r"((\d+)-?(\d+)?)([awdnogu]+)", configStr)
    
    config.range = [int((result.group(2) or 0)), int((result.group(3) or result.group(2) or 0))]
    modes = result.group(4).lower()
    
    if "a" in modes:
        config.warfare = True
        config.day = True
        config.night = True
        config.offensive = True
        config.axis = True
        config.allies = True
    if "w" in modes:
        config.warfare = True
        if "d" in modes or "n" in modes:
            config.day = "d" in modes
            config.night = "n" in modes
        else: 
            config.day = True
            config.night = True
    if "o" in modes:
        config.offensive = True
        if "g" in modes or "u" in modes:
            config.axis = "g" in modes
            config.allies = "u" in modes
        else: 
            config.axis = True
            config.allies = True
    
    return config

def main(argv):
    weighted = True
    duplicates = False
    consecutive = False
    config = '3-5w 1-2o 2w 1o'

    opts, args = getopt.getopt(argv, "hwdxnc:", ["weight", "allow-dupes", "allow-consecutive", "no-weight", "config="])
    for opt, arg in opts:
        if opt == '-h':
            print('new_rotation.py --weight --config "<configs>"')
            sys.exit()
        elif opt in ("-w", "--weight"):
            weighted = True
        elif opt in ("-n", "--no-weight"):
            weighted = False
        elif opt in ("-d", "--allow-dupes"):
            duplicates = True
        elif opt in ("-x", "--allow-consecutive"):
            consecutive = True
        elif opt in ("-c", "--config"):
           config = arg
    # print('Using weight : ', weighted)
    # print('Allow dupes  : ', duplicates)
    configs = config.split(" ")
    # print('Configs      : ', configs)
    
    data = []
    with open("hll_rcon_maps.csv", "r") as file:
        reader = csv.reader(file);
        headers = next(reader);
        data = [{h:x for (h,x) in zip(headers,row)} for row in reader]
    
    full_rotation = [];
    # print()
    for configStr in configs:
        config = readConfig(configStr);
        # print('Generating for config: [', configStr, ']')
        # print(', '.join("%s: %s" % item for item in vars(config).items()))
        
        map_options = []
        map_weights = []
        for row in data:
            append = False
            if config.warfare and row["mode"] == "warfare" and (config.day and row["variant"] == "day" or config.night and row["variant"] == "night"):
                append = True
            if config.offensive and row["mode"] == "offensive" and (config.axis and row["variant"] == "axis" or config.allies and row["variant"] == "allies"):
                append = True

            if append:
                map_options.append(row["map"])
                if weighted:
                    map_weights.append(float(row["weight"]))
                else:
                    map_weights.append(float(50))
        amount = random.randint(config.range[0], config.range[1])

        for i in range(0, amount, 1):
            while True:
                result = random.choices(map_options, weights=map_weights, k=1)[0];

                good_result = True
                if not duplicates and result in full_rotation:
                    good_result = False
                if not consecutive and len(full_rotation) > 0 and result.split("_")[0] == full_rotation[len(full_rotation)-1].split("_")[0]:
                    good_result = False
                
                if good_result:
                    full_rotation.append(result)
                    break
    
    # print('Generation done full rotation:')
    print(full_rotation)

if __name__ == "__main__":
    main(sys.argv[1:])