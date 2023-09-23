# Map Rotation Generator

Generate random weighted map rotations for the hll_rcon_tool

## Usage

```sh
# 9 warfares in a row with default settings with seed rotation
$ ./new_rotation.py -s -c "9w"

# 9 warfares with extended stress distance printed for the MapRotation.ini file
$ ./new_rotation.py -c "9w" -r 2 -f "ini"

# 9 warfares with finer stress/nonstress control
$ ./new_rotation.py -s -c "1ws 4wt 1ws 1wt 1ws 1wt" -r 0

# all 13 unique maps alternating stress and nonstress
$ ./new_rotation.py -c "13w" -t 1 -r 1

# alternate warfare and offensive with default settings
$ ./new_rotation.py -c "1w 1o 1w 1o 1w 1o"

# rotation for the new update using only the new maps. tweak dupe and stress options
$ ./new_rotation.py -c "1w 1og 1w 1ou 1w 1ou" -i "update14_maps.csv" -e 1 -g 1

# night maps only. most are stress so set stress distance to 0
$ ./new_rotation.py -r 0 -c "5wn"

# offensive only alternating attack and defense for teams. increase stress map distance to 2
$ ./new_rotation.py -r 2 -c "3og 3ou 3og 3ou 3og 3ou"
```

### Options

- `-d` or `--debug` default off. print extra messages to debug
- `-i "<file>"` or `--input "<file>"` default `hll_rcon_maps.csv`. specify the csv file to pick maps from 
- `-n` or `--no-weight` default off. generate the list with no weighting
- `-f "<format>"` or `--format "<format>"` default `autosettings`. accepted values: `autosettings`, `ini`. how to print out the rotation
- `-e <int>` or `--exact-dupe-dist <int>` default `-1` (disabled). allow/distance of exact duplicates
    - Example: two *carentan_warfare* in the list
	- Requires at least a `general-dupe-dist` of 0 to work
- `-g <int>` or `--general-dupe-dist <int>` default `-1` (disabled). allow/distance of the same general map
	- Example: two *carentan* of any type in the list
- `-r <int>` or `--stress-dist <int>` default `1`. distance between stressful maps
	- Example: space between *remagen_warfare* and *hill400_warfare* to fill with non stressful maps
- `-t <int>` or `--nonstress-dist <int>` default `0`. distance between non-stress maps
	- Example: space between *stmariedumont_warfare* and *stmereeglise_warfare* to fill with stressful maps
- `-s` or `--seed` default off. generate an ideal seeding rotation based off the generated rotation to prevent or distance duplicate maps when going from seed to live
- `-c "<config>"` or  `--config "<config>"` default `7w 2o`. advanced specify generated config by number/range/type
    - `#` static amount
	- `#-#` range amount
	- `a` all modes/variants
    - `w` warfare mode. includes both variants by default
		- `d` day variant
		- `n` night variant
	- `o` offensive mode. includes both variants by default
	    - `g` axis attacking variant
		- `u` allies attacking variant
	- `s` stress map
	- `t` nonstress map