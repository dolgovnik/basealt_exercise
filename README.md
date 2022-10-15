# Basealt test exersise

Test exersise for interview in Basealt company

## Technical details

Class **basealt.Branch** is used to download binary package data for repository branch. It downloads binary package data for every supported archetecture for specified branch and keeps it in special structures for future comparsion with anothed **basealt.Branch** object.  
**basealt_cli.py** is command line interface utility which wraps **basealt.Branch** functionality and performs filtering of comparsion results.

### Comparsion results
Comparsion result has the following json structure:
```
{
    "current_branch": "sisyphus",  
    "compared_to_branch": "p10",  
    "result": {  
        "noarch": {  
            "added": [
                [
                    "CFR",
                    "0.151"
                ],

                     ],
            "removed": [
                [
                    "1c-preinstall",
                    "8.3"
                ],...
                       ],
            "updated": [
                [
                    "GraphicsMagick-ImageMagick-compat",
                    "1.3.38",
                    "1.3.36"
                ],...
                      ],
            "suspicious": [
                [
                    "universal-ctags",
                    "5.9.20211017.0",
                    "p5.9.20201115.0"
                ],...
                          ]
                  },
        "x86_64": {....
                  },...
             }
```
### Requirements
The following python packages should be instaled before usage of this script: `asyncio`, `aiohttp`

## Usage
Help message  
`python3 basealt_cli.py -h`

Get all archetectures for branch **p10**:  
`python3 basealt_cli.py getarchs p10`

Compare packages in two branches **sisyphus** and **p10**:  
`python3 basealt_cli.py compare sisyphus p10`

Compare packages in two branches **sisyphus** and **p10**, but show results for **x86_64** and **noarch** archetectures
and only **added** and **updated** packages:  
`python3 basealt_cli.py compare sisyphus p10 -t added updated -a x86_64 noarch`
