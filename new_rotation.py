import sys
import getopt
import csv
import random
import re

def rindex(lst, value):
    # reversed is a buitin backward iterator
    # operator.indexOf can handle this iterator
    # if value is not Found it raises
    #    ValueError: sequence.index(x): x not in sequence
    _ = operator.indexOf(reversed(lst), value)
    # we must fix the resersed index
    return len(lst) - _ - 1


class Config:
    def __init__(self):
        self.str = ""
        self.range = [0, 0]
        self.warfare = False
        self.day = False
        self.night = False
        self.offensive = False
        self.axis = False
        self.allies = False

def readConfig(configStr):
    config = Config()
    config.str = configStr

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

# Outputs 
# type - live/seed
# rotation - maps list
# stress_maps - optional to highlight stress maps in output
def print_json_copy_paste(type, rotation, stress_maps):
    print(" ##### ", type, " (", len(rotation)," maps) ##### ", sep='')
    print()
    print('"rotation": [')
    print("  \"","\",\n  \"".join(rotation),"\"", sep='')
    print("]")
    print()

# Outputs 
# type - live/seed
# rotation - maps list
# stress_maps - optional to highlight stress maps in output
def print_ini_copy_paste(type, rotation, stress_maps):
    print(" ##### ", type, " (", len(rotation)," maps) ##### ", sep='')
    print()
    print("\n".join(rotation), sep='')
    print()

