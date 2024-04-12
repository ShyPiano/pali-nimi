# pali nimi
## a tool to generate names
generate names based on toki pona's phonotactics  
can be used to help name characters, worlds, pets, etc

## instalation
this python script was made using python 3.10  
might work on other python3 versions as well

to install, simply clone this repository:  
```bash
git clone https://github.com/ShyPiano/pali-nimi.git
```

## usage
in the repository's directory, run the following command:  
```bash
python3 palinimi.py 2 3
```
this will print out all possible valid toki pona names with 2 to 3 syllables  

you can pick the minimum and maximum number of syllables, but large numbers will
take a long time to generate due to the exponential growth of possible syllable
permutations  
and long names probably aren't too good anyway

you can optionally exclude toki pona vocabulary, restrict words to match a regex,
and set how often words are randomly dropped  
doing this will constrain the amount of words outputted to more manageable numbers  
learn how by viewing the help message:  
```bash
python3 palinimi.py -h
```

you can also use this as a module for other python scripts
```python
import palinimi
```

## contributing
feel free to  
just fork the repository, make your changes in a new branch, commit and make a pull request

## License
pali nimi is licensed under the [mit license](LICENSE)

