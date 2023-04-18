# Map Rotation Generator

Generate random weighted map rotations for the hll_rcon_tool

## Usage

```sh
$ ./new_rotation.py -c "4w 1-2o"
$ ./new_rotation.py -c "3-5w 1-2o 1-2w 1o"
$ ./new_rotation.py -nc "8a"
```

### Options

- `-w` or  `--weight` generate the list with weight. enabled by default
- `-n` or  `--no-weight` generate the list with no weight.
- `-d` or `--allow-dupes` allow duplicates in the list. disabled by default
- `-x` or `--allow-consecutive` allow consecutive of the same general map. disabled by default
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