def main(argv):
    debug = False

    format = "autosettings"
    config_input = "7w 1o"
    exact_dupe_dist = -1
    general_dupe_dist = -1
    make_seed_rotation = False
    input_file = "hll_rcon_maps.csv"
    stress_dist = 1
    nonstress_dist = 0
    weighted = True

    opts, args = getopt.getopt(argv, "hdnf:e:g:si:r:t:c:", [
        "help", "debug", "no-weight", "format=", "exact-dupe-dist=", "general-dupe-dist=", "seed", "input=", "stress-dist=", "nonstress-dist=", "config="
    ])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Check the README.md for parameter documentation")
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-n", "--no-weight"):
            weighted = False
        elif opt in ("-f", "--format"):
            format = arg
        elif opt in ("-e", "--exact-dupe-dist"):
            if arg != None and arg.isnumeric():
                exact_dupe_dist = int(arg)
        elif opt in ("-g", "--general-dupe-dist"):
            if arg != None and arg.isnumeric():
                general_dupe_dist = int(arg)
        elif opt in ("-r", "--stress-dist"):
            if arg != None and arg.isnumeric():
                stress_dist = int(arg)
        elif opt in ("-t", "--nonstress-dist"):
            if arg != None and arg.isnumeric():
                nonstress_dist = int(arg)
        elif opt in ("-s", "--seed"):
            make_seed_rotation = True
        elif opt in ("-c", "--config"):
            config_input = arg

    # general_dupe_dist = max(exact_dupe_dist, general_dupe_dist)

    if debug:
        print("config_input=\"", config_input, '"',
              "  format=\"", format, '"',
              "  exact_dupe_dist=", exact_dupe_dist,
              "  general_dupe_dist=", general_dupe_dist,
              "  stress_dist=", stress_dist,
              "  nonstress_dist=", nonstress_dist,
              "  input_file=\"", input_file, '"',
              "  make_seed_rotation=", make_seed_rotation,
              "  weighted=", weighted, sep='')
        print()

    configs = []
    for config_str in config_input.split(" "):
        configs.append(readConfig(config_str))
    csv_data = []
    stress_maps = []
    seed_maps = []
    with open(input_file, "r") as file:
        reader = csv.reader(file)
        headers = next(reader)
        csv_data = [{h:x for (h,x) in zip(headers,row)} for row in reader]
    for row in csv_data:
        if str(row["stress"]).upper() == "TRUE":
            stress_maps.append(row["map"])
        if str(row["seeding"]).upper() == "TRUE":
            seed_maps.append(row["map"])
    
    if debug:
        print("Seed maps: ", seed_maps)
        print("Stress maps: ", stress_maps)
        print()

    def generate_seed_rotation(live_rotation):
        seed_temp = []
        for map in seed_maps:
            seed_temp.append(map)
        
        seed_rotation = []
        for i in range(0, min(len(seed_temp), len(live_rotation)), 1):
            seed_rotation.append("")

        # Match index
        for i in range(0, len(seed_temp), 1):
            if i > len(live_rotation):
                break
            if live_rotation[i] in seed_temp:
                seed_rotation[i] = live_rotation[i]
                seed_temp.remove(seed_rotation[i])

        # Fill in blanks by distance for dupes outside seed rotation length
        dist_tuples = []
        for map in seed_temp:
            if map in live_rotation:
                full_ind = live_rotation.index(map)
                dist_tuples.append((full_ind, map))
        dist_tuples.sort()
        for tuple in dist_tuples:
            # print(tuple, " dist ", tuple[0] - seed_rotation.index(""))
            seed_rotation[seed_rotation.index("")] = tuple[1]
            seed_temp.remove(tuple[1])

        # Fill in remaining blanks if they exist
        for i in range(0, len(seed_rotation), 1):
            if seed_rotation[i] == "" and len(seed_temp) > 0:
                seed_rotation[i] = seed_temp[0]
                seed_temp.remove(seed_temp[0])
        
        return seed_rotation

    def generate_live_rotation(csv_data):
        live_rotation = []

        def check_good_result(result):
            good_result = True
            length = len(live_rotation)
            
            if exact_dupe_dist == -1 and result in live_rotation:
                good_result = False
                if debug: print(result, " is bad [exact dupe dist == -1]")
            if not good_result: return False
            if exact_dupe_dist > -1 and result in live_rotation:
                l = length-exact_dupe_dist
                if (l < 0): l = 0
                for j in range(l, length, 1):
                    if result == live_rotation[j]:
                        good_result = False
                if debug and not good_result: print(result, " is bad [exact dupe dist > -1] ", l, length)
            if not good_result: return False

            if general_dupe_dist == -1:
                for j in range(0, length, 1):
                    if result.split("_")[0] == live_rotation[j].split("_")[0]:
                        good_result = False
                if debug and not good_result: print(result, " is bad [general dupe dist == -1]")
            if not good_result: return False
            if general_dupe_dist > -1:
                l = length-general_dupe_dist
                if (l < 0): l = 0
                for j in range(l, length, 1):
                    if result.split("_")[0] == live_rotation[j].split("_")[0]:
                        good_result = False
                if debug and not good_result: print(result, " is bad [general dupe dist > -1] ", l, length)
            if not good_result: return False

            if stress_dist == -1 and result in stress_maps:
                good_result = False
                if debug: print(result, " is bad [stress dist == -1]")
            if not good_result: return False
            if stress_dist > -1 and result in stress_maps and length > 0:
                l = length-stress_dist
                if (l < 0): l = 0
                for j in range(l, length, 1):
                    if live_rotation[j] in stress_maps:
                        good_result = False
                if debug and not good_result: print(result, " is bad [stress dist > -1] ", l, length)
            if not good_result: return False

            if nonstress_dist == -1 and result not in stress_maps:
                good_result = False
                if debug: print(result, " is bad [nonstress dist == -1]")
            if not good_result: return False
            if nonstress_dist > -1 and result not in stress_maps and length > 0:
                l = length-nonstress_dist
                if (l < 0): l = 0
                for j in range(l, length, 1):
                    if live_rotation[j] not in stress_maps:
                        good_result = False
                if debug and not good_result: print(result, " is bad [nonstress dist == -1] ", l, length)
            if not good_result: return False

            return good_result
        
        for config in configs:
            if debug: print()

            picked = []
            map_options = []
            map_weights = []
            for row in csv_data:
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
            
            if exact_dupe_dist == -1:
                amount = min(len(map_options), amount)

            if debug:
                print("Config [",
                      "str=", config.str,
                      " range=", config.range,
                      " w=", config.warfare,
                      " d=", config.day,
                      " n=", config.night,
                      " o=", config.offensive,
                      " g=", config.axis,
                      " u=", config.allies,
                      "]", sep='')
                print("Map options: ", map_options)
                print("Map weights: ", map_weights)
            
            for i in range(0, amount, 1):
                if debug: print("Picking", i, "of", amount)
                while True and len(map_options) > 0:
                    result = random.choices(map_options, weights=map_weights, k=1)[0];
                    good_result = check_good_result(result)
                    
                    any_good_results = False
                    for map in map_options:
                        if check_good_result(map):
                            any_good_results = True
                    
                    if good_result:
                        if debug: print(result, ' is good')
                        picked.append(result)
                        live_rotation.append(result)

                        if exact_dupe_dist == -1: 
                            result_index = map_options.index(result)
                            del map_options[result_index]
                            del map_weights[result_index]
                        break
                    if not any_good_results:
                        if debug: print("No more good results possible, stopping early.")
                        break
            
            if debug: print("Picked: ", picked)

        return live_rotation
    
    print()
    live_rotation = generate_live_rotation(csv_data)
    if format == 'ini':
        print_ini_copy_paste("Live", live_rotation, stress_maps=[])
    else:
        print_json_copy_paste("Live", live_rotation, stress_maps=[])
    
    if make_seed_rotation:
        seed_rotation = generate_seed_rotation(live_rotation)
        if format == 'ini':
            print_ini_copy_paste("Seed", seed_rotation, stress_maps=[])
        else:
            print_json_copy_paste("Seed", seed_rotation, stress_maps=[])


if __name__ == "__main__":
    main(sys.argv[1:])
