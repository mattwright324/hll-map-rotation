# Map Rotation Generator

Generate random weighted map rotations for the hll_rcon_tool

## Usage

```sh
$ ./new_rotation.py -cs "5w 1o 5w 1o"
$ ./new_rotation.py -cs "7-8wd 1wn 2og"
$ ./new_rotation.py -cs "11w"
$ ./new_rotation.py -ncs "8a"
```

### Options

- `-n` or  `--no-weight` generate the list with no weight.
- `-d` or `--allow-dupes` allow exact duplicates in the list. disabled by default
    - Example: two *carentan_warfare* in the list
- `-g` or `--disable-general-dupes` allow general duplicates in the list. enabled by default
    - Example: two *carentan* of any type in the list
- `-x` or `--allow-consecutive` allow consecutive of the same general map. disabled by default
    - Example: *foy_warfare* followed by *foy_warfare_night*
	- Dependent on allowed duplicate options
- `-c "<config>"` or  `--config "<config>"` advanced specify generated config by number/range/type
    - `#` static amount
	- `#-#` range amount
	- `a` all modes/variants
    - `w` warfare mode. includes both variants by default
		- `d` day variant
		- `n` night variant
	- `o` offensive mode. includes both variants by default
	    - `g` axis attacking variant
		- `u` allies attacking variant
- `-s` or `--seed` generate ideal seeding rotation based on the generated rotation
    - Tries to make sure duplicates/consecutives do not happen or are far enough apart when changing from seeding to live rotations.