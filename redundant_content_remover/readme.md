# redundant content remover

<p align="center">
    <a href="https://github.com/sbzgen/discogs-csv-collection-import/blob/main/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <a>
        <img alt="GitHub" src="https://img.shields.io/badge/python-3.7%2B-blue">
    </a>
</p>

## Features

- Removes redundant files in source content path
- Compares hashes, not just file names

## Requirements

- Python >= 3.7

## Usage
```shell
$ __main__.py -cf path/to/your/maps/content -ca path/to/your/games/content
```
## cli options
**all are required**
* `-cf` `--content_for`: (string) content folder to remove redundant files from
* `-ca` `--content_against`: (string) content folder to compare to (ie: `custom` when folder structure is `custom/models`)

## Author

[**sbzgen**](https://github.com/sbzgen)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.