# prop_static scaler

<p align="center">
    <a href="https://github.com/sbzgen/discogs-csv-collection-import/blob/main/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <a>
        <img alt="GitHub" src="https://img.shields.io/badge/python-3.7%2B-blue">
    </a>
</p>

## Features

- Scales prop_statics that have `uniformscale` key with one command
- Automatically replaces model references in .vmf

## Requirements

- Python >= 3.7
- [Crowbar](https://steamcommunity.com/groups/CrowbarTool)

`CrowbarCommandLineDecomp.exe` must be placed in your game's bin folder.

## Usage
```shell
$ __main__.py -vmf_in path/to/your/map.vmf -vmf_out out.vmf -models_in path/to/your/content -models_out path/to/your/content_output -bin path/to/your/game/bin
```
## cli options
**all are required**
* `-vmf_in`: (string) `*.vmf` to use
* `-vmf_out`: (string) file path/name to output edited `.vmf` to
* `-models_in`: (string) content folder to pull models from (ie: `custom` when folder structure is `custom/models`)
* `-models_out`: (string) folder to store decompiled models in, make this as short as possible [1]
* `-bin`: (string) bin folder for tools, ie: `steamapps/common/GarrysMod/bin`

[1] - content model paths can be very long and file paths in windows are limited to 255 characters

## Author

[**sbzgen**](https://github.com/sbzgen)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.