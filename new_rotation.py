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

def generateSeedRotation(data, full_rotation):
    seed_maps = []
    for row in data:
        if str(row["seeding"]).upper() == "TRUE":
            seed_maps.append(row["map"])

    # Populate blanks
    seed_rotation = []
    for i in range(0, min(len(seed_maps), len(full_rotation)), 1):
        seed_rotation.append("")

    # Match index
    for i in range(0, len(seed_maps), 1):
        if i > len(full_rotation):
            break;
        if full_rotation[i] in seed_maps:
            seed_rotation[i] = full_rotation[i]
            seed_maps.remove(seed_rotation[i])

    # Fill in blanks by distance for dupes outside seed rotation length
    dist_tuples = []
    for map in seed_maps:
        if map in full_rotation:
            full_ind = full_rotation.index(map)
            dist_tuples.append((full_ind, map))
    dist_tuples.sort()
    for tuple in dist_tuples:
        # print(tuple, " dist ", tuple[0] - seed_rotation.index(""))
        seed_rotation[seed_rotation.index("")] = tuple[1]
        seed_maps.remove(tuple[1])

    # Fill in remaining blanks if they exist
    for i in range(0, len(seed_rotation), 1):
        if seed_rotation[i] == "" and len(seed_maps) > 0:
            seed_rotation[i] = seed_maps[0]
            seed_maps.remove(seed_maps[0])

    return seed_rotation

def main(argv):
    weighted = True
    exact_dupes = False
    general_dupes = False
    seeding = False
    config = '11w'
    consec_stress = False

    opts, args = getopt.getopt(argv, "hndgxnc:s", ["no-weight", "allow-dupes", "disable-general-dupes", "general-dupe-dist=", "seed", "config="])
    for opt, arg in opts:
        if opt == '-h':
            print('new_rotation.py --weight --config "<configs>"')
            sys.exit()
        elif opt in ("-n", "--no-weight"):
            weighted = False
        elif opt in ("-d", "--allow-exact-dupes"):
            exact_dupes = True
        elif opt in ("-x", "--disable-general-dupes"):
            general_dupes = False
        elif opt in ("-p", "--general-dupe-dist"):
            general_dupe_dist = arg
        elif opt in ("-s", "--seed"):
            seeding = True
        elif opt in ("-c", "--config"):
            config = arg
    configs = config.split(" ")
    
    stress_maps = []
    data = []
    with open("hll_rcon_maps.csv", "r") as file:
        reader = csv.reader(file);
        headers = next(reader);
        data = [{h:x for (h,x) in zip(headers,row)} for row in reader]

    for row in data:
        if str(row["stress"]).upper() == "TRUE":
            stress_maps.append(row["map"])

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
        
        if not exact_dupes:
            amount = min(len(map_options), amount)

        def check_good_result(result):
            good_result = True
            length = len(full_rotation)

            if not exact_dupes and result in full_rotation:
                good_result = False
            if not general_dupes: # and result.split("_")[0] == full_rotation[len(full_rotation)-1].split("_")[0]
                for j in range(0, length, 1):
                    if result.split("_")[0] == full_rotation[j].split("_")[0]:
                        good_result = False
            if not consec_stress:
                if result in stress_maps and length > 0 and full_rotation[length-1] in stress_maps:
                    good_result = False
                    
            return good_result

        for i in range(0, amount, 1):
            while True:
                result = random.choices(map_options, weights=map_weights, k=1)[0];
                good_result = check_good_result(result)
                
                any_good_results = False
                for map in map_options:
                    if check_good_result(map):
                        any_good_results = True
                
                if good_result:
                    full_rotation.append(result)
                    break
                if not any_good_results:
                    # print("No more good results possible, stopping early.")
                    break
    
    # print('Generation done full rotation:')
    # print(full_rotation)

    print("### Live Rotation ###")
    print('"rotation": [')
    print("  \"","\",\n  \"".join(full_rotation),"\"", sep='')
    print("]")
    print()
    print()

    if seeding:
        seed_rotation = generateSeedRotation(data, full_rotation);
        
        print("### Seed Rotation ###")
        print('"rotation": [')
        print("  \"","\",\n  \"".join(seed_rotation),"\"", sep='')
        print("]")
        print()
        print()

if __name__ == "__main__":
    main(sys.argv[1:])